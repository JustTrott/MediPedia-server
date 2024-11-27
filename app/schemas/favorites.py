from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class FavoriteBase(BaseModel):
    user_id: int
    medicine_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    time: datetime