from rest_framework import serializers
from apps.candidates.models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[]) # disable default unique email validator for status code: 409 compatability
    
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
