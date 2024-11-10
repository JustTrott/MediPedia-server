from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
    comment: str = Field(..., min_length=1, description="Review comment text")
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="Sentiment analysis score between -1 and 1")

    @validator('comment')
    def comment_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Comment cannot be empty')
        return v.strip()

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    medicine_id: int
    rating: int
    comment: str
    sentiment_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True