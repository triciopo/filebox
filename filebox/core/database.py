from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from filebox.core.config import settings


def get_db_url(env: str) -> str:
    if env == "tests":
        return "sqlite+aiosqlite:///test.db"
    return f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"


engine = create_async_engine(
    get_db_url(settings.ENV),
    future=True,
    echo=False,
)

AsyncSessionFactory = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db)]
Base = declarative_base()
