from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q, F, Value
from django.db.models.functions import TruncDay, TruncWeek, Substr, StrIndex
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from apps.candidates.models import Candidate
from api.permissions import IsAdminOrReadOnly
from .serializers import StatusMetricsQuerySerializer, StuckCandidatesQuerySerializer


# STATUS METRICS REPORT
class StatusMetricsReportView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    ALLOWED_PARAMS = {"from", "to", "groupBy", "includeDomains"}

    @extend_schema(
        parameters=[
            OpenApiParameter("from", OpenApiTypes.DATE),
            OpenApiParameter("to", OpenApiTypes.DATE),
            OpenApiParameter("groupBy", OpenApiTypes.STR),
            OpenApiParameter("includeDomains", OpenApiTypes.BOOL),
        ],
        description="Candidate status metrics report",
    )
    def get(self, request):

        # Strict param validation
        unknown = set(request.query_params.keys()) - self.ALLOWED_PARAMS
        if unknown:
            return Response(
                {"detail": f"Unsupported query params: {', '.join(sorted(unknown))}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StatusMetricsQuerySerializer(data=request.query_params.dict())
        serializer.is_valid(raise_exception=True)

        qs = Candidate.objects.all()

        from_dt, to_dt = serializer.get_datetime_range()

        if from_dt:
            qs = qs.filter(created_at__gte=from_dt)

        if to_dt:
            qs = qs.filter(created_at__lte=to_dt)

        group_by = serializer.validated_data["groupBy"]

        trunc = (
            TruncWeek("created_at") if group_by == "week" else TruncDay("created_at")
        )

        # Core metrics
        metrics_qs = (
            qs.annotate(period=trunc)
            .values("period")
            .annotate(
                total_created=Count("id"),
                processed=Count("id", filter=Q(status__in=["SUCCESS", "FAILED"])),
                success=Count("id", filter=Q(status="SUCCESS")),
                failure=Count("id", filter=Q(status="FAILED")),
                avg_attempts_success=Avg(
                    "attempt_count",
                    filter=Q(status="SUCCESS"),
                ),
            )
            .order_by("period")
        )

        metrics = []
        for row in metrics_qs:
            processed = row["processed"] or 0
            success = row["success"] or 0
            row["success_rate"] = success / processed if processed else 0
            metrics.append(row)

        # Retry histogram
        retry_histogram = list(
            qs.values("attempt_count")
            .annotate(count=Count("id"))
            .order_by("attempt_count")
        )

        # Top domains
        top_domains = []

        if serializer.validated_data["includeDomains"]:
            top_domains = list(
                qs.annotate(at_pos=StrIndex("email", Value("@")))
                .filter(at_pos__gt=0)
                .annotate(domain=Substr("email", F("at_pos") + 1))
                .values("domain")
                .annotate(
                    success=Count("id", filter=Q(status="SUCCESS")),
                    total=Count("id"),
                )
                .annotate(success_rate=F("success") * 1.0 / F("total"))
                .order_by("-success_rate", "-total")[:10]
            )

        return Response(
            {
                "metrics": metrics,
                "retryHistogram": retry_histogram,
                "topDomains": top_domains,
            },
            status=status.HTTP_200_OK,
        )


# STUCK CANDIDATES REPORT
class StuckCandidatesReportView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    ALLOWED_PARAMS = {"minAttempts", "failedHours", "pendingHours"}

    @extend_schema(
        parameters=[
            OpenApiParameter("minAttempts", OpenApiTypes.INT),
            OpenApiParameter("failedHours", OpenApiTypes.INT),
            OpenApiParameter("pendingHours", OpenApiTypes.INT),
        ],
        description="Detect stuck or needs-attention candidates",
    )
    def get(self, request):

        # Strict param validation
        unknown = set(request.query_params.keys()) - self.ALLOWED_PARAMS
        if unknown:
            return Response(
                {"detail": f"Unsupported query params: {', '.join(sorted(unknown))}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StuckCandidatesQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        params = serializer.validated_data

        now = timezone.now()

        failed_cutoff = now - timedelta(hours=params["failedHours"])
        pending_cutoff = now - timedelta(hours=params["pendingHours"])

        stuck_qs = Candidate.objects.filter(
            Q(
                status="FAILED",
                attempt_count__gte=params["minAttempts"],
                last_attempt_at__lte=failed_cutoff,
            )
            | Q(
                status="PENDING",
                attempt_count=0,
                created_at__lte=pending_cutoff,
            )
        ).order_by("-created_at")

        results = []

        for c in stuck_qs:
            reference_time = c.last_attempt_at or c.created_at
            age_hours = (now - reference_time).total_seconds() / 3600

            results.append(
                {
                    "attemptCount": c.attempt_count,
                    "lastAttemptAt": c.last_attempt_at,
                    "ageHours": round(age_hours, 2),
                    "lastBatchId": getattr(c, "batch_id", None),
                }
            )

        return Response(
            {"items": results},
            status=status.HTTP_200_OK,
        )
