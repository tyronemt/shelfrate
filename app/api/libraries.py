from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.db import get_db
from app.models import Library
from app.schemas.libraries import LibraryCreate, LibraryUpdate, LibraryRead

router = APIRouter(prefix="/api/libraries", tags=["libraries"])


def _slugify(name: str, city: str) -> str:
    import re
    s = f"{name}-{city}".lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:220]


@router.get("", response_model=List[LibraryRead])
async def list_libraries(
    db: AsyncSession = Depends(get_db),
    city: Optional[str] = None,
    access_level: Optional[str] = None,
    has_quiet_zone: Optional[bool] = None,
    free_parking: Optional[bool] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    stmt = select(Library)
    if city:
        stmt = stmt.where(Library.city == city)
    if access_level:
        stmt = stmt.where(Library.access_level == access_level)
    if has_quiet_zone is not None:
        stmt = stmt.where(Library.has_quiet_zone == has_quiet_zone)
    if free_parking:
        stmt = stmt.where(Library.parking_type == "free_lot")
    stmt = stmt.order_by(Library.name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    libs = result.scalars().all()
    return [LibraryRead.from_orm_with_geo(l) for l in libs]


@router.get("/{library_id}", response_model=LibraryRead)
async def get_library(library_id: int, db: AsyncSession = Depends(get_db)):
    lib = await db.get(Library, library_id)
    if not lib:
        raise HTTPException(404, "Library not found")
    return LibraryRead.from_orm_with_geo(lib)


@router.post("", response_model=LibraryRead, status_code=status.HTTP_201_CREATED)
async def create_library(payload: LibraryCreate, db: AsyncSession = Depends(get_db)):
    point = from_shape(Point(payload.longitude, payload.latitude), srid=4326)
    lib = Library(
        **payload.model_dump(exclude={"latitude", "longitude"}),
        slug=_slugify(payload.name, payload.city),
        location=point,
    )
    db.add(lib)
    try:
        await db.commit()
        await db.refresh(lib)
    except Exception as e:
        await db.rollback()
        raise HTTPException(400, f"Could not create: {e}")
    return LibraryRead.from_orm_with_geo(lib)
    

@router.patch("/{library_id}", response_model=LibraryRead)
async def update_library(library_id: int, payload: LibraryUpdate, db: AsyncSession = Depends(get_db)):
    lib = await db.get(Library, library_id)
    if not lib:
        raise HTTPException(404, "Library not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(lib, k, v)
    await db.commit()
    await db.refresh(lib)
    return LibraryRead.from_orm_with_geo(lib)


@router.delete("/{library_id}", status_code=204)
async def delete_library(library_id: int, db: AsyncSession = Depends(get_db)):
    lib = await db.get(Library, library_id)
    if not lib:
        raise HTTPException(404, "Library not found")
    await db.delete(lib)
    await db.commit()
    return