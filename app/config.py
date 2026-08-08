from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = "postgresql+psycopg://shelfrate:shelfrate_dev@localhost:5433/shelfrate"
    sync_database_url: str = "postgresql+psycopg://shelfrate:shelfrate_dev@localhost:5433/shelfrate"

    # Auth
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    # App
    debug: bool = False
    log_level: str = "INFO"

    # Scraping
    scrape_user_agent: str = "ShelfRateBot/0.1 (contact: you@example.com)"
    scrape_delay_seconds: float = 1.5


@lru_cache
def get_settings() -> Settings:
    return Settings()