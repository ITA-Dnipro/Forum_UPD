from sqlalchemy import select
from crud import NotFoundError
from models.regions import RegionOrm
from schemas.regions import Region
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession 


class RegionRepository:
    @staticmethod
    async def add_one(
        data: Region, 
        session: AsyncSession
        ):
        region_dict = data.model_dump()
        region = RegionOrm(**region_dict)
        session.add(region)
        await session.commit()
        return region.id


    @staticmethod
    async def get_all(session: AsyncSession):
        query = select(RegionOrm)
        result = await session.execute(query)
        region_models = result.scalars().all()
        return region_models


    @staticmethod
    async def get_by_id_or_404(
        region_id: int,
        session: AsyncSession
        ):
        region = await session.get(RegionOrm, region_id)
        if not region:
            raise HTTPException(
                status_code=404, detail="region not found"
                )
        return region
    

    @staticmethod
    async def get_list_by_ids(
        regions_id: list[int], 
        session: AsyncSession):
        """
        Takes list of region ids and returns list of respective RegionOrm objects
        """
        regions = await session.execute(
        select(RegionOrm).where(RegionOrm.id.in_(regions_id))
        )
        regions = regions.scalars().all()
        if not regions or len(regions_id) > len(regions):
            raise NotFoundError('Region not found')
        return regions
        
            
    @staticmethod
    async def update_or_404(
        region_id: int,
        data: Region,
        session: AsyncSession
        ):
        region = await session.get(RegionOrm, region_id)
        if not region:
            raise HTTPException(
                status_code=404, detail="region not found"
                )
        region.__dict__.update(data)
        await session.commit()
        return region
    

    @staticmethod
    async def delete_or_404(
        region_id: int,
        session: AsyncSession
        ):
        region = await session.get(RegionOrm, region_id)
        if not region:
            raise HTTPException(
                status_code=404, detail="region not found"
                )
        await session.delete(region)
        await session.commit()
        return region
            
