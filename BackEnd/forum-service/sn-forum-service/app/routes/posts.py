# app/routes/posts.py
import base64
from fastapi import APIRouter, Body, HTTPException, Query, UploadFile, File, Form
from app.schemas.pagination import PaginatedResponse
from app.services.cassandra import get_session
from app.schemas.post import CategoryInfo, CommentReplyResponse, Image, PostByAuthorEnhanced, PostCommentResponse, PostCreate, PostResponse, TagInfo
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
import os
import shutil
import json
import logging
from cassandra.query import SimpleStatement
from fastapi import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post(
    "/",
    response_model=PostResponse,
    summary="Create a New Post",
    description="Creates a new blog post with the provided title, content, categories, tags, and optional image files.",
    response_description="The created post object with its details."
)
async def create_post(
    author_id: int = Form(..., description="The ID of the author creating the post"),
    title: str = Form(..., description="The title of the post"),
    content: str = Form(..., description="The content/body of the post"),
    categories: Optional[str] = Form(None, description="A JSON string of category UUIDs (e.g., '[\"uuid1\", \"uuid2\"]')"),
    tags: Optional[str] = Form(None, description="A JSON string of tag UUIDs (e.g., '[\"uuid1\", \"uuid2\"]')"),
    files: List[UploadFile] = File(default=[], description="Optional image files to attach to the post")
):
    from pydantic import ValidationError
    parsed_categories = []
    if categories:
        try:
            category_ids = json.loads(categories)
            if isinstance(category_ids, list):
                parsed_categories = [UUID(cat_id) for cat_id in category_ids]  
            else:
                logger.warning(f"Categories is not a list: {categories}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid categories format: {str(e)}, input: {categories}")
            raise HTTPException(status_code=422, detail=f"Invalid categories format: {str(e)}")

    parsed_tags = []
    if tags:
        try:
            tag_ids = json.loads(tags)
            if isinstance(tag_ids, list):
                parsed_tags = [UUID(tag_id) for tag_id in tag_ids]  
            else:
                logger.warning(f"Tags is not a list: {tags}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid tags format: {str(e)}, input: {tags}")
            raise HTTPException(status_code=422, detail=f"Invalid tags format: {str(e)}")

    post_obj = PostCreate(
        author_id=author_id,
        title=title,
        content=content,
        categories=[CategoryInfo(id=cat_id, name="") for cat_id in parsed_categories], 
        tags=[TagInfo(id=tag_id, name="") for tag_id in parsed_tags]                  
    )

    session = await get_session()
    post_id = uuid4()
    created_at = datetime.utcnow()

    image_urls = []
    images_data = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, f"{post_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        url_path = f"/{file_path}"
        image_urls.append(Image(url=url_path))
        images_data.append(url_path)

    categories_data = parsed_categories  
    tags_data = parsed_tags             

    try:
        session.execute(
            """
            INSERT INTO blog_posts (
                post_id, author_id, title, content, likes_count, dislikes_count, saves_count, images, categories, tags, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                post_id,
                post_obj.author_id,
                post_obj.title,
                post_obj.content,
                0,
                0,
                0,
                images_data,
                categories_data,
                tags_data,
                created_at
            )
        )
        session.execute(
            """
            INSERT INTO posts_by_author (author_id, created_at, post_id, title, categories, tags)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                post_obj.author_id,
                created_at,
                post_id,
                post_obj.title,
                categories_data,
                tags_data
            )
        )

        for category_id in parsed_categories:
            session.execute(
                """
                INSERT INTO posts_by_category (category_id, post_id, created_at, title)
                VALUES (%s, %s, %s, %s)
                """,
                (category_id, post_id, created_at, post_obj.title)
            )

        for tag_id in parsed_tags:
            session.execute(
                """
                INSERT INTO posts_by_tag (tag_id, post_id, created_at, title)
                VALUES (%s, %s, %s, %s)
                """,
                (tag_id, post_id, created_at, post_obj.title)
            )
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    categories_with_names = []
    for cat_id in parsed_categories:
        cat_row = session.execute("SELECT name FROM categories WHERE category_id = %s", (cat_id,)).one()
        categories_with_names.append(CategoryInfo(id=cat_id, name=cat_row.name if cat_row else ""))

    tags_with_names = []
    for tag_id in parsed_tags:
        tag_row = session.execute("SELECT name FROM tags WHERE tag_id = %s", (tag_id,)).one()
        tags_with_names.append(TagInfo(id=tag_id, name=tag_row.name if tag_row else ""))

    return PostResponse(
        post_id=post_id,
        author_id=post_obj.author_id,
        title=post_obj.title,
        content=post_obj.content,
        images=image_urls,
        categories=categories_with_names,
        tags=tags_with_names,
        likes_count=0,
        dislikes_count=0,
        saves_count=0,
        comments=[],
        created_at=created_at
    )

