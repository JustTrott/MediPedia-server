from fastapi import APIRouter, HTTPException
from app.models.medicine import Medicine

router = APIRouter()

@router.get("/")
async def get_medicines():
    try:
        medicines = list(Medicine.select().dicts())
        return medicines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{medicine_id}")
async def get_medicine(medicine_id: int):
    try:
        medicine = Medicine.get_by_id(medicine_id)
        return medicine.__data__
    except Medicine.DoesNotExist:
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 