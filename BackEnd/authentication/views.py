import logging

from django.core.signing import(
    TimestampSigner,
    BadSignature,
)
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.contrib.auth import(
  get_user_model,
  authenticate
)

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
    LogoutSerializer,
)

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

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

                signer = TimestampSigner()
                uid = str(user.pk)
                signed_token = signer.sign(uid)

                email_subject = "Account Activation"
                activation_link = f"http://localhost:8080/auth/activate/?token={signed_token}"
                email_message = render_to_string("email/custom_activation.html", {
                    'user': user,
                    'activation_link': activation_link,
                })

                send_mail(
                    email_subject,
                    email_message,
                    'noreply@example.com',
                    [user.email]
                )

                return Response(user_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.error(f"Unexpected error occurred.")
            return Response({"detail": "Internal server error. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountActivationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="activate_account",
        summary="Activate a user account",
        description="Activate a newly registered user account by providing a signed token as a query parameter.",
        parameters=[
            OpenApiParameter(
                name="token",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="The signed activation token sent via email."
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Account activated successfully.",
                response={"detail": "Account activated successfully."}
            ),
            400: OpenApiResponse(
                description="Bad request (e.g., missing or invalid token).",
                response={"error": "Invalid or expired token."}
            )
        }
    )
    def get(self, request):
        token = request.query_params.get('token')

        if not token:
            logger.error(f"No token provided.")
            return Response({"detail": "No token provided."}, status=status.HTTP_400_BAD_REQUEST)

        signer = TimestampSigner()
        try:
            uid = signer.unsign(token, max_age=3600)

            user = get_user_model().objects.get(pk=uid)

            user.is_active = True
            user.save()

            logger.info("Account activated successfully.")
            return Response({"detail": "Account activated successfully."}, status=status.HTTP_200_OK)
        except BadSignature:
            logger.error(f"Invalid or expired token.")
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        except get_user_model().DoesNotExist:
            logger.error(f"User not found.")
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="User login with email and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password'],
        ),
        responses={
            200: "Login successful",
            400: "Invalid credentials",
        }
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {"error": "Invalid password or email"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout by blacklisting the provided refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Refresh token to be blacklisted',
                    example='your_refresh_token_here',
                ),
            },
            required=['refresh'],
        ),
        responses={
            200: "Logout successful",
            400: "Invalid or missing refresh token",
        }
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            logger.error(f"Validation error: {serializer.errors},  Request Data: {request.data}")
            return Response({"error": "Access denied."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh_token = serializer.validated_data['refresh']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info("User logged out successfully.")

            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
