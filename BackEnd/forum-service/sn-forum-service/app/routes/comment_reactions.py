# app/routes/comment_reactions.py
from fastapi import APIRouter, HTTPException, Path, Body, Query
from app.services.cassandra import get_session
from app.schemas.comment_reaction import CommentReactionRequest, CommentReactionResponse, CommentReactionSummary
from uuid import UUID
from datetime import datetime
import logging
import copy  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/",
    response_model=CommentReactionResponse,
    summary="Add a Reaction to a Comment",
    description="Adds a like or dislike reaction to a comment on a blog post.",
    response_description="The reaction object with its details."
)
async def add_comment_reaction(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    reaction: CommentReactionRequest = Body(..., description="Request body with user_id and is_like")
):
    session = await get_session()
    
    post = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not post or not post.comments:
        raise HTTPException(status_code=404, detail="Post or comments not found")
    
    comment_exists = False
    comments = copy.deepcopy(post.comments) 
    comment_index = None
    
    for i, c in enumerate(comments):
        if c and isinstance(c, dict) and str(c.get("id")) == str(comment_id):
            comment_exists = True
            comment_index = i
            break
    
    if not comment_exists:
        raise HTTPException(status_code=404, detail="Comment not found")

    created_at = datetime.utcnow()
    
    if reaction.is_like:
        
        existing_like = session.execute(
            "SELECT user_id FROM comment_likes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
            (post_id, comment_id, reaction.user_id)
        ).one()
        
        if existing_like:
            raise HTTPException(status_code=400, detail="User already liked this comment")

        existing_dislike = session.execute(
            "SELECT user_id FROM comment_dislikes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
            (post_id, comment_id, reaction.user_id)
        ).one()
        
        if existing_dislike:
            
            session.execute(
                "DELETE FROM comment_dislikes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
                (post_id, comment_id, reaction.user_id)
            )
            
            current_dislikes = comments[comment_index].get("dislikes", 0)
            comments[comment_index]["dislikes"] = max(0, current_dislikes - 1)
        
        session.execute(
            "INSERT INTO comment_likes (post_id, comment_id, user_id, created_at) VALUES (%s, %s, %s, %s)",
            (post_id, comment_id, reaction.user_id, created_at)
        )
        
        current_likes = comments[comment_index].get("likes", 0)
        comments[comment_index]["likes"] = current_likes + 1
        
        session.execute(
            "UPDATE blog_posts SET comments = %s WHERE post_id = %s",
            (comments, post_id)
        )
    else:
        
        existing_dislike = session.execute(
            "SELECT user_id FROM comment_dislikes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
            (post_id, comment_id, reaction.user_id)
        ).one()
        
        if existing_dislike:
            raise HTTPException(status_code=400, detail="User already disliked this comment")

        existing_like = session.execute(
            "SELECT user_id FROM comment_likes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
            (post_id, comment_id, reaction.user_id)
        ).one()
        
        if existing_like:
            
            session.execute(
                "DELETE FROM comment_likes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
                (post_id, comment_id, reaction.user_id)
            )
            
            current_likes = comments[comment_index].get("likes", 0)
            comments[comment_index]["likes"] = max(0, current_likes - 1)
        
        session.execute(
            "INSERT INTO comment_dislikes (post_id, comment_id, user_id, created_at) VALUES (%s, %s, %s, %s)",
            (post_id, comment_id, reaction.user_id, created_at)
        )
        
        current_dislikes = comments[comment_index].get("dislikes", 0)
        comments[comment_index]["dislikes"] = current_dislikes + 1
        
        session.execute(
            "UPDATE blog_posts SET comments = %s WHERE post_id = %s",
            (comments, post_id)
        )

    return CommentReactionResponse(
        post_id=post_id,
        comment_id=comment_id,
        user_id=reaction.user_id,
        is_like=reaction.is_like,
        created_at=created_at
    )

@router.delete(
    "/",
    response_model=dict,
    summary="Remove a Reaction from a Comment",
    description="Removes a user’s like or dislike reaction from a comment.",
    response_description="A confirmation message."
)
async def remove_comment_reaction(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    request: CommentReactionRequest = Body(..., description="Request body with user_id and is_like")
):
    session = await get_session()
    
    post = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not post or not post.comments:
        raise HTTPException(status_code=404, detail="Post or comments not found")
    
    comment_exists = False
    comments = copy.deepcopy(post.comments) 
    comment_index = None
    
    for i, c in enumerate(comments):
        if c and isinstance(c, dict) and str(c.get("id")) == str(comment_id):
            comment_exists = True
            comment_index = i
            break
    
    if not comment_exists:
        raise HTTPException(status_code=404, detail="Comment not found")

    if request.is_like:
        
        existing_like = session.execute(
            "SELECT user_id FROM comment_likes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
            (post_id, comment_id, request.user_id)
        ).one()
        
        if existing_like:
            session.execute(
                "DELETE FROM comment_likes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
                (post_id, comment_id, request.user_id)
            )
            
            current_likes = comments[comment_index].get("likes", 0)
            comments[comment_index]["likes"] = max(0, current_likes - 1)
            
            session.execute(
                "UPDATE blog_posts SET comments = %s WHERE post_id = %s",
                (comments, post_id)
            )
            
            return {"message": "Like removed successfully"}
    else:
        
        existing_dislike = session.execute(
            "SELECT user_id FROM comment_dislikes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
            (post_id, comment_id, request.user_id)
        ).one()
        
        if existing_dislike:
            
            session.execute(
                "DELETE FROM comment_dislikes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
                (post_id, comment_id, request.user_id)
            )
            
            current_dislikes = comments[comment_index].get("dislikes", 0)
            comments[comment_index]["dislikes"] = max(0, current_dislikes - 1)
            
            session.execute(
                "UPDATE blog_posts SET comments = %s WHERE post_id = %s",
                (comments, post_id)
            )
            
            return {"message": "Dislike removed successfully"}

    raise HTTPException(status_code=400, detail="No reaction found to remove")

@router.get(
    "/summary",
    response_model=CommentReactionSummary,
    summary="Get Comment Reaction Summary",
    description="Retrieves the total likes, dislikes, and current user’s reaction for a comment.",
    response_description="A summary of reactions for the comment."
)
async def get_comment_reaction_summary(
    post_id: UUID = Path(..., description="The UUID of the post"),
    comment_id: UUID = Path(..., description="The UUID of the comment"),
    user_id: int = Query(None, description="The ID of the user to check their reaction (optional)")
):
    session = await get_session()
    
    post = session.execute("SELECT comments FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not post or not post.comments:
        raise HTTPException(status_code=404, detail="Post or comments not found")
    
    likes_count = 0
    dislikes_count = 0
    for c in post.comments:
        if c and isinstance(c, dict) and str(c.get("id")) == str(comment_id):
            likes_count = c.get("likes", 0)
            dislikes_count = c.get("dislikes", 0)
            break
    else:
        raise HTTPException(status_code=404, detail="Comment not found")

    current_user_reaction = None
    if user_id is not None:
        
        like = session.execute(
            "SELECT user_id FROM comment_likes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
            (post_id, comment_id, user_id)
        ).one()
        
        if like:
            current_user_reaction = True
        else:
            
            dislike = session.execute(
                "SELECT user_id FROM comment_dislikes WHERE post_id = %s AND comment_id = %s AND user_id = %s",
                (post_id, comment_id, user_id)
            ).one()
            
            if dislike:
                current_user_reaction = False

    return CommentReactionSummary(
        likes_count=likes_count,
        dislikes_count=dislikes_count,
        current_user_reaction=current_user_reaction
    )