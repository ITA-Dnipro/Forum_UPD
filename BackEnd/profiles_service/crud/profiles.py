from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import new_session
from models.profiles import ProfileOrm
from crud.categories import CategoryRepository
from crud.regions import RegionRepository
from schemas.profiles import Profile, ProfileOptional

class ProfileRepository:
    @staticmethod
    async def add_one(data: Profile):
        async with new_session() as session:
            profile_dict = data.model_dump()
            categories = await CategoryRepository.get_list_by_ids(profile_dict["profile_categories"])
            profile_dict["profile_categories"] = categories
            regions = await RegionRepository.get_list_by_ids(profile_dict["profile_regions"])
            profile_dict["profile_regions"] = regions
            profile = ProfileOrm(**profile_dict)
            session.add(profile)
            await session.commit()
            return profile.id


    @staticmethod
    async def get_all():
        async with new_session() as session:
            query = select(ProfileOrm)\
            .options(selectinload(ProfileOrm.profile_categories))\
            .options(selectinload(ProfileOrm.profile_regions))
            result = await session.execute(query)
            profile_models = result.scalars().all()
            return profile_models


    @staticmethod
    async def get_by_id(profile_id: int):

        async with new_session() as session:
            profile = await session.get(ProfileOrm, profile_id)
            return profile
        
            
    @staticmethod
    async def update(profile_id: int, data: Profile):
        profile_dict = data.model_dump()
        async with new_session() as session:
            profile = await session.get(ProfileOrm, profile_id)
            if profile:
                categories = await CategoryRepository.get_list_by_ids(profile_dict["profile_categories"])
                regions = await RegionRepository.get_list_by_ids(profile_dict["profile_regions"])
                profile_dict["profile_categories"] = categories
                profile_dict["profile_regions"] = regions
                profile.__dict__.update(profile_dict)
            await session.flush()
            await session.commit()
            return profile
       

    @staticmethod
    async def partial_update(profile_id: int, data: ProfileOptional): 
        update_fields : dict = data.model_dump(exclude_unset=True, exclude_defaults=True)
        async with new_session() as session:
            query = select(ProfileOrm).where(ProfileOrm.id == profile_id)\
            .options(selectinload(ProfileOrm.profile_categories))\
            .options(selectinload(ProfileOrm.profile_regions))
            result = await session.execute(query)
            profile = result.scalars().first()
            
            if update_fields.get("profile_categories") is not None: 
                update_fields["profile_categories"] = [
                    await session.merge(category) for category in await CategoryRepository.get_list_by_ids(update_fields["profile_categories"])
                ]
            if update_fields.get("profile_regions") is not None: 
                update_fields["profile_regions"] = [
                    await session.merge(category) for category in await RegionRepository.get_list_by_ids(update_fields["profile_regions"])
                ]

            for key, value in update_fields.items():
                setattr(profile, key, value)
            session.commit()
            return profile


    @staticmethod
    async def delete(profile_id: int):
        async with new_session() as session:
            profile = await session.get(ProfileOrm, profile_id)
            if profile:
                await session.delete(profile)
                await session.commit()
                return profile
            
