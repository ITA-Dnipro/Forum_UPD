# app/schemas/post.py
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class Category(BaseModel):
    id: int
    name: str

class Tag(BaseModel):
    id: int
    name: str

class PostCreate(BaseModel):
    author_id: int
    title: str
    content: str
    categories: Optional[List[Dict[str,str]]] = []
    tags: Optional[List[Dict[str,str]]] = []

class PostResponse(BaseModel):
    post_id: int
    author_id: int
    title: str
    content: str
    categories: Optional[List[Dict[str,str]]] = []
    tags: Optional[List[Dict[str,str]]] = []
    views_count: int
    likes_count: int
    created_at: datetime

class PostList(BaseModel):
    post_id: int
    title: str
    author_id: int
    created_at: datetime
