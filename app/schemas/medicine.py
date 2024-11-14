from pydantic import BaseModel

class MedicineCreate(BaseModel):
    name: str
    description: str | None = None
    fda_id: str | None = None

class MedicineResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    fda_id: str | None = None