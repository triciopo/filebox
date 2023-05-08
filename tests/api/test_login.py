def test_login_with_correct_credentials(client, test_user):
    response = client.post(
        "/api/v1/token",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_incorrect_credentials(client, test_user):
    response = client.post(
        "/api/v1/token",
        data={"username": test_user["username"], "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_me_with_valid_token(client, access_token):
    response = client.post(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"


def test_get_me_with_invalid_token(client):
    response = client.post(
        "/api/v1/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
