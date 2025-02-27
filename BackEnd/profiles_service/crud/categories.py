from sqlalchemy import select
from database import new_session
from models.categories import CategoryOrm
from schemas.categories import Category
from fastapi import HTTPException

class CategoryRepository:
    @staticmethod
    async def add_one(data: Category):
        async with new_session() as session:
            category_dict = data.model_dump()
            category = CategoryOrm(**category_dict)
            session.add(category)
            await session.flush()
            await session.commit()
            return category.id


    @staticmethod
    async def get_all():
        async with new_session() as session:
            query = select(CategoryOrm)
            result = await session.execute(query)
            category_models = result.scalars().all()
            return category_models


    @staticmethod
    async def get_by_id_or_404(category_id: int):
        async with new_session() as session:
            category = await session.get(CategoryOrm, category_id)
            if not category:
                raise HTTPException(
                    status_code=404, detail="Category not found"
                    )
            return category
    
    @staticmethod
    async def get_by_id_list(category_id: list[int]):
        async with new_session() as session:
            category = await session.get(CategoryOrm, category_id)
            if not category:
                raise HTTPException(
                    status_code=404, detail="Category not found"
                    )
            return category
        
            
    @staticmethod
    async def update_or_404(category_id: int, data: Category):
        async with new_session() as session:
            category = await session.get(CategoryOrm, category_id)
            if not category:
                raise HTTPException(
                    status_code=404, detail="Category not found"
                    )
            category.__dict__.update(data)
            await session.flush()
            await session.commit()
            return category
    
    @staticmethod
    async def delete_or_404(category_id: int):
        async with new_session() as session:
            category = await session.get(CategoryOrm, category_id)
            if not category:
                raise HTTPException(
                    status_code=404, detail="Category not found"
                    )
            await session.delete(category)
            await session.commit()
            return category
            
