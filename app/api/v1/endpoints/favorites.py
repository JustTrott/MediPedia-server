from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.database import get_db
from app.models.favorites import Favorite
from app.schemas.favorites import FavoriteCreate, FavoriteResponse

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.post("/", response_model=FavoriteResponse)
def create_favorite(favorite: FavoriteCreate, db=Depends(get_db)):
    """
    Create a new favorite for a user
    """
    try:
        new_favorite = Favorite.create(
            user_id=favorite.user_id, 
            medicine_id=favorite.medicine_id
        )
        return new_favorite
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[FavoriteResponse])
def get_user_favorites(user_id: int, db=Depends(get_db)):
    """
    Retrieve all favorites for a specific user
    """
    favorites = Favorite.select().where(Favorite.user_id == user_id)
    return list(favorites)

@router.delete("/{favorite_id}", response_model=dict)
def delete_favorite(favorite_id: int, db=Depends(get_db)):
    """
    Delete a specific favorite by its ID
    """
    try:
        deleted_count = Favorite.delete().where(Favorite.id == favorite_id).execute()
        if not deleted_count:
            raise HTTPException(status_code=404, detail="Favorite not found")
        return {"message": "Favorite deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))