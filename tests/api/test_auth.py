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
