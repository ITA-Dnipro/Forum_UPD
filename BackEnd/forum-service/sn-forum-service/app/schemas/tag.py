# app/schemas/tag.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TagCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TagResponse(BaseModel):
    tag_id: UUID
    name: str
    description: Optional[str]
    posts_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None 