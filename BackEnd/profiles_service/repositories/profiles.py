from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
from core.exceptions import InvalidRelatedEntityError, NotFoundError
from models.base import Model
from repositories.base import BaseRepository

class ProfileRepository(BaseRepository):

    def __init__(self, model: Model, session: AsyncSession):
        super().__init__(model, session)


    def _get_query(self):
        return select(self.model).where(self.model.is_deleted == False)
    

    async def add_one(self, profile_dict: dict):
        profile_dict["is_deleted"] = False
        return await super().add_one(profile_dict)


class InvestorRepository(ProfileRepository):

    def __init__(
            self, 
            model: Model, 
            session: AsyncSession, 
            startup_category_repo: BaseRepository=None
            ):
        
        super().__init__(model, session)
        self.startup_category_repo=startup_category_repo


    async def _fetch_related_by_id(self, data: dict):
        if data.get("investment_categories") is not None:
            try:
                data["investment_categories"] = await self.startup_category_repo.get_list_by_ids(data["investment_categories"])
            except NotFoundError: 
                raise InvalidRelatedEntityError("One or more categories does not exist")
        
        return data

    async def add_one(self, profile_dict):
        print('Im here')
        profile_dict = await self._fetch_related_by_id(profile_dict)
        
        profile = await super().add_one(profile_dict)
        
        return profile
    
    async def update(self, instance_id, data):
        data = await self._fetch_related_by_id(data)
        return await super().update(instance_id, data)



class InvestorRepository(ProfileRepository):

    def __init__(
            self, 
            model: Model, 
            session: AsyncSession, 
            startup_category_repo: BaseRepository=None
            ):
        
        super().__init__(model, session)
        self.startup_category_repo=startup_category_repo


    async def _fetch_related_by_id(self, data: dict):
        if data.get("investment_categories") is not None:
            try:
                data["investment_categories"] = await self.startup_category_repo.get_list_by_ids(data["investment_categories"])
            except NotFoundError: 
                raise InvalidRelatedEntityError("One or more categories does not exist")
        
        return data

    async def add_one(self, profile_dict):
        profile_dict = await self._fetch_related_by_id(profile_dict)
        profile = await super().add_one(profile_dict)
        return profile
    
    async def update(self, instance_id, data):
        data = await self._fetch_related_by_id(data)
        return await super().update(instance_id, data)
    

class StartupRepository(ProfileRepository):

    def __init__(
            self, 
            model: Model, 
            session: AsyncSession, 
            category_repo: BaseRepository=None, 
            region_repo: BaseRepository=None, 
            ):
        
        super().__init__(model, session)
        self.category_repo = category_repo
        self.region_repo = region_repo


    async def add_one(self, profile_dict):
        profile_dict = await self._fetch_related_by_id(profile_dict)
        return await super().add_one(profile_dict)
    
    async def update(self, instance_id, data):
        data = await self._fetch_related_by_id(data)
        return await super().update(instance_id, data)
    

    
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