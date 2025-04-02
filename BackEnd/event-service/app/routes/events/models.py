from sqlalchemy import String, Text, Date, Time, DateTime, func
from sqlalchemy.orm import  Mapped, mapped_column, relationship, validates
from database import Base, str_100, intpk
from enums import StatusEnum, TypeEnum
from datetime import datetime
from ..participants import models
from typing import List

class Event(Base):
    __tablename__ = "events"
    
    id: Mapped[intpk]
    title: Mapped[str_100]
    description: Mapped[str | None]
    organizer_id: Mapped[int]
    date: Mapped[datetime.date] = mapped_column(Date)
    starting_time: Mapped[datetime.time] = mapped_column(Time)
    location: Mapped[str]
    capacity: Mapped[int | None]
    available_slots: Mapped[int]
    type: Mapped[TypeEnum]
    summary: Mapped[str | None] = mapped_column(Text)
    image: Mapped[str | None] = mapped_column(String)
    status: Mapped[StatusEnum]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
   
    participants: Mapped[List["models.EventParticipant"]] = relationship(
        back_populates="event",
        lazy="joined"
    )
    
    @validates('available_slots')
    def validate_available_slots(self, key, value):
        if value is None:
            value = self.capacity
        return value