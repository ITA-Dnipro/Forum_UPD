from fastapi import APIRouter
from celery.result import AsyncResult
from celery import shared_task
from app.tasks.worker import validate_code_task
from app.celery_config import celery_app

import time

router = APIRouter()


@router.get("/validate/codes")
def validate_code(code: str):
    task = validate_code_task.delay(code)
    task_result = AsyncResult(task.id, app=celery_app)

    return {"status": task_result.get()}