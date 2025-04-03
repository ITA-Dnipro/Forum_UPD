from .settings import *

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

RATE_LIMIT_MAX_CALLS = 1  # Maximum number of calls allowed
RATE_LIMIT_PERIOD = 5    # Time window in seconds (600 seconds = 10 minutes)

KAFKA_PRODUCER_ENABLED = False
