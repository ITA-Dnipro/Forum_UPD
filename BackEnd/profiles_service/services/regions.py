from utils.uow import UOW
from repositories.base import BaseRepository
from schemas.regions import Region
from core.exceptions import UniqueConstraintViolationError

class RegionService:

    def __init__(self, uow: UOW, repo: BaseRepository):
        self.repository = repo
        self.uow = uow


    async def add_one(self, data: Region):
        region_dict = data.model_dump()
        region_name = region_dict["name"]
        if await self.repository.get_all(name=region_name):
            raise UniqueConstraintViolationError
        async with self.uow as uow:
            return await self.repository.add_one(region_dict)
         


    async def get_all(self):
        return await self.repository.get_all()


    async def get_list_by_ids(self, regions_id: list[int]):
        """
        Takes list of region ids and returns list of respective region objects
        """
        return await self.repository.get_list_by_ids(regions_id)


    async def get_by_id(self, region_id: int):
        region = await self.repository.get_by_id(region_id)
        return region
    
            
    async def update(self, region_id: int, data: Region):
        region_dict = data.model_dump()
        region_name = region_dict["name"]
        if await self.repository.get_all(name=region_name):
            raise UniqueConstraintViolationError
        async with self.uow as uow:
            return await self.repository.update(region_id, region_dict)
  

            