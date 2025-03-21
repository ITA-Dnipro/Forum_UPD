from datetime import datetime
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.orm import selectinload
from exceptions import NotFoundError
from models import Model


class BaseRepository:

    def __init__(self, model: Model, session: AsyncSession):
        self.model = model
        self.session = session
        self.many_to_many = self._get_many_to_many_fields()


    def _get_query(self):
        return select(self.model)


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
        query = self._get_query()
        for field in self.many_to_many:
            query = query.options(selectinload(getattr(self.model, field)))

        result = await self.session.execute(query)
        instance_list = result.scalars().all()
        return instance_list


    async def get_by_id(self, instance_id: int):
        query = self._get_query().where(self.model.id == instance_id)
        for field in self.many_to_many:
            query = query.options(selectinload(getattr(self.model, field)))
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
        instance.__dict__.update(data)
        await self.session.commit()
        return instance
    

    async def partial_update(self, instance_id: int, update_fields: dict): 
        instance = await self.get_by_id(instance_id)
        for key, value in update_fields.items():
            setattr(instance, key, value)
        await self.session.commit()
        return instance



class ProfileRepository(BaseRepository):

    def __init__(self, model, session: AsyncSession):
        self.model = model
        self.session = session
        self.many_to_many = self._get_many_to_many_fields()


    def _get_query(self):
        return select(self.model).where(self.model.is_deleted == False)
    

    async def add_one(self, profile_dict: dict):
        profile_dict["is_deleted"] = False
        return await super().add_one(profile_dict)


    async def update(self, profile_id: int, profile_dict: dict):
        profile_dict["updated_at"] = datetime.now()
        return await super().update(profile_id, profile_dict)


    async def partial_update(self, profile_id: int, update_fields: dict): 
        update_fields["updated_at"] = datetime.now()
        return await super().partial_update(profile_id, update_fields)


    async def soft_delete(self, profile_id: int):
        profile = await self.get_by_id(profile_id)
        profile.is_deleted = True
        await self.session.commit()
