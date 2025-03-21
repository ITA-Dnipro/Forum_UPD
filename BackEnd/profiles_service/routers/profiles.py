from typing import Annotated
from fastapi import APIRouter, Depends, Response
from exceptions import NotFoundError
from schemas.profiles import ProfileOptional, Profile
from services.profiles import ProfileStartupService
from dependencies import get_startup_service, profile_create_dependency, profile_optional_create_dependency
from fastapi import HTTPException


router = APIRouter(
    tags=["Startup_profiles"]
)


@router.get("/", status_code=200)
async def startup_profiles_list(
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)],
    ):
    profiles = await service.startups_list()
    return profiles


@router.post("/", status_code=201)
async def create_startup_profile(
    profile: Annotated[Profile, Depends(dependency=profile_create_dependency)],
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    profile = await service.add_startup(profile)
    return profile


@router.get("/{profile_id}", status_code=200)
async def startup_profiles_detail(
    profile_id: int, 
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        profile = await service.get_startup_by_id(profile_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.put("/{profile_id}")
async def startup_profile_update(
    profile_id: int, 
    profile_data: Annotated[Profile, Depends(dependency=profile_create_dependency)],
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        profile = await service.partial_startup_update(profile_id, profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.patch("/{profile_id}")
async def startup_profile_partial_update(
    profile_id: int, 
    profile_data: Annotated[ProfileOptional, Depends(dependency=profile_optional_create_dependency)],
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        profile = await service.partial_startup_update(profile_id, data=profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.delete("/{profile_id}")
async def startup_profile_delete(
    profile_id: int,
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        await service.startup_delete(profile_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return Response(status_code=204)