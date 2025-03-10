from sqlalchemy import Column, Integer, String, Text, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    organizer_id = Column(Integer, nullable=False) # FK to Profile service
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    location = Column(String(255), nullable=True)
    capacity = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # "online", "offline", "auction"
    summary = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)  
    active = Column(Boolean, default=False)  
    participants = relationship("EventParticipant", back_populates="event")
    
    
class EventParticipant(Base):
    __tablename__ = "event_participants"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, nullable=False)
    slots = Column(Integer, nullable=False, default=1)
    event = relationship("Event", back_populates="participants")