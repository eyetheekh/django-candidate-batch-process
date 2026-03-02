from datetime import datetime, time
from django.utils import timezone
from rest_framework import serializers


class StatusMetricsQuerySerializer(serializers.Serializer):
    from_ = serializers.DateField(required=False)
    to = serializers.DateField(required=False)
    groupBy = serializers.ChoiceField(
        choices=["day", "week"],
        required=False,
        default="day",
    )
    includeDomains = serializers.BooleanField(required=False, default=False)

    def to_internal_value(self, data):
        data = data.copy()
        if "from" in data:
            data["from_"] = data.pop("from")
        return super().to_internal_value(data)

    def validate(self, attrs):
        from_date = attrs.get("from_")
        to_date = attrs.get("to")

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError(
                {"to": "Must be greater than or equal to 'from'."}
            )
        return attrs

    def get_datetime_range(self):
        validated = self.validated_data

        from_date = validated.get("from_")
        to_date = validated.get("to")

        from_dt = None
        to_dt = None

        if from_date:
            from_dt = timezone.make_aware(datetime.combine(from_date, time.min))

        if to_date:
            to_dt = timezone.make_aware(datetime.combine(to_date, time.max))

        return from_dt, to_dt


class StuckCandidatesQuerySerializer(serializers.Serializer):
    minAttempts = serializers.IntegerField(required=False, default=3)
    failedHours = serializers.IntegerField(required=False, default=6)
    pendingHours = serializers.IntegerField(required=False, default=12)

    def validate(self, attrs):
        if attrs["minAttempts"] < 0:
            raise serializers.ValidationError({"minAttempts": "Must be >= 0"})
        if attrs["failedHours"] < 0:
            raise serializers.ValidationError({"failedHours": "Must be >= 0"})
        if attrs["pendingHours"] < 0:
            raise serializers.ValidationError({"pendingHours": "Must be >= 0"})
        return attrs
