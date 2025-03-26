from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base, intpk
from ..events import models
from datetime import datetime

class EventParticipant(Base):
    __tablename__ = "event_participants"

    id: Mapped[intpk]
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    user_id: Mapped[int]
    human_slots: Mapped[int] = mapped_column(default=1)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    event: Mapped["models.Event"] = relationship(
        back_populates="participants",
        lazy="joined"
    )