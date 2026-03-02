from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .serializers import LoginSerializer, LogoutSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={205: None},
        description="Blacklist refresh token (JWT logout)",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            # Token already blacklisted or invalid
            return Response(
                {"detail": "Token already blacklisted."},
                status=status.HTTP_205_RESET_CONTENT,
            )

        return Response(
            {"detail": "Logged out successfully"},
            status=status.HTTP_205_RESET_CONTENT,
        )
