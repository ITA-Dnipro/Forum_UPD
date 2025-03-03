# database.py
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from app.models import NewsModel
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017/news")

async def init_db():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client['news']
    await init_beanie(database=db, document_models=[NewsModel])
