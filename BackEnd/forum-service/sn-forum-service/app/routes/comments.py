# app/routes/comments.py
from fastapi import APIRouter, HTTPException, Path, Body
from app.services.cassandra import get_session
from app.schemas.post import CommentReplyResponse, PostCommentCreate, PostCommentResponse, PostCommentUpdate
from uuid import UUID, uuid4
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def safe_dict(obj):
    
    if isinstance(obj, dict):
        return {k: safe_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_dict(i) for i in obj]
    elif isinstance(obj, UUID):
        return str(obj)
    elif hasattr(obj, 'dict'):
        return safe_dict(obj.dict())
    else:
        return obj
    
@router.post(
    "/{post_id}/comments",
    response_model=PostCommentResponse,
    summary="Create a Comment",
    description="Adds a new comment to a specific blog post.",
    response_description="The created comment object with its details."
)
async def create_comment(
    post_id: UUID = Path(..., description="The UUID of the post to comment on"),
    comment: PostCommentCreate = Body(..., description="Request body with author_id and content")
):
    session = await get_session()

    existing = session.execute("SELECT post_id FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not existing:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment_id = uuid4()
    created_at = datetime.utcnow()
    
    query = """
    UPDATE blog_posts 
    SET comments = comments + [{
        id: %s, 
        author_id: %s, 
        content: %s, 
        created_at: %s, 
        likes: 0, 
        dislikes: 0, 
        replies: []
    }]
    WHERE post_id = %s
    """
    
    session.execute(
        query,
        (comment_id, comment.author_id, comment.content, created_at, post_id)
    )
    
    result = session.execute("SELECT comments FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    logger.info(f"Comments after insert: {result.comments}")
    
    return PostCommentResponse(
        id=comment_id,
        author_id=comment.author_id,
        content=comment.content,
        created_at=created_at,
        likes=0,
        dislikes=0,
        replies=[]
    )

@router.get(
    "/{post_id}/comments/{comment_id}",
    response_model=PostCommentResponse,
    summary="Get a Comment by ID",
    description="Retrieves a specific comment from a blog post by its UUID.",
    response_description="The requested comment object with its details."
)
async def get_comment(
    post_id: UUID = Path(..., description="The UUID of the post containing the comment"),
    comment_id: UUID = Path(..., description="The UUID of the comment to retrieve")
):
    session = await get_session()
    try:
        row = session.execute("SELECT comments FROM blog_posts WHERE post_id = %s", (post_id,)).one()
        if not row or not row.comments:
            raise HTTPException(status_code=404, detail="Comments not found")

        comment = next((c for c in row.comments if c["id"] == comment_id), None)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if isinstance(comment["id"], str):
            comment_id = UUID(comment["id"])
        else:
            comment_id = comment["id"]

        return PostCommentResponse(
            id=comment_id,
            author_id=comment["author_id"],
            content=comment["content"],
            created_at=comment["created_at"],
            likes=comment.get("likes", 0),
            dislikes=comment.get("dislikes", 0),
            replies=[
                CommentReplyResponse(
                    id=UUID(r["id"]) if isinstance(r["id"], str) else r["id"],
                    author_id=r["author_id"],
                    content=r["content"],
                    created_at=r["created_at"],
                    likes=r.get("likes", 0),
                    dislikes=r.get("dislikes", 0)
                )
                for r in comment.get("replies", [])
            ]
        )
    except Exception as e:
        logger.error(f"Error getting comment: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error getting comment: {str(e)}")

@router.put(
    "/{post_id}/comments/{comment_id}",
    response_model=PostCommentResponse,
    summary="Update a Comment",
    description="Updates the content, likes, dislikes, or replies of an existing comment.",
    response_description="The updated comment object with its details."
)
async def update_comment(
    post_id: UUID = Path(..., description="The UUID of the post containing the comment"),
    comment_id: UUID = Path(..., description="The UUID of the comment to update"),
    comment_update: PostCommentUpdate = Body(..., description="Request body with updated fields")
):
    session = await get_session()
    try:
        row = session.execute("SELECT comments FROM blog_posts WHERE post_id = %s", (post_id,)).one()
        if not row or not row.comments:
            raise HTTPException(status_code=404, detail="Comments not found")

        comments = row.comments
        comment_idx = next((i for i, c in enumerate(comments) if c["id"] == comment_id), -1)
        if comment_idx == -1:
            raise HTTPException(status_code=404, detail="Comment not found")

        updated_comment = dict(comments[comment_idx])
        if comment_update.content is not None:
            updated_comment["content"] = comment_update.content
        if comment_update.likes is not None:
            updated_comment["likes"] = comment_update.likes
        if comment_update.dislikes is not None:
            updated_comment["dislikes"] = comment_update.dislikes
        if comment_update.replies is not None:
            updated_comment["replies"] = [
                {
                    "id": uuid4(),
                    "author_id": r.author_id,
                    "content": r.content,
                    "created_at": datetime.utcnow(),
                    "likes": 0,
                    "dislikes": 0
                }
                for r in comment_update.replies
            ]

        query = """
        UPDATE blog_posts 
        SET comments[%s] = {
            id: %s,
            author_id: %s,
            content: %s,
            created_at: %s,
            likes: %s,
            dislikes: %s,
            replies: %s
        }
        WHERE post_id = %s
        """
        session.execute(
            query,
            (
                comment_idx,
                updated_comment["id"],
                updated_comment["author_id"],
                updated_comment["content"],
                updated_comment["created_at"],
                updated_comment["likes"],
                updated_comment["dislikes"],
                updated_comment["replies"],
                post_id
            )
        )

        verify_row = session.execute("SELECT comments FROM blog_posts WHERE post_id = %s", (post_id,)).one()
        logger.info(f"Comments after update: {verify_row.comments}")

        return PostCommentResponse(
            id=updated_comment["id"],
            author_id=updated_comment["author_id"],
            content=updated_comment["content"],
            created_at=updated_comment["created_at"],
            likes=updated_comment.get("likes", 0),
            dislikes=updated_comment.get("dislikes", 0),
            replies=[
                CommentReplyResponse(
                    id=r["id"],
                    author_id=r["author_id"],
                    content=r["content"],
                    created_at=r["created_at"],
                    likes=r.get("likes", 0),
                    dislikes=r.get("dislikes", 0)
                )
                for r in updated_comment.get("replies", [])
            ]
        )
    except Exception as e:
        logger.error(f"Error updating comment: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error updating comment: {str(e)}")
    
@router.delete(
    "/{post_id}/comments/{comment_id}",
    summary="Delete a Comment",
    description="Removes a comment from a blog post by its UUID.",
    response_description="A confirmation message with the deleted comment’s UUID."
)
async def delete_comment(
    post_id: UUID = Path(..., description="The UUID of the post containing the comment"),
    comment_id: UUID = Path(..., description="The UUID of the comment to delete")
):
    session = await get_session()
    try:
        row = session.execute("SELECT comments FROM blog_posts WHERE post_id = %s", (post_id,)).one()
        if not row or not row.comments:
            raise HTTPException(status_code=404, detail="Comments not found")

        original_count = len(row.comments)
        comments = [c for c in row.comments if c["id"] != comment_id]
        
        if len(comments) == original_count:
            raise HTTPException(status_code=404, detail="Comment not found")

        session.execute(
            """
            UPDATE blog_posts SET comments = %s WHERE post_id = %s
            """,
            (comments, post_id)
        )

        return {"message": "Comment deleted", "comment_id": str(comment_id)}
    except Exception as e:
        logger.error(f"Error deleting comment: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error deleting comment: {str(e)}")