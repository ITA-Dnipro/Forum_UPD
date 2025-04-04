# app/schemas/comment_reply_reaction.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class CommentReplyReactionRequest(BaseModel):
    """Request to add a reaction to a comment reply"""
    user_id: int
    is_like: bool 

class CommentReplyReactionResponse(BaseModel):
    """Reply to add a reaction"""
    post_id: UUID
    comment_id: UUID
    reply_id: UUID
    user_id: int
    is_like: bool
    created_at: datetime

class CommentReplyReactionSummary(BaseModel):
    """Response Summary"""
    likes_count: int
    dislikes_count: int
    current_user_reaction: Optional[bool] = None  