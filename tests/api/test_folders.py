import pytest


@pytest.mark.asyncio
async def test_getfolders_unauthenticated(client):
    response = await client.get("/api/v1/folders")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_getfolders(client, access_token, test_folder):
    response = await client.get(
        "/api/v1/folders", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["path"] == "/"
    assert response.json()[1]["path"] == "/testfolder"


@pytest.mark.asyncio
async def test_create_folder_unauthenticated(client):
    response = await client.post("/api/v1/folders", data={"path": "/testfolder"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_folder(client, access_token):
    response = await client.post(
        "/api/v1/folders",
        json={"path": "/folder"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    assert response.json()["path"] == "/folder"


@pytest.mark.asyncio
async def test_create_folder_already_exists(client, access_token, test_folder):
    response = await client.post(
        "/api/v1/folders",
        json={"path": "/testfolder"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Folder already exists"}


@pytest.mark.asyncio
async def test_get_folder_unauthenticated(client):
    response = await client.get("/api/v1/folders/testfolder")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_folder_not_found(client, access_token):
    response = await client.get(
        "/api/v1/folders/folder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_folder(client, access_token, test_folder):
    response = await client.get(
        "/api/v1/folders/testfolder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_folder_unauthenticated(client):
    response = await client.delete("/api/v1/folders/testfolder")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_folder_not_found(client, access_token):
    response = await client.delete(
        "/api/v1/folders/folder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_folder(client, access_token, test_folder):
    response = await client.delete(
        "/api/v1/folders/testfolder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_root_folder(client, access_token):
    response = await client.delete(
        "/api/v1/folders/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Cannot delete root folder"}
