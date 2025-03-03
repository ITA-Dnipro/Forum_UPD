from sqlalchemy import select
from database import new_session
from models.regions import RegionOrm
from schemas.regions import Region
from fastapi import HTTPException

class RegionRepository:
    @staticmethod
    async def add_one(data: Region):
        async with new_session() as session:
            region_dict = data.model_dump()
            region = RegionOrm(**region_dict)
            session.add(region)
            await session.flush()
            await session.commit()
            return region.id


    @staticmethod
    async def get_all():
        async with new_session() as session:
            query = select(RegionOrm)
            result = await session.execute(query)
            region_models = result.scalars().all()
            return region_models


    @staticmethod
    async def get_by_id_or_404(region_id: int):
        async with new_session() as session:
            region = await session.get(RegionOrm, region_id)
            if not region:
                raise HTTPException(
                    status_code=404, detail="region not found"
                    )
            return region
    
    @staticmethod
    async def get_list_by_ids(regions_id: list[int]):
        """
        Takes list of region ids and returns list of respective RegionOrm objects
        """
        async with new_session() as session:
            regions = await session.execute(
            select(RegionOrm).where(RegionOrm.id.in_(regions_id))
            )
            regions = regions.scalars().all()
            if not regions:
                raise HTTPException(status_code=400, detail="Invalid region IDs")
            return regions
        
            
    @staticmethod
    async def update_or_404(region_id: int, data: Region):
        async with new_session() as session:
            region = await session.get(RegionOrm, region_id)
            if not region:
                raise HTTPException(
                    status_code=404, detail="region not found"
                    )
            region.__dict__.update(data)
            await session.flush()
            await session.commit()
            return region
    
    @staticmethod
    async def delete_or_404(region_id: int):
        async with new_session() as session:
            region = await session.get(RegionOrm, region_id)
            if not region:
                raise HTTPException(
                    status_code=404, detail="region not found"
                    )
            await session.delete(region)
            await session.commit()
            return region
            
