from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Model
from models.startups import InvestorProfileOrm, StartupProfileOrm
from sqlalchemy import ForeignKey


class StartupProfileCategoryORM(Model):
    __tablename__ = "startup_profile_category"
    startup_profile_id: Mapped[int] = mapped_column(
        ForeignKey("startup_profiles.id"),
        primary_key=True
    )
    startup_category_id: Mapped[int] = mapped_column(
        ForeignKey("startup_category.id"),
        primary_key=True
    )


class StartupCategoryOrm(Model):
    __tablename__ = "startup_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    startup_category_profiles: Mapped[list["StartupProfileOrm"]] = relationship(
        back_populates="profile_categories", 
        secondary="startup_profile_category"
        )
    investor_startup_categories: Mapped[list["InvestorProfileOrm"]] = relationship(
        back_populates="investment_categories", 
        secondary="investor_startup_categories"
        )


    def __repr__(self):
        return self.name


class InvestorStartupCategoryOrm(Model):
    __tablename__ = "investor_startup_categories"
    investor_profile_id = mapped_column(
        ForeignKey("investor_profiles.id"),
        primary_key=True)
    startup_category_id = mapped_column(
        ForeignKey("startup_category.id"),
        primary_key=True
    )