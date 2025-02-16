import logging

from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import(
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)

from ratelimit.decorators import RateLimitDecorator


from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserRegistrationResponseSerializer,
)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(APIView):
    @extend_schema(
        operation_id="user_register",
        summary="Register a new user",
        description="Register as a new user with email, password, name, surname, and company details.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=UserRegistrationSerializer,
                description="User registration successful",
            ),
            400: OpenApiResponse(description="Bad request (validation error or missing fields)"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    @RateLimitDecorator(
        calls=10,
        period=600,
    )
    def post(self, request):
        if getattr(request, 'limited', False):
            return Response({"detail": "Request limit exceeded."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                user_data = UserRegistrationResponseSerializer(user).data
                logger.info("User created successfully")
                return Response(user_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.error(f"Unexpected error occurred.")
            return Response({"detail": "Internal server error. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
