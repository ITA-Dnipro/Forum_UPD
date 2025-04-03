from enum import Enum
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Model
from datetime import datetime


class StatusEnum(Enum):
  UNDEFINED = "Undefined"
  PENDING = "Pending"
  BLOCKED = "Blocked"
  APPROVED = "Approved"
  AUTOAPPROVED = "Autopproved"

class StartupProfileOrm(Model):
    __tablename__ = "startup_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    status: Mapped[StatusEnum]
    is_registered: Mapped[bool]
    is_startup: Mapped[bool]
    is_fop: Mapped[bool]
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default="FALSE", nullable=False)
    profile_categories: Mapped[list["StartupCategoryOrm"]] = relationship( # type: ignore
        back_populates="startup_category_profiles", 
        secondary="startup_profile_category",
        lazy="selectin"
        )
    profile_regions: Mapped[list["RegionOrm"]] = relationship( # type: ignore
        back_populates="region_profiles", 
        secondary="profile_region",
        lazy="selectin"
        )
    phone: Mapped[str] = mapped_column(String(15), default=None, nullable=True)
    edrpou: Mapped[str] = mapped_column(String(8), default=None, nullable=True)
    rnokpp: Mapped[str] = mapped_column(String(10), default=None, nullable=True)
    founded: Mapped[int] = mapped_column(nullable=True)
    startup_idea: Mapped[str] = mapped_column(Text, default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now())

    banner_id: Mapped[int] = mapped_column(
    ForeignKey("profile_images.id"), 
    nullable=True)

    banner: Mapped["ProfileImage"] = relationship( # type: ignore
        back_populates="profile_banner", 
        foreign_keys=[banner_id],
        uselist=False)
    
    validations: Mapped["ProfileValidationOrm"] = relationship( # type: ignore
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        lazy='joined'
    )

    def __repr__(self):
        attrs = ", ".join(f"{key}={value!r}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}({attrs})"

class InvestorProfileOrm(Model):
    __tablename__ = "investor_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    status: Mapped[StatusEnum]
    is_legal_entity: Mapped[bool]
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default="FALSE", nullable=False)
    phone: Mapped[str] = mapped_column(String(15), default=None, nullable=True)
    edrpou: Mapped[str] = mapped_column(String(8), default=None, unique=True, nullable=True)
    rnokpp: Mapped[str] = mapped_column(String(10), default=None, unique=True, nullable=True)
    available_funds: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now())
    investment_categories: Mapped[list["StartupCategoryOrm"]] = relationship( # type: ignore
        back_populates="investor_startup_categories", 
        secondary="investor_startup_categories",
        lazy="selectin"
        )