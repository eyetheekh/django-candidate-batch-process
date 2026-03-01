from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response(
        {
            "health": reverse("health", request=request),
            "auth_login": reverse("api_login", request=request),
            "auth_refresh": reverse("token_refresh", request=request),
            "candidates": reverse("candidate-list", request=request),
        }
    )


urlpatterns = [
    path("", api_root, name="api_root"),
    path("health/", include("api.health.urls")),
    path("auth/", include("api.auth.urls")),
    path("candidates/", include("api.candidates.urls")),
]
