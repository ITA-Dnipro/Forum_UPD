from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

def verify_recaptcha(token):
    """
    Validates the reCAPTCHA token with Google's API.
    """
    recaptcha_url = settings.RECAPTCHA_URL

    private_key = settings.RECAPTCHA_V2_PRIVATE_KEY
    if not private_key:
        logger.error("reCAPTCHA private key is missing or None.")
        return False

    recaptcha_data = {
        "secret": private_key,
        "response": token,
    }

    try:
        response = requests.post(recaptcha_url, data=recaptcha_data)
        result = response.json()

        if response.status_code != 200:
            logger.error("reCAPTCHA verification failed with status code %d", response.status_code)
            return False

        if result.get("success", False):
            logger.info("reCAPTCHA validation successful.")
        else:
            logger.warning("reCAPTCHA validation failed: %s", result.get("error-codes", "Unknown error"))

        return result.get("success", False)

    except requests.exceptions.RequestException as e:
        logger.error("Error occurred while verifying reCAPTCHA: %s", e)
        return False
