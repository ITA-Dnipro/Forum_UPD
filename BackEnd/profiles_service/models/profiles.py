from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Model
from schemas.profiles import StatusEnum



class ProfileOrm(Model):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    status: Mapped[StatusEnum]
    is_registered: Mapped[bool]
    is_startup: Mapped[bool]
    is_fop: Mapped[bool]
    profile_categories: Mapped[list["CategoryOrm"]] = relationship( # type: ignore
        back_populates="category_profiles", 
        secondary="profile_category"
        )
    profile_regions: Mapped[list["RegionOrm"]] = relationship( # type: ignore
        back_populates="region_profiles", 
        secondary="profile_region"
        )
    