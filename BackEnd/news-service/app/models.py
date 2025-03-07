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
        collection = "news"
        json_encoders = {
            ObjectId: str,
        }
        arbitrary_types_allowed = True

