from typing import Annotated, Optional, Union
from pydantic import BaseModel, conlist, field_validator
from enum import Enum
from pydantic_extra_types.phone_numbers import PhoneNumberValidator, PhoneNumber

MyNumberType = Annotated[
  Union[str, PhoneNumber],
  PhoneNumberValidator(
    default_region="UA",
    number_format="E164"
  )
]

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
  phone: Optional[MyNumberType]
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