import uuid
from django.db import models
from django.utils import timezone


class CandidateStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"


# Soft delete queryset
class CandidateQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class CandidateManager(models.Manager):
    def get_queryset(self):
        return CandidateQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        return CandidateQuerySet(self.model, using=self._db)


# Candidate Model
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

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # managers
    objects = CandidateManager()  # hides deleted
    all_objects = models.Manager()  # includes deleted

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            # Optimized index for batch processor
            models.Index(fields=["status", "picked_at", "is_deleted"]),
        ]

    # Soft delete helpers
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def __str__(self):
        return f"{self.email} ({self.status})"
