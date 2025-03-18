from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Model
from schemas.profiles import StatusEnum
from datetime import datetime



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
        secondary="startup_profile_category"
        )
    profile_regions: Mapped[list["RegionOrm"]] = relationship( # type: ignore
        back_populates="region_profiles", 
        secondary="profile_region"
        )
    phone: Mapped[str] = mapped_column(String(15), default=None, nullable=True)
    edrpou: Mapped[str] = mapped_column(String(8), default=None, unique=True, nullable=True)
    rnokpp: Mapped[str] = mapped_column(String(10), default=None, unique=True, nullable=True)
    founded: Mapped[int] = mapped_column(nullable=True)
    startup_idea: Mapped[str] = mapped_column(Text, default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True) 



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
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    investment_categories: Mapped[list["StartupCategoryOrm"]] = relationship( # type: ignore
        back_populates="investor_startup_categories", 
        secondary="investor_startup_categories"
        )