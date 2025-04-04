# app/schemas/comment_reaction.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class CommentReactionRequest(BaseModel):
    """Request to add a reaction to a comment"""
    user_id: int
    is_like: bool 

class CommentReactionResponse(BaseModel):
    """Reply to add a reaction"""
    post_id: UUID
    comment_id: UUID
    user_id: int
    is_like: bool
    created_at: datetime

class CommentReactionSummary(BaseModel):
    """Comment Reaction Summary"""
    likes_count: int
    dislikes_count: int
    current_user_reaction: Optional[bool] = None 