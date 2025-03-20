from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.orm import selectinload
from exceptions import NotFoundError


class BaseRepository:

    def __init__(self, model, session: AsyncSession):
        self.model = model
        self.session = session
        self.many_to_many = self._get_many_to_many_fields()

    def _get_many_to_many_fields(self):
        many_to_many_fields = []
        for name, relationship in inspect(self.model).relationships.items():
            if relationship.direction.name == "MANYTOMANY":
                many_to_many_fields.append(name)

        return many_to_many_fields
    

    async def add_one(self, data: dict):
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        return instance


    async def get_all(self):
        query = select(self.model)
        for field in self.many_to_many:
            query = query.options(selectinload(getattr(self.model, field)))

        result = await self.session.execute(query)
        instance_list = result.scalars().all()
        return instance_list


    async def get_by_id(self, instance_id: int):
        query = select(self.model).where(self.model.id == instance_id)
        for field in self.many_to_many:
            query = query.options(selectinload(getattr(self.model, field)))
        result = await self.session.execute(query)
        profile = result.scalars().first()
        if not profile:
            raise NotFoundError("Object not foud")
        return profile
    

    async def get_list_by_ids(self, instance_ids: list[int]):
        """
        Takes list of category ids and returns list of respective category objects
        """
        instances = await self.session.execute(
        select(self.model).where(self.model.id.in_(instance_ids))
        )
        categories = categories.scalars().all()
        if not categories or len(instance_ids) > len(instances):
            raise NotFoundError('Object not found')
        return categories


    async def update(self, instance_id: int, data: dict):
        instance = await self.get_by_id(instance_id)
        instance.__dict__.update(data)
        await self.session.commit()
        return instance
    

    async def partial_update(self, instance_id: int, update_fields: dict): 
        instance = await self.get_by_id(instance_id)
        for key, value in update_fields.items():
            setattr(instance, key, value)
        await self.session.commit()
        return instance


