# app/schemas/post.py
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class CategoryInfo(BaseModel):
    id: UUID
    name: str

class TagInfo(BaseModel):
    id: UUID
    name: str

class Image(BaseModel):
    url: str

class CommentReplyCreate(BaseModel):
    author_id: int
    content: str

class CommentReplyResponse(BaseModel):
    id: UUID
    author_id: int
    content: str
    created_at: datetime
    likes: int
    dislikes: int

class PostCommentCreate(BaseModel):
    author_id: int
    content: str

class PostCommentUpdate(BaseModel):
    content: Optional[str] = None
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    replies: Optional[List[CommentReplyCreate]] = None

class PostCommentResponse(BaseModel):
    id: UUID
    author_id: int
    content: str
    created_at: datetime
    likes: int
    dislikes: int
    replies: List[CommentReplyResponse]

class PostCreate(BaseModel):
    author_id: int
    title: str
    content: str
    categories: Optional[List[CategoryInfo]] = []
    tags: Optional[List[TagInfo]] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    categories: Optional[List[CategoryInfo]] = None
    tags: Optional[List[TagInfo]] = None

class PostResponse(BaseModel):
    post_id: UUID
    author_id: int
    title: str
    content: str
    images: List[Image]
    categories: List[CategoryInfo]
    tags: List[TagInfo]
    likes_count: int
    dislikes_count: int
    saves_count: int
    comments: List[PostCommentResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

class PostByAuthor(BaseModel):
    post_id: UUID
    title: str
    created_at: datetime

class CommentReplyUpdate(BaseModel):
    author_id: Optional[int] = None
    content: Optional[str] = None

class SavePostRequest(BaseModel):
    user_id: int

class UnsavePostRequest(BaseModel):
    user_id: int


class PostByAuthorEnhanced(BaseModel):
    post_id: UUID
    title: str
    content: str
    images: List[Image] = []
    categories: List[CategoryInfo] = []
    tags: List[TagInfo] = []
    likes_count: int = 0
    dislikes_count: int = 0
    saves_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
