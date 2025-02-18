from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

def verify_recaptcha(token):
    """
    Validates the reCAPTCHA token with Google's API.
    """
    recaptcha_url = settings.RECAPTCHA_URL
    recaptcha_data = {
        "secret": settings.RECAPTCHA_V2_PRIVATE_KEY,
        "response": token,
    }
    response = requests.post(recaptcha_url, data=recaptcha_data)
    result = response.json()
    logger.info("Successful reCAPTCHA")
    return result.get("success", False)
