from django.urls import path, include

urlpatterns = [
    path("health/", include("api.health.urls")),
    path("auth/", include("api.auth.urls")),
    path("candidates/", include("api.candidates.urls")),
    path("reports/", include("api.reports.urls")),
    path("batch_runs/", include("api.batch_runs.urls")),
]
