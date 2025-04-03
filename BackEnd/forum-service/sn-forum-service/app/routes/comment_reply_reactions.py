# app/routes/comment_reply_reactions.py
from fastapi import APIRouter, HTTPException, Path, Query, Body
from app.services.cassandra import get_session
from app.schemas.comment_reply_reaction import CommentReplyReactionRequest, CommentReplyReactionResponse, CommentReplyReactionSummary
from uuid import UUID
from datetime import datetime
import logging
from cassandra.query import BatchStatement, BatchType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/",
    response_model=CommentReplyReactionResponse,
    summary="Add a Reaction to a Comment Reply",
    description="Adds a like or dislike reaction to a specific reply on a comment.",
    response_description="The reaction object with its details."
)
async def add_comment_reply_reaction(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reply_id: UUID = Path(..., description="The UUID of the reply"),
    reaction: CommentReplyReactionRequest = Body(..., description="Request body with user_id and is_like")
):
    session = await get_session()
    
    reply = session.execute(
        "SELECT * FROM comment_replies WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
        (post_id, comment_id, reply_id)
    ).one()
    
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    created_at = datetime.utcnow()
    
    batch = BatchStatement(batch_type=BatchType.LOGGED)
    
    if reaction.is_like:
        
        existing_like = session.execute(
            "SELECT user_id FROM comment_reply_likes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
            (post_id, comment_id, reply_id, reaction.user_id)
        ).one()
        
        if existing_like:
            raise HTTPException(status_code=400, detail="User already liked this reply")

        existing_dislike = session.execute(
            "SELECT user_id FROM comment_reply_dislikes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
            (post_id, comment_id, reply_id, reaction.user_id)
        ).one()
        
        if existing_dislike:
            
            batch.add(
                "DELETE FROM comment_reply_dislikes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
                (post_id, comment_id, reply_id, reaction.user_id)
            )
            
            new_dislikes = max(0, reply.dislikes - 1)
            batch.add(
                "UPDATE comment_replies SET dislikes = %s WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
                (new_dislikes, post_id, comment_id, reply_id)
            )
        
        batch.add(
            "INSERT INTO comment_reply_likes (post_id, comment_id, reply_id, user_id, created_at) VALUES (%s, %s, %s, %s, %s)",
            (post_id, comment_id, reply_id, reaction.user_id, created_at)
        )
        
        batch.add(
            "UPDATE comment_replies SET likes = %s WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
            (reply.likes + 1, post_id, comment_id, reply_id)
        )
    else:
        
        existing_dislike = session.execute(
            "SELECT user_id FROM comment_reply_dislikes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
            (post_id, comment_id, reply_id, reaction.user_id)
        ).one()
        
        if existing_dislike:
            raise HTTPException(status_code=400, detail="User already disliked this reply")

        existing_like = session.execute(
            "SELECT user_id FROM comment_reply_likes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
            (post_id, comment_id, reply_id, reaction.user_id)
        ).one()
        
        if existing_like:
            
            batch.add(
                "DELETE FROM comment_reply_likes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
                (post_id, comment_id, reply_id, reaction.user_id)
            )
            
            new_likes = max(0, reply.likes - 1)
            batch.add(
                "UPDATE comment_replies SET likes = %s WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
                (new_likes, post_id, comment_id, reply_id)
            )
        
        batch.add(
            "INSERT INTO comment_reply_dislikes (post_id, comment_id, reply_id, user_id, created_at) VALUES (%s, %s, %s, %s, %s)",
            (post_id, comment_id, reply_id, reaction.user_id, created_at)
        )
        
        batch.add(
            "UPDATE comment_replies SET dislikes = %s WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
            (reply.dislikes + 1, post_id, comment_id, reply_id)
        )
    
    session.execute(batch)

    return CommentReplyReactionResponse(
        post_id=post_id,
        comment_id=comment_id,
        reply_id=reply_id,
        user_id=reaction.user_id,
        is_like=reaction.is_like,
        created_at=created_at
    )

@router.delete(
    "/",
    response_model=dict,
    summary="Remove a Reaction from a Comment Reply",
    description="Removes a user’s like or dislike reaction from a specific reply.",
    response_description="A confirmation message with details of the removed reaction."
)
async def remove_comment_reply_reaction(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reply_id: UUID = Path(..., description="The UUID of the reply"),
    request: CommentReplyReactionRequest = Body(..., description="Request body with user_id and is_like")
):
    session = await get_session()
    
    reply = session.execute(
        "SELECT * FROM comment_replies WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
        (post_id, comment_id, reply_id)
    ).one()
    
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    batch = BatchStatement(batch_type=BatchType.LOGGED)
    reaction_removed = False
    
    if request.is_like:
        
        existing_like = session.execute(
            "SELECT user_id FROM comment_reply_likes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
            (post_id, comment_id, reply_id, request.user_id)
        ).one()
        
        if existing_like:
            
            batch.add(
                "DELETE FROM comment_reply_likes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
                (post_id, comment_id, reply_id, request.user_id)
            )
            
            new_likes = max(0, reply.likes - 1)
            batch.add(
                "UPDATE comment_replies SET likes = %s WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
                (new_likes, post_id, comment_id, reply_id)
            )
            
            reaction_removed = True
    else:
        
        existing_dislike = session.execute(
            "SELECT user_id FROM comment_reply_dislikes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
            (post_id, comment_id, reply_id, request.user_id)
        ).one()
        
        if existing_dislike:
            
            batch.add(
                "DELETE FROM comment_reply_dislikes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
                (post_id, comment_id, reply_id, request.user_id)
            )
            
            new_dislikes = max(0, reply.dislikes - 1)
            batch.add(
                "UPDATE comment_replies SET dislikes = %s WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
                (new_dislikes, post_id, comment_id, reply_id)
            )
            
            reaction_removed = True

    if not reaction_removed:
        raise HTTPException(status_code=400, detail="No reaction found to remove")
    
    session.execute(batch)
    
    return {
        "message": "Reaction removed successfully",
        "post_id": str(post_id),
        "comment_id": str(comment_id),
        "reply_id": str(reply_id),
        "user_id": request.user_id
    }

@router.get(
    "/summary",
    response_model=CommentReplyReactionSummary,
    summary="Get Comment Reply Reaction Summary",
    description="Retrieves the total likes, dislikes, and current user’s reaction for a specific reply.",
    response_description="A summary of reactions for the reply."
)
async def get_comment_reply_reaction_summary(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reply_id: UUID = Path(..., description="The UUID of the reply"),
    user_id: int = Query(None, description="The ID of the user to check their reaction (optional)")
):
    session = await get_session()
    
    reply = session.execute(
        "SELECT likes, dislikes FROM comment_replies WHERE post_id = %s AND comment_id = %s AND reply_id = %s",
        (post_id, comment_id, reply_id)
    ).one()
    
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    current_user_reaction = None
    
    if user_id is not None:
        
        like = session.execute(
            "SELECT user_id FROM comment_reply_likes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
            (post_id, comment_id, reply_id, user_id)
        ).one()
        
        if like:
            current_user_reaction = True
        else:
            
            dislike = session.execute(
                "SELECT user_id FROM comment_reply_dislikes WHERE post_id = %s AND comment_id = %s AND reply_id = %s AND user_id = %s",
                (post_id, comment_id, reply_id, user_id)
            ).one()
            
            if dislike:
                current_user_reaction = False

    return CommentReplyReactionSummary(
        likes_count=reply.likes if reply.likes is not None else 0,
        dislikes_count=reply.dislikes if reply.dislikes is not None else 0,
        current_user_reaction=current_user_reaction
    )