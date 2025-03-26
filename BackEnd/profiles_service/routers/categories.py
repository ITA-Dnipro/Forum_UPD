from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from exceptions import NotFoundError, UniqueConstraintViolationError
from schemas.categories import Category, CategoryResponse
from services.categories import CategoryService
from dependencies import get_caterory_service


router = APIRouter(
    tags=["Categories"]
)


@router.get("/", status_code=200, response_model=List[CategoryResponse])
async def categories_list(
    service: CategoryService = Depends(get_caterory_service)
    ):
    categories = await service.get_all()
    return categories


@router.post("/", status_code=201, response_model=CategoryResponse)
async def create_category(
    category: Annotated[Category, Depends()],
    service: CategoryService = Depends(get_caterory_service)
    ):
    try:
        category = await service.add_one(category)
    except UniqueConstraintViolationError:
        raise HTTPException(
            status_code=400, detail="Category already exists"
            )
    
    return category


@router.get("/{category_id}", status_code=200, response_model=CategoryResponse)
async def categories_detail(
    category_id: int,
    service: CategoryService = Depends(get_caterory_service)
    ):
    try:
        category = await service.get_by_id(category_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def category_update(
    category_id: int, 
    category_data: Annotated[Category, Depends()],
    service: CategoryService = Depends(get_caterory_service)
    ):
    try:
        category = await service.update(category_id, category_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return category
