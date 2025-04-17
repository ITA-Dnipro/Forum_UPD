from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
from core.exceptions import NotFoundError
from models.base import Model


class BaseRepository:

    def __init__(self, model: Model, session: AsyncSession):
        self.model = model
        self.session = session

    def _get_query(self):
        return select(self.model)


    async def add_one(self, data: dict):
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance


    async def get_all(self, **filters):
        query = self._get_query()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        instance_list = result.scalars().all()
        return instance_list


    async def get_by_id(self, instance_id: int):
        query = self._get_query().where(self.model.id == instance_id)
        result = await self.session.execute(query)
        profile = result.scalars().first()
        if not profile:
            raise NotFoundError("Object not foud")
        return profile
    

    async def get_list_by_ids(self, instance_ids: list[int]):
        """
        Takes list of object ids and returns list of respective ORM objects
        """
        instances = await self.session.execute(
        self._get_query().where(self.model.id.in_(instance_ids))
        )
        instances = instances.scalars().all()
        if not instances or len(instance_ids) > len(instances):
            raise NotFoundError('Object not found')
        return instances


    async def update(self, instance_id: int, data: dict):
        instance = await self.get_by_id(instance_id)
        for key, value in data.items():
            setattr(instance, key, value)
        await self.session.flush()
        return instance


    async def soft_delete(self, instance_id: int):
        instance = await self.get_by_id(instance_id)
        instance.is_deleted = True
        await self.session.flush()