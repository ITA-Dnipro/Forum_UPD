from fastapi import Body, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.profiles import Profile, StatusEnum, ProfileOptional
from typing import List
from database import new_session

def profile_create_dependency(
    name: str = Body(...),
    status: StatusEnum = Body(...),
    is_registered: bool = Body(False),
    is_startup: bool = Body(False),
    is_fop: bool = Body(False),
    profile_categories: List[int] = Body(...),
    profile_regions: List[int] = Body(...) ,
) -> Profile:
    try:
        profile = Profile(
        name=name,
        status=status,
        is_registered=is_registered,
        is_startup=is_startup,
        is_fop=is_fop,
        profile_categories = profile_categories,
        profile_regions = profile_regions
    )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
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
        raise HTTPException(status_code=422, detail=e.errors())
    return profile


async def get_async_session() -> AsyncSession:
    async with new_session() as session:
        yield session
