# app/routes/comment_replies.py
from fastapi import APIRouter, HTTPException, Path, Body
from app.services.cassandra import get_session
from app.schemas.post import CommentReplyCreate, CommentReplyResponse, CommentReplyUpdate  
from uuid import UUID, uuid4
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/{post_id}/comments/{comment_id}/replies",
    response_model=CommentReplyResponse,
    summary="Create a Reply",
    description="Adds a new reply to a specific comment on a blog post.",
    response_description="The created reply object with its details."
)
async def create_reply(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reply: CommentReplyCreate = Body(..., description="Request body with author_id and content")
):
    session = await get_session()
    try:
        post_row = session.execute("SELECT post_id FROM blog_posts WHERE post_id = %s", (post_id,)).one()
        if not post_row:
            raise HTTPException(status_code=404, detail="Post not found")
            
        comment_row = session.execute(
            "SELECT comments FROM blog_posts WHERE post_id = %s", (post_id,)
        ).one()
        
        comment_exists = False
        if comment_row and comment_row.comments:
            for comment in comment_row.comments:
                if comment.get('id') == comment_id:
                    comment_exists = True
                    break
        
        if not comment_exists:
            raise HTTPException(status_code=404, detail="Comment not found")

        reply_id = uuid4()
        created_at = datetime.utcnow()
        
        session.execute(
            """
            INSERT INTO comment_replies (
                post_id, comment_id, reply_id, author_id, content, created_at, likes, dislikes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (post_id, comment_id, reply_id, reply.author_id, reply.content, created_at, 0, 0)
        )
        
        logger.info(f"Reply created: post_id={post_id}, comment_id={comment_id}, reply_id={reply_id}")
        
        return CommentReplyResponse(
            id=reply_id,
            author_id=reply.author_id,
            content=reply.content,
            created_at=created_at,
            likes=0,
            dislikes=0
        )
    except Exception as e:
        logger.error(f"Error creating reply: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error creating reply: {str(e)}")

@router.get(
    "/{post_id}/comments/{comment_id}/replies/{reply_id}",
    response_model=CommentReplyResponse,
    summary="Get a Reply by ID",
    description="Retrieves a specific reply to a comment by its UUID.",
    response_description="The requested reply object with its details."
)
async def get_reply(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reply_id: UUID = Path(..., description="The UUID of the reply to retrieve")
):
    session = await get_session()
    try:
        
        reply_row = session.execute(
            """
            SELECT * FROM comment_replies 
            WHERE post_id = %s AND comment_id = %s AND reply_id = %s
            """,
            (post_id, comment_id, reply_id)
        ).one()
        
        if not reply_row:
            raise HTTPException(status_code=404, detail="Reply not found")
        
        return CommentReplyResponse(
            id=reply_row.reply_id,
            author_id=reply_row.author_id,
            content=reply_row.content,
            created_at=reply_row.created_at,
            likes=reply_row.likes,
            dislikes=reply_row.dislikes
        )
    except Exception as e:
        logger.error(f"Error getting reply: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error getting reply: {str(e)}")

@router.put(
    "/{post_id}/comments/{comment_id}/replies/{reply_id}",
    response_model=CommentReplyResponse,
    summary="Update a Reply",
    description="Updates the author_id or content of an existing reply.",
    response_description="The updated reply object with its details."
)
async def update_reply(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reply_id: UUID = Path(..., description="The UUID of the reply to update"),
    reply_update: CommentReplyUpdate = Body(..., description="Request body with updated fields")
):
    session = await get_session()
    try:
        
        reply_row = session.execute(
            """
            SELECT * FROM comment_replies 
            WHERE post_id = %s AND comment_id = %s AND reply_id = %s
            """,
            (post_id, comment_id, reply_id)
        ).one()
        
        if not reply_row:
            raise HTTPException(status_code=404, detail="Reply not found")
        
        update_parts = []
        params = []
        
        if reply_update.author_id is not None:
            update_parts.append("author_id = %s")
            params.append(reply_update.author_id)
            
        if reply_update.content is not None:
            update_parts.append("content = %s")
            params.append(reply_update.content)
            
        if not update_parts:
            return CommentReplyResponse(
                id=reply_row.reply_id,
                author_id=reply_row.author_id,
                content=reply_row.content,
                created_at=reply_row.created_at,
                likes=reply_row.likes,
                dislikes=reply_row.dislikes
            )
        
        query = f"""
        UPDATE comment_replies 
        SET {", ".join(update_parts)}
        WHERE post_id = %s AND comment_id = %s AND reply_id = %s
        """
        
        params.extend([post_id, comment_id, reply_id])
        
        session.execute(query, params)
        
        updated_reply = session.execute(
            """
            SELECT * FROM comment_replies 
            WHERE post_id = %s AND comment_id = %s AND reply_id = %s
            """,
            (post_id, comment_id, reply_id)
        ).one()
        
        return CommentReplyResponse(
            id=updated_reply.reply_id,
            author_id=updated_reply.author_id,
            content=updated_reply.content,
            created_at=updated_reply.created_at,
            likes=updated_reply.likes,
            dislikes=updated_reply.dislikes
        )
    except Exception as e:
        logger.error(f"Error updating reply: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error updating reply: {str(e)}")
    
    
@router.delete(
    "/{post_id}/comments/{comment_id}/replies/{reply_id}",
    summary="Delete a Reply",
    description="Removes a reply from a comment by its UUID.",
    response_description="A confirmation message with the deleted reply’s UUID."
)
async def delete_reply(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reply_id: UUID = Path(..., description="The UUID of the reply to delete")
):
    session = await get_session()
    try:
        
        reply_row = session.execute(
            """
            SELECT reply_id FROM comment_replies 
            WHERE post_id = %s AND comment_id = %s AND reply_id = %s
            """,
            (post_id, comment_id, reply_id)
        ).one()
        
        if not reply_row:
            raise HTTPException(status_code=404, detail="Reply not found")
        
        session.execute(
            """
            DELETE FROM comment_replies 
            WHERE post_id = %s AND comment_id = %s AND reply_id = %s
            """,
            (post_id, comment_id, reply_id)
        )
        
        return {"message": "Reply deleted", "reply_id": str(reply_id)}
    except Exception as e:
        logger.error(f"Error deleting reply: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error deleting reply: {str(e)}")

@router.get(
    "/{post_id}/comments/{comment_id}/replies",
    response_model=list[CommentReplyResponse],
    summary="List Replies",
    description="Retrieves all replies to a specific comment on a blog post.",
    response_description="A list of reply objects."
)
async def list_replies(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment")
):
    session = await get_session()
    try:
        
        replies = session.execute(
            """
            SELECT * FROM comment_replies 
            WHERE post_id = %s AND comment_id = %s
            """,
            (post_id, comment_id)
        ).all()
        
        result = [
            CommentReplyResponse(
                id=r.reply_id,
                author_id=r.author_id,
                content=r.content,
                created_at=r.created_at,
                likes=r.likes,
                dislikes=r.dislikes
            )
            for r in replies
        ]
        
        return result
    except Exception as e:
        logger.error(f"Error getting replies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting replies: {str(e)}")