import secrets
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    STORAGE_DIR: str = "uploads/"
    DEFAULT_STORAGE_SPACE: int = 1024 * 1024 * 1024

    CORS_ORIGINS: list[str] = ["*"]
    REDOC_URL: str = "/redoc"
    DOCS_URL: str = "/docs"
    API_PREFIX: str = "/api/v1"
    API_SECRET_KEY: str = secrets.token_urlsafe(32)
    API_ALGORITHM: str = "HS256"
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    ENV: str = "default"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
