import re
from django.core.exceptions import ValidationError


def validate_password_long(password_value: str):
    if len(password_value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if len(password_value) > 128:
        raise ValidationError("The password must not exceed 128 characters.")


def validate_password_include_symbols(password_value: str):
    if (
        not any(char.isupper() for char in password_value)
        or not any(char.islower() for char in password_value)
        or not any(char.isdigit() for char in password_value)
    ):
        raise ValidationError(
            "Password must include at least one uppercase letter (A-Z), one lowercase letter (a-z) and one digit (0-9)."
        )


def validate_password_strength(password_value: str):
    """
    Validates the strength of the password by checking for:
    - Special characters
    - Common or easily guessable passwords
    - Predictable sequences or repeated characters
    Raises ValidationError if the password is weak.
    """
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password_value):
        raise ValidationError(
            "Password must include at least one special character (e.g., !@#$%^&*)."
        )

    common_passwords = [
        "123456", "password", "qwerty", "admin", "letmein", "12345678", "123123", "111111"
    ]

    if password_value.lower() in common_passwords:
        raise ValidationError(
            "Password is too common or easily guessable."
        )

    sequences = [
        "1234", "2345", "3456", "4567", "5678", "6789", "7890",
        "abcd", "bcde", "cdef", "defg", "efgh", "fghi", "ghij",
        "qwert", "werty", "ertyui", "rtyui", "tyuio", "yuiop",
    ]

    for seq in sequences:
        if seq in password_value.lower():
            raise ValidationError(
                "Password contains predictable sequences."
            )

    # Check for sequences (e.g., "abcd", "1234")
    if re.search(r'(.)\1{2,}', password_value):
        raise ValidationError(
            "Password contains repeated characters."
        )
