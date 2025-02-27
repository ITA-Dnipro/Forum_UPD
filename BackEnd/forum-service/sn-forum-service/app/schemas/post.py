# app/schemas/post.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class Category(BaseModel):
    id: int
    name: str

class Tag(BaseModel):
    id: int
    name: str

class PostCreate(BaseModel):
    author_id: int
    title: str = Field(..., min_length=3, max_length=255)

    content: str = Field(..., min_length=10)

    categories: Optional[List[Category]] = []
    tags: Optional[List[Tag]] = []

class PostResponse(BaseModel):
    post_id: int
    author_id: int
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    
    categories: Optional[List[Category]] = []
    tags: Optional[List[Tag]] = []

    views_count: int = Field(0, ge=0)  
    likes_count: int = Field(0, ge=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostList(BaseModel):
    post_id: int
    title: str = Field(..., min_length=3, max_length=200)
    author_id: int
created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))