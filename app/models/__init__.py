from datetime import datetime, time
import enum
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, ForeignKey, DateTime, Time, Text, JSON, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db import Base


# ============================================================
# Enums
# ============================================================
class SystemType(str, enum.Enum):
    county    = "county"
    municipal = "municipal"
    academic  = "academic"
    private   = "private"
    special   = "special"


class AccessLevel(str, enum.Enum):
    open_to_all      = "open_to_all"
    card_required    = "card_required"
    day_pass         = "day_pass"
    students_only    = "students_only"
    members_only     = "members_only"
    appointment_only = "appointment_only"


class WifiPolicy(str, enum.Enum):
    free                = "free"
    card_only           = "card_only"
    day_pass            = "day_pass"
    guest_pass_at_desk  = "guest_pass_at_desk"
    not_available       = "not_available"


class NoisePolicy(str, enum.Enum):
    strict_silence   = "strict_silence"
    quiet_talk       = "quiet_talk"
    low_conversation = "low_conversation"
    mixed            = "mixed"


class FoodPolicy(str, enum.Enum):
    no_food       = "no_food"
    drinks_only   = "drinks_only"
    covered_drink = "covered_drink"
    snacks_ok     = "snacks_ok"
    cafe_on_site  = "cafe_on_site"


class ParkingType(str, enum.Enum):
    free_lot    = "free_lot"
    metered     = "metered"
    paid_lot    = "paid_lot"
    validation  = "validation"
    permit_only = "permit_only"
    street_only = "street_only"
    none        = "none"


class WorkZone(str, enum.Enum):
    quiet            = "quiet"
    group            = "group"
    individual_booth = "individual_booth"
    zoom_pod         = "zoom_pod"
    whiteboard_wall  = "whiteboard_wall"
    reservable_room  = "reservable_room"


class WalkInPolicy(str, enum.Enum):
    anytime         = "anytime"
    sign_in_at_desk = "sign_in_at_desk"
    card_swipe      = "card_swipe"


# ============================================================
# Models
# ============================================================
class User(Base):
    __tablename__ = "users"
    id:            Mapped[int]      = mapped_column(primary_key=True)
    email:         Mapped[str]      = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]      = mapped_column(String(255))
    display_name:  Mapped[str]      = mapped_column(String(100))
    is_admin:      Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Library(Base):
    __tablename__ = "libraries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    address: Mapped[str] = mapped_column(String(300))
    city: Mapped[str] = mapped_column(String(100), index=True)
    state: Mapped[str] = mapped_column(String(2), default="CA")
    zip_code: Mapped[str] = mapped_column(String(10), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    website: Mapped[Optional[str]] = mapped_column(String(300))
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326))

    # System & governance
    system_name:    Mapped[Optional[str]]   = mapped_column(String(200))
    system_type:    Mapped[SystemType]      = mapped_column(Enum(SystemType))
    catalog_system: Mapped[Optional[str]]   = mapped_column(String(50))

    # Hours
    hours_json:  Mapped[Optional[dict]] = mapped_column(JSON)
    is_24_hour:  Mapped[bool]           = mapped_column(Boolean, default=False)
    closing_time: Mapped[Optional[time]] = mapped_column(Time)

    # Access (the important one)
    access_level: Mapped[AccessLevel]            = mapped_column(Enum(AccessLevel))
    wifi_policy:  Mapped[WifiPolicy]             = mapped_column(Enum(WifiPolicy))
    membership_required_for: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    access_notes: Mapped[Optional[str]]          = mapped_column(Text)
    walk_in_policy: Mapped[WalkInPolicy]         = mapped_column(
        Enum(WalkInPolicy), default=WalkInPolicy.anytime
    )

    # Laptop-friendly inputs
    outlet_density_score:   Mapped[Optional[int]] = mapped_column(Integer)
    seating_time_limit_min:  Mapped[Optional[int]] = mapped_column(Integer)
    has_long_term_seating:   Mapped[bool]          = mapped_column(Boolean, default=False)
    total_seats:             Mapped[Optional[int]] = mapped_column(Integer)
    has_quiet_zone:          Mapped[bool]          = mapped_column(Boolean, default=False)
    has_outdoor_seating:     Mapped[bool]          = mapped_column(Boolean, default=False)
    has_charging_stations:   Mapped[bool]          = mapped_column(Boolean, default=False)
    has_free_water:          Mapped[bool]          = mapped_column(Boolean, default=False)
    natural_light:           Mapped[bool]          = mapped_column(Boolean, default=False)

    # Noise & work zones
    noise_policy:     Mapped[Optional[NoisePolicy]] = mapped_column(Enum(NoisePolicy))
    work_zones:       Mapped[Optional[list]]        = mapped_column(JSON, default=list)
    recommended_for:  Mapped[Optional[list]]        = mapped_column(JSON, default=list)

    # Parking
    parking_type:   Mapped[Optional[ParkingType]] = mapped_column(Enum(ParkingType))
    parking_notes:  Mapped[Optional[str]]         = mapped_column(Text)
    has_bike_parking: Mapped[bool]                 = mapped_column(Boolean, default=False)

    # Other amenities
    has_study_rooms:       Mapped[bool] = mapped_column(Boolean, default=False)
    has_public_computers:  Mapped[bool] = mapped_column(Boolean, default=False)
    has_printing:          Mapped[bool] = mapped_column(Boolean, default=False)
    has_outlets:           Mapped[bool] = mapped_column(Boolean, default=True)
    has_free_wifi:         Mapped[bool] = mapped_column(Boolean, default=True)
    is_wheelchair_accessible: Mapped[bool] = mapped_column(Boolean, default=True)

    # Programs
    programs: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Metadata
    last_verified_at:     Mapped[Optional[datetime]] = mapped_column(DateTime)
    data_freshness_score: Mapped[Optional[float]]    = mapped_column(Float)
    scrape_source:        Mapped[Optional[str]]      = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    disclaimers: Mapped[List["Disclaimer"]] = relationship(
        back_populates="library", cascade="all, delete-orphan"
    )
    speed_tests: Mapped[List["SpeedTest"]] = relationship(
        back_populates="library", cascade="all, delete-orphan"
    )
    reviews:     Mapped[List["Review"]] = relationship(
        back_populates="library", cascade="all, delete-orphan"
    )


