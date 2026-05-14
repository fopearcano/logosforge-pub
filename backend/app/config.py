from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "LOGOSFORGE"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    api_prefix: str = "/api"

    database_url: str = f"sqlite:///{(BASE_DIR / 'logosforge.db').as_posix()}"
    database_echo: bool = False

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Authentication — development defaults. Override via environment in
    # any non-development deployment.
    secret_key: str = "logosforge-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Local file storage root. Real uploads land under this directory;
    # placeholder attachment records do not touch disk.
    storage_path: str = (BASE_DIR / "storage").as_posix()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
