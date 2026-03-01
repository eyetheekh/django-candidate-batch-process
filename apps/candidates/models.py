import uuid
from django.db import models


class CandidateStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"


class Candidate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # form
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    link = models.URLField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    # processing states
    status = models.CharField(
        max_length=20,
        choices=CandidateStatus.choices,
        default=CandidateStatus.PENDING,
        db_index=True,
    )
    picked_at = models.DateTimeField(null=True, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.status})"
