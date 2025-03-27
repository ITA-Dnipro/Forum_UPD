from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.orm import selectinload, joinedload
from core.exceptions import NotFoundError
from models import Model


class BaseRepository:

    def __init__(self, model: Model, session: AsyncSession):
        self.model = model
        self.session = session
        self.many_to_many_fields = []
        self.many_to_one_fields = []

        self._get_relationship_fields()


    def _get_query(self):
        return select(self.model)


    def _get_relationship_fields(self):
        for name, relationship in inspect(self.model).relationships.items():
            if relationship.direction.name == "MANYTOMANY":
                self.many_to_many_fields.append(name)
            elif relationship.direction.name == "MANYTOONE":
                self.many_to_one_fields.append(name)
    

    def _apply_eager_loading(self, query):
        for field in self.many_to_many_fields:
            query = query.options(selectinload(getattr(self.model, field)))
        for field in self.many_to_one_fields:
            query = query.options(joinedload(getattr(self.model, field)))
        return query

    

    async def add_one(self, data: dict):
        try:
            instance = self.model(**data)
            self.session.add(instance)
            await self.session.commit()
            return instance
        except Exception as e:
            await self.session.rollback()
            raise e


    async def get_all(self, **filters):
        query = self._get_query()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
            
        query = self._apply_eager_loading(query=query)

        result = await self.session.execute(query)
        instance_list = result.scalars().all()
        return instance_list


    async def get_by_id(self, instance_id: int):
        query = self._get_query().where(self.model.id == instance_id)
        query = self._apply_eager_loading(query=query)
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
        try:
            instance = await self.get_by_id(instance_id)
            for key, value in data.items():
                setattr(instance, key, value)
            await self.session.commit()
            return instance
        except Exception as e:
            await self.session.rollback()
            raise e
    

    async def partial_update(self, instance_id: int, update_fields: dict):
        try: 
            instance = await self.get_by_id(instance_id)
            for key, value in update_fields.items():
                setattr(instance, key, value)
            await self.session.commit()
            return instance
        except Exception as e:
            await self.session.rollback()
            raise e


    async def soft_delete(self, instance_id: int):
        try: 
            instance = await self.get_by_id(instance_id)
            instance.is_deleted = True
            await self.session.commit()
        except Exception as e:
                await self.session.rollback()
                raise e


class ProfileRepository(BaseRepository):

    def __init__(self, model: Model, session: AsyncSession):
        super().__init__(model, session)


    def _get_query(self):
        return select(self.model).where(self.model.is_deleted == False)
    

    async def add_one(self, profile_dict: dict):
        profile_dict["is_deleted"] = False
        return await super().add_one(profile_dict)


    async def soft_delete(self, profile_id: int):
        try: 
            profile = await self.get_by_id(profile_id)
            profile.is_deleted = True
            await self.session.commit()
        except Exception as e:
                await self.session.rollback()
                raise e
