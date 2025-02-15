import logging

from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import(
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)


from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer
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
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserRegistrationSerializer(user).data
            logger.info("User created successfully")
            return Response(user_data, status=status.HTTP_201_CREATED)
        logger.error(f"Unexpected error occurred: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
