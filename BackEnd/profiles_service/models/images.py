from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Model
from sqlalchemy.orm import Mapped

class ImageTypeEnum(Enum):
    BANNER = "Banner"
    LOGO = "Logo"




class ProfileImage(Model):
    __tablename__ = "profile_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    # image_type: Mapped[ImageTypeEnum]
    image_path: Mapped[str] = mapped_column(String(255))
    is_approved: Mapped[bool] = mapped_column(default=False, nullable=False) 
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    profile_banner = relationship("StartupProfileOrm", back_populates="banner")
