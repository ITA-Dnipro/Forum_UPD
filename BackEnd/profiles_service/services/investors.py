from models.categories import StartupCategoryOrm
from models.profiles import StatusEnum
from schemas.profiles import Investor, InvestorOptional
from exceptions import InvalidRelatedEntityError, NotFoundError
from utils.repositories import ProfileRepository, BaseRepository



class InvestorsService:

    def __init__(self, repo: ProfileRepository):
        self.repository = repo


    async def _fetch_related_by_id(self, data: dict):
        if data.get("investment_categories") is not None:
            category_repo = BaseRepository(model=StartupCategoryOrm, session=self.repository.session)
            try:
                data["investment_categories"] = await category_repo.get_list_by_ids(data["investment_categories"])
            except NotFoundError: 
                raise InvalidRelatedEntityError("One or more categories does not exist")
        
        return data

    async def investors_list(self):
        return await self.repository.get_all()

    async def get_investor_by_id(self, investor_id):
        return await self.repository.get_by_id(investor_id)
    

    async def add_investor(self, data: Investor):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        profile_dict["status"] = StatusEnum.UNDEFINED
        profile_dict = await self._fetch_related_by_id(profile_dict)
        return await self.repository.add_one(profile_dict=profile_dict)
    

    async def partial_investor_update(self, profile_id: int, data: InvestorOptional):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        profile_dict = await self._fetch_related_by_id(data=profile_dict)
        return await self.repository.partial_update(instance_id=profile_id, update_fields=profile_dict)


    async def investor_update(self, profile_id: int, data: Investor):
        profile_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        self._fetch_related_by_id(profile_dict)
        
        return await self.repository.update(instance_id=profile_id, profile_dict=profile_dict)


    async def investor_delete(self, profile_id: int):
        await self.repository.soft_delete(profile_id)

