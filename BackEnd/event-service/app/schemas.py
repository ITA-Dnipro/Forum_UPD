from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from enums import TypeEnum

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: date
    starting_time: time
    location: Optional[str] = None
    capacity: int
    available_slots: int
    type: TypeEnum
    image: Optional[str] = None
    summary: Optional[str] = None
    
    class Config:
        use_enum_values = True

class EventUpdate(BaseModel):
    title: str
    description: str
    location: str
    date: date
    starting_time: time
    capacity: int

    class Config:
        orm_mode = True