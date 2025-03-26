# app/routes/post_reactions.py
import base64
from fastapi import APIRouter, HTTPException, Path, Body, Query
from app.schemas.pagination import PaginatedResponse
from app.services.cassandra import get_session
from app.schemas.post_reaction import PostReactionRemoveRequest, PostReactionRequest, PostReactionResponse, PostReactionSummary, LikedPostInfo, DislikedPostInfo
from app.schemas.post import PostResponse, CategoryInfo, TagInfo, Image, PostCommentResponse, CommentReplyResponse
from uuid import UUID
from datetime import datetime
from typing import List, Optional
import logging
from fastapi import Query
from cassandra.query import SimpleStatement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/{post_id}/reactions",
    response_model=PostReactionResponse,
    summary="Add a Reaction to a Post",
    description="Adds a like or dislike reaction to a blog post by a user.",
    response_description="The reaction object with its details."
)
async def add_reaction(
    post_id: UUID = Path(..., description="The UUID of the post to react to"),
    reaction: PostReactionRequest = Body(..., description="Request body with user_id and is_like")
):
    session = await get_session()
    
    post = session.execute("SELECT likes_count, dislikes_count FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    created_at = datetime.utcnow()
    
    if reaction.is_like:
        
        existing_like = session.execute(
            "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s",
            (post_id, reaction.user_id)
        ).one()
        if existing_like:
            raise HTTPException(status_code=400, detail="User already liked this post")

        existing_dislike = session.execute(
            "SELECT user_id FROM post_dislikes WHERE post_id = %s AND user_id = %s",
            (post_id, reaction.user_id)
        ).one()
        if existing_dislike:
            session.execute(
                "DELETE FROM post_dislikes WHERE post_id = %s AND user_id = %s",
                (post_id, reaction.user_id)
            )
            session.execute(
                "UPDATE blog_posts SET dislikes_count = %s WHERE post_id = %s",
                (post.dislikes_count - 1 if post.dislikes_count > 0 else 0, post_id)
            )

        session.execute(
            "INSERT INTO post_likes (post_id, user_id, created_at) VALUES (%s, %s, %s)",
            (post_id, reaction.user_id, created_at)
        )
        session.execute(
            "UPDATE blog_posts SET likes_count = %s WHERE post_id = %s",
            (post.likes_count + 1, post_id)
        )
    else:
        
        existing_dislike = session.execute(
            "SELECT user_id FROM post_dislikes WHERE post_id = %s AND user_id = %s",
            (post_id, reaction.user_id)
        ).one()
        if existing_dislike:
            raise HTTPException(status_code=400, detail="User already disliked this post")

        existing_like = session.execute(
            "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s",
            (post_id, reaction.user_id)
        ).one()
        if existing_like:
            session.execute(
                "DELETE FROM post_likes WHERE post_id = %s AND user_id = %s",
                (post_id, reaction.user_id)
            )
            session.execute(
                "UPDATE blog_posts SET likes_count = %s WHERE post_id = %s",
                (post.likes_count - 1 if post.likes_count > 0 else 0, post_id)
            )

        session.execute(
            "INSERT INTO post_dislikes (post_id, user_id, created_at) VALUES (%s, %s, %s)",
            (post_id, reaction.user_id, created_at)
        )
        session.execute(
            "UPDATE blog_posts SET dislikes_count = %s WHERE post_id = %s",
            (post.dislikes_count + 1, post_id)
        )

    return PostReactionResponse(
        post_id=post_id,
        user_id=reaction.user_id,
        is_like=reaction.is_like,
        created_at=created_at
    )

@router.delete(
    "/{post_id}/reactions",
    response_model=dict,
    summary="Remove a Reaction from a Post",
    description="Removes a user’s like or dislike reaction from a blog post.",
    response_description="A confirmation message."
)
async def remove_reaction(
    post_id: UUID = Path(..., description="The UUID of the post"),
    request: PostReactionRemoveRequest = Body(..., description="Request body with user_id")
):
    session = await get_session()
    
    post = session.execute("SELECT likes_count, dislikes_count FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = session.execute(
        "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s",
        (post_id, request.user_id)
    ).one()
    if existing_like:
        session.execute(
            "DELETE FROM post_likes WHERE post_id = %s AND user_id = %s",
            (post_id, request.user_id)
        )
        session.execute(
            "UPDATE blog_posts SET likes_count = %s WHERE post_id = %s",
            (post.likes_count - 1 if post.likes_count > 0 else 0, post_id)
        )
        return {"message": "Like removed successfully"}

    existing_dislike = session.execute(
        "SELECT user_id FROM post_dislikes WHERE post_id = %s AND user_id = %s",
        (post_id, request.user_id)
    ).one()
    if existing_dislike:
        session.execute(
            "DELETE FROM post_dislikes WHERE post_id = %s AND user_id = %s",
        (post_id, request.user_id)
        )
        session.execute(
            "UPDATE blog_posts SET dislikes_count = %s WHERE post_id = %s",
            (post.dislikes_count - 1 if post.dislikes_count > 0 else 0, post_id)
        )
        return {"message": "Dislike removed successfully"}

    raise HTTPException(status_code=400, detail="No reaction found to remove")

@router.get(
    "/reactions/summary/{post_id}",
    response_model=PostReactionSummary,
    summary="Get Post Reaction Summary",
    description="Retrieves the total likes, dislikes, and current user’s reaction for a post.",
    response_description="A summary of reactions for the post."
)
async def get_reaction_summary(
    post_id: UUID = Path(..., description="The UUID of the post"),
    user_id: int = Query(None, description="The ID of the user to check their reaction (optional)")
):
    session = await get_session()
    
    post = session.execute("SELECT likes_count, dislikes_count FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    current_user_reaction = None
    if user_id is not None:
        like = session.execute(
            "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s",
            (post_id, user_id)
        ).one()
        if like:
            current_user_reaction = True
        else:
            dislike = session.execute(
                "SELECT user_id FROM post_dislikes WHERE post_id = %s AND user_id = %s",
                (post_id, user_id)
            ).one()
            if dislike:
                current_user_reaction = False

    return PostReactionSummary(
        likes_count=post.likes_count,
        dislikes_count=post.dislikes_count,
        current_user_reaction=current_user_reaction
    )

@router.get(
    "/reactions/liked/{user_id}",
    response_model=PaginatedResponse[PostResponse],
    summary="List Liked Posts",
    description="Retrieves a paginated list of posts liked by a specific user.",
    response_description="A paginated list of liked post objects."
)
async def get_liked_posts(
    user_id: int = Path(..., description="The ID of the user whose liked posts to retrieve"),
    page_size: int = Query(10, ge=1, le=100, description="Number of posts to return per page (1-100)"),
    paging_state: Optional[str] = Query(None, description="Base64-encoded paging state for the next page")
):
    session = await get_session()
    
    query = "SELECT post_id FROM post_likes WHERE user_id = %s ALLOW FILTERING"
    statement = SimpleStatement(query, fetch_size=page_size)
    
    try:
        if paging_state:
            paging_state_bytes = base64.b64decode(paging_state)
            liked_rows = session.execute(statement, (user_id,), paging_state=paging_state_bytes)
            logger.debug(f"Executing get_liked_posts with paging_state: {paging_state}, fetch_size: {page_size}")
        else:
            liked_rows = session.execute(statement, (user_id,))
            logger.debug(f"Executing initial get_liked_posts query with fetch_size: {page_size}")
        
        liked_posts_data = []
        for i, row in enumerate(liked_rows):
            if i >= page_size:
                break
            liked_posts_data.append(row)
            logger.debug(f"Collected liked post_id: {row.post_id}")
        
        if not liked_posts_data:
            logger.debug("No liked posts found, returning empty response")
            return PaginatedResponse(items=[], next_paging_state=None)
        
        all_category_ids = set()
        all_tag_ids = set()
        for row in liked_posts_data:
            post_row = session.execute("SELECT categories, tags FROM blog_posts WHERE post_id = %s", (row.post_id,)).one()
            if post_row:
                all_category_ids.update(post_row.categories or [])
                all_tag_ids.update(post_row.tags or [])
        
        category_map = {}
        if all_category_ids:
            placeholders = ','.join(['%s'] * len(all_category_ids))
            cat_rows = session.execute(f"SELECT category_id, name FROM categories WHERE category_id IN ({placeholders})", list(all_category_ids)).all()
            category_map = {row.category_id: row.name for row in cat_rows}
        
        tag_map = {}
        if all_tag_ids:
            placeholders = ','.join(['%s'] * len(all_tag_ids))
            tag_rows = session.execute(f"SELECT tag_id, name FROM tags WHERE tag_id IN ({placeholders})", list(all_tag_ids)).all()
            tag_map = {row.tag_id: row.name for row in tag_rows}
        
        result = []
        for row in liked_posts_data:
            post_row = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (row.post_id,)).one()
            if post_row:
                categories_with_names = [
                    CategoryInfo(id=cat_id, name=category_map.get(cat_id, ""))
                    for cat_id in post_row.categories or []
                ]
                tags_with_names = [
                    TagInfo(id=tag_id, name=tag_map.get(tag_id, ""))
                    for tag_id in post_row.tags or []
                ]
                valid_comments = []
                if post_row.comments:
                    for c in post_row.comments:
                        if c and isinstance(c, dict) and c.get('id') and c.get('author_id'):
                            comment_id = c.get('id')
                            replies_rows = session.execute(
                                "SELECT * FROM comment_replies WHERE post_id = %s AND comment_id = %s",
                                (post_row.post_id, comment_id)
                            ).all()
                            comment_replies = [
                                CommentReplyResponse(
                                    id=r.reply_id,
                                    author_id=r.author_id,
                                    content=r.content,
                                    created_at=r.created_at,
                                    likes=r.likes,
                                    dislikes=r.dislikes
                                )
                                for r in replies_rows
                            ]
                            valid_comments.append(PostCommentResponse(
                                id=UUID(str(c.get('id'))) if isinstance(c.get('id'), str) else c.get('id'),
                                author_id=c.get('author_id'),
                                content=c.get('content', ''),
                                created_at=c.get('created_at') or datetime.now(),
                                likes=c.get('likes', 0),
                                dislikes=c.get('dislikes', 0),
                                replies=comment_replies
                            ))
                
                result.append(PostResponse(
                    post_id=post_row.post_id,
                    author_id=post_row.author_id,
                    title=post_row.title,
                    content=post_row.content,
                    images=[Image(url=url) for url in post_row.images or []],
                    categories=categories_with_names,
                    tags=tags_with_names,
                    likes_count=post_row.likes_count,
                    dislikes_count=post_row.dislikes_count,
                    saves_count=post_row.saves_count,
                    comments=valid_comments,
                    created_at=post_row.created_at,
                    updated_at=post_row.updated_at
                ))
        
        next_paging_state = base64.b64encode(liked_rows.paging_state).decode('utf-8') if liked_rows.paging_state else None
        logger.debug(f"Next paging_state: {next_paging_state}")
        
        return PaginatedResponse(
            items=result,
            next_paging_state=next_paging_state
        )
    except Exception as e:
        logger.error(f"Error in get_liked_posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@router.get(
    "/reactions/disliked/{user_id}",
    response_model=PaginatedResponse[PostResponse],
    summary="List Disliked Posts",
    description="Retrieves a paginated list of posts disliked by a specific user.",
    response_description="A paginated list of disliked post objects."
)
async def get_disliked_posts(
    user_id: int = Path(..., description="The ID of the user whose disliked posts to retrieve"),
    page_size: int = Query(10, ge=1, le=100, description="Number of posts to return per page (1-100)"),
    paging_state: Optional[str] = Query(None, description="Base64-encoded paging state for the next page")
):
    session = await get_session()
    
    query = "SELECT post_id FROM post_dislikes WHERE user_id = %s ALLOW FILTERING"
    statement = SimpleStatement(query, fetch_size=page_size)
    
    try:
        if paging_state:
            paging_state_bytes = base64.b64decode(paging_state)
            disliked_rows = session.execute(statement, (user_id,), paging_state=paging_state_bytes)
            logger.debug(f"Executing get_disliked_posts with paging_state: {paging_state}, fetch_size: {page_size}")
        else:
            disliked_rows = session.execute(statement, (user_id,))
            logger.debug(f"Executing initial get_disliked_posts query with fetch_size: {page_size}")
        
        disliked_posts_data = []
        for i, row in enumerate(disliked_rows):
            if i >= page_size:
                break
            disliked_posts_data.append(row)
            logger.debug(f"Collected disliked post_id: {row.post_id}")
        
        if not disliked_posts_data:
            logger.debug("No disliked posts found, returning empty response")
            return PaginatedResponse(items=[], next_paging_state=None)
        
        all_category_ids = set()
        all_tag_ids = set()
        for row in disliked_posts_data:
            post_row = session.execute("SELECT categories, tags FROM blog_posts WHERE post_id = %s", (row.post_id,)).one()
            if post_row:
                all_category_ids.update(post_row.categories or [])
                all_tag_ids.update(post_row.tags or [])
        
        category_map = {}
        if all_category_ids:
            placeholders = ','.join(['%s'] * len(all_category_ids))
            cat_rows = session.execute(f"SELECT category_id, name FROM categories WHERE category_id IN ({placeholders})", list(all_category_ids)).all()
            category_map = {row.category_id: row.name for row in cat_rows}
        
        tag_map = {}
        if all_tag_ids:
            placeholders = ','.join(['%s'] * len(all_tag_ids))
            tag_rows = session.execute(f"SELECT tag_id, name FROM tags WHERE tag_id IN ({placeholders})", list(all_tag_ids)).all()
            tag_map = {row.tag_id: row.name for row in tag_rows}
        
        result = []
        for row in disliked_posts_data:
            post_row = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (row.post_id,)).one()
            if post_row:
                categories_with_names = [
                    CategoryInfo(id=cat_id, name=category_map.get(cat_id, ""))
                    for cat_id in post_row.categories or []
                ]
                tags_with_names = [
                    TagInfo(id=tag_id, name=tag_map.get(tag_id, ""))
                    for tag_id in post_row.tags or []
                ]
                valid_comments = []
                if post_row.comments:
                    for c in post_row.comments:
                        if c and isinstance(c, dict) and c.get('id') and c.get('author_id'):
                            comment_id = c.get('id')
                            replies_rows = session.execute(
                                "SELECT * FROM comment_replies WHERE post_id = %s AND comment_id = %s",
                                (post_row.post_id, comment_id)
                            ).all()
                            comment_replies = [
                                CommentReplyResponse(
                                    id=r.reply_id,
                                    author_id=r.author_id,
                                    content=r.content,
                                    created_at=r.created_at,
                                    likes=r.likes,
                                    dislikes=r.dislikes
                                )
                                for r in replies_rows
                            ]
                            valid_comments.append(PostCommentResponse(
                                id=UUID(str(c.get('id'))) if isinstance(c.get('id'), str) else c.get('id'),
                                author_id=c.get('author_id'),
                                content=c.get('content', ''),
                                created_at=c.get('created_at') or datetime.now(),
                                likes=c.get('likes', 0),
                                dislikes=c.get('dislikes', 0),
                                replies=comment_replies
                            ))
                
                result.append(PostResponse(
                    post_id=post_row.post_id,
                    author_id=post_row.author_id,
                    title=post_row.title,
                    content=post_row.content,
                    images=[Image(url=url) for url in post_row.images or []],
                    categories=categories_with_names,
                    tags=tags_with_names,
                    likes_count=post_row.likes_count,
                    dislikes_count=post_row.dislikes_count,
                    saves_count=post_row.saves_count,
                    comments=valid_comments,
                    created_at=post_row.created_at,
                    updated_at=post_row.updated_at
                ))
        
        next_paging_state = base64.b64encode(disliked_rows.paging_state).decode('utf-8') if disliked_rows.paging_state else None
        logger.debug(f"Next paging_state: {next_paging_state}")
        
        return PaginatedResponse(
            items=result,
            next_paging_state=next_paging_state
        )
    except Exception as e:
        logger.error(f"Error in get_disliked_posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")