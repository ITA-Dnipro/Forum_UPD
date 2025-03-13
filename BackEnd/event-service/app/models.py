from sqlalchemy import String, Text, Date, Time
from sqlalchemy.orm import  Mapped, mapped_column
from database import Base, str_100, intpk
from enums import StatusEnum, TypeEnum
from datetime import datetime


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