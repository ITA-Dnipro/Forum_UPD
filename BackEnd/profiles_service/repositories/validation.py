import uuid
from sqlalchemy.ext.asyncio import AsyncSession 
from models.base import Model
from repositories.base import BaseRepository

class ValidationRepository(BaseRepository):

    def __init__(self, model: Model, session: AsyncSession):
        super().__init__(model, session)


    async def add_one(self, data: dict):
        
        validation_data = {
            "profile_id": data["profile_id"],
            "last_validation_request_uuid": str(uuid.uuid4())
        }
        return await super().add_one(validation_data)
    

    async def update(self, validation_id, data: dict):
        
        validation_data = {
            "profile_id": data["profile_id"],
            "last_validation_request_uuid": str(uuid.uuid4())
        }
        return await super().update(validation_id, validation_data)