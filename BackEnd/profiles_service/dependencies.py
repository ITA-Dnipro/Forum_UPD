from fastapi import Body, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from models.profiles import StartupProfileOrm
from repositories import ProfileRepository
from schemas.profiles import Profile, StatusEnum, ProfileOptional
from typing import List
from database import new_session
from services.profiles import ProfileStartupService

def profile_create_dependency(
    name: str = Body(...),
    status: StatusEnum = Body(...),
    is_registered: bool = Body(False),
    is_startup: bool = Body(False),
    is_fop: bool = Body(False),
    phone: str = Body(None),
    edrpou: str = Body(None),
    rnokpp: str = Body(None),
    startup_idea: str = Body(None),
    founded: int = Body(None),
    profile_categories: List[int] = Body(None),
    profile_regions: List[int] = Body(None), 
) -> Profile:
    try:
        profile = Profile(
            name=name,
            status=status,
            is_registered=is_registered,
            is_startup=is_startup,
            is_fop=is_fop,
            profile_categories=profile_categories,
            profile_regions=profile_regions,
            phone=phone,
            edrpou=edrpou,
            rnokpp=rnokpp,
            founded=founded,
            startup_idea=startup_idea,
        )
    except ValidationError as e:
        error_messages = [error['msg'] for error in e.errors()]
        raise HTTPException(status_code=422, detail=error_messages)
    return profile


def profile_optional_create_dependency(
    name: str = Body(None),
    status: StatusEnum = Body(None),
    is_registered: bool = Body(False),
    is_startup: bool = Body(False),
    is_fop: bool = Body(False),
    phone: str = Body(None),
    edrpou: str = Body(None),
    rnokpp: str = Body(None),
    startup_idea: str = Body(None),
    founded: int = Body(None),
    profile_categories: List[int] = Body(None),
    profile_regions: List[int] = Body(None), 
) -> ProfileOptional:
    try:
        profile = ProfileOptional(
            name=name,
            status=status,
            is_registered=is_registered,
            is_startup=is_startup,
            is_fop=is_fop,
            profile_categories=profile_categories,
            profile_regions=profile_regions,
            phone=phone,
            edrpou=edrpou,
            rnokpp=rnokpp,
            founded=founded,
            startup_idea=startup_idea,
        )
    except ValidationError as e:
        error_messages = [error['msg'] for error in e.errors()]
        raise HTTPException(status_code=422, detail=error_messages)
    return profile


async def get_async_session() -> AsyncSession:
    async with new_session() as session:
        yield session


def get_startup_profile_repo(session: AsyncSession = Depends(get_async_session)):
    return ProfileRepository(model=StartupProfileOrm, session=session)


def get_startup_service(repo: ProfileStartupService = Depends(dependency=get_startup_profile_repo)):
    return ProfileStartupService(repo)