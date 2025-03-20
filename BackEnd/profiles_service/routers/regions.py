from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from exceptions import NotFoundError
from schemas.regions import Region
from services.regions import RegionService
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_async_session
from models.regions import RegionOrm 


router = APIRouter(
    tags=["Regions"]
)


@router.get("/", status_code=200)
async def regions_list(session: AsyncSession = Depends(get_async_session)):
    regions = await RegionService(model=RegionOrm, session=session).get_all()
    return regions


@router.post("/", status_code=201)
async def create_region(
    region: Annotated[Region, Depends()],
    session: AsyncSession = Depends(get_async_session)
    ):
    region = await RegionService(model=RegionOrm, session=session).add_one(region)
    
    return region


@router.get("/{region_id}", status_code=200)
async def regions_detail(
    region_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        region = await RegionService(model=RegionOrm, session=session).get_by_id(region_id)
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
        region = await RegionService(model=RegionOrm, session=session).update(region_id, region_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return region
