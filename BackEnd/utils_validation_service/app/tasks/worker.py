from app.celery_config import celery_app
from app.selenium_validation import validate_code

@celery_app.task
def validate_code_task(code):
    return validate_code(code)
