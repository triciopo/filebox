from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_SERVER: str = None
    POSTGRES_USER: str = None
    POSTGRES_PASSWORD: str = None
    POSTGRES_DB: str = None

    STORAGE_DIR: str = "uploads/"
    SIZE_LIMIT: int = 104857600
    API_PREFIX: str = "/api/v1"

    ENV: str = "default"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
