from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: date
    time: time
    location: Optional[str] = None
    capacity: int
    available_slots: int
    category: str
    type: str
    image: Optional[str] = None
    active: Optional[bool] = False
    summary: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    location: Optional[str]
    date: Optional[str]
    time: Optional[str]
    capacity: Optional[int]

    class Config:
        from_attributes = True