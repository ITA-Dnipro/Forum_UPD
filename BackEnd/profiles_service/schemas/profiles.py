from datetime import datetime
from typing import Annotated, Optional, Union
from pydantic import BaseModel, conlist, constr, field_validator, model_validator
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
  name: constr(max_length=45)
  status: StatusEnum
  is_registered: bool = False
  is_startup: bool = False
  is_fop: bool = False
  phone: Optional[MyNumberType]
  edrpou: Optional[str] = None
  rnokpp: Optional[str] = None
  startup_idea: Optional[str] = None
  founded: Optional[int] = None
  profile_categories: conlist(int, min_length=1)
  profile_regions: conlist(int, min_length=1)


  @field_validator('edrpou', mode='after')
  @classmethod
  def validate_edrpou(cls, value: str):
    if value is None:
      return value
    if not value.isdigit() or len(value) != 8:
      raise ValueError("EDRPOU must be exactly 8 digits.")
  

  @field_validator('rnokpp', mode='after')
  @classmethod
  def validate_rnokpp(cls, value: str):
    if value is None:
      return value
    if not value.isdigit() or len(value) != 10:
      raise ValueError("RNOKPP must be exactly 10 digits.")
  

  @field_validator("founded", mode="after")
  @classmethod
  def validate_founded(cls, value: str):
      if value is None:
          return value
      if not value.isdigit() or len(value) != 4:
          raise ValueError("Foundation year must be a 4-digit number.")
      
      year = int(value)
      current_year = datetime.now().year
      if year < 1800 or year > current_year:
          raise ValueError(f"Foundation year must be between 1800 and {current_year}.")
    

  @model_validator(mode='after')
  def validate_fop_and_identifiers(self):
    if self.is_fop and self.edrpou is not None:
      raise ValueError("For the EDRPOU field filled out, FOP must be set to False")
    if self.rnokpp and not self.is_fop:
      raise ValueError("For the RNOKPP field filled out, FOP must be set to True")


class ProfileOptional(Profile):
  name: Optional[str] = None
  status: Optional[StatusEnum] = None
  profile_categories: Optional[conlist(int, min_length=1)] = None
  profile_regions: Optional[conlist(int, min_length=1)] = None