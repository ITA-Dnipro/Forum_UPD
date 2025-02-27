from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Model
from models.profiles import ProfileOrm
from sqlalchemy import ForeignKey


class ProfileRegionORM(Model):
    __tablename__ = "profile_region"
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id"),
        primary_key=True
    )
    region_id: Mapped[int] = mapped_column(
        ForeignKey("region.id"),
        primary_key=True
    )


class RegionOrm(Model):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    region_profiles: Mapped[list["ProfileOrm"]] = relationship(
        back_populates="profile_categories",
        secondary="profile_region"
        )


    def __repr__(self):
        return self.name
    
