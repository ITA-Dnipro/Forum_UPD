from typing import Annotated
from fastapi import APIRouter, Depends
from schemas.categories import Category
from crud.categories import CategoryRepository


router = APIRouter(
    tags=["Categories"]
)


@router.get("/", status_code=200)
async def categories_list():
    categories = await CategoryRepository.get_all()
    return categories


@router.post("/", status_code=201)
async def create_category(
    category: Annotated[Category, Depends()]
    ):
    category_id = await CategoryRepository.add_one(category)
    
    return {
        "message": "ok",
        "category_id": category_id}


@router.get("/{category_id}", status_code=200)
async def categorys_detail(category_id: int):
    category = await CategoryRepository.get_by_id_or_404(category_id)
    return category


@router.put("/{category_id}")
async def category_update(
    category_id: int, category_data: Annotated[Category, Depends()]
    ):
    category = await CategoryRepository.update_or_404(category_id, category_data)
    return category

@router.delete("/{category_id}")
async def category_delete(
    category_id: int
    ):
    category = await CategoryRepository.delete_or_404(category_id)
    return category