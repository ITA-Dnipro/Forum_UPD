# app/schemas/reaction.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class PostReactionRequest(BaseModel):
    """Request to add a reaction to a post"""
    user_id: int
    is_like: bool 

class PostReactionResponse(BaseModel):
    """Reply to add/remove reaction"""
    post_id: UUID
    user_id: int
    is_like: bool
    created_at: datetime

class PostReactionSummary(BaseModel):
    """Summary of post reactions"""
    likes_count: int
    dislikes_count: int
    current_user_reaction: Optional[bool] = None 

class LikedPostInfo(BaseModel):
    """Information about the liked post to display in lists"""
    post_id: UUID
    title: str
    created_at: datetime

class DislikedPostInfo(BaseModel):
    """Information about the liked post to display in lists"""
    post_id: UUID
    title: str
    created_at: datetime

class PostReactionRemoveRequest(BaseModel):
    user_id: int