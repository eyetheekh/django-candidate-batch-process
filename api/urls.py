from django.urls import path, include

urlpatterns = [
    path("health/", include("api.health.urls")),
    path("auth/", include("api.auth.urls")),
    path("candidates/", include("api.candidates.urls")),
]
