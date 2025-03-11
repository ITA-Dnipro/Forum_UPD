from pydantic import BaseModel, Field


class Region(BaseModel):
  name: str = Field(max_length=50)
