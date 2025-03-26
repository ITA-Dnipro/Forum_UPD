from models.categories import StartupCategoryOrm
from models.regions import RegionOrm
from models.profiles import StatusEnum
from schemas.profiles import Startup, StartupOptional, ModerationFeedback, ProfileModerationEnum
from exceptions import InvalidRelatedEntityError, NotFoundError
from utils.repositories import ProfileRepository, BaseRepository



class ProfileStartupService:

    def __init__(self, repo: ProfileRepository):
        self.repository = repo


    async def _fetch_related_by_id(self, data: dict):
        if data.get("profile_categories") is not None:
            category_repo = BaseRepository(model=StartupCategoryOrm, session=self.repository.session)
            try:
                data["profile_categories"] = await category_repo.get_list_by_ids(data["profile_categories"])
            except NotFoundError: 
                raise InvalidRelatedEntityError("One or more categories does not exist")

        if data.get("profile_regions") is not None: 
            region_repo = BaseRepository(model=RegionOrm, session=self.repository.session)
            try:
                data["profile_regions"] = await region_repo.get_list_by_ids(data["profile_regions"])
            except NotFoundError: 
                raise InvalidRelatedEntityError("One or more regions does not exist")
        
        return data

    async def startups_list(self):
        return await self.repository.get_all()

    async def get_startup_by_id(self, startup_id):
        return await self.repository.get_by_id(startup_id)
    

    async def add_startup(self, data: Startup):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        profile_dict["status"] = StatusEnum.PENDING if "banner_id" in profile_dict else StatusEnum.UNDEFINED
        profile_dict = await self._fetch_related_by_id(profile_dict)
        return await self.repository.add_one(profile_dict=profile_dict)
    

    async def partial_startup_update(self, profile_id: int, data: StartupOptional):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        if "banner_id" in profile_dict:
            profile_dict["status"] = StatusEnum.PENDING 
        profile_dict = await self._fetch_related_by_id(data=profile_dict)
        return await self.repository.partial_update(instance_id=profile_id, update_fields=profile_dict)


    async def startup_update(self, profile_id: int, data: Startup):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        if "banner_id" in profile_dict:
            profile_dict["status"] = StatusEnum.PENDING 
        profile_dict["status"] = StatusEnum.PENDING if "banner_id" in profile_dict else StatusEnum.UNDEFINED
        self._fetch_related_by_id(profile_dict)
        
        return await self.repository.update(instance_id=profile_id, profile_dict=profile_dict)


    async def startup_delete(self, profile_id: int):
        await self.repository.soft_delete(profile_id)

    
    async def handle_moderation_feedback(self, profile_id, feedback: ModerationFeedback):

        feedback_dict = feedback.model_dump()
        if feedback_dict["moderation_status"] == ProfileModerationEnum.APPROVED:  
            update_fields = {"status": StatusEnum.APPROVED}
        elif feedback_dict["moderation_status"] == ProfileModerationEnum.REJECTED:
            update_fields = {"status": StatusEnum.BLOCKED}
        return await self.repository.partial_update(instance_id=profile_id, update_fields=update_fields)



