from pydantic import BaseModel, Field


class Region(BaseModel):
  name: str = Field(max_length=50)


class RegionResponse(BaseModel):
  id: int
  name: str

  class Config:
    from_attributes = True