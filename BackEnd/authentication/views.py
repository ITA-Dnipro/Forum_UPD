import logging

from rest_framework_simplejwt.views import TokenObtainPairView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
    @swagger_auto_schema(
        operation_description="Register as a new user with email, password, name, surname, and company details",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                're_password': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'surname': openapi.Schema(type=openapi.TYPE_STRING),'captcha': openapi.Schema(type=openapi.TYPE_STRING, description="CAPTCHA token (optional)"),
                'company': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_registered': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'is_startup': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'is_fop': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                    required=['name', 'is_registered', 'is_startup', 'is_fop']
                )
            },
            required=['email', 'password', 're_password', 'name', 'surname', 'company'],
        ),
        responses={
            201: openapi.Response(
                description="User registration successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'surname': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
            ),
            400: "Bad request (validation error or missing fields)",
        }
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
