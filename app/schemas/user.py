from pydantic import BaseModel, field_validator, ConfigDict
import re
from typing import Optional
from .profile import PersonalProfileResponse, MedicalDataResponse

class UserCreate(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v
class UserBase(BaseModel):
    id: int
    email: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

class UserDetailResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    profile: Optional[PersonalProfileResponse] = None
    medical_data: Optional[MedicalDataResponse] = None