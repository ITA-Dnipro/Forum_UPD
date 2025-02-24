import datetime
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def validate_foundation_year_range(foundation_year_value: int) -> None:
    if not (
        foundation_year_value
        in range(1800, (datetime.datetime.now().year + 1))
    ):
        error_string = "Foundation year must be exactly in range 1800-current year."
        logging.error(error_string)
        raise ValidationError(
            error_string
        )
