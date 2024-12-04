from fastapi import APIRouter, HTTPException
from typing import List
from app.models.user import User
from app.models.medicine import Medicine
from app.models.favorites import Favorite
from app.schemas.favorites import FavoriteCreate, FavoriteResponse
from app.schemas.medicine import MedicineResponse

router = APIRouter(
    tags=["favorites"]
)

@router.post("/users/{user_id}/favorites", response_model=FavoriteResponse)
async def add_favorite(
    user_id: int,
    favorite_data: FavoriteCreate
):
    # Retrieve the user using user_id
    user = User.get_or_none(User.id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if medicine exists
    medicine = Medicine.get_or_none(Medicine.id == favorite_data.medicine_id)
    if medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # Check if favorite already exists
    exists = Favorite.select().where(
        (Favorite.user == user) & (Favorite.medicine == medicine)
    ).exists()
    if exists:
        raise HTTPException(status_code=400, detail="Medicine already in favorites")

    # Create favorite
    favorite = Favorite.create(user=user, medicine=medicine)
    return FavoriteResponse.model_validate({
        'id': favorite.id,
        'user_id': favorite.user.id,
        'medicine': MedicineResponse.model_validate(favorite.medicine),
        'added_at': favorite.added_at
    })

@router.get("/users/{user_id}/favorites", response_model=List[FavoriteResponse])
async def get_user_favorites(user_id: int):
    # Retrieve the user
    user = User.get_or_none(User.id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    favorites = Favorite.select().where(Favorite.user == user).join(Medicine)
    return [
        FavoriteResponse.model_validate({
            'id': fav.id,
            'user_id': fav.user.id,
            'medicine': MedicineResponse.model_validate(fav.medicine),
            'added_at': fav.added_at
        })
        for fav in favorites
    ]
@router.delete("/users/{user_id}/favorites/{medicine_id}", response_model=dict)
async def remove_favorite(
    user_id: int,
    medicine_id: int
):
    # Retrieve the user
    user = User.get_or_none(User.id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Remove favorite
    deleted = Favorite.delete().where(
        (Favorite.user == user) & (Favorite.medicine_id == medicine_id)
    ).execute()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")

    return {"detail": "Favorite removed successfully"}