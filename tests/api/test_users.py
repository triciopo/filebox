from datetime import date


def test_get_users(client, super_access_token):
    response = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 200


def test_get_users_not_authenticated(client, access_token):
    response = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_me_with_valid_token(client, access_token):
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_get_user(client, test_user, super_access_token):
    response = client.get(
        f"/api/v1/users/{test_user['id']}",
        headers={"Authorization": f"Bearer {super_access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]
    assert response.json()["username"] == test_user["username"]
    assert response.json()["created_at"] == test_user["created_at"]


def test_get_user_not_authenticated(client):
    response = client.get("/api/v1/users/5")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_user_not_found(client, super_access_token):
    response = client.get(
        "/api/v1/users/5", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User 5 not found"


def test_create_user(client):
    user_data = {
        "id": "1",
        "username": "new_user",
        "created_at": str(date.today()),
        "email": "new_email@mail.com",
        "password": "test",
    }
    response = client.post("/api/v1/users/create", json=user_data)

    assert response.status_code == 201
    assert response.json()["username"] == "new_user"
    assert response.json()["created_at"] == str(date.today())


def test_create_existing_user(client, test_user):
    response = client.post("/api/v1/users/create", json=test_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_update_user(client, test_user, access_token):
    data = {"username": "mod_user", "email": "mod_email@mail.com", "password": "test"}
    response = client.put(
        f"/api/v1/users/{test_user['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=data,
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]
    assert response.json()["username"] == "mod_user"
    assert response.json()["email"] == "mod_email@mail.com"


def test_update_user_not_authenticated(client, access_token, test_super_user):
    data = {"username": "mod_user", "email": "mod_email@mail.com", "password": "test"}
    response = client.put(
        f"/api/v1/users/{test_super_user.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=data,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_update_user_not_found(client, super_access_token):
    data = {"username": "mod_user", "email": "mod_email@mail.com", "password": "test"}
    response = client.put(
        "/api/v1/users/5",
        headers={"Authorization": f"Bearer {super_access_token}"},
        json=data,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User 5 not found"}


def test_delete_user(client, test_super_user, super_access_token):
    id = test_super_user.id
    response = client.delete(
        f"/api/v1/users/{id}", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "User deleted"}


def test_delete_user_not_authenticated(client, access_token):
    response = client.delete(
        "/api/v1/users/5", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_user_not_found(client, super_access_token):
    response = client.delete(
        "/api/v1/users/1", headers={"Authorization": f"Bearer {super_access_token}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
