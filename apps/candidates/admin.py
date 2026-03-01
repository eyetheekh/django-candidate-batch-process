from django.contrib import admin
from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone_number",
        "status",
        "attempt_count",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "email", "phone_number")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
