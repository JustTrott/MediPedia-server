from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from app.models.review import Review

router = APIRouter()

@router.get("/")
async def get_reviews():
    try:
        reviews = list(Review.select().dicts())
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{review_id}")
async def get_review(review_id: int):
    try:
        review = Review.get_by_id(review_id)
        return review.__data__
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Review not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medicine/{medicine_id}")
async def get_reviews_by_medicine(medicine_id: int):
    try:
        reviews = list(Review.select().where(Review.medicine_id == medicine_id).dicts())
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_reviews_by_user(user_id: int):
    try:
        reviews = list(Review.select().where(Review.user_id == user_id).dicts())
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 