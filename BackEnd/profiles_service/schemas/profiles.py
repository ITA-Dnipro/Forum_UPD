from datetime import datetime
from typing import Annotated, Optional, Union
from pydantic import BaseModel, conlist, constr, field_validator, model_validator
from enum import Enum
from models.profiles import StatusEnum
from pydantic_extra_types.phone_numbers import PhoneNumberValidator, PhoneNumber
from schemas.categories import CategoryResponse
from schemas.regions import RegionResponse
from utils.create_optional_model import create_optional_model


MyNumberType = Annotated[
  Union[str, PhoneNumber],
  PhoneNumberValidator(
    default_region="UA",
    number_format="E164"
  )
]


class Profile(BaseModel):
  name: constr(max_length=45)
  phone: Optional[MyNumberType] = None
  edrpou: Optional[str] = None
  rnokpp: Optional[str] = None
  

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


class Startup(Profile):
  is_registered: bool = False
  is_startup: bool = False
  is_fop: bool = False
  startup_idea: Optional[str] = None
  founded: Optional[int] = None
  profile_categories: Optional[conlist(int, min_length=1)] = None
  profile_regions: Optional[conlist(int, min_length=1)] = None
  banner_id: Optional[int] = None


  @field_validator("founded", mode="after")
  @classmethod
  def validate_founded(cls, value: int):
    if value is None:
        return value
    current_year = datetime.now().year
    if value < 1800 or value > current_year:
        raise ValueError(f"Foundation year must be between 1800 and {current_year}.")
    

  @model_validator(mode='after')
  def validate_fop_and_identifiers(self):
    if self.is_fop and self.edrpou is not None:
      raise ValueError("For the EDRPOU field filled out, FOP must be set to False")
    if self.rnokpp and not self.is_fop:
      raise ValueError("For the RNOKPP field filled out, FOP must be set to True")


class Investor(Profile):
  is_legal_entity: bool = False
  available_funds: Optional[float] = None
  investment_categories: Optional[conlist(int, min_length=1)] = None

  @model_validator(mode='after')
  def validate_fop_and_identifiers(self):
    if self.is_legal_entity and self.edrpou is not None:
      raise ValueError("For the EDRPOU field filled out, is_legal_entity  must be set to False")
    if self.rnokpp and not self.is_legal_entity:
      raise ValueError("For the RNOKPP field filled out, is_legal_entity must be set to True")


InvestorOptional = create_optional_model(Investor)
StartupOptional = create_optional_model(Startup)

class ProfileModerationEnum(Enum):
  APPROVED = "Approved"
  REJECTED = "Rejected"

class ModerationFeedback(BaseModel):
  moderation_status: ProfileModerationEnum


class ProfileImageResponse(BaseModel):
  id: int
  is_approved: bool
  created_at: datetime
  approved_image_path: str
  class Config:
      orm_mode = True 



class StartupResponse(BaseModel):
  id: int
  name: str
  status: StatusEnum
  phone: Optional[MyNumberType]
  edrpou: Optional[str]
  rnokpp: Optional[str]
  is_registered: bool
  is_startup: bool
  is_fop: bool
  startup_idea: Optional[str]
  founded: Optional[int]
  banner_id: Optional[int]

  profile_categories: Optional[list[CategoryResponse]]
  profile_regions: Optional[list[RegionResponse]]
  banner: Optional[ProfileImageResponse]

  class Config:
      from_attributes = True


class InvestorResponse(BaseModel):
  id: int
  name: str
  status: StatusEnum
  phone: Optional[MyNumberType]
  edrpou: Optional[str]
  rnokpp: Optional[str]
  is_legal_entity: bool
  available_funds: Optional[float]
  investment_categories: Optional[conlist(int, min_length=1)]

  class Config:
      from_attributes = True
