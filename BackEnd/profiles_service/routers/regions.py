from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from exceptions import NotFoundError
from schemas.regions import Region
from crud.regions import RegionRepository
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_async_session

router = APIRouter(
    tags=["regions"]
)


@router.get("/", status_code=200)
async def regions_list(session: AsyncSession = Depends(get_async_session)):
    regions = await RegionRepository.get_all(session=session)
    return regions


@router.post("/", status_code=201)
async def create_region(
    region: Annotated[Region, Depends()],
    session: AsyncSession = Depends(get_async_session)
    ):
    region = await RegionRepository.add_one(region, session=session)
    
    return region


@router.get("/{region_id}", status_code=200)
async def regions_detail(
    region_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        region = await RegionRepository.get_by_id(region_id, session=session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return region


@router.put("/{region_id}")
async def region_update(
    region_id: int, 
    region_data: Annotated[Region, Depends()],
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        region = await RegionRepository.update(region_id, region_data, session=session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return region


@router.delete("/{region_id}")
async def region_delete(
    region_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        await RegionRepository.delete(region_id, session=session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return Response(status_code=204)