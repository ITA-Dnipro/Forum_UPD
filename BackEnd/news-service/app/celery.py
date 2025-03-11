from celery import Celery
import os
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry
from dotenv import load_dotenv

load_dotenv()


# Load environment variables
REDIS_URL_BROKER = os.getenv("REDIS_URL_BROKER", "redis://redis_cache:6379/0")
REDIS_URL_BACKEND = os.getenv("REDIS_URL_BACKEND", "redis://redis_cache:6379/1")


celery = Celery(
    "tasks",
    broker=REDIS_URL_BROKER,
    backend=REDIS_URL_BACKEND,
    include=["app.tasks"]
)

celery.conf.update(
    {
        "beat_scheduler": "redbeat.RedBeatScheduler",  # Use RedBeat scheduler
        "redbeat_redis_url": REDIS_URL_BROKER,  # Ensure RedBeat uses the broker Redis
        "timezone": "UTC",
    }
)

# Define a periodic task
entry = RedBeatSchedulerEntry(
    "scrape_news_task",
    "app.tasks.scrape_news_task",
    crontab(minute="*"),  # Runs every minute
    app=celery,
)
entry.save()  # Save the task in Redis