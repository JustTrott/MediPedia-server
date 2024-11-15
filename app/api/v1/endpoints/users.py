from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist, prefetch
from app.models.user import User
from app.models.profile import PersonalProfile, MedicalData
from app.schemas.user import UserCreate, UserResponse, UserDetailResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users():
    users = list(User.select().dicts())
    return users
        
@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(user_id: int):
    try:
        # Get user first
        user = User.get_by_id(user_id)
        
        # Use prefetch to efficiently load related data
        query = prefetch(
            User.select().where(User.id == user_id),
            PersonalProfile.select(),
            MedicalData.select()
        )
        
        user_with_data = list(query)[0]
        
        # Structure the response
        user_data = {
            "id": user_with_data.id,
            "email": user_with_data.email,
            "profile": None,
            "medical_data": None
        }

        # Add profile if exists
        if hasattr(user_with_data, 'profile'):
            profile = user_with_data.profile[0] if user_with_data.profile else None
            if profile:
                user_data["profile"] = {
                    "id": profile.id,
                    "user_id": profile.user_id,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "age": profile.age,
                    "gender": profile.gender,
                    "phone": profile.phone,
                    "address": profile.address,
                    "created_at": profile.created_at,
                    "updated_at": profile.updated_at
                }
                
                # Add medical data if exists
                if hasattr(profile, 'medical_data'):
                    medical = profile.medical_data[0] if profile.medical_data else None
                    if medical:
                        user_data["medical_data"] = {
                            "id": medical.id,
                            "profile_id": medical.profile_id,
                            "allergies": medical.allergies,
                            "conditions": medical.conditions,
                            "preferred_medication_type": medical.preferred_medication_type,
                            "created_at": medical.created_at,
                            "updated_at": medical.updated_at
                        }

        return user_data
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    try:
        user = User.get(User.email == email)
        return user.__data__
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    try:
        if User.select().where(User.email == user_data.email).exists():
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User.create(email=user_data.email)
        return user.__data__
    except HTTPException as e:
        raise e