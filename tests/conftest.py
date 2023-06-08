from datetime import date
from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.config import environ

environ["STORAGE_DIR"] = "tests/test-files/"
environ["SIZE_LIMIT"] = "20971520"
environ["ENV"] = "tests"

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    future=True,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(name="session")
async def session() -> AsyncGenerator:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator:
    from filebox.core.database import Base
    from filebox.main import app

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(client):
    user_data = {
        "id": 1,
        "username": "testuser",
        "created_at": str(date.today()),
        "email": "testemail@mail.com",
        "password": "test_password",
    }
    await client.post("/api/v1/users", json=user_data)
    return user_data


@pytest_asyncio.fixture
async def test_super_user(session: AsyncSession):
    from filebox.core.auth import get_hashed_password
    from filebox.models.user import User

    user = User(
        id=2,
        username="testsuperuser",
        hashed_password=get_hashed_password("test_password"),
        email="testemail@mail.com",
        is_super_user=True,
        created_at=date.today(),
    )
    session.add(user)
    await session.commit()

    return user


@pytest_asyncio.fixture
async def access_token(client, test_user):
    response = await client.post(
        "/api/v1/token",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def super_access_token(client, test_super_user):
    response = await client.post(
        "/api/v1/token",
        data={
            "username": test_super_user.username,
            "password": "test_password",
        },
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def test_file(client, access_token):
    file_content = b"some file content"
    files = {"file": ("file.txt", file_content)}
    file_post = await client.post(
        "/api/v1/files",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    file = file_post.json()

    return file


@pytest_asyncio.fixture
async def test_folder(client, access_token):
    folder_post = await client.post(
        "/api/v1/folders",
        json={"path": "/testfolder"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    folder_path = folder_post.json()["path"]
    return folder_path
