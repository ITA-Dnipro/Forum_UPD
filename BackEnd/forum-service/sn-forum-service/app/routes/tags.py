from fastapi import APIRouter, HTTPException, Path, Body
from app.services.cassandra import get_session
from app.schemas.tag import TagCreate, TagResponse
from uuid import UUID, uuid4
from datetime import datetime
from typing import List

router = APIRouter()

@router.post(
    "/",
    response_model=TagResponse,
    summary="Create a New Tag",
    description="Creates a new tag with a unique name and optional description.",
    response_description="The created tag object with its details."
)
async def create_tag(tag: TagCreate = Body(..., description="Request body with tag name and optional description")):
    session = await get_session()
    
    existing = session.execute(
        "SELECT tag_id FROM tags WHERE name = %s ALLOW FILTERING",
        (tag.name,)
    ).one()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Tag with name '{tag.name}' already exists"
        )
    
    tag_id = uuid4()
    created_at = datetime.utcnow()
    
    session.execute("""
        INSERT INTO tags (tag_id, name, description, posts_count, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (tag_id, tag.name, tag.description, 0, created_at))
    
    return TagResponse(
        tag_id=tag_id, name=tag.name, description=tag.description,
        posts_count=0, created_at=created_at
    )

@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Get a Tag by ID",
    description="Retrieves a specific tag by its UUID.",
    response_description="The requested tag object with its details."
)
async def get_tag(tag_id: UUID = Path(..., description="The UUID of the tag to retrieve")):
    session = await get_session()
    row = session.execute("SELECT * FROM tags WHERE tag_id = %s", (tag_id,)).one()
    if not row:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagResponse(**row._asdict())

@router.get(
    "/",
    response_model=List[TagResponse],
    summary="List All Tags",
    description="Retrieves a list of all tags in the system.",
    response_description="A list of tag objects."
)
async def list_tags():
    session = await get_session()
    rows = session.execute("SELECT * FROM tags").all()
    return [TagResponse(**row._asdict()) for row in rows]

@router.put(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Update a Tag",
    description="Updates an existing tag’s name and/or description.",
    response_description="The updated tag object with its details."
)
async def update_tag(
    tag_id: UUID = Path(..., description="The UUID of the tag to update"),
    tag: TagCreate = Body(..., description="Request body with new name and/or description")
):
    session = await get_session()
    existing = session.execute("SELECT * FROM tags WHERE tag_id = %s", (tag_id,)).one()
    if not existing:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    updated_at = datetime.utcnow()
    session.execute("""
        UPDATE tags SET name = %s, description = %s, updated_at = %s
        WHERE tag_id = %s
    """, (tag.name, tag.description, updated_at, tag_id))
    
    updated = session.execute("SELECT * FROM tags WHERE tag_id = %s", (tag_id,)).one()
    return TagResponse(**updated._asdict())

@router.delete(
    "/{tag_id}",
    summary="Delete a Tag",
    description="Deletes a tag by its UUID.",
    response_description="A confirmation message with the deleted tag’s UUID."
)
async def delete_tag(tag_id: UUID = Path(..., description="The UUID of the tag to delete")):
    session = await get_session()
    existing = session.execute("SELECT tag_id FROM tags WHERE tag_id = %s", (tag_id,)).one()
    if not existing:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    session.execute("DELETE FROM tags WHERE tag_id = %s", (tag_id,))
    return {"message": "Tag deleted", "tag_id": tag_id}