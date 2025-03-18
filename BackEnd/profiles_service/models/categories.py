from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Model
from models.profiles import StartupProfileOrm
from sqlalchemy import ForeignKey


class ProfileCategoryORM(Model):
    __tablename__ = "profile_category"
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("startup_profiles.id"),
        primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id"),
        primary_key=True
    )


class CategoryOrm(Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    category_profiles: Mapped[list["StartupProfileOrm"]] = relationship(
        back_populates="profile_categories", 
        secondary="profile_category"
        )


    def __repr__(self):
        return self.name
    
