from typing import Annotated
from fastapi import APIRouter, Depends
from schemas.profiles import Profile
from crud.profiles import ProfileRepository


router = APIRouter(
    tags=["Profiles"]
)


@router.get("/", status_code=200)
async def profiles_list():
    profiles = await ProfileRepository.get_all()
    return profiles


@router.post("/", status_code=201)
async def create_profile(
    profile: Profile #Annotated[Profile, Depends()]
    ):
    profile_id = await ProfileRepository.add_one(profile)
    
    return {
        "message": "ok",
        "profile_id": profile_id}


@router.get("/{profile_id}", status_code=200)
async def profiles_detail(profile_id: int):
    profile = await ProfileRepository.get_by_id_or_404(profile_id)
    return profile


@router.put("/{profile_id}")
async def profile_update(
    profile_id: int, profile_data: Annotated[Profile, Depends()]
    ):
    profile = await ProfileRepository.update_or_404(profile_id, profile_data)
    return profile

@router.delete("/{profile_id}")
async def profile_delete(
    profile_id: int
    ):
    profile = await ProfileRepository.delete_or_404(profile_id)
    return profile