from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer


def build_auth_response(user):
    """Creates the authentication response with token and user data."""
    token, _ = Token.objects.get_or_create(user=user)

    return {
        "token": token.key,
        "username": user.username,
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(APIView):
    """Endpoint for new user registration."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Processes registration and returns a token."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                build_auth_response(user),
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Endpoint for user login."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticates user and returns a token."""
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password"),
        )

        if user:
            return Response(build_auth_response(user), status=status.HTTP_200_OK)

        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )