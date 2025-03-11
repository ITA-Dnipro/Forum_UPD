from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()


# Load environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379/0")

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]
)

# Configure periodic task for Celery Beat
celery.conf.beat_scheduler = "redbeat.RedBeatScheduler"
celery.conf.redbeat_lock_key = None  # Disable locking issues



celery.conf.timezone = "UTC"
