from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
    comment: str = Field(..., min_length=1, description="Review comment text")
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="Sentiment analysis score between -1 and 1")

    @field_validator('comment')
    def comment_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Comment cannot be empty')
        return v.strip()

class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: int
    medicine: int
    rating: int
    comment: str
    sentiment_score: Optional[float]
    created_at: datetime