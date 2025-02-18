from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def validate_phone_number_len(phone_number_value: str):
    if len(phone_number_value) != 12:
        error_string = "Phone number must be exactly 12 characters long."
        logger.error(error_string)
        raise ValidationError(
            error_string
        )


def validate_phone_number_is_digit(phone_number_value: str):
    if not phone_number_value.isdigit():
        error_string = "Phone number must contain only numbers."
        logger.error(error_string)
        raise ValidationError(error_string)
