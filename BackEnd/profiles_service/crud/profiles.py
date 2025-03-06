from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.orm import selectinload
from models.profiles import ProfileOrm
from crud.categories import CategoryRepository
from crud.regions import RegionRepository
from schemas.profiles import Profile, ProfileOptional
from exceptions import NotFoundError

class ProfileRepository:
    @staticmethod
    async def add_one(data: Profile, session: AsyncSession):
        profile_dict = data.model_dump()
        categories = await CategoryRepository.get_list_by_ids(profile_dict["profile_categories"], session=session)
        profile_dict["profile_categories"] = categories
        regions = await RegionRepository.get_list_by_ids(profile_dict["profile_regions"], session=session)
        profile_dict["profile_regions"] = regions
        profile = ProfileOrm(**profile_dict)
        session.add(profile)
        await session.commit()
        return profile


    @staticmethod
    async def get_all(session: AsyncSession):
        query = select(ProfileOrm)\
        .options(selectinload(ProfileOrm.profile_categories))\
        .options(selectinload(ProfileOrm.profile_regions))
        result = await session.execute(query)
        profile_models = result.scalars().all()
        return profile_models


    @staticmethod
    async def get_by_id(profile_id: int, session: AsyncSession):
        query = select(ProfileOrm).where(ProfileOrm.id == profile_id)\
        .options(selectinload(ProfileOrm.profile_categories))\
        .options(selectinload(ProfileOrm.profile_regions))
        result = await session.execute(query)
        profile = result.scalars().first()
        if not profile:
            raise NotFoundError("Profile not foud")
        return profile
        
            
    @classmethod
    async def update(cls, profile_id: int, data: Profile, session: AsyncSession):
        profile = await cls.get_by_id(profile_id, session=session)
        profile_dict = data.model_dump()
        categories = await CategoryRepository.get_list_by_ids(profile_dict["profile_categories"], session=session)
        profile_dict["profile_categories"] = categories
        regions = await RegionRepository.get_list_by_ids(profile_dict["profile_regions"], session=session)
        profile_dict["profile_regions"] = regions
        profile.__dict__.update(profile_dict)
        await session.commit()
        return profile
       

    @classmethod
    async def partial_update(cls, profile_id: int, data: ProfileOptional, session: AsyncSession): 
        profile = await cls.get_by_id(profile_id, session=session)
        update_fields : dict = data.model_dump(exclude_unset=True, exclude_defaults=True)
        
        if update_fields.get("profile_categories") is not None: 
            update_fields["profile_categories"] = await CategoryRepository.get_list_by_ids(update_fields["profile_categories"], session=session)
            
        if update_fields.get("profile_regions") is not None: 
            update_fields["profile_regions"] = await RegionRepository.get_list_by_ids(update_fields["profile_regions"], session=session)

        for key, value in update_fields.items():
            setattr(profile, key, value)
        session.commit()
        return profile


    @classmethod
    async def delete(cls, profile_id: int, session: AsyncSession):
        profile = cls.get_by_id(profile_id, session=session)
        await session.delete(profile)
        await session.commit()
            
