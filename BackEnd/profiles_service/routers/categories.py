from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from crud import NotFoundError
from schemas.categories import Category
from crud.categories import CategoryRepository
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_async_session


router = APIRouter(
    tags=["Categories"]
)


@router.get("/", status_code=200)
async def categories_list(session: AsyncSession = Depends(get_async_session)):
    categories = await CategoryRepository.get_all(session=session)
    return categories


@router.post("/", status_code=201)
async def create_category(
    category: Annotated[Category, Depends()],
    session: AsyncSession = Depends(get_async_session)
    ):
    category = await CategoryRepository.add_one(category, session=session)
    
    return category


@router.get("/{category_id}", status_code=200)
async def categorys_detail(
    category_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        category = await CategoryRepository.get_by_id(category_id, session=session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return category


@router.put("/{category_id}")
async def category_update(
    category_id: int, 
    category_data: Annotated[Category, Depends()],
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        category = await CategoryRepository.update(category_id, category_data, session=session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return category


@router.delete("/{category_id}")
async def category_delete(
    category_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        category = await CategoryRepository.delete(category_id, session=session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return Response(status_code=204)