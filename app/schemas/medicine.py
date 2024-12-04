from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .review import ReviewResponse

class MedicineCreate(BaseModel):
    name: str
    description: str | None = None
    fda_id: str | None = None

class MedicineBase(BaseModel):
    id: int
    name: str
    description: str | None = None
    fda_id: str | None = None

class MedicineResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    fda_id: str | None = None

    model_config = ConfigDict(from_attributes=True)

class SafetyResult(BaseModel):
    can_take: bool
    warning: Optional[str] = None

class MedicineWithReviews(MedicineBase):
    reviews: List[ReviewResponse]

class MedicineSearchResponse(BaseModel):
    medicine: MedicineWithReviews
    safety: SafetyResult

    model_config = ConfigDict(from_attributes=True)