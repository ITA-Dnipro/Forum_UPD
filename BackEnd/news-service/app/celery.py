from celery import Celery
import os
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry
from dotenv import load_dotenv

load_dotenv()


REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379/0")



celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]
)

celery.conf.update(
    {
        "beat_scheduler": "redbeat.RedBeatScheduler",
        "redbeat_redis_url": REDIS_URL,
        "timezone": "UTC",
        "task_serializer": "json",  # Recommended for compatibility
        "result_serializer": "json",
        "accept_content": ["json"],  # Ensure Celery accepts JSON payloads only
        "worker_concurrency": 2,  # Set concurrency level (adjust based on workload)
    }
)

def setup_periodic_tasks():
    """Creates and saves RedBeatSchedulerEntry only when explicitly called."""
    entry = RedBeatSchedulerEntry(
        "scrape_news_task",
        "app.tasks.scrape_news_task",
        crontab(minute=0, hour="14,17,20,23"),  # Runs every day in 12:00, 15:00, 18:00, 21:00
        app=celery,
    )
    entry.save()