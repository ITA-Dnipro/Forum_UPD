from typing import Annotated
from fastapi import APIRouter, Depends, Response
from exceptions import NotFoundError
from schemas.profiles import ProfileOptional, Profile
from crud.profiles import ProfileStartupRepository
from services.profiles import ProfileStartupService
from dependencies import profile_create_dependency, profile_optional_create_dependency, get_async_session
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.profiles import StartupProfileOrm


router = APIRouter(
    tags=["Startup_profiles"]
)


@router.get("/", status_code=200)
async def startup_profiles_list(
    session: AsyncSession = Depends(get_async_session)
    ):
    profiles = await ProfileStartupService(model=StartupProfileOrm, session=session).startups_list()
    return profiles


@router.post("/", status_code=201)
async def create_startup_profile(
    profile: Annotated[Profile, Depends(dependency=profile_create_dependency)],
    session: AsyncSession = Depends(get_async_session)
    ):
    profile = await ProfileStartupService(model=StartupProfileOrm, session=session).add_startup(profile)
    return profile


@router.get("/{profile_id}", status_code=200)
async def startup_profiles_detail(
    profile_id: int, 
    session: AsyncSession = Depends(get_async_session)):
    try:
        profile = await ProfileStartupService(model=StartupProfileOrm, session=session).get_startup_by_id(profile_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.put("/{profile_id}")
async def startup_profile_update(
    profile_id: int, 
    profile_data: Annotated[Profile, Depends(dependency=profile_create_dependency)],
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        profile = await ProfileStartupService(model=StartupProfileOrm, session=session).partial_startup_update(profile_id, profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.patch("/{profile_id}")
async def startup_profile_partial_update(
    profile_id: int, 
    profile_data: Annotated[ProfileOptional, Depends(dependency=profile_optional_create_dependency)],
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        profile = await ProfileStartupService(model=StartupProfileOrm, session=session).partial_startup_update(profile_id, data=profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.delete("/{profile_id}")
async def startup_profile_delete(
    profile_id: int,
    session: AsyncSession = Depends(get_async_session)
    ):
    try:
        await ProfileStartupRepository(session=session).soft_delete(profile_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return Response(status_code=204)