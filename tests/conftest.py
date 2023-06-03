from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.config import environ

environ["STORAGE_DIR"] = "tests/test-files/"
environ["SIZE_LIMIT"] = "20971520"
environ["ENV"] = "tests"

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="session")
def session():
    from filebox.core.database import Base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    from filebox.core.database import get_db
    from filebox.main import app

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    user_data = {
        "id": 1,
        "username": "testuser",
        "created_at": str(date.today()),
        "email": "testemail@mail.com",
        "password": "test_password",
    }
    client.post("/api/v1/users", json=user_data)
    return user_data


@pytest.fixture()
def test_super_user(session):
    from filebox.core.auth import get_hashed_password
    from filebox.models.user import User

    user = User(
        id="2",
        username="testsuperuser",
        hashed_password=get_hashed_password("test_password"),
        email="testemail@mail.com",
        is_super_user=True,
        created_at=date.today(),
    )
    session.add(user)
    session.commit()

    return user


@pytest.fixture()
def access_token(client, test_user):
    response = client.post(
        "/api/v1/token",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture()
def super_access_token(client, test_super_user):
    response = client.post(
        "/api/v1/token",
        data={
            "username": test_super_user.username,
            "password": "test_password",
        },
    )
    return response.json()["access_token"]


@pytest.fixture()
def test_file(client, access_token):
    file_content = b"some file content"
    files = {"file": ("file.txt", file_content)}
    file_post = client.post(
        "/api/v1/files",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    file = file_post.json()

    return file


@pytest.fixture()
def test_folder(client, access_token):
    folder_post = client.post(
        "/api/v1/folders",
        json={"path": "/testfolder"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    folder_path = folder_post.json()["path"]
    return folder_path
