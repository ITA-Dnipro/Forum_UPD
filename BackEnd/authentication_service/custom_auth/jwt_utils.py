import jwt
from datetime import datetime
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError


def validate_jwt(token):
    """
    Validate JWT token:
      - Check the signature using SECRET_KEY from settings
      - Check the expiration of the token
    Returns:
      - Payload the dict with data or an error message
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        exp = payload.get('exp')
        if not exp or datetime.utcfromtimestamp(exp) < datetime.utcnow():
            return None, 'Token has expired'
        if 'roles' not in payload:
            payload['roles'] = 'Public'
        return payload, None
    except ExpiredSignatureError:
        return None, 'Token has expired'
    except (InvalidSignatureError, DecodeError) as e:
        return None, str(e)


def get_user_role_from_payload(payload):
    """
    Get the user role from payload.
    """
    return payload.get('roles', 'Public')
