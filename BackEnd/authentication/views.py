import logging
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, get_user_model, logout
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    signer
)
from validation.validate_password import (
    validate_password_long,
    validate_password_include_symbols,
    validate_password_strength)

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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


def get_email_from_request(group, request):
    """
    Retrieve the email address from the request data, falling back to the client's IP address.
    Parameters:
        group: Unused parameter required by django-ratelimit.
        request: The Django HttpRequest object containing request data and metadata.
    Returns:
        str: The email address from the request data if present; otherwise, the client's IP address.
    """
    return request.data.get('email') or request.META.get('REMOTE_ADDR')


class PasswordResetRequestView(APIView):
    """
    API view to handle password reset requests. The view is protected by a rate limiting decorator, which restricts requests based on the email
    (or IP address, if email is absent) to one request per minute. Exceeding the limit results in a
    429 (Too Many Requests) response.

    Responses:
        200 OK:
            - If the email exists: a reset link is sent to the user.
            - If the email does not exist: a generic message is returned.
        400 Bad Request:
            - If the request data is invalid.
        429 Too Many Requests:
            - If the rate limit is exceeded.
        500 Internal Server Error:
            - If an unexpected error occurs during processing.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Request a password reset by providing your email address.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User\'s email address'),
            },
            required=['email'],
        ),
        responses={
            200: openapi.Response(
                description="Password reset email sent successfully",
                examples={
                    "application/json": {
                        "message": "The link for password reset was sent. Please, check your mail."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid email or user not found",
                examples={
                    "application/json": {
                        "error": "User does not exist."
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "error": "An unexpected error occurred."
                    }
                }
            ),
        }
    )
    @method_decorator(ratelimit(key=get_email_from_request, rate="1/m", method='POST', block=False))
    def post(self, request):
        if getattr(request, 'limited', False):
            return Response({"error": "Too many requests. Please, try again later."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Password reset request validation failed.")
            return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.info("Password reset requested for non-existent email.")
            return Response(
                {"message": "If an account with that email exists, a password reset link was sent."},
                status=status.HTTP_200_OK
            )

        try:
            token = signer.sign(f"{user.pk}:{user.password}")
            reset_link = f"https://frontend.com/reset-password/{token}/"
            send_mail(
                subject="Password Reset Request",
                message=f"Please, click on the following link for password reset: {reset_link}",
                from_email="noreply@example.com",
                recipient_list=[email],
            )
            logger.info("Password reset email sent.")
            return Response({"message": "If an account with that email exists, a password reset link was sent."},
                            status=status.HTTP_200_OK)

        except Exception:
            logger.error("Failed to send password reset email due to an unexpected error.")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    """
    API view to confirm password reset.

    This view processes POST requests containing a password reset token and a new password.
    It validates the provided token—expected to be a signed string that includes the user's ID
    and current password hash—and checks that the new password meets defined security requirements.

    Token Validation:
        - The token is unsinged and validated with a maximum age (e.g., 3600 seconds).
        - If the token is invalid, expired, or its format is incorrect, the view returns a 400 response.

    Password Validation:
        - The view applies validators to ensure the new password meets length, symbol, and strength requirements.
        - If the new password fails any validation, a 400 error is returned with a generic message
          indicating that the new password does not meet security requirements.

    On successful validation, the user's password is updated and a 200 OK response is returned with
    a confirmation message. Otherwise, a 400 Bad Request response is returned.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Confirm password reset by providing the token and new password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token received via email'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password for the account'),
            },
            required=['token', 'new_password'],
        ),
        responses={
            200: openapi.Response(
                description="Password reset successful",
                examples={
                    "application/json": {
                        "message": "The password was updated successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid or expired token",
                examples={
                    "application/json": {
                        "error": "Token is invalid or expired."
                    }
                }
            ),
        }
    )
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            unsign_value = signer.unsign(token, max_age=3600)
            parts = unsign_value.split(":")
            if len(parts) != 2:
                raise ValueError("Invalid token format.")
            user_id, password_hash = parts
            user = User.objects.get(pk=user_id)

            if user.password != password_hash:
                raise ValueError("Token is no longer valid.")
        except Exception:
            return Response(
                {"error": "Token is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        custom_errors = []
        try:
            validate_password_long(new_password)
        except ValidationError:
            custom_errors.append("Password does not meet length requirements.")
        try:
            validate_password_include_symbols(new_password)
        except ValidationError:
            custom_errors.append("Password must include symbols.")
        try:
            validate_password_strength(new_password)
        except ValidationError:
            custom_errors.append("Password is not strong enough.")

        if custom_errors:
            error_message = "new password does not meet security requirements: " + " ".join(custom_errors)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "The password was updated successfully."},
            status=status.HTTP_200_OK
        )


class PasswordChangeView(APIView):
    """
    API view to change the password of an authenticated user.

    This view handles POST requests that allow an authenticated user to update their password.
    It expects three fields in the request body:
        - old_password: The user's current password.
        - new_password: The new password the user wants to set.
        - confirm_password: Confirmation of the new password.

    Validation:
        - Verifies that the old_password matches the user's current password.
        - Checks that the new_password meets all defined security requirements
          (such as minimum length, inclusion of symbols, and overall strength).
        - Ensures that new_password and confirm_password match.

    Responses:
        200 OK:
            Returns a success message confirming that the password was updated.
        400 Bad Request:
            Returns an error message if the provided data is invalid or if there is a mismatch
            between the new passwords.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change the password of an authenticated user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Current password'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                   description='Confirmation of the new password'),
            },
            required=['old_password', 'new_password', 'confirm_password'],
        ),
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                examples={
                    "application/json": {
                        "message": "Password was updated successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input or password mismatch",
                examples={
                    "application/json": {
                        "error": "Old password is incorrect."
                    }
                }
            ),
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logout(request)
            return Response({"message": "Password was updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
