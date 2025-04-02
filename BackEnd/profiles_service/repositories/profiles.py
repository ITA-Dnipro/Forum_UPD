from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
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
      