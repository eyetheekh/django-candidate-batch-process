from django.db import models
from apps.candidates.models import Candidate


class BatchRun(models.Model):
    class RunStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        PARTIAL = "PARTIAL", "Partial Success"

    status = models.CharField(
        max_length=15, choices=RunStatus.choices, default=RunStatus.PENDING
    )

    scheduled_for = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    batch_size = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    total_processed = models.IntegerField(default=0)

    is_deleted = models.BooleanField(default=False)
    tenant_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BatchRun {self.id} [{self.status}] - {self.scheduled_for}%"


class CandidateAttempt(models.Model):
    class ResultStatus(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    batch_run = models.ForeignKey(
        BatchRun, on_delete=models.CASCADE, related_name="attempts"
    )

    attempt_no = models.PositiveIntegerField(default=1)
    result_status = models.CharField(max_length=10, choices=ResultStatus.choices)
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)
    tenant_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return f"Attempt {self.attempt_no} for {self.candidate_id} in batch {self.batch_run_id}"
