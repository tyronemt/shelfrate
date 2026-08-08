from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    rating_overall:      int = Field(..., ge=1, le=5)
    rating_noise:        Optional[int] = Field(None, ge=1, le=5)
    rating_outlets:      Optional[int] = Field(None, ge=1, le=5)
    rating_seating:      Optional[int] = Field(None, ge=1, le=5)
    rating_staff:        Optional[int] = Field(None, ge=1, le=5)
    crowdedness:         Optional[str] = None
    body:                str = Field(..., min_length=20)


class ReviewRead(ReviewCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    library_id: int
    user_id:    int
    created_at: datetime