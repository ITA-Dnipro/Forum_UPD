from sqlalchemy import select
from models.categories import CategoryOrm
from schemas.categories import Category
from fastapi import HTTPException
from crud import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession 

class CategoryRepository:
    @staticmethod
    async def add_one(
        data: Category,
        session: AsyncSession
        ):
        category_dict = data.model_dump()
        category = CategoryOrm(**category_dict)
        session.add(category)
        await session.commit()
        return category.id


    @staticmethod
    async def get_all(session: AsyncSession):
        query = select(CategoryOrm)
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
        select(CategoryOrm).where(CategoryOrm.id.in_(categories_id))
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
        category = await session.get(CategoryOrm, category_id)
        if not category:
            raise NotFoundError('Region not found')
        return category
    
            
    @classmethod
    async def update(
        cls,
        category_id: int,
        data: Category,
        session: AsyncSession
        ):
        category = cls.get_by_id(category_id, session=session)
        category.__dict__.update(data)
        await session.commit()
        return category
    
    
    @classmethod
    async def delete(
        cls,
        category_id: int, 
        session: AsyncSession
        ):
        category = cls.get_by_id(category_id, session=session)
        category = await session.get(CategoryOrm, category_id)
        await session.delete(category)
        await session.commit()
        return category
            