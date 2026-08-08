from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SpeedTestCreate(BaseModel):
    download_mbps: float = Field(..., ge=0)
    upload_mbps:   float = Field(..., ge=0)
    ping_ms:       float = Field(..., ge=0)


class SpeedTestRead(SpeedTestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    library_id: int
    created_at: datetime