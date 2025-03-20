from repositories import BaseRepository
from schemas.categories import Category
from sqlalchemy.ext.asyncio import AsyncSession 

class CategoryService:

    def __init__(self, model, session: AsyncSession):
        self.session = session
        self.repository = BaseRepository(model, session)


    async def add_one(self, data: Category):
        category_dict = data.model_dump()
        category = await self.repository.add_one(category_dict)
        return category


    async def get_all(self):
        categories = await self.repository.get_all()
        return categories


    async def get_list_by_ids(self, categories_id: list[int]):
        """
        Takes list of category ids and returns list of respective category objects
        """
        categories = await self.repository.get_list_by_ids(categories_id)
        return categories


    async def get_by_id(self, category_id: int):
        category = await self.repository.get_by_id(category_id)
        return category
    
            
    async def update(self, category_id: int, data: Category, ):
        category_dict = data.model_dump()
        category = await self.repository.update(category_id, category_dict)
        return category
    

            