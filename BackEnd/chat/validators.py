import bleach
from django.core.exceptions import ValidationError

def custom_validator_that_escapes_xss(value):
    """
    Sanitizes input to remove potentially harmful HTML/JS.
    """
    cleaned_value = bleach.clean(value)  # Remove harmful scripts while allowing safe HTML
    if value != cleaned_value:
        raise ValidationError("Invalid characters detected. Potential XSS attack prevented.")
    return cleaned_value
