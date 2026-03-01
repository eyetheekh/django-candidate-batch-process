from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginAPIView, LogoutView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="api_logout"),
]
