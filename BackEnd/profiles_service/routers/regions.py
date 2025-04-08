from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from core.exceptions import NotFoundError, UniqueConstraintViolationError
from schemas.regions import Region, RegionResponse
from services.regions import RegionService
from dependencies import get_region_service


router = APIRouter(
    tags=["Regions"]
)


@router.get("/", status_code=200, response_model=List[RegionResponse])
async def regions_list(service: RegionService = Depends(get_region_service)):
    regions = await service.get_all()
    return regions


@router.post("/", status_code=201, response_model=RegionResponse)
async def create_region(
    region: Annotated[Region, Depends()],
    service: RegionService = Depends(get_region_service)
    ):
    try:
        region = await service.add_one(region)
    except UniqueConstraintViolationError:
        raise HTTPException(
            status_code=400, detail="Region already exists"
            )
    
    return region


@router.get("/{region_id}", status_code=200, response_model=RegionResponse)
async def regions_detail(
    region_id: int,
    service: RegionService = Depends(get_region_service)
    ):
    try:
        region = await service.get_by_id(region_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return region


@router.put("/{region_id}", response_model=RegionResponse)
async def region_update(
    region_id: int, 
    region_data: Annotated[Region, Depends()],
    service: RegionService = Depends(get_region_service)
    ):
    try:
        region = await service.update(region_id, region_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return region
