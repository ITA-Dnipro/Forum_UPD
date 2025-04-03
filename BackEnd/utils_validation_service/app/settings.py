import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_DIR = Path(__file__).resolve().parent
LOG_DIR = SERVICE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'error.log'

if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

if not LOG_FILE.exists():
    LOG_FILE.touch()


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
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "utils_validation_service": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


