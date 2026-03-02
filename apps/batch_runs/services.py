import requests
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from django.conf import settings
from apps.candidates.models import Candidate
from apps.batch_runs.models import BatchRun, CandidateAttempt


EXTERNAL_API_URL = getattr(settings, 'EXTERNAL_BATCH_API_URL', "http://127.0.0.1:8001/batch/process")
MAX_BATCH_SIZE = int(getattr(settings, 'MAX_BATCH_SIZE', 10))
PICK_TIMEOUT_MINUTES = int(getattr(settings, 'PICK_TIMEOUT_MINUTES', 10))


def run_external_batch():
    """
    Core batch engine.
    Can be called from:
        - Scheduler (Celery)
        - Manual trigger API
    """

    now = timezone.now()
    stale_pick_time = now - timedelta(minutes=PICK_TIMEOUT_MINUTES)

    with transaction.atomic():
        # Release stale locks (safe restart)
        Candidate.objects.filter(picked_at__lt=stale_pick_time).update(picked_at=None)

        # Lock eligible rows
        candidates = (
            Candidate.objects.select_for_update(skip_locked=True)
            .filter(
                Q(status="PENDING") | Q(status="FAILED"),
                is_deleted=False,
                picked_at__isnull=True,
            )
            .order_by("created_at")[:MAX_BATCH_SIZE]
        )

        candidates = list(candidates)

        if not candidates:
            return None

        # Mark picked
        for c in candidates:
            c.picked_at = now
            c.save(update_fields=["picked_at"])

        batch = BatchRun.objects.create(
            status=BatchRun.RunStatus.RUNNING,
            scheduled_for=now,
            started_at=now,
            batch_size=len(candidates),
        )

    # Call external API outside transaction
    payload = [
        {
            "id": str(c.id),
            "name": c.name,
            "email": c.email,
            "phoneNumber": c.phone_number,
            "link": c.link,
            "dob": c.dob.strftime("%d/%m/%Y") if c.dob else None,
        }
        for c in candidates
    ]

    try:
        response = requests.post(EXTERNAL_API_URL, json=payload, timeout=20)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException:
        _fail_batch(batch, candidates)
        raise

    _process_results(batch, candidates, results)
    return batch


def _fail_batch(batch, candidates):
    with transaction.atomic():
        batch.status = BatchRun.RunStatus.FAILED
        batch.finished_at = timezone.now()
        batch.save()

        Candidate.objects.filter(id__in=[c.id for c in candidates]).update(
            picked_at=None
        )


def _process_results(batch, candidates, results):

    result_map = {r["id"]: r["status"] for r in results}

    success_count = 0
    failed_count = 0

    with transaction.atomic():
        for c in candidates:
            result_status = result_map.get(c.id, "FAILED")

            c.attempt_count += 1
            c.last_attempt_at = timezone.now()
            c.picked_at = None

            if result_status == "SUCCESS":
                c.status = "SUCCESS"
                success_count += 1
            else:
                c.status = "FAILED"
                failed_count += 1

            c.save()

            CandidateAttempt.objects.create(
                candidate=c,
                batch_run=batch,
                attempt_no=c.attempt_count,
                result_status=result_status,
            )

        total = success_count + failed_count

        if failed_count == 0:
            final_status = BatchRun.RunStatus.COMPLETED
        elif success_count == 0:
            final_status = BatchRun.RunStatus.FAILED
        else:
            final_status = BatchRun.RunStatus.PARTIAL

        batch.success_count = success_count
        batch.failed_count = failed_count
        batch.total_processed = total
        batch.status = final_status
        batch.finished_at = timezone.now()
        batch.save()
