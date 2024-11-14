from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from app.models.medicine import Medicine
from app.models.profile import MedicalData, PersonalProfile
from app.schemas.medicine import MedicineCreate
from app.models.user import User
from app.services.cohere_service import CohereService
from app.services.openfda_service import OpenFDAService
from app.utils import convert_to_string
import json

router = APIRouter()
cohere_service = CohereService()
openfda_service = OpenFDAService()

@router.get("/")
async def get_medicines():
    medicines = list(Medicine.select().dicts())
    return medicines


@router.get("/{medicine_id}")
async def get_medicine(medicine_id: int):
    try:
        medicine = Medicine.get_by_id(medicine_id)
        return medicine.__data__
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Medicine not found")

@router.post("/")
async def create_medicine(medicine_data: MedicineCreate):
    return Medicine.create(
        name=medicine_data.name,
        description=medicine_data.description,
        fda_id=medicine_data.fda_id
    ).__data__

@router.post("/{user_id}/search/{query}")
async def display_list(query: str, user_id: int):
    try:
        print(f"[DEBUG] Starting search for query: {query}, user_id: {user_id}")
        
        # Get user profile and medical data
        try:
            user = User.get_by_id(user_id)
            print(f"[DEBUG] Found user: {user.__data__}")
            
            profile = PersonalProfile.get(PersonalProfile.user == user)
            print(f"[DEBUG] Found profile: {profile.__data__}")
            
            medical_data = MedicalData.get(MedicalData.profile == profile)
            print(f"[DEBUG] Found medical data: {medical_data.__data__}")
            
        except DoesNotExist:
            print("[DEBUG] Failed to find user profile or medical data")
            raise HTTPException(status_code=404, detail="User profile or medical data not found")

        # Extract medicine label using Cohere
        label = cohere_service.extract_label(query)
        print(f"[DEBUG] Extracted label from Cohere: {label}")
        if not label:
            print("[DEBUG] Failed to extract medicine name from Cohere")
            raise HTTPException(status_code=400, detail="Could not extract medicine name")

        # Get medicine data from OpenFDA
        medicine_data = openfda_service.find_medicine_by_label(label)
        print(f"[DEBUG] OpenFDA medicine data: {medicine_data}")
        if not medicine_data:
            print("[DEBUG] Failed to find medicine in FDA database")
            raise HTTPException(status_code=404, detail="Medicine not found in FDA database")

        # Convert profile and medical data to strings
        profile_str = convert_to_string(profile)
        medical_str = convert_to_string(medical_data)
        profile_data = json.dumps({
            "profile": profile_str,
            "medical": medical_str
        })
        print(f"[DEBUG] Converted profile data: {profile_data}")

        # Convert medicine data to string
        medicine_str = json.dumps(medicine_data)
        print(f"[DEBUG] Converted medicine data: {medicine_str}")

        # Check if medicine is safe for user
        safety_result = cohere_service.filter_by_profile(medicine_str, profile_data)
        print(f"[DEBUG] Safety check result: {safety_result}")
        
        return {
            "medicine": medicine_data,
            "safety": safety_result
        }

    except HTTPException as e:
        print(f"[DEBUG] HTTPException occurred: {str(e)}")
        raise e


