from django.contrib import admin
from .models import BatchRun


@admin.register(BatchRun)
class BatchRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant_id",
        "scheduled_for",
        "started_at",
        "finished_at",
        "batch_size",
        "success_count",
        "failed_count",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    search_fields = ("status", "id", "tenant_id", "batch_size")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
