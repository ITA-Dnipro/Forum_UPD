from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Model
from models.profiles import StartupProfileOrm
from sqlalchemy import ForeignKey


class StartupProfileCategoryORM(Model):
    __tablename__ = "starup_profile_category"
    startup_profile_id: Mapped[int] = mapped_column(
        ForeignKey("startup_profiles.id"),
        primary_key=True
    )
    startup_category_id: Mapped[int] = mapped_column(
        ForeignKey("starup_category.id"),
        primary_key=True
    )


class StartupCategoryOrm(Model):
    __tablename__ = "starup_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    starup_category_profiles: Mapped[list["StartupProfileOrm"]] = relationship(
        back_populates="profile_categories", 
        secondary="starup_profile_category"
        )


    def __repr__(self):
        return self.name
    
