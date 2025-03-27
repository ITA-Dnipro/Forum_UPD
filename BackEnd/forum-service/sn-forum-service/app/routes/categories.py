from fastapi import APIRouter, HTTPException, Path, Body
from app.services.cassandra import get_session
from app.schemas.category import CategoryCreate, CategoryResponse
from uuid import UUID, uuid4
from datetime import datetime
from typing import List

router = APIRouter()

@router.post(
    "/",
    response_model=CategoryResponse,
    summary="Create a New Category",
    description="Creates a new category with a unique name and optional description.",
    response_description="The created category object with its details."
)
async def create_category(category: CategoryCreate = Body(..., description="Request body with category name and optional description")):
    session = await get_session()
    
    existing = session.execute(
        "SELECT category_id FROM categories WHERE name = %s ALLOW FILTERING",
        (category.name,)
    ).one()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Category with name '{category.name}' already exists"
        )
    
    category_id = uuid4()
    created_at = datetime.utcnow()
    
    session.execute("""
        INSERT INTO categories (category_id, name, description, posts_count, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (category_id, category.name, category.description, 0, created_at))
    
    return CategoryResponse(
        category_id=category_id, name=category.name, description=category.description,
        posts_count=0, created_at=created_at
    )

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get a Category by ID",
    description="Retrieves a specific category by its UUID.",
    response_description="The requested category object with its details."
)
async def get_category(category_id: UUID = Path(..., description="The UUID of the category to retrieve")):
    session = await get_session()
    row = session.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,)).one()
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse(**row._asdict())

@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="List All Categories",
    description="Retrieves a list of all categories in the system.",
    response_description="A list of category objects."
)
async def list_categories():
    session = await get_session()
    rows = session.execute("SELECT * FROM categories").all()
    return [CategoryResponse(**row._asdict()) for row in rows]

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a Category",
    description="Updates an existing category’s name and/or description.",
    response_description="The updated category object with its details."
)
async def update_category(
    category_id: UUID = Path(..., description="The UUID of the category to update"),
    category: CategoryCreate = Body(..., description="Request body with new name and/or description")
):
    session = await get_session()
    existing = session.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,)).one()
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")
    
    updated_at = datetime.utcnow()
    session.execute("""
        UPDATE categories SET name = %s, description = %s, updated_at = %s
        WHERE category_id = %s
    """, (category.name, category.description, updated_at, category_id))
    
    updated = session.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,)).one()
    return CategoryResponse(**updated._asdict())

@router.delete(
    "/{category_id}",
    summary="Delete a Category",
    description="Deletes a category by its UUID.",
    response_description="A confirmation message with the deleted category’s UUID."
)
async def delete_category(category_id: UUID = Path(..., description="The UUID of the category to delete")):
    session = await get_session()
    existing = session.execute("SELECT category_id FROM categories WHERE category_id = %s", (category_id,)).one()
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")
    
    session.execute("DELETE FROM categories WHERE category_id = %s", (category_id,))
    return {"message": "Category deleted", "category_id": category_id}