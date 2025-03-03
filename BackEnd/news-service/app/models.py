from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from beanie import Document


class NewsBase(BaseModel):
    """Base model for news data validation."""
    title: str
    content: str
    link: str
    published_at: datetime = Field(default_factory=datetime.now)


class NewsModel(NewsBase, Document):
    """MongoDB document model for news storage."""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    class Settings:
        collection = "news"
