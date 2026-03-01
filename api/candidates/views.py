from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status

from apps.candidates.models import Candidate
from .serializers import CandidateSerializer
from api.permissions import IsAdminOrReadOnly


class CandidateViewSet(ModelViewSet):
    """
    ADMIN: full access
    REVIEWER: read-only
    """

    queryset = Candidate.objects.all().order_by("-created_at")
    serializer_class = CandidateSerializer
    permission_classes = [IsAdminOrReadOnly]