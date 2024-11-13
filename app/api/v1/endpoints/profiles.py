from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from datetime import datetime
from app.models.profile import PersonalProfile, MedicalData
from app.models.user import User
from app.schemas.profile import (
    PersonalProfileCreate, 
    PersonalProfileResponse,
    MedicalDataCreate,
    MedicalDataResponse
)

router = APIRouter()

@router.post("/{user_id}", response_model=PersonalProfileResponse)
async def create_profile(user_id: int, profile_data: PersonalProfileCreate):
    try:
        # Validate user exists
        try:
            User.get_by_id(user_id)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        # Check for existing profile
        if PersonalProfile.select().where(PersonalProfile.user_id == user_id).exists():
            raise HTTPException(status_code=400, detail="Profile already exists for this user")

        # Create profile
        profile = PersonalProfile.create(
            user_id=user_id,
            **profile_data.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Initialize empty medical data
        MedicalData.create(profile=profile)
        
        return profile
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{profile_id}", response_model=PersonalProfileResponse)
async def update_profile(profile_id: int, profile_data: PersonalProfileCreate):
    # First check if profile exists
    try:
        profile = PersonalProfile.get_by_id(profile_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Update profile
        for field, value in profile_data.model_dump().items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.now()
        profile.save()
        
        return profile
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{profile_id}/medical", response_model=MedicalDataResponse)
async def update_medical_data(profile_id: int, medical_data: MedicalDataCreate):
    # First check if medical data exists
    try:
        data = MedicalData.get(MedicalData.profile_id == profile_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Medical data not found")

    try:
        # Update medical data
        for field, value in medical_data.model_dump().items():
            setattr(data, field, value)
        
        data.updated_at = datetime.now()
        data.save()
        
        return data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


def convert_to_string(instance):
    return " ".join(str(value) for value in instance.__data__.values())
