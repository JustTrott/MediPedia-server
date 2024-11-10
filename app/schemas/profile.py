from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re

class PersonalProfileBase(BaseModel):
    first_name: str
    last_name: str
    age: int
    gender: str
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        if not 0 <= v <= 120:
            raise ValueError("Age must be between 0 and 120")
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r'^\+?1?\d{9,15}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid phone number format")
        return v

class PersonalProfileCreate(PersonalProfileBase):
    pass

class PersonalProfileResponse(PersonalProfileBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class MedicalDataBase(BaseModel):
    allergies: Optional[str] = None
    conditions: Optional[str] = None
    preferred_medication_type: Optional[str] = None

class MedicalDataCreate(MedicalDataBase):
    pass

class MedicalDataResponse(MedicalDataBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    profile_id: int
    created_at: datetime
    updated_at: datetime