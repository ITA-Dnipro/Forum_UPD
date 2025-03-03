from sqlalchemy import select
from database import new_session
from models.profiles import ProfileOrm
from crud.categories import CategoryRepository
from crud.regions import RegionRepository
from schemas.profiles import Profile
from fastapi import HTTPException

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
            await session.flush()
            await session.commit()
            return profile.id


    @staticmethod
    async def get_all():
        async with new_session() as session:
            query = select(ProfileOrm)
            result = await session.execute(query)
            profile_models = result.scalars().all()
            return profile_models


    @staticmethod
    async def get_by_id_or_404(profile_id: int):
        async with new_session() as session:
            profile = await session.get(ProfileOrm, profile_id)
            if not profile:
                raise HTTPException(
                    status_code=404, detail="Profile not found"
                    )
            return profile
        
            
    @staticmethod
    async def update_or_404(profile_id: int, data: Profile):
        async with new_session() as session:
            profile = await session.get(ProfileOrm, profile_id)
            if not profile:
                raise HTTPException(
                    status_code=404, detail="Profile not found"
                    )
            profile.__dict__.update(data)
            await session.flush()
            await session.commit()
            return profile


    @staticmethod
    async def delete_or_404(profile_id: int):
        async with new_session() as session:
            profile = await session.get(ProfileOrm, profile_id)
            if not profile:
                raise HTTPException(
                    status_code=404, detail="Profile not found"
                    )
            await session.delete(profile)
            await session.commit()
            return profile
            
