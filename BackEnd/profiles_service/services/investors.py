from utils.uow import UOW
from models.startups import StatusEnum
from schemas.profiles import Investor, InvestorOptional
from repositories.base import BaseRepository
from repositories.profiles import ProfileRepository



class InvestorsService:

    def __init__(self, uow: UOW, repo: ProfileRepository):
        self.uow=uow
        self.repository = repo


    async def investors_list(self):
        return await self.repository.get_all()

    async def get_investor_by_id(self, investor_id):
        return await self.repository.get_by_id(investor_id)
    

    async def add_investor(self, data: Investor):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        profile_dict["status"] = StatusEnum.UNDEFINED
        async with self.uow as uow:
            return await self.repository.add_one(profile_dict=profile_dict)
    

    async def investor_update(self, profile_id: int, data: InvestorOptional):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        async with self.uow as uow:
            return  await self.repository.update(instance_id=profile_id, data=profile_dict)
        


    async def investor_delete(self, profile_id: int):
        async with self.uow as uow:
            return await self.repository.soft_delete(profile_id)


