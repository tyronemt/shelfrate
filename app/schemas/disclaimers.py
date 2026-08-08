from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DisclaimerCreate(BaseModel):
    category:   str = Field(..., max_length=50)
    title:      str = Field(..., max_length=200)
    body:       str
    source_url: Optional[str] = None


class DisclaimerRead(DisclaimerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    upvotes: int
    created_at: datetime