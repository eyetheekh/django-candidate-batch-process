from rest_framework import serializers
from apps.batch_runs.models import BatchRun


class BatchRunSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = BatchRun
        fields = "__all__"

    def get_duration_seconds(self, obj):
        if obj.started_at and obj.finished_at:
            return (obj.finished_at - obj.started_at).total_seconds()
        return None
