from typing import Annotated, List
from fastapi import APIRouter, Depends, Response
from core.exceptions import NotFoundError, InvalidRelatedEntityError
from schemas.profiles import Investor, InvestorOptional, InvestorResponse
from services.investors import InvestorsService 
from dependencies import get_investor_service, investor_create_dependency, investor_optional_create_dependency
from fastapi import HTTPException


router = APIRouter(
    tags=["Investors"]
)


@router.get("/", status_code=200, response_model=List[InvestorResponse])
async def investors_profiles_list(
    service: Annotated[InvestorsService, Depends(dependency=get_investor_service)],
    ):
    profiles = await service.investors_list()
    return profiles


@router.post("/", status_code=201, response_model=InvestorResponse)
async def create_investor_profile(
    profile: Annotated[Investor, Depends(dependency=investor_create_dependency)],
    service: Annotated[InvestorsService, Depends(dependency=get_investor_service)]
    ):
    try:
        profile = await service.add_investor(profile)
        return profile
    except InvalidRelatedEntityError as e:
        raise HTTPException(
            status_code=400, detail=f"{e}"
            )


@router.get("/{profile_id}", status_code=200, response_model=InvestorResponse)
async def investor_profiles_detail(
    profile_id: int, 
    service: Annotated[InvestorsService, Depends(dependency=get_investor_service)]
    ):
    try:
        profile = await service.get_investor_by_id(profile_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.put("/{profile_id}", response_model=InvestorResponse)
async def investor_profile_update(
    profile_id: int, 
    profile_data: Annotated[Investor, Depends(dependency=investor_create_dependency)],
    service: Annotated[InvestorsService, Depends(dependency=get_investor_service)]
    ):
    try:
        profile = await service.partial_investor_update(profile_id, profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    except InvalidRelatedEntityError as e:
        raise HTTPException(
            status_code=422, detail=f"{e}"
            )
    return profile


@router.patch("/{profile_id}", response_model=InvestorResponse)
async def investor_profile_partial_update(
    profile_id: int, 
    profile_data: Annotated[InvestorOptional, Depends(dependency=investor_optional_create_dependency)],
    service: Annotated[InvestorsService, Depends(dependency=get_investor_service)]
    ):
    try:
        profile = await service.partial_investor_update(profile_id, data=profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    except InvalidRelatedEntityError as e:
        raise HTTPException(
            status_code=400, detail=f"{e}"
            )
    return profile


@router.delete("/{profile_id}", response_model=InvestorResponse)
async def investor_profile_delete(
    profile_id: int,
    service: Annotated[InvestorsService, Depends(dependency=get_investor_service)]
    ):
    try:
        await service.investor_delete(profile_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return Response(status_code=204)