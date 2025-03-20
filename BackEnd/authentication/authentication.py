from django.utils.timezone import now
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
from jwt import decode as jwt_decode

logger = logging.getLogger(__name__)


class DjoserTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            logger.error(f"Invalid token")
            raise AuthenticationFailed("Invalid token")

        if token.created <= now() - settings.TOKEN_EXPIRATION_TIME:
            logger.warning(
                f"Token expired for user {token.user}. Deleting token."
            )
            token.delete()
            raise AuthenticationFailed(
                "Your session has expired. Please login again."
            )
        return token.user, token


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Authenticates the user using JWT token.
        Handles cases where the token is missing, expired, or invalid.
        """
        header = self.get_header(request)

        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)

            if not user.is_active:
                raise AuthenticationFailed("User account is deactivated.")

            return user, validated_token

        except (InvalidToken, TokenError) as e:
            raise AuthenticationFailed(f"Invalid or expired token: {str(e)}")
        except AuthenticationFailed as e:
            raise AuthenticationFailed(
                f"Authentication failed. Please log in again: {str(e)}"
            )
        except Exception as e:
            raise AuthenticationFailed(
                f"An error occurred during authentication: {str(e)}"
            )


User = get_user_model()


class JWTAuthMiddleware:
    """Middleware to authenticate user for channels"""

    def __init__(self, app):
        """Initializing the app."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Authenticate the user based on jwt."""
        close_old_connections()
        try:

            # Decode the query string and get token parameter from it.
            token = self.get_token_from_scope(scope)
            # Decode the token to get the user id from it.
            if token is None:
                scope["user"] = AnonymousUser()
                return await self.app(scope, receive, send)
            data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # Get the user from database based on user id and add it to the scope.
            scope["user"] = await self.get_user(data["user_id"])
        except (
            TypeError,
            KeyError,
            InvalidSignatureError,
            ExpiredSignatureError,
            DecodeError,
        ):
            # Set the user to Anonymous if token is not valid or expired.
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        """Return the user based on user id."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

    def get_token_from_scope(self, scope):
        headers = dict(scope.get("headers", []))

        auth_header = headers.get(b"authorization", b"").decode("utf-8")

        if auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        else:
            return None


def JWTAuthMiddlewareStack(app):
    """This function wrap channels authentication stack with JWTAuthMiddleware."""
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
