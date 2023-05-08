from datetime import date


def test_get_users(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 200


def test_get_user(client, test_user):
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]
    assert response.json()["username"] == test_user["username"]
    assert response.json()["created_at"] == test_user["created_at"]


def test_get_user_not_found(client):
    response = client.get("/api/v1/users/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "User 1 not found"


def test_create_user(client):
    user_data = {
        "id": "1",
        "username": "new_user",
        "created_at": str(date.today()),
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


def test_delete_user(client, test_user):
    id = test_user["id"]
    response = client.delete(f"/api/v1/users/{id}")
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "User deleted"}


def test_delete_user_not_found(client):
    response = client.delete("/api/v1/users/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
