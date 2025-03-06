from typing import Annotated
from fastapi import APIRouter, Depends, Response
from exceptions import NotFoundError
from schemas.profiles import ProfileOptional, Profile
from crud.profiles import ProfileRepository
from dependencies import profile_create_dependency, profile_optional_create_dependency, get_async_session
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    tags=["Profiles"]
)


@router.get("/", status_code=200)
async def profiles_list(session: AsyncSession = Depends(get_async_session)):
    profiles = await ProfileRepository.get_all(session=session)
    return profiles


@router.post("/", status_code=201)
async def create_profile(
    profile: Annotated[Profile, Depends(dependency=profile_create_dependency)],
    session: AsyncSession = Depends(get_async_session)
    ):
    profile = await ProfileRepository.add_one(profile, session)
    return profile


@router.get("/{profile_id}", status_code=200)
async def profiles_detail(
    profile_id: int, 
    session: AsyncSession = Depends(get_async_session)):
    try:
        profile = await ProfileRepository.get_by_id(profile_id, session=session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.put("/{profile_id}")
async def profile_update(
    profile_id: int, 
    profile_data: Annotated[Profile, Depends(dependency=profile_create_dependency)],
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        profile = await ProfileRepository.partial_update(profile_id, profile_data, session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.patch("/{profile_id}")
async def profile_partial_update(
    profile_id: int, 
    profile_data: Annotated[ProfileOptional, Depends(dependency=profile_optional_create_dependency)],
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        profile = await ProfileRepository.partial_update(profile_id, profile_data, session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.delete("/{profile_id}")
async def profile_delete(
    profile_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        await ProfileRepository.partial_update(profile_id, session)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return Response(status_code=204)