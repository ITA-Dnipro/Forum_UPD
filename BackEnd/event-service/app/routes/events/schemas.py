from pydantic import BaseModel
from typing import Optional
from datetime import date as dt, time
from ..basic_schema import EventsModel
from ..participants.schemas import EventsRelationModel

class EventUpdateModel(BaseModel):
    """Schema for updating an event."""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[dt] = None
    starting_time: Optional[time] = None
    capacity: Optional[int] = None

    class Config:
        from_attributes = True
        
class EventParticipantsModel(EventsModel):
    """Schema for retrieving an event with all registrations."""
    participants: list["EventsRelationModel"] = []