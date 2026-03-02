from celery import shared_task
from apps.batch_runs.services import run_external_batch


@shared_task(bind=True, max_retries=3)
def scheduled_external_batch(self):
    try:
        batch = run_external_batch()
        return f"Batch {batch.id}" if batch else "No candidates"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
