from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def validate_password_long(password_value: str):
    if len(password_value) < 8:
        error_string = "Password must be at least 8 characters long."
        logger.error(error_string)
        raise ValidationError(error_string)
    if len(password_value) > 128:
        error_string = "The password must not exceed 128 characters"
        logger.error(error_string)
        raise ValidationError(error_string)


def validate_password_include_symbols(password_value: str):
    if (
        not any(char.isupper() for char in password_value)
        or not any(char.islower() for char in password_value)
        or not any(char.isdigit() for char in password_value)
    ):
        error_string = "Password must include at least one uppercase letter (A-Z), one lowercase letter (a-z) and one digit (0-9)."
        logger.error(error_string)
        raise ValidationError(
            error_string
        )
