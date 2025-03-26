from pydantic import BaseModel, Field


class Category(BaseModel):
  name: str = Field(max_length=50)
