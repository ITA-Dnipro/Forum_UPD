from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.orm import selectinload
from models.profiles import StartupProfileOrm
from crud.categories import CategoryRepository
from crud.regions import RegionRepository
from exceptions import NotFoundError

class ProfileRepository:

    def __init__(self, model, session: AsyncSession):
        self.model = model
        self.session = session
        self.many_to_many = self._get_many_to_many_fields()

    def _get_many_to_many_fields(self):
        many_to_many_fields = []
        for name, relationship in inspect(self.model).relationships.items():
            if relationship.direction.name == "MANYTOMANY":
                many_to_many_fields.append(name)

        return many_to_many_fields
    

    async def add_one(self, profile_dict: dict):
        try:
            profile_dict["is_deleted"] = False
            profile = self.model(**profile_dict)
            self.session.add(profile)
            await self.session.commit()
            return profile
        except Exception as e:
            await self.session.rollback()
            raise e
        


    async def get_all(self):
        query = select(self.model).where(self.model.is_deleted == False)
        for field in self.many_to_many:
            query = query.options(selectinload(getattr(self.model, field)))

        result = await self.session.execute(query)
        profile_models = result.scalars().all()
        return profile_models


    async def get_by_id(self, profile_id: int):
        query = select(StartupProfileOrm).where(StartupProfileOrm.id == profile_id, StartupProfileOrm.is_deleted == False)
        for field in self.many_to_many:
            query = query.options(selectinload(getattr(self.model, field)))
        result = await self.session.execute(query)
        profile = result.scalars().first()
        if not profile:
            raise NotFoundError("Profile not foud")
        return profile
        
        
    async def update(self, profile_id: int, profile_dict: dict):
        try:
            profile = await self.get_by_id(profile_id)
            for key, value in profile_dict.items():
                setattr(profile, key, value)
            await self.session.commit()
            return profile
        except Exception as e:
            await self.session.rollback()
            raise e
       

    async def partial_update(self, profile_id: int, update_fields: dict): 
        profile = await self.get_by_id(profile_id)
        
        for key, value in update_fields.items():
            setattr(profile, key, value)
        await self.session.commit()
        return profile


    async def soft_delete(self, profile_id: int):
        try:
            profile = await self.get_by_id(profile_id)
            profile.is_deleted = True
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

            

class ProfileStartupRepository(ProfileRepository):

    def __init__(self, session):
        super().__init__(model=StartupProfileOrm, session=session)


    async def _fetch_related(self, data: dict):
        if data.get("profile_categories") is not None:
            data["profile_categories"] = await CategoryRepository.get_list_by_ids(
                data["profile_categories"], session=self.session
            )
        if data.get("profile_regions") is not None:
            data["profile_regions"] = await RegionRepository.get_list_by_ids(
                data["profile_regions"], session=self.session
            )

        return data


    async def add_one(self, profile_dict: dict):
        profile_dict = await self._fetch_related(profile_dict)        
        return await super().add_one(profile_dict=profile_dict)
    

    async def partial_update(self, profile_id: int, update_fields: dict): 
        profile_dict = await self._fetch_related(profile_dict) 
        return await super().partial_update(profile_id=profile_id, update_fields=update_fields)


    async def update(self, profile_id: int, profile_dict: dict):
        profile_dict = await self._fetch_related(profile_dict) 
        return await super().update(profile_id=profile_id, profile_dict=profile_dict)

