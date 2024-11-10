from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.get("/")
async def get_users():
    try:
        users = list(User.select().dicts())
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    try:
        user = User.get_by_id(user_id)
        return user
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    try:
        if User.select().where(User.email == user_data.email).exists():
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User.create(email=user_data.email)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 