from typing import Annotated
from fastapi import APIRouter, Depends
from schemas.regions import Region
from crud.regions import RegionRepository


router = APIRouter(
    tags=["regions"]
)


@router.get("/", status_code=200)
async def regions_list():
    regions = await RegionRepository.get_all()
    return regions


@router.post("/", status_code=201)
async def create_region(
    region: Annotated[Region, Depends()]
    ):
    region_id = await RegionRepository.add_one(region)
    
    return {
        "message": "ok",
        "region_id": region_id}


@router.get("/{region_id}", status_code=200)
async def regions_detail(region_id: int):
    region = await RegionRepository.get_by_id_or_404(region_id)
    return region


@router.put("/{region_id}")
async def region_update(
    region_id: int, region_data: Annotated[Region, Depends()]
    ):
    region = await RegionRepository.update_or_404(region_id, region_data)
    return region

@router.delete("/{region_id}")
async def region_delete(
    region_id: int
    ):
    region = await RegionRepository.delete_or_404(region_id)
    return region