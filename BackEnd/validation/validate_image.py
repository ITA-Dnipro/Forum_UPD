from django.core.exceptions import ValidationError
from PIL import Image
import logging

logger = logging.getLogger(__name__)

Image.MAX_IMAGE_PIXELS = None

MAX_ALLOWED_BANNER_IMAGE_SIZE = 5 * 1024 * 1024
MAX_ALLOWED_LOGO_IMAGE_SIZE = 1 * 1024 * 1024


def validate_image_format(image: Image):
    valid_formats = ["PNG", "JPEG"]
    with Image.open(image) as img:
        format_ = img.format
        if format_ not in valid_formats:
            error_string = "Unsupported image format. Only PNG and JPEG are allowed."
            logger.error(error_string)
            raise ValidationError(
                error_string
            )


def validate_banner_size(image_file):
    max_size = image_file.size
    if max_size > MAX_ALLOWED_BANNER_IMAGE_SIZE:
        error_string = "Image size exceeds the maximum allowed (5MB)."
        logger.error(error_string)
        raise ValidationError(error_string)


def validate_logo_size(image_file):
    max_size = image_file.size
    if max_size > MAX_ALLOWED_LOGO_IMAGE_SIZE:
        error_string = "Image size exceeds the maximum allowed (1MB)."
        logger.error(error_string)
        raise ValidationError(error_string)
