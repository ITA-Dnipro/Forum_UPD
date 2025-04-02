from models.startups import StatusEnum
from schemas.profiles import Startup, StartupOptional, ModerationFeedback, ProfileModerationEnum
from core.exceptions import InvalidRelatedEntityError, NotFoundError
from repositories.base import BaseRepository
from repositories.profiles import ProfileRepository
from task import autoapprove_image



MODERATION_HOURS = 0.02


class ProfileStartupService:

    def __init__(self, repo: ProfileRepository, category_repo: BaseRepository, region_repo: BaseRepository, image_repo):
        self.repository = repo
        self.category_repo = category_repo
        self.region_repo = region_repo
        self.image_repo = image_repo


    async def _fetch_related_by_id(self, data: dict):
        if data.get("profile_categories") is not None:
            try:
                data["profile_categories"] = await self.category_repo.get_list_by_ids(data["profile_categories"])
            except NotFoundError: 
                raise InvalidRelatedEntityError("One or more categories does not exist")

        if data.get("profile_regions") is not None: 
            try:
                data["profile_regions"] = await self.region_repo.get_list_by_ids(data["profile_regions"])
            except NotFoundError: 
                raise InvalidRelatedEntityError("One or more regions does not exist")
        return data

    async def startups_list(self):
        return await self.repository.get_all()

    async def get_startup_by_id(self, startup_id):
        return await self.repository.get_by_id(startup_id)
    

    async def add_startup(self, data: Startup):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        profile_dict["status"] = StatusEnum.UNDEFINED
        profile_dict = await self._fetch_related_by_id(profile_dict)
        return await self.repository.add_one(profile_dict=profile_dict)


    async def partial_startup_update(self, profile_id: int, data: StartupOptional):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        if "banner_id" in profile_dict:
            profile_dict["status"] = StatusEnum.PENDING 
            autoapprove_image.apply_async(args=(profile_id,), countdown=MODERATION_HOURS*3600)

        profile_dict = await self._fetch_related_by_id(data=profile_dict)
        return await self.repository.update(instance_id=profile_id, data=profile_dict)


    async def startup_update(self, profile_id: int, data: Startup):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        if "banner_id" in profile_dict:
            profile_dict["status"] = StatusEnum.PENDING 
            autoapprove_image.delay(profile_id=profile_id)

        profile_dict["status"] = StatusEnum.PENDING if "banner_id" in profile_dict else StatusEnum.UNDEFINED
        self._fetch_related_by_id(profile_dict)
        
        return await self.repository.update(instance_id=profile_id, data=profile_dict)


    async def startup_delete(self, profile_id: int):
        await self.repository.soft_delete(profile_id)

    
    async def handle_moderation_feedback(self, profile_id, feedback: ModerationFeedback):     

        feedback_dict = feedback.model_dump()
        if feedback_dict["moderation_status"] == ProfileModerationEnum.APPROVED:  
            profile_update_fields = {"status": StatusEnum.APPROVED}
            profile = await self.repository.update(instance_id=profile_id, data=profile_update_fields)

            banner_id = profile.banner_id
            
            await self.image_repo.update(instance_id=banner_id, data={"is_approved": True})
            
        elif feedback_dict["moderation_status"] == ProfileModerationEnum.REJECTED:
            profile_update_fields = {"status": StatusEnum.BLOCKED}
            await self.repository.soft_delete(profile_id=profile_id)
            profile = await self.repository.update(instance_id=profile_id, data=profile_update_fields)

            banner_id = profile.banner_id
            
            await self.image_repo.update(instance_id=banner_id, data={"is_approved": False})
        return profile



