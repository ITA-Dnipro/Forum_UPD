from typing import Annotated, List
from fastapi import APIRouter, Depends, Response
from core.exceptions import NotFoundError, InvalidRelatedEntityError
from schemas.profiles import StartupOptional, Startup, ModerationFeedback, StartupResponse, StartupResponseUnverified
from services.startups import ProfileStartupService
from dependencies import get_startup_service, startup_create_dependency, startup_optional_create_dependency
from fastapi import HTTPException


router = APIRouter(
    tags=["Startup_profiles"]
)


@router.get("/", status_code=200, response_model=List[StartupResponse])
async def startup_profiles_list(
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)],
    ):
    profiles = await service.startups_list()
    return profiles


@router.post("/", status_code=201, response_model=StartupResponse)
async def create_startup_profile(
    profile: Annotated[Startup, Depends(dependency=startup_create_dependency)],
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        profile = await service.add_startup(profile)
        return profile
    except InvalidRelatedEntityError as e:
        raise HTTPException(
            status_code=400, detail=f"{e}"
            )


@router.get("/{profile_id}", status_code=200, response_model=StartupResponse)
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


@router.put("/{profile_id}", response_model=StartupResponse)
async def startup_profile_update(
    profile_id: int, 
    profile_data: Annotated[Startup, Depends(dependency=startup_create_dependency)],
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        profile = await service.partial_startup_update(profile_id, profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    except InvalidRelatedEntityError as e:
        raise HTTPException(
            status_code=422, detail=f"{e}"
            )
    return profile


@router.patch("/{profile_id}")
async def startup_profile_partial_update(
    profile_id: int, 
    profile_data: Annotated[StartupOptional, Depends(dependency=startup_optional_create_dependency)],
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        profile = await service.partial_startup_update(profile_id, data=profile_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    except InvalidRelatedEntityError as e:
        raise HTTPException(
            status_code=400, detail=f"{e}"
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



@router.patch("/{profile_id}/images_moderation", response_model=StartupResponse)
async def startup_images_moderation(
    profile_id: int, 
    moderation_feedback: Annotated[ModerationFeedback, Depends()],
    service: Annotated[ProfileStartupService, Depends(dependency=get_startup_service)]
    ):
    try:
        profile = await service.handle_moderation_feedback(profile_id, feedback=moderation_feedback)
    except NotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}"
            )
    return profile


@router.get("/{profile_id}/images_moderation", response_model=StartupResponseUnverified)
async def startup_view_unmoderated_profile(
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