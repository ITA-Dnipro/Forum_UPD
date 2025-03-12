from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from beanie import Document, Indexed
from typing import Annotated


class NewsBase(BaseModel):
    """Base model for news data validation."""
    title: str
    content: str
    link: Annotated[str, Indexed(unique=True)]
    published_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic configuration to ensure correct serialization."""
        json_encoders = {
            ObjectId: str,
        }
        from_attributes = True

class NewsModel(NewsBase, Document):
    """MongoDB document model for news storage."""
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        json_encoders = {
            ObjectId: str,
        }
        arbitrary_types_allowed = True
    
    class Settings:
        collection = "news"
