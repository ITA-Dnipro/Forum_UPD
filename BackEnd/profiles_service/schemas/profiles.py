from typing import Optional
from pydantic import BaseModel, conlist
from enum import Enum


class StatusEnum(Enum):
  UNDEFINED = "Undefined"
  PENDING = "Pending"
  BLOCKED = "Blocked"
  APPROVED = "Approved"
  AUTOAPPROVED = "Autopproved"

class Profile(BaseModel):
  name: str
  status: StatusEnum
  is_registered: bool = False
  is_startup: bool = False
  is_fop: bool = False
  phone: Optional[str] = None
  edrpou: Optional[str] = None
  rnokpp: Optional[str] = None
  startup_idea: Optional[str] = None
  founded: Optional[int] = None
  startup_idea: Optional[str] = None
  profile_categories: conlist(int, min_length=1)
  profile_regions: conlist(int, min_length=1)
  

class ProfileOptional(Profile):
    name: Optional[str] = None
    status: Optional[StatusEnum] = None
    profile_categories: Optional[conlist(int, min_length=1)] = None
    profile_regions: Optional[conlist(int, min_length=1)] = None