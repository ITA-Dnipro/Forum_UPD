from django.core.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)

def validate_rnokpp(rnokpp: str):
    if len(rnokpp) != 10 or not rnokpp.isdecimal():
        error_string = "RNOKPP must be exactly 10 digits long."
        logger.error(error_string)
        raise ValidationError(error_string)
    value_for_validation = [int(i) for i in rnokpp]
    # Weight coefficients for calculating the checksum key
    weight_coeff_base = [-1, 5, 7, 9, 4, 6, 10, 5, 7]
    # Calculate the checksum key using the first 9 digits of RNOKPP code and weight coefficients.
    key = (
        sum(weight_coeff_base[i] * value_for_validation[i] for i in range(9))
        % 11
    ) % 10
    # Validate the RNOKPP by comparing the calculated checksum key with its last digit.
    if key == value_for_validation[-1]:
        return True
    else:
        error_string = "RNOKPP is not correct, checksum key is not valid."
        logger.error(error_string)
        raise ValidationError(
            error_string
        )
