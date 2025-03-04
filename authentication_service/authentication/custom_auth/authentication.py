from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication


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
            raise AuthenticationFailed(f"Authentication failed. Please log in again: {str(e)}")
        except Exception as e:
            raise AuthenticationFailed(f"An error occurred during authentication: {str(e)}")