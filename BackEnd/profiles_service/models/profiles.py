from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
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
    profile_categories: Mapped[list["CategoryOrm"]] = relationship(back_populates="category_profiles" ,secondary="profile_category")