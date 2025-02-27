from pydantic import BaseModel, conlist
from enum import Enum


class StatusEnum(Enum):
  UNDEFINED = "Undefined"
  PENDING = "Pendingoderation"
  BLOCKED = "Blocked"
  APPROVED = "Approved"
  AUTOAPPROVED = "Autopproved"


class Profile(BaseModel):
  name: str
  status: StatusEnum
  is_registered: bool = False
  is_startup: bool = False
  is_fop: bool = False
  profile_categories: conlist(int, min_length=1)
  