from fastapi import Body, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from models.profiles import StartupProfileOrm, InvestorProfileOrm
from models.categories import StartupCategoryOrm
from models.regions import RegionOrm
from repositories import BaseRepository, ProfileRepository
from schemas.profiles import StatusEnum, Startup, StartupOptional, Investor, InvestorOptional
from typing import List
from database import new_session
from services.categories import CategoryService
from services.profiles import ProfileStartupService
from services.investors import InvestorsService 
from services.regions import RegionService


def startup_create_dependency(
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
) -> Startup:
    try:
        profile = Startup(
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


def startup_optional_create_dependency(
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
) -> StartupOptional:
    try:
        profile = StartupOptional(
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


def investor_create_dependency(
    name: str = Body(...),
    status: StatusEnum = Body(...),
    is_legal_entity: bool = Body(False),
    phone: str = Body(None),
    edrpou: str = Body(None),
    rnokpp: str = Body(None),
    investment_categories: List[int] = Body(None),
) -> Investor:
    try:
        profile = Investor(
            name=name,
            status=status,
            is_legal_entity=is_legal_entity, 
            phone=phone,
            edrpou=edrpou,
            rnokpp=rnokpp,
            investment_categories=investment_categories,
        )
    except ValidationError as e:
        error_messages = [error['msg'] for error in e.errors()]
        raise HTTPException(status_code=422, detail=error_messages)
    return profile


def investor_optional_create_dependency(
    name: str = Body(None),
    status: StatusEnum = Body(None),
    is_legal_entity=Body(False),
    phone: str = Body(None),
    edrpou: str = Body(None),
    rnokpp: str = Body(None),
    investment_categories: List[int] = Body(None),
) -> InvestorOptional:
    try:
        profile = InvestorOptional(
            name=name,
            status=status,
            is_legal_entity=is_legal_entity, 
            phone=phone,
            edrpou=edrpou,
            rnokpp=rnokpp,
            investment_categories=investment_categories,
        )
    except ValidationError as e:
        error_messages = [error['msg'] for error in e.errors()]
        raise HTTPException(status_code=422, detail=error_messages)
    return profile


async def get_async_session() -> AsyncSession:
    async with new_session() as session:
        yield session



def get_startup_service(session: AsyncSession = Depends(get_async_session)):
    repo = ProfileRepository(model=StartupProfileOrm, session=session)
    return ProfileStartupService(repo)


def get_investor_service(session: AsyncSession = Depends(get_async_session)):
    repo = ProfileRepository(model=InvestorProfileOrm, session=session)
    return InvestorsService(repo)


def get_caterory_service(session: AsyncSession = Depends(get_async_session)):
    repo = BaseRepository(model=StartupCategoryOrm, session=session)
    return CategoryService(repo)


def get_region_service(session: AsyncSession = Depends(get_async_session)):
    repo = BaseRepository(model=RegionOrm, session=session)
    return RegionService(repo)