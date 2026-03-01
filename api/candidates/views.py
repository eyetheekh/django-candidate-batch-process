from rest_framework.viewsets import ModelViewSet
from apps.candidates.models import Candidate
from .serializers import CandidateSerializer
from api.permissions import IsAdminOrReadOnly
from api.exceptions import AlreadyExistsConflictException


class CandidateViewSet(ModelViewSet):
    """
    ADMIN: full access
    REVIEWER: read-only
    """

    queryset = Candidate.objects.all().order_by("-created_at")
    serializer_class = CandidateSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        email = serializer.validated_data.get("email")
        if Candidate.objects.filter(email=email).exists():
            raise AlreadyExistsConflictException(
                "Candidate with this email already exists."
            )
        serializer.save()

    def perform_update(self, serializer):
        email = serializer.validated_data.get("email")
        qs = Candidate.objects.filter(email=email).exclude(pk=serializer.instance.pk)
        if qs.exists():
            raise AlreadyExistsConflictException(
                "Candidate with this email already exists."
            )
        serializer.save()
