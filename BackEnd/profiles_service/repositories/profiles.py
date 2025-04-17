from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
from core.exceptions import InvalidRelatedEntityError, NotFoundError
from models.base import Model
from repositories.base import BaseRepository

class ProfileRepository(BaseRepository):

    def __init__(self, model: Model, session: AsyncSession):
        super().__init__(model, session)
        self.related_repos = {}


    def _get_query(self):
        return select(self.model).where(self.model.is_deleted == False)
    

    async def _fetch_related_by_id(self, data:dict):
        for field, repo in self.related_repos.items():
            if data.get(field) is not None:
                try:
                    data[field] = await repo.get_list_by_ids(data[field])
                except NotFoundError: 
                    raise InvalidRelatedEntityError(f"One or more {field} does not exist")
        return data


    async def add_one(self, profile_dict: dict):
        profile_dict = await self._fetch_related_by_id(profile_dict)
        profile_dict["is_deleted"] = False
        profile = await super().add_one(profile_dict)
        return profile
    
    async def update(self, instance_id, data):
        data = await self._fetch_related_by_id(data)

        profile = await super().update(instance_id, data)

        return profile


class InvestorRepository(ProfileRepository):

    def __init__(
            self, 
            model: Model, 
            session: AsyncSession, 
            startup_category_repo: BaseRepository=None
            ):
        
        super().__init__(model, session)
        self.startup_category_repo=startup_category_repo
        self.related_repos = {
            "investment_categories": self.startup_category_repo
        }


    async def update(self, instance_id, data):
        data = await self._fetch_related_by_id(data)

        profile = await super().update(instance_id, data)

        if "edrpou" in data or "rnokpp" in data:
            if profile.validations:
                await self.validation_repo.update(profile.validations.id, {"profile_id": profile.id})
            else:
                await self.validation_repo.add_one({"profile_id": profile.id})

        return profile
    

class StartupRepository(ProfileRepository):

    def __init__(
            self, 
            model: Model, 
            session: AsyncSession, 
            category_repo: BaseRepository=None, 
            region_repo: BaseRepository=None, 
            validation_repo: BaseRepository=None
            ):
        
        super().__init__(model, session)
        self.category_repo = category_repo
        self.region_repo = region_repo
        self.validation_repo = validation_repo
        self.related_repos = {
            "profile_categories": self.category_repo,
            "profile_regions": self.region_repo
        }
    
    async def update(self, instance_id, data):

        profile = await super().update(instance_id, data)

        if "edrpou" in data or "rnokpp" in data:
            if profile.validations:
                await self.validation_repo.update(profile.validations.id, {"profile_id": profile.id})
            else:
                await self.validation_repo.add_one({"profile_id": profile.id})

        return profile