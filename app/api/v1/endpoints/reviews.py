from datetime import datetime
from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.models.user import User
from app.models.medicine import Medicine

router = APIRouter()

@router.get("/")
async def get_reviews():
    reviews = list(Review.select().dicts())
    return reviews

@router.get("/{review_id}")
async def get_review(review_id: int):
    try:
        review = Review.get_by_id(review_id)
        return review.__data__
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Review not found")

@router.get("/medicine/{medicine_id}")
async def get_reviews_by_medicine(medicine_id: int):
    if not Medicine.select().where(Medicine.id == medicine_id).exists():
        raise HTTPException(status_code=404, detail="Medicine not found")
    reviews = list(Review.select().where(Review.medicine == medicine_id).dicts())
    return reviews

@router.get("/user/{user_id}")
async def get_reviews_by_user(user_id: int):
    if not User.select().where(User.id == user_id).exists():
        raise HTTPException(status_code=404, detail="User not found")
    reviews = list(Review.select().where(Review.user == user_id).dicts())
    return reviews

@router.post("/", response_model=ReviewResponse)
async def create_review(user_id: int, medicine_id: int, review_data: ReviewCreate):
    try:
        user = User.get_by_id(user_id)
        medicine = Medicine.get_by_id(medicine_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User or Medicine not found")

    if Review.select().where(
        (Review.user == user_id) & 
        (Review.medicine == medicine_id)
    ).exists():
        raise HTTPException(
            status_code=400,
            detail="User has already reviewed this medicine"
        )

    return Review.create(
        user=user,
        medicine=medicine,
        rating=review_data.rating,
        comment=review_data.comment,
        sentiment_score=review_data.sentiment_score,
    ).__data__