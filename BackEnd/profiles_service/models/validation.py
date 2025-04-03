from enum import Enum
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Model
from datetime import datetime
from models.startups import StartupProfileOrm


class ProfileValidationOrm(Model):
    __tablename__ = "profile_validations" 


    id: Mapped[int] = mapped_column(primary_key=True)    
    rnokkpp_valid: Mapped[bool] = mapped_column(default=False, nullable=False)
    edrpou_valid: Mapped[bool] = mapped_column(default=False,nullable=False)
    last_validation_request_uuid: Mapped[str] = mapped_column(
        String(36),
        nullable=True,
        default=None
    )
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("startup_profiles.id")
    )
    profile: Mapped["StartupProfileOrm"] = relationship(
        back_populates="validations",
        uselist=False
        )

    