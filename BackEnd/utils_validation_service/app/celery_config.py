import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis_cache:6379/0')
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'pyamqp://guest@rabbitmq//')

celery_app = Celery(
    "tasks",
    broker=RABBITMQ_URL,
    backend=REDIS_URL,
    include=['app.tasks.worker']
)

celery_app.autodiscover_tasks(["app.tasks.worker"])
