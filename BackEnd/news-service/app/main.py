# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import router
from app.celery import setup_periodic_tasks
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()

        setup_periodic_tasks()
        logger.info("Periodic tasks registered successfully.")
        yield
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise Exception("Database initialization failed, please check the logs for more details.") from e
  
    
app = FastAPI(lifespan=lifespan)


app.include_router(router, prefix="/api")