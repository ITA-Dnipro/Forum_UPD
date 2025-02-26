from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from app.services.cassandra import get_session
from app.schemas.post import PostCreate, PostResponse, PostList
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[PostList])
async def list_posts(
    limit: int = 10,
    author_id: Optional[int] = None
):
    try:
        session = get_session()
        
        if author_id:
            query = "SELECT post_id, title, author_id, created_at FROM blog_posts WHERE author_id = %s ALLOW FILTERING"
            rows = session.execute(query, [author_id])
        else:
            query = "SELECT post_id, title, author_id, created_at FROM blog_posts LIMIT %s"
            rows = session.execute(query, [limit])
        
        return [
            {
                "post_id": row.post_id,
                "title": row.title,
                "author_id": row.author_id,
                "created_at": row.created_at
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching posts: {str(e)}"
        )