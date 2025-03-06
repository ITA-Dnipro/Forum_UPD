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
    async def get_by_id_or_404(
        category_id: int,
        session: AsyncSession
        ):
        category = await session.get(CategoryOrm, category_id)
        if not category:
            raise HTTPException(
                status_code=404, detail="Category not found"
                )
        return category
    

    @staticmethod
    async def get_by_id_list(
        category_id: list[int],
        session: AsyncSession
        ):
        category = await session.get(CategoryOrm, category_id)
        if not category:
            raise HTTPException(
                status_code=404, detail="Category not found"
                )
        return category
    
            
    @staticmethod
    async def update_or_404(category_id: int,
                            data: Category,
                            session: AsyncSession
                            ):
        category = await session.get(CategoryOrm, category_id)
        if not category:
            raise HTTPException(
                status_code=404, detail="Category not found"
                )
        category.__dict__.update(data)
        await session.commit()
        return category
    
    
    @staticmethod
    async def delete_or_404(
        category_id: int, 
        session: AsyncSession
        ):
        category = await session.get(CategoryOrm, category_id)
        if not category:
            raise HTTPException(
                status_code=404, detail="Category not found"
                )
        await session.delete(category)
        await session.commit()
        return category
            
