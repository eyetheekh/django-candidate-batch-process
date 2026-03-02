from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "role", "is_active", "is_staff", "created_at")
    search_fields = ("email",)
    list_filter = ("role", "is_active", "created_at")
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("password"):
            obj.set_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)
