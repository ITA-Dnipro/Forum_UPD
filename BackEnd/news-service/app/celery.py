from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()


# Load environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379/0")

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

