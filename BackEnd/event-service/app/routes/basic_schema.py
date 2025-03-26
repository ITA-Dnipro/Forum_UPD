"""File for overcoming circular imports in different schemas. Basic Event schema can be imported from here."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date as dt, time, datetime
from enums import TypeEnum, StatusEnum

class EventCreateModel(BaseModel):
    """Schema for creating an event."""
    title: str
    description: Optional[str] = None
    date: dt
    starting_time: time
    location: Optional[str] = None
    capacity: int
    available_slots: Optional[int] = None
    type: TypeEnum = Field(
        description=f"Type of event. Possible values: {", ".join([type.value for type in TypeEnum])}")
    image: Optional[str] = None
    summary: Optional[str] = None
    
    @field_validator("capacity", mode="before")
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError("Capacity must be positive")
        return v
    
    @field_validator("available_slots", mode="before")
    def validate_available_slots(cls, v, info):
        capacity = info.data.get("capacity")
        if v is None:
            return capacity
        elif capacity is not None and v > capacity:
            raise ValueError("Available slots cannot be greater than capacity")
        return v
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "title": "Green Project startups demonstration.",
                "description": "Find an interested project to invest while helping our nature.",
                "date": "2025-04-10",
                "starting_time": "12:30",
                "location": "Zoom link",
                "capacity": 50,
                "type": TypeEnum.online.value
            }
        }

class EventsModel(EventCreateModel):
    """Basic schema for events. Used for GET responses."""
    id: int
    organizer_id: int
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        use_enum_values = True