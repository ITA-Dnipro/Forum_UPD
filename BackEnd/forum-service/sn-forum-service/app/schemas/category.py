# app/schemas/category.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    category_id: UUID
    name: str
    description: Optional[str]
    posts_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None 