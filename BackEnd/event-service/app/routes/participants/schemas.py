from pydantic import BaseModel, Field
from datetime import datetime

from ..basic_schema import EventsModel

class EventParticipantBaseModel(BaseModel):
    """Base schema. Used for creating or updating a registration."""
    human_slots: int = Field(default=1)
    class Config:
        from_attributes = True
        
class ParticipantsRequestBaseModel(EventParticipantBaseModel):
    """Basic schema with information about registration."""
    id: int
    created_at: datetime
    updated_at: datetime
        
class EventsRelationModel(ParticipantsRequestBaseModel):
    """Schema for retreiving a data about single registration."""
    user_id: int
        
class EventsRegisteredRequestModel(ParticipantsRequestBaseModel):
    """Schema for retreiving an event data for single registration."""
    
    event: "EventsModel"