from django.urls import path
from .views import (
    StatusMetricsReportView,
    StuckCandidatesReportView,
)

urlpatterns = [
    path(
        "status-metrics/",
        StatusMetricsReportView.as_view(),
        name="status-metrics-report",
    ),
    path(
        "stuck-candidates/",
        StuckCandidatesReportView.as_view(),
        name="stuck-candidates-report",
    ),
]
