from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.schemas.medicine import MedicineResponse

class FavoriteCreate(BaseModel):
    medicine_id: int = Field(..., description="ID of the medicine to favorite")

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    medicine: MedicineResponse
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)