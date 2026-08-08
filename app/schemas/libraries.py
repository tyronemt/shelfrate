from datetime import datetime, time
from typing import Optional, List
from pydantic import Field
from pydantic import BaseModel, ConfigDict, model_validator 
from geoalchemy2.shape import to_shape 

from app.models import (
    SystemType, AccessLevel, WifiPolicy, NoisePolicy, FoodPolicy,
    ParkingType, WorkZone, WalkInPolicy,
)


class LibraryBase(BaseModel):
    name:    str  = Field(..., max_length=200)
    address: str  = Field(..., max_length=300)
    city:    str  = Field(..., max_length=100)
    state:   str  = Field("CA", max_length=2)
    zip_code: str = Field(..., max_length=10)
    latitude:  float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    phone:    Optional[str] = None
    website:  Optional[str] = None

    system_name:    Optional[str] = None
    system_type:    SystemType
    catalog_system: Optional[str] = None

    access_level:   AccessLevel
    wifi_policy:    WifiPolicy
    walk_in_policy: WalkInPolicy = WalkInPolicy.anytime
    membership_required_for: List[str] = []
    access_notes:   Optional[str] = None

    outlet_density_score:  Optional[int] = Field(None, ge=1, le=5)
    seating_time_limit_min: Optional[int] = Field(None, ge=0)
    has_long_term_seating: bool = False
    total_seats:           Optional[int] = Field(None, ge=0)
    has_quiet_zone:        bool = False
    has_outdoor_seating:   bool = False
    has_charging_stations: bool = False
    has_free_water:        bool = False
    natural_light:         bool = False

    noise_policy:    Optional[NoisePolicy] = None
    work_zones:      List[str] = []
    recommended_for: List[str] = []

    parking_type:   Optional[ParkingType] = None
    parking_notes:  Optional[str] = None
    has_bike_parking: bool = False

    has_study_rooms:        bool = False
    has_public_computers:   bool = False
    has_printing:           bool = False
    has_outlets:            bool = True
    has_free_wifi:          bool = True
    is_wheelchair_accessible: bool = True

    programs: List[str] = []


class LibraryCreate(LibraryBase):
    pass


class LibraryUpdate(BaseModel):
    """All fields optional for PATCH."""
    name: Optional[str] = None
    address: Optional[str] = None
    seating_time_limit_min: Optional[int] = None
    outlet_density_score: Optional[int] = None
    noise_policy: Optional[NoisePolicy] = None
    access_notes: Optional[str] = None
    # ... add more as needed for moderators


from pydantic import BaseModel, ConfigDict, model_validator
from geoalchemy2.shape import to_shape


class LibraryRead(LibraryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    latitude: float | None = None
    longitude: float | None = None
    laptop_score: float | None = None

    @model_validator(mode="before")
    @classmethod
    def _inject_lat_lng(cls, data):
        # data is either an ORM Library instance or a dict
        if hasattr(data, "location"):
            location = data.location
            extra = {
                k: v
                for k, v in data.__dict__.items()
                if not k.startswith("_")
            }
        else:
            location = (data or {}).get("location")
            extra = dict(data or {})

        if location is not None:
            try:
                point = to_shape(location)
                extra["latitude"] = point.y
                extra["longitude"] = point.x
            except Exception:
                extra.setdefault("latitude", None)
                extra.setdefault("longitude", None)
        else:
            extra.setdefault("latitude", None)
            extra.setdefault("longitude", None)

        return extra

    # keep your old helper around if other code calls it
    @classmethod
    def from_orm_with_geo(cls, lib) -> "LibraryRead":
        return cls.model_validate(lib)