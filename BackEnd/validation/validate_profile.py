from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from profiles.models import Profile
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def validate_profile(user_email):
    user = User.objects.filter(email=user_email, is_active=False).first()
    if (
        user
        and Profile.objects.filter(
            person=user, is_deleted=True, status=Profile.BLOCKED
        ).first()
    ):
        error_string = "Profile has been blocked."
        logger.error(error_string)
        raise ValidationError(error_string)
