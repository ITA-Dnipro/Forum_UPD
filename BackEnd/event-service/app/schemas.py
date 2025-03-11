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
    summary: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    capacity: Optional[int] = None

    class Config:
        orm_mode = True