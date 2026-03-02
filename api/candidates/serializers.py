from rest_framework import serializers
from django.db import models
from apps.candidates.models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    # disable default unique email validator for status code: 409 compatability
    email = serializers.EmailField(validators=[])

    class Meta:
        model = Candidate
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "link",
            "dob",
            "status",
            "picked_at",
            "attempt_count",
            "last_attempt_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "picked_at",
            "attempt_count",
            "last_attempt_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        link = attrs.get("link")

        if link and not link.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                {"link": "URL must start with http:// or https://"}
            )

        return attrs

class CandidateStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PASSED = "PASSED", "Passed"
    FAILED = "FAILED", "Failed"
    REVIEW = "REVIEW", "Under Review"

class CandidateSearchSerializer(serializers.ModelSerializer):
    currentStatus = serializers.ChoiceField(
        source="status",
        choices=CandidateStatus.choices,
        read_only=True,
    )
    attemptCount = serializers.IntegerField(source="attempt_count", read_only=True)
    lastAttemptAt = serializers.DateTimeField(
        source="last_attempt_at",
        allow_null=True,
        read_only=True,
    )

    class Meta:
        model = Candidate
        fields = [
            "id",
            "name",
            "email",
            "link",
            "dob",
            "phone_number",
            "currentStatus",
            "attemptCount",
            "lastAttemptAt",
        ]
        read_only_fields = fields