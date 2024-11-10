from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_users():
    try:
        users = list(User.select().dicts())
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user(user_id: int):
    try:
        user = User.get_by_id(user_id)
        return user.__data__
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 