@router.get(
    "/",
    response_model=PaginatedResponse[PostResponse],
    summary="List All Posts",
    description="Retrieves a paginated list of all blog posts.",
    response_description="A paginated response containing a list of posts and an optional next_paging_state."
)
async def list_posts(
    page_size: int = Query(10, ge=1, le=100, description="Number of posts to return per page (1-100)"),
    paging_state: Optional[str] = Query(None, description="Base64-encoded paging state for fetching the next page")
):
    session = await get_session()
    
    query = "SELECT * FROM blog_posts" 
    statement = SimpleStatement(query, fetch_size=page_size)
    
    try:
        if paging_state:
            try:
                paging_state_bytes = base64.b64decode(paging_state)
                rows = session.execute(statement, paging_state=paging_state_bytes)
                logger.debug(f"Executing with paging_state: {paging_state}, fetch_size: {page_size}")
            except Exception as e:
                logger.error(f"Error decoding paging_state: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid paging state: {str(e)}")
        else:
            rows = session.execute(statement)
            logger.debug(f"Executing initial query with fetch_size: {page_size}")
        
        posts_data = []
        for i, row in enumerate(rows):
            if i >= page_size:
                break
            posts_data.append(row)
            logger.debug(f"Collected post: {row.post_id}")
        
        logger.debug(f"Collected {len(posts_data)} posts from rows")
        
        if not posts_data:
            logger.debug("No posts collected, returning empty response")
            return PaginatedResponse(items=[], next_paging_state=None)
        
        all_category_ids = {cat_id for row in posts_data for cat_id in (row.categories or [])}
        all_tag_ids = {tag_id for row in posts_data for tag_id in (row.tags or [])}
        
        category_map = {}
        if all_category_ids:
            if len(all_category_ids) == 1:
                cat_id = list(all_category_ids)[0]
                cat_row = session.execute(
                    "SELECT category_id, name FROM categories WHERE category_id = %s", 
                    (cat_id,)
                ).one()
                if cat_row:
                    category_map[cat_id] = cat_row.name
            else:
                placeholders = ','.join(['%s'] * len(all_category_ids))
                query = f"SELECT category_id, name FROM categories WHERE category_id IN ({placeholders})"
                cat_rows = session.execute(query, list(all_category_ids)).all()
                category_map = {row.category_id: row.name for row in cat_rows}
        
        tag_map = {}
        if all_tag_ids:
            if len(all_tag_ids) == 1:
                tag_id = list(all_tag_ids)[0]
                tag_row = session.execute(
                    "SELECT tag_id, name FROM tags WHERE tag_id = %s", 
                    (tag_id,)
                ).one()
                if tag_row:
                    tag_map[tag_id] = tag_row.name
            else:
                placeholders = ','.join(['%s'] * len(all_tag_ids))
                query = f"SELECT tag_id, name FROM tags WHERE tag_id IN ({placeholders})"
                tag_rows = session.execute(query, list(all_tag_ids)).all()
                tag_map = {row.tag_id: row.name for row in tag_rows}
        
        result = []
        for row in posts_data:
            try:
                categories_with_names = [
                    CategoryInfo(id=cat_id, name=category_map.get(cat_id, ""))
                    for cat_id in row.categories or []
                ]
                tags_with_names = [
                    TagInfo(id=tag_id, name=tag_map.get(tag_id, ""))
                    for tag_id in row.tags or []
                ]
                valid_comments = []
                if row.comments:
                    for c in row.comments:
                        if c and isinstance(c, dict) and c.get('id') and c.get('author_id'):
                            comment_id = c.get('id')
                            replies_rows = session.execute(
                                "SELECT * FROM comment_replies WHERE post_id = %s AND comment_id = %s",
                                (row.post_id, comment_id)
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
                
                post_response = PostResponse(
                    post_id=row.post_id,
                    author_id=row.author_id,
                    title=row.title,
                    content=row.content,
                    images=[Image(url=url) for url in row.images or []],
                    categories=categories_with_names,
                    tags=tags_with_names,
                    likes_count=row.likes_count,
                    dislikes_count=row.dislikes_count,
                    saves_count=row.saves_count,
                    comments=valid_comments,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                result.append(post_response)
            except Exception as e:
                logger.error(f"Error processing post: {e}, Post ID: {row.post_id}")
                continue
        
        next_paging_state = base64.b64encode(rows.paging_state).decode('utf-8') if rows.paging_state else None
        logger.debug(f"Next paging_state: {next_paging_state}")
        
        return PaginatedResponse(
            items=result,
            next_paging_state=next_paging_state
        )
    except Exception as e:
        logger.error(f"Error in list_posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 

@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a Post by ID",
    description="Retrieves a specific blog post by its UUID.",
    response_description="The requested post object with its details."
)
async def get_post(post_id: UUID = Path(..., description="The UUID of the post to retrieve")):
    session = await get_session()
    row = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")

    categories_with_names = []
    for cat_id in row.categories or []:
        cat_row = session.execute("SELECT name FROM categories WHERE category_id = %s", (cat_id,)).one()
        categories_with_names.append(CategoryInfo(id=cat_id, name=cat_row.name if cat_row else ""))

    tags_with_names = []
    for tag_id in row.tags or []:
        tag_row = session.execute("SELECT name FROM tags WHERE tag_id = %s", (tag_id,)).one()
        tags_with_names.append(TagInfo(id=tag_id, name=tag_row.name if tag_row else ""))

    valid_comments = []
    if row.comments:
        for c in row.comments:
            if c and isinstance(c, dict) and 'id' in c and 'author_id' in c:
                comment_id = c.get('id')
                if comment_id:
                    replies_rows = session.execute(
                        """
                        SELECT * FROM comment_replies 
                        WHERE post_id = %s AND comment_id = %s
                        """,
                        (post_id, comment_id)
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
                    valid_comments.append(
                        PostCommentResponse(
                            id=UUID(str(c.get('id'))) if isinstance(c.get('id'), str) else c.get('id'),
                            author_id=c.get('author_id'),
                            content=c.get('content', ''),
                            created_at=c.get('created_at'),
                            likes=c.get('likes', 0),
                            dislikes=c.get('dislikes', 0),
                            replies=comment_replies
                        )
                    )

    return PostResponse(
        post_id=row.post_id,
        author_id=row.author_id,
        title=row.title,
        content=row.content,
        images=[Image(url=url) for url in row.images or []],
        categories=categories_with_names,
        tags=tags_with_names,
        likes_count=row.likes_count,
        dislikes_count=row.dislikes_count,
        saves_count=row.saves_count,
        comments=valid_comments,
        created_at=row.created_at,
        updated_at=row.updated_at
    )
@router.put("/{post_id}", response_model=PostResponse)

@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update a Post",
    description="Updates an existing blog post with new title, content, categories, tags, or images.",
    response_description="The updated post object with its details."
)
async def update_post(
    post_id: UUID = Path(..., description="The UUID of the post to update"),  
    title: Optional[str] = Form(None, description="New title for the post (optional)"),
    content: Optional[str] = Form(None, description="New content for the post (optional)"),
    categories: Optional[str] = Form(None, description="A JSON string of new category UUIDs (optional)"),
    tags: Optional[str] = Form(None, description="A JSON string of new tag UUIDs (optional)"),
    files: List[UploadFile] = File(default=[], description="New image files to attach (optional)")
):
    session = await get_session()
    existing = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    if not existing:
        raise HTTPException(status_code=404, detail="Post not found")

    parsed_categories = []
    if categories:
        try:
            category_ids = json.loads(categories)
            if isinstance(category_ids, list):
                
                for cat_id in category_ids:
                    cat_uuid = UUID(cat_id) if isinstance(cat_id, str) else cat_id
                    cat_row = session.execute("SELECT name FROM categories WHERE category_id = %s", (cat_uuid,)).one()
                    if not cat_row:
                        raise HTTPException(status_code=404, detail=f"Category with ID {cat_id} not found")
                    parsed_categories.append(cat_uuid)
            else:
                logger.warning(f"Categories is not a list: {categories}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid categories format: {str(e)}, input: {categories}")
            raise HTTPException(status_code=422, detail=f"Invalid categories format: {str(e)}")

    parsed_tags = []
    if tags:
        try:
            tag_ids = json.loads(tags)
            if isinstance(tag_ids, list):
                
                for tag_id in tag_ids:
                    tag_uuid = UUID(tag_id) if isinstance(tag_id, str) else tag_id
                    tag_row = session.execute("SELECT name FROM tags WHERE tag_id = %s", (tag_uuid,)).one()
                    if not tag_row:
                        raise HTTPException(status_code=404, detail=f"Tag with ID {tag_id} not found")
                    parsed_tags.append(tag_uuid)
            else:
                logger.warning(f"Tags is not a list: {tags}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid tags format: {str(e)}, input: {tags}")
            raise HTTPException(status_code=422, detail=f"Invalid tags format: {str(e)}")

    updated_at = datetime.utcnow()
    update_query = """
        UPDATE blog_posts SET updated_at = %s
        {updates}
        WHERE post_id = %s
    """
    updates = []
    params = [updated_at]

    if title is not None:
        updates.append(", title = %s")
        params.append(title)
    if content is not None:
        updates.append(", content = %s")
        params.append(content)

    if files:
        image_urls = []
        images_data = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, f"{post_id}_{file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            url_path = f"/{file_path}"
            image_urls.append(Image(url=url_path))
            images_data.append(url_path)
        updates.append(", images = %s")
        params.append(images_data)

    if parsed_categories:
        updates.append(", categories = %s")
        params.append(parsed_categories)
        
        if existing.categories:
            for cat_id in existing.categories:
                
                category_rows = session.execute("""
                    SELECT category_id, created_at, post_id
                    FROM posts_by_category 
                    WHERE category_id = %s
                """, (cat_id,)).all()
                
                for row in category_rows:
                    if row.post_id == post_id:
                        session.execute("""
                            DELETE FROM posts_by_category 
                            WHERE category_id = %s AND created_at = %s AND post_id = %s
                        """, (row.category_id, row.created_at, row.post_id))

        for cat_id in parsed_categories:
            session.execute("""
                INSERT INTO posts_by_category (category_id, post_id, created_at, title)
                VALUES (%s, %s, %s, %s)
            """, (cat_id, post_id, existing.created_at, title or existing.title))

    if parsed_tags:
        updates.append(", tags = %s")
        params.append(parsed_tags)
        
        if existing.tags:
            for tag_id in existing.tags:
                
                tag_rows = session.execute("""
                    SELECT tag_id, created_at, post_id
                    FROM posts_by_tag 
                    WHERE tag_id = %s
                """, (tag_id,)).all()
                
                for row in tag_rows:
                    if row.post_id == post_id:
                        session.execute("""
                            DELETE FROM posts_by_tag 
                            WHERE tag_id = %s AND created_at = %s AND post_id = %s
                        """, (row.tag_id, row.created_at, row.post_id))
        
        for tag_id in parsed_tags:
            session.execute("""
                INSERT INTO posts_by_tag (tag_id, post_id, created_at, title)
                VALUES (%s, %s, %s, %s)
            """, (tag_id, post_id, existing.created_at, title or existing.title))

    if updates:
        session.execute(update_query.format(updates="".join(updates)), params + [post_id])

    updated = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (post_id,)).one()
    
    categories_with_names = []
    for cat_id in updated.categories or []:
        cat_row = session.execute("SELECT name FROM categories WHERE category_id = %s", (cat_id,)).one()
        categories_with_names.append(CategoryInfo(
            id=cat_id, 
            name=cat_row.name if cat_row else ""
        ))
    
    tags_with_names = []
    for tag_id in updated.tags or []:
        tag_row = session.execute("SELECT name FROM tags WHERE tag_id = %s", (tag_id,)).one()
        tags_with_names.append(TagInfo(
            id=tag_id, 
            name=tag_row.name if tag_row else ""
        ))

    return PostResponse(
        post_id=updated.post_id,
        author_id=updated.author_id,
        title=updated.title,
        content=updated.content,
        images=[Image(url=url) for url in updated.images or []],
        categories=categories_with_names,
        tags=tags_with_names,
        likes_count=updated.likes_count,
        dislikes_count=updated.dislikes_count,
        saves_count=updated.saves_count,
        comments=updated.comments or [],
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )

@router.delete(
    "/{post_id}",
    summary="Delete a Post",
    description="Deletes a blog post by its UUID.",
    response_description="A confirmation message with the deleted post's UUID."
)
async def delete_post(post_id: UUID = Path(..., description="The UUID of the post to delete")):    
    session = await get_session()
    
    existing = session.execute(
        "SELECT author_id, created_at FROM blog_posts WHERE post_id = %s", 
        (post_id,)
    ).one()
    if not existing:
        raise HTTPException(status_code=404, detail="Post not found")
    
    session.execute("DELETE FROM blog_posts WHERE post_id = %s", (post_id,))
    
    session.execute(
        "DELETE FROM posts_by_author WHERE author_id = %s AND created_at = %s AND post_id = %s",
        (existing.author_id, existing.created_at, post_id)
    )
    
    return {"message": "Post deleted", "post_id": post_id}

@router.get(
    "/by-author/{author_id}",
    response_model=PaginatedResponse[PostByAuthorEnhanced],
    summary="List Posts by Author",
    description="Retrieves a paginated list of posts created by a specific author.",
    response_description="A paginated response containing a list of posts by the author and an optional next_paging_state."
)
async def get_posts_by_author(
    author_id: int = Path(..., description="The ID of the author whose posts to retrieve"),  
    page_size: int = Body(10, ge=1, le=100, description="Number of posts to return per page (1-100)"),
    paging_state: Optional[str] = Body(None, description="Base64-encoded paging state for fetching the next page")
):
    session = await get_session()
    
    query = "SELECT post_id, title, created_at FROM posts_by_author WHERE author_id = %s"
    statement = SimpleStatement(query, fetch_size=page_size)
    
    try:
        if paging_state:
            paging_state_bytes = base64.b64decode(paging_state)
            rows = session.execute(statement, (author_id,), paging_state=paging_state_bytes)
            logger.debug(f"Executing get_posts_by_author with paging_state: {paging_state}, fetch_size: {page_size}")
        else:
            rows = session.execute(statement, (author_id,))
            logger.debug(f"Executing initial get_posts_by_author query with fetch_size: {page_size}")
        
        posts_data = []
        for i, row in enumerate(rows):
            if i >= page_size:
                break
            posts_data.append(row)
            logger.debug(f"Collected post: {row.post_id}")
        
        logger.debug(f"Collected {len(posts_data)} posts from rows")
        
        if not posts_data:
            logger.debug("No posts collected, returning empty response")
            return PaginatedResponse(items=[], next_paging_state=None)
        
        result = []
        for row in posts_data:
            post_data = session.execute("SELECT * FROM blog_posts WHERE post_id = %s", (row.post_id,)).one()
            if post_data:
                categories_with_names = [
                    CategoryInfo(
                        id=cat_id,
                        name=session.execute("SELECT name FROM categories WHERE category_id = %s", (cat_id,)).one().name if cat_id else ""
                    )
                    for cat_id in post_data.categories or []
                ]
                tags_with_names = [
                    TagInfo(
                        id=tag_id,
                        name=session.execute("SELECT name FROM tags WHERE tag_id = %s", (tag_id,)).one().name if tag_id else ""
                    )
                    for tag_id in post_data.tags or []
                ]
                result.append(PostByAuthorEnhanced(
                    post_id=post_data.post_id,
                    title=post_data.title,
                    content=post_data.content,
                    images=[Image(url=url) for url in post_data.images or []],
                    categories=categories_with_names,
                    tags=tags_with_names,
                    likes_count=post_data.likes_count,
                    dislikes_count=post_data.dislikes_count,
                    saves_count=post_data.saves_count,
                    created_at=post_data.created_at,
                    updated_at=post_data.updated_at
                ))
        
        next_paging_state = base64.b64encode(rows.paging_state).decode('utf-8') if rows.paging_state else None
        logger.debug(f"Next paging_state: {next_paging_state}")
        
        return PaginatedResponse(
            items=result,
            next_paging_state=next_paging_state
        )
    except Exception as e:
        logger.error(f"Error in get_posts_by_author: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")