from models.categories import StartupCategoryOrm
from models.regions import RegionOrm
from schemas.profiles import Profile, ProfileOptional
from exceptions import NotFoundError
from repositories import ProfileRepository, BaseRepository



class ProfileStartupService:

    def __init__(self, repo: ProfileRepository):
        self.repository = repo
    
    async def startups_list(self):
        return await self.repository.get_all()

    async def get_startup_by_id(self, startup_id):
        return await self.repository.get_by_id(startup_id)
    

    async def add_startup(self, data: Profile):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)

        if profile_dict.get("profile_categories") is not None:
            category_repo = BaseRepository(model=StartupCategoryOrm, session=self.repository.session)
            profile_dict["profile_categories"] = await category_repo.get_list_by_ids(profile_dict["profile_categories"])

        if profile_dict.get("profile_regions") is not None: 
            region_repo = BaseRepository(model=RegionOrm, session=self.repository.session)
            profile_dict["profile_regions"] = await region_repo.get_list_by_ids(profile_dict["profile_regions"])

        return await self.repository.add_one(profile_dict=profile_dict)
    

    async def partial_startup_update(self, profile_id: int, data: ProfileOptional):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)

        if profile_dict.get("profile_categories") is not None:
            category_repo = BaseRepository(model=StartupCategoryOrm, session=self.repository.session)
            profile_dict["profile_categories"] = await category_repo.get_list_by_ids(profile_dict["profile_categories"])

        if profile_dict.get("profile_regions") is not None: 
            region_repo = BaseRepository(model=RegionOrm, session=self.repository.session)
            profile_dict["profile_regions"] = await region_repo.get_list_by_ids(profile_dict["profile_regions"])

        return await self.repository.partial_update(profile_id=profile_id, update_fields=profile_dict)


    async def startup_update(self, profile_id: int, data: Profile):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)

        if profile_dict.get("profile_categories") is not None:
            category_repo = BaseRepository(model=StartupCategoryOrm, session=self.repository.session)
            profile_dict["profile_categories"] = await category_repo.get_list_by_ids(profile_dict["profile_categories"])

        if profile_dict.get("profile_regions") is not None: 
            region_repo = BaseRepository(model=RegionOrm, session=self.repository.session)
            profile_dict["profile_regions"] = await region_repo.get_list_by_ids(profile_dict["profile_regions"])

        return await self.repository.update(profile_id=profile_id, profile_dict=profile_dict)


    async def startup_delete(self, profile_id: int):
        await self.repository.soft_delete(profile_id)

