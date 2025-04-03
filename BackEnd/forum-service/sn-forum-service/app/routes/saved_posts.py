# app/routes/saved_posts.py

import base64
from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, Path, Query
from app.schemas.pagination import PaginatedResponse
from app.services.cassandra import get_session
from app.schemas.post import CategoryInfo, CommentReplyResponse, Image, PostCommentResponse, PostResponse, SavePostRequest, TagInfo, UnsavePostRequest
from uuid import UUID
from typing import Optional
import logging
from cassandra.query import SimpleStatement

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/",
    response_model=PaginatedResponse[PostResponse],
    summary="List Saved Posts",
    description="Retrieves a paginated list of posts saved by a specific user.",
    response_description="A paginated response containing a list of saved posts and an optional next_paging_state."
)
async def get_saved_posts(
    user_id: int = Query(..., description="The ID of the user whose saved posts to retrieve"),
    page_size: int = Query(10, ge=1, le=100, description="Number of posts to return per page (1-100)"),
    paging_state: Optional[str] = Query(None, description="Base64-encoded paging state for fetching the next page")
):
    session = await get_session()
    
    query = "SELECT post_id FROM saved_posts WHERE user_id = %s"
    statement = SimpleStatement(query, fetch_size=page_size)
    
    if paging_state:
        paging_state_bytes = base64.b64decode(paging_state)
        saved_rows = session.execute(statement, (user_id,), paging_state=paging_state_bytes)
    else:
        saved_rows = session.execute(statement, (user_id,))
    
    posts = []
    for row in saved_rows:
        post_row = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (row.post_id,)).one()
        if post_row:
            valid_categories = [
                CategoryInfo(id=UUID(str(cat.get('id'))), name=str(cat.get('name', '')))
                for cat in (post_row.categories or [])
                if cat and isinstance(cat, dict) and 'id' in cat and 'name' in cat
            ]
            valid_tags = [
                TagInfo(id=UUID(str(tag.get('id'))), name=str(tag.get('name', '')))
                for tag in (post_row.tags or [])
                if tag and isinstance(tag, dict) and 'id' in tag and 'name' in tag
            ]
            valid_comments = [
                PostCommentResponse(
                    id=UUID(str(c.get('id'))) if isinstance(c.get('id'), str) else c.get('id'),
                    author_id=c.get('author_id'),
                    content=c.get('content', ''),
                    created_at=c.get('created_at'),
                    likes=c.get('likes', 0),
                    dislikes=c.get('dislikes', 0),
                    replies=[
                        CommentReplyResponse(
                            id=r.reply_id,
                            author_id=r.author_id,
                            content=r.content,
                            created_at=r.created_at,
                            likes=r.likes,
                            dislikes=r.dislikes
                        )
                        for r in session.execute(
                            "SELECT * FROM comment_replies WHERE post_id = %s AND comment_id = %s",
                            (post_row.post_id, c.get('id'))
                        ).all()
                    ]
                )
                for c in post_row.comments or []
                if c and isinstance(c, dict) and 'id' in c and 'author_id' in c
            ]
            posts.append(PostResponse(
                post_id=post_row.post_id,
                author_id=post_row.author_id,
                title=post_row.title,
                content=post_row.content,
                images=[Image(url=url) for url in post_row.images or []],
                categories=valid_categories,
                tags=valid_tags,
                likes_count=post_row.likes_count,
                dislikes_count=post_row.dislikes_count,
                saves_count=post_row.saves_count,
                comments=valid_comments,
                created_at=post_row.created_at,
                updated_at=post_row.updated_at
            ))
    
    next_paging_state = base64.b64encode(saved_rows.paging_state).decode('utf-8') if saved_rows.paging_state else None
    
    return PaginatedResponse(
        items=posts,
        next_paging_state=next_paging_state
    ) 

@router.post(
    "/{post_id}/save",
    summary="Save a Post",
    description="Saves a blog post for a specific user.",
    response_description="A confirmation message indicating the post was saved successfully."
)
async def save_post(
    post_id: UUID = Path(..., description="The UUID of the post to save"),  
    save_request: SavePostRequest = Body(..., description="Request body containing the user_id")  
):
    session = await get_session()
    try:
        
        post_row = session.execute("SELECT post_id, saves_count FROM blog_posts WHERE post_id = %s", (post_id,)).one()
        if not post_row:
            raise HTTPException(status_code=404, detail="Post not found")
            
        existing_saved = session.execute(
            """
            SELECT user_id FROM saved_posts
            WHERE user_id = %s AND post_id = %s
            """,
            (save_request.user_id, post_id)
        ).one()
        
        if existing_saved:
            raise HTTPException(status_code=409, detail="Post already saved by user")
            
        saved_at = datetime.utcnow()
        session.execute(
            """
            INSERT INTO saved_posts (user_id, post_id, saved_at)
            VALUES (%s, %s, %s)
            """,
            (save_request.user_id, post_id, saved_at)
        )
        
        new_count = post_row.saves_count + 1
        session.execute(
            """
            UPDATE blog_posts
            SET saves_count = %s
            WHERE post_id = %s
            """,
            (new_count, post_id)
        )
        
        return {"message": "Post saved successfully"}
    except Exception as e:
        logger.error(f"Error saving post: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error saving post: {str(e)}")

@router.delete(
    "/{post_id}/unsave",
    summary="Unsave a Post",
    description="Removes a blog post from a user's saved posts.",
    response_description="A confirmation message indicating the post was unsaved successfully."
)
async def unsave_post(
    post_id: UUID = Path(..., description="The UUID of the post to unsave"),  
    unsave_request: UnsavePostRequest = Body(..., description="Request body containing the user_id")
):
    session = await get_session()
    try:
        
        post_row = session.execute("SELECT post_id, saves_count FROM blog_posts WHERE post_id = %s", (post_id,)).one()
        if not post_row:
            raise HTTPException(status_code=404, detail="Post not found")
            
        existing_saved = session.execute(
            """
            SELECT user_id FROM saved_posts
            WHERE user_id = %s AND post_id = %s
            """,
            (unsave_request.user_id, post_id)
        ).one()
        
        if not existing_saved:
            raise HTTPException(status_code=404, detail="Post not saved by user")
            
        session.execute(
            """
            DELETE FROM saved_posts
            WHERE user_id = %s AND post_id = %s
            """,
            (unsave_request.user_id, post_id)
        )
        
        new_count = max(0, post_row.saves_count - 1)
        session.execute(
            """
            UPDATE blog_posts
            SET saves_count = %s
            WHERE post_id = %s
            """,
            (new_count, post_id)
        )
        
        return {"message": "Post unsaved successfully"}
    except Exception as e:
        logger.error(f"Error unsaving post: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error unsaving post: {str(e)}")