# database.py
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
from app.models import NewsModel
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "news")
MAX_POOL_SIZE = int(os.getenv("MAX_POOL_SIZE", 10))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    try:

        client = AsyncIOMotorClient(
            MONGO_URL,
            maxPoolSize=MAX_POOL_SIZE
            )
        
        db = client[MONGO_DB_NAME]
        await init_beanie(database=db, document_models=[NewsModel])
        logger.info("Database connection established and Beanie initialized successfully.")
        
    
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise Exception(f"An error occurred while initializing the database: {e}")
