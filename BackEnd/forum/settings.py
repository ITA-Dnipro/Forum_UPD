"""
Django settings for Forum project.

Generated by "django-admin startproject" using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import mongoengine
import os
from datetime import timedelta
from pathlib import Path

from corsheaders.defaults import default_headers
from decouple import config
from dotenv import load_dotenv
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

FRONTEND_URL = "http://localhost:8080"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
    "0.0.0.0",
    config("ALLOWED_ENV_HOST"),
]
# ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "daphne",
    "channels",
    "chat.apps.ChatConfig",
    "chat_notifications.apps.ChatNotificationsConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "debug_toolbar",
    "authentication",
    "profiles",
    "administration",
    "search",
    "images",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = False

CORS_ORIGIN_WHITELIST = [
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://0.0.0.0",
    config("CORS_ORIGIN_WHITELIST"),
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://0.0.0.0",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "Access-Control-Expose-Headers",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Origin",
    "Content-Type",
]

ROOT_URLCONF = "forum.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "forum.wsgi.application"

# CELERY_BROKER_URL = config("REDIS_URL")
# CELERY_RESULT_BACKEND = config("REDIS_URL")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("PG_DB"),
        "USER": config("PG_USER"),
        "PASSWORD": config("PG_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}


load_dotenv()


mongo_db_name = os.getenv("MONGO_DB_NAME")
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = int(os.getenv("MONGO_PORT", 27017))
mongo_authentication_source = os.getenv("MONGO_AUTHENTICATION_SOURCE", "admin")


try:
    # Attempt to connect to MongoDB with values from environment variables
    mongoengine.connect(
        db=mongo_db_name,
        username=mongo_username,
        password=mongo_password,
        host=mongo_host,
        port=mongo_port,
        authentication_source=mongo_authentication_source,
    )
    logger.info("MongoDB connection successful.")
except mongoengine.errors.ConnectionError as e:
    logger.error(f"MongoDB connection error: {e}")
    raise  # Re-raise the exception after logging it to stop execution
except mongoengine.errors.OperationError as e:
    logger.error(f"MongoDB operation error: {e}")
    raise  # Re-raise the exception after logging it to stop execution
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
    raise  # Re-raise the exception after logging it to stop execution

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "public", "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "public", "media")


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "authentication.CustomUser"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Forum Project",
    "DESCRIPTION": "Forum Project",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

TOKEN_EXPIRATION_TIME = timedelta(days=14)

# SMTP
EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_USE_TLS = config("EMAIL_USE_TLS")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")


DELAY_FOR_LOGIN = 600  # delay time for login in seconds
ATTEMPTS_FOR_LOGIN = 10  # attempts for login during delay for login


def show_toolbar(request):
    return DEBUG


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "django.log"),
            "when": "W0",
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "error.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "profiles": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "authentication": {
            "handlers": ["file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "validation": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "administration": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagade": False,
        },
        "utils": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# ReCaptcha V2 Invisible
RECAPTCHA_V2_PRIVATE_KEY = config("RECAPTCHA_V2_PRIVATE_KEY")
RECAPTCHA_URL = config("RECAPTCHA_URL")

CONTACTS_INFO = {
    "email": "craft.forum0@gmail.com",
    "phone": "+38 050 234 23 23",
    "university": "Львівська Політехніка",
    "address": "вул. Степана Бандери 12, Львів",
}
DJANGO_SETTINGS_MODULE = config("DJANGO_SETTINGS_MODULE")

ASGI_APPLICATION = "forum.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}
