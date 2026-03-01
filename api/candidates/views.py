from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.decorators import action
from apps.candidates.models import Candidate
from .serializers import CandidateSerializer, CandidateSearchSerializer
from api.permissions import IsAdminOrReadOnly
from api.exceptions import AlreadyExistsConflictException


class CandidateViewSet(ModelViewSet):
    queryset = Candidate.objects.all().order_by("-created_at")
    serializer_class = CandidateSerializer
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "q",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Search over name and email (partial match)",
            ),
            OpenApiParameter(
                "status",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="One or more statuses",
                many=True,
            ),
            OpenApiParameter(
                "createdFrom",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
                description="Filter candidates created after this date",
            ),
            OpenApiParameter(
                "createdTo",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
                description="Filter candidates created before this date",
            ),
            OpenApiParameter(
                "hasLink",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter by presence of link (true|false)",
            ),
            OpenApiParameter(
                "minAttempts",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Minimum attempt count",
            ),
            OpenApiParameter(
                "sort",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Sorting: recent | attempts_desc | status_then_recent",
            ),
            OpenApiParameter(
                "page",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Page number",
            ),
            OpenApiParameter(
                "pageSize",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Page size",
            ),
        ],
        responses={200: CandidateSearchSerializer(many=True)},
        description="Search candidates with filters and pagination",
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        qs = self.queryset

        # q = search over name, email
        q = request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q))

        # status = one or more statuses
        statuses = request.query_params.getlist("status")
        if statuses:
            qs = qs.filter(status__in=statuses)

        # createdFrom, createdTo
        created_from = request.query_params.get("createdFrom")
        created_to = request.query_params.get("createdTo")
        if created_from:
            qs = qs.filter(created_at__gte=created_from)
        if created_to:
            qs = qs.filter(created_at__lte=created_to)

        # hasLink
        has_link = request.query_params.get("hasLink")
        if has_link == "true":
            qs = qs.exclude(link__isnull=True).exclude(link__exact="")
        elif has_link == "false":
            qs = qs.filter(Q(link__isnull=True) | Q(link__exact=""))

        # minAttempts
        min_attempts = request.query_params.get("minAttempts")
        if min_attempts:
            qs = qs.filter(attempt_count__gte=min_attempts)

        # sort
        sort = request.query_params.get("sort")
        if sort == "recent":
            qs = qs.order_by("-created_at")
        elif sort == "attempts_desc":
            qs = qs.order_by("-attempt_count")
        elif sort == "status_then_recent":
            qs = qs.order_by("status", "-created_at")

        # pagination
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pageSize", 20))
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        qs = qs[start:end]

        serializer = CandidateSearchSerializer(qs, many=True)
        return Response(
            {
                "items": serializer.data,
                "page": page,
                "pageSize": page_size,
                "total": total,
            },
            status=status.HTTP_200_OK,
        )

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
