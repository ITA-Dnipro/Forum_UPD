from typing import Annotated
from fastapi import APIRouter, Depends
from schemas.profiles import ProfileOptional, Profile
from crud.profiles import ProfileRepository
from dependencies import profile_create_dependency, profile_optional_create_dependency
from fastapi import HTTPException

router = APIRouter(
    tags=["Profiles"]
)


@router.get("/", status_code=200)
async def profiles_list():
    profiles = await ProfileRepository.get_all()
    return profiles


@router.post("/", status_code=201)
async def create_profile(
    profile: Annotated[Profile, Depends(dependency=profile_create_dependency)]
    ):
    profile_id = await ProfileRepository.add_one(profile)
    
    return {
        "message": "ok",
        "profile_id": profile_id}


@router.get("/{profile_id}", status_code=200)
async def profiles_detail(profile_id: int):
    profile = await ProfileRepository.get_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=404, detail="Profile not found"
            )
    return profile


@router.put("/{profile_id}")
async def profile_update(
    profile_id: int, profile_data: Annotated[Profile, Depends(dependency=profile_create_dependency)]
    ):
    profile = await ProfileRepository.update(profile_id, profile_data)
    if not profile:
        raise HTTPException(
            status_code=404, detail="Profile not found"
            )
    return profile


@router.patch("/{profile_id}")
async def profile_partial_update(
    profile_id: int, profile_data: Annotated[ProfileOptional, Depends(dependency=profile_optional_create_dependency)]
    ):
    profile = await ProfileRepository.partial_update(profile_id, profile_data)
    if not profile:
        raise HTTPException(
            status_code=404, detail="Profile not found"
            )
    return profile


@router.delete("/{profile_id}")
async def profile_delete(
    profile_id: int
    ):
    profile = await ProfileRepository.delete(profile_id)
    if not profile:
        raise HTTPException(
            status_code=404, detail="Profile not found"
            )
    return profile