class Disclaimer(Base):
    __tablename__ = "disclaimers"
    id:         Mapped[int]      = mapped_column(primary_key=True)
    library_id: Mapped[int]      = mapped_column(ForeignKey("libraries.id"))
    category:   Mapped[str]      = mapped_column(String(50))
    title:      Mapped[str]      = mapped_column(String(200))
    body:       Mapped[str]      = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String(300))
    upvotes:    Mapped[int]      = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    library:    Mapped["Library"] = relationship(back_populates="disclaimers")


class SpeedTest(Base):
    __tablename__ = "speed_tests"
    id:            Mapped[int]      = mapped_column(primary_key=True)
    library_id:    Mapped[int]      = mapped_column(ForeignKey("libraries.id"), index=True)
    user_id:       Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    download_mbps: Mapped[float]    = mapped_column(Float)
    upload_mbps:   Mapped[float]    = mapped_column(Float)
    ping_ms:       Mapped[float]    = mapped_column(Float)
    client_ip:     Mapped[Optional[str]] = mapped_column(String(45))
    user_agent:    Mapped[Optional[str]] = mapped_column(String(300))
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    library:       Mapped["Library"] = relationship(back_populates="speed_tests")


class Review(Base):
    __tablename__ = "reviews"
    id:                  Mapped[int]      = mapped_column(primary_key=True)
    library_id:          Mapped[int]      = mapped_column(ForeignKey("libraries.id"))
    user_id:             Mapped[int]      = mapped_column(ForeignKey("users.id"))
    rating_overall:      Mapped[int]      = mapped_column(Integer)
    rating_noise:        Mapped[Optional[int]] = mapped_column(Integer)
    rating_outlets:      Mapped[Optional[int]] = mapped_column(Integer)
    rating_seating:      Mapped[Optional[int]] = mapped_column(Integer)
    rating_staff:        Mapped[Optional[int]] = mapped_column(Integer)
    crowdedness:         Mapped[Optional[str]] = mapped_column(String(20))
    body:                Mapped[str]      = mapped_column(Text)
    created_at:          Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# Make Alembic happy — explicit imports so Base.metadata sees everything
__all__ = ["Base", "User", "Library", "Disclaimer", "SpeedTest", "Review",
           "SystemType", "AccessLevel", "WifiPolicy", "NoisePolicy",
           "FoodPolicy", "ParkingType", "WorkZone", "WalkInPolicy"]