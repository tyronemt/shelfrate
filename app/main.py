from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from app.db import engine
from app.config import get_settings

from app.api.libraries import router as libraries_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm up DB connection
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    # Shutdown: clean up
    await engine.dispose()


app = FastAPI(
    title="ShelfRate API",
    description="A study spot finder for California libraries.",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

app.include_router(libraries_router)


@app.get("/health")
async def health():
    async with engine.connect() as conn:
        db_ok = (await conn.execute(text("SELECT 1"))).scalar() == 1
    return {"status": "ok", "db": db_ok, "version": app.version}