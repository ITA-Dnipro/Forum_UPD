from sqlalchemy import select
from models.categories import StartupCategoryOrm
from schemas.categories import Category
from exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession 

class CategoryRepository:
    @staticmethod
    async def add_one(
        data: Category,
        session: AsyncSession
        ):
        category_dict = data.model_dump()
        category = StartupCategoryOrm(**category_dict)
        session.add(category)
        await session.commit()
        return category


    @staticmethod
    async def get_all(session: AsyncSession):
        query = select(StartupCategoryOrm)
        result = await session.execute(query)
        category_models = result.scalars().all()
        return category_models


    @staticmethod
    async def get_list_by_ids(
        categories_id: list[int], 
        session: AsyncSession
        ):
        """
        Takes list of category ids and returns list of respective category objects
        """
        categories = await session.execute(
        select(StartupCategoryOrm).where(StartupCategoryOrm.id.in_(categories_id))
        )
        categories = categories.scalars().all()
        if not categories or len(categories_id) > len(categories):
            raise NotFoundError('Category not found')
        return categories


    @staticmethod
    async def get_by_id(
        category_id: int,
        session: AsyncSession
        ):
        category = await session.get(StartupCategoryOrm, category_id)
        if not category:
            raise NotFoundError('Category not found')
        return category
    
            
    @classmethod
    async def update(
        cls,
        category_id: int,
        data: Category,
        session: AsyncSession
        ):
        category = await cls.get_by_id(category_id, session=session)
        category_dict = data.model_dump()
        for key, value in category_dict.items():
            setattr(category, key, value)
        await session.commit()
        return category
    

            