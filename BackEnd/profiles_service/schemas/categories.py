from pydantic import BaseModel, Field


class Category(BaseModel):
  name: str = Field(max_length=50)


class CategoryResponse(BaseModel):
  id: int
  name: str

  class Config:
    from_attributes = True