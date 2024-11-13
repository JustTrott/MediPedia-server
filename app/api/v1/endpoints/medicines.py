from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from app.api.v1.endpoints.profiles import convert_to_string
from app.models.medicine import Medicine
from app.models.profile import MedicalData, PersonalProfile
from app.schemas.medicine import MedicineCreate
from app.models.user import User
from app.services.openfda_service import extract_label, find_medicine_by_label, filter_by_profile

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
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_medicine(medicine_data: MedicineCreate):
    try:
        medicine = Medicine.create(
            name=medicine_data.name,
            description=medicine_data.description,
            fda_id=medicine_data.fda_id
        )
        return medicine.__data__
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#assuming the user only inputs one medicine at a time
#Input -> get label -> find medicine -> filter by profile -> call openfda -> return result
@router.post("/{user_id}/search/{query}")
async def display_list(query: str, user_id: int):
    try:
        userProfile = PersonalProfile.get_by_id(user_id)

        userMedicalProfile = MedicalData.get_by_id(user_id)

        #creates one giant string

        stringProfileRep = convert_to_string(userProfile)+convert_to_string(userMedicalProfile)

        extractLabel = extract_label(query)

        medicineByLabel = find_medicine_by_label(extractLabel)

        filterResult = filter_by_profile(medicineByLabel, stringProfileRep)

        return filterResult
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Missing Profile Records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


