from django.utils.timezone import now
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

class DjoserTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            logger.error(f"Invalid token")
            raise AuthenticationFailed("Invalid token")

        if token.created <= now() - settings.TOKEN_EXPIRATION_TIME:
            logger.warning(f"Token expired for user {token.user}. Deleting token.")
            token.delete()
            raise AuthenticationFailed(
                "Your session has expired. Please login again."
            )
        return token.user, token
