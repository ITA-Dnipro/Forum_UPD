from exceptions import UniqueConstraintViolationError
from utils.repositories import BaseRepository
from schemas.categories import Category

class CategoryService:

    def __init__(self, repo: BaseRepository):
        self.repository = repo


    async def add_one(self, data: Category):
        category_dict = data.model_dump()
        category_name = category_dict["name"]
        if self.repository.get_all(name=category_name):
            raise UniqueConstraintViolationError
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


    async def update(self, category_id: int, data: Category):
        category_dict = data.model_dump()
        category_name = category_dict["name"]
        if self.repository.get_all(name=category_name):
            raise UniqueConstraintViolationError
        category = await self.repository.update(category_id, category_dict)
        return category
    

            