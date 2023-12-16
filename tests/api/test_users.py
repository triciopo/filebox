from datetime import date

import pytest


@pytest.mark.asyncio
async def test_get_users(client, super_access_token):
    response = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_users_not_authenticated(client, access_token):
    response = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_me_with_valid_token(client, access_token):
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_me_with_invalid_token(client):
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_user(client, test_user, super_access_token):
    response = await client.get(
        f"/api/v1/users/{test_user['id']}",
        headers={"Authorization": f"Bearer {super_access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]
    assert response.json()["username"] == test_user["username"]
    assert response.json()["created_at"] == test_user["created_at"]


@pytest.mark.asyncio
async def test_get_user_no_permission(client, access_token, test_super_user):
    response = await client.get(
        f"/api/v1/users/{test_super_user.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": f"User {test_super_user.id} not found"}


@pytest.mark.asyncio
async def test_get_user_not_authenticated(client):
    response = await client.get("/api/v1/users/5")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_user_not_found(client, super_access_token):
    response = await client.get(
        "/api/v1/users/5", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User 5 not found"


@pytest.mark.asyncio
async def test_create_user(client):
    user_data = {
        "username": "newuser",
        "email": "new_email@mail.com",
        "password": "test",
    }
    response = await client.post("/api/v1/users", json=user_data)

    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert response.json()["created_at"] == str(date.today())


@pytest.mark.asyncio
async def test_create_existing_user(client, test_user):
    response = await client.post("/api/v1/users", json=test_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


@pytest.mark.asyncio
async def test_create_user_existing_email(client, test_user):
    user_data = {
        "username": "newuser",
        "email": "testemail@mail.com",
        "password": "test",
    }
    response = await client.post("/api/v1/users", json=user_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already in use"}


@pytest.mark.asyncio
async def test_update_user(client, test_user, access_token):
    data = {"username": "moduser", "email": "mod_email@mail.com", "password": "test"}
    response = await client.put(
        f"/api/v1/users/{test_user['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=data,
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]
    assert response.json()["username"] == "moduser"
    assert response.json()["email"] == "mod_email@mail.com"


@pytest.mark.asyncio
async def test_update_user_not_authenticated(client, access_token, test_super_user):
    data = {"username": "moduser", "email": "mod_email@mail.com", "password": "test"}
    response = await client.put(
        f"/api/v1/users/{test_super_user.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=data,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_update_user_not_found(client, super_access_token):
    data = {"username": "moduser", "email": "mod_email@mail.com", "password": "test"}
    response = await client.put(
        "/api/v1/users/5",
        headers={"Authorization": f"Bearer {super_access_token}"},
        json=data,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User 5 not found"}


@pytest.mark.asyncio
async def test_delete_user(client, test_super_user, super_access_token):
    id = test_super_user.id
    response = await client.delete(
        f"/api/v1/users/{id}", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "User deleted"}


@pytest.mark.asyncio
async def test_delete_user_not_authenticated(client, access_token):
    response = await client.delete(
        "/api/v1/users/5", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_delete_user_not_found(client, super_access_token):
    response = await client.delete(
        "/api/v1/users/1", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
