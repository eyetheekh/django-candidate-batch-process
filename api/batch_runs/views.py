from django.utils import timezone
from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.batch_runs.models import BatchRun, Candidate
from .serializers import BatchRunSerializer
from ..permissions import IsAdmin, IsAdminOrReadOnly


# GET /batch-runs  (ADMIN, REVIEWER)
class BatchRunListView(generics.ListAPIView):
    """
    Paginated batch run inspection
    """

    queryset = BatchRun.objects.all().order_by("-created_at")
    serializer_class = BatchRunSerializer
    permission_classes = [IsAdminOrReadOnly]


# POST /batch-runs/trigger/  (ADMIN)
class BatchRunTriggerView(APIView):
    """
    Manually trigger one batch immediately.
    Max 10 candidates processed.
    """

    permission_classes = [IsAdmin]

    MAX_BATCH_SIZE = 10

    def post(self, request):

        # Prevent concurrent running batch
        if BatchRun.objects.filter(status="RUNNING").exists():
            return Response(
                {"detail": "A batch is already running."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch up to 10 pending candidates
        candidates = Candidate.objects.filter(status="PENDING").order_by("created_at")[
            : self.MAX_BATCH_SIZE
        ]

        if not candidates:
            return Response(
                {"detail": "No pending candidates found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            batch = BatchRun.objects.create(
                status="RUNNING",
                total_processed=0,
                success_count=0,
                failed_count=0,
                started_at=timezone.now(),
            )

            processed = 0
            success = 0
            failure = 0

            for candidate in candidates:
                # ---- Simulated processing ----
                candidate.status = "SUCCESS"
                candidate.batch = batch
                candidate.attempt_count += 1
                candidate.last_attempt_at = timezone.now()
                candidate.save()

                processed += 1
                success += 1  # replace with real logic if needed

            batch.status = "COMPLETED"
            batch.total_processed = processed
            batch.success_count = success
            batch.failed_count = failure
            batch.finished_at = timezone.now()
            batch.save()

        return Response(
            BatchRunSerializer(batch).data,
            status=status.HTTP_201_CREATED,
        )
