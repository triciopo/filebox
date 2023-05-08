import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_SERVER: str = None
    POSTGRES_USER: str = None
    POSTGRES_PASSWORD: str = None
    POSTGRES_DB: str = None

    STORAGE_DIR: str = "uploads/"
    SIZE_LIMIT: int = 104857600
    API_PREFIX: str = "/api/v1"
    API_SECRET_KEY: str = secrets.token_urlsafe(32)
    API_ALGORITHM: str = "HS256"
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    ENV: str = "default"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
