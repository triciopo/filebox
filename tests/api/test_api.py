import os

from filebox.core.config import settings


def test_root(client):
    response = client.get("/api/v1")
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_get_file(client, access_token, test_file):
    response = client.get(
        f"/api/v1/files{test_file['path']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["uuid"] == test_file["uuid"]


def test_get_files(client, access_token, test_file):
    response = client.get(
        "/api/v1/files", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["uuid"] == test_file["uuid"]


def test_get_random(client, access_token):
    response = client.get(
        "/api/v1/files/test.jpg", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "File /test.jpg not found"}


def test_upload_file(client, access_token):
    file = {"file": ("file.txt", b"some file content")}
    response = client.post(
        "/api/v1/files",
        files=file,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    file_id = response.json()["uuid"]

    assert response.status_code == 201
    assert f"{file_id}.txt" in os.listdir(f"{settings.STORAGE_DIR}{file_id}")


def test_upload_file_already_exists(client, access_token, test_file):
    files = {"file": ("file.txt", b"some file content")}
    response = client.post(
        "/api/v1/files",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "File already exists"}


def test_upload_file_path_not_found(client, access_token):
    file = {"file": ("file.txt", b"some file content")}
    response = client.post(
        "/api/v1/files",
        files=file,
        params={"path": "/testfolder"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Folder /testfolder not found"}


def test_upload_batch_file(client, access_token):
    files = [
        ("files", ("file.txt", b"some file content")),
        ("files", ("file2.txt", b"some file content")),
    ]
    response = client.post(
        "/api/v1/files/batch",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response_json = response.json()
    uuid = [file["uuid"] for file in response_json]

    assert response.status_code == 201
    assert len(uuid) == 2
    assert f"{uuid[0]}.txt" in os.listdir(f"{settings.STORAGE_DIR}{uuid[0]}")
    assert f"{uuid[1]}.txt" in os.listdir(f"{settings.STORAGE_DIR}{uuid[1]}")


def test_upload_batch_file_path_not_found(client, access_token):
    files = [
        ("files", ("file.txt", b"some file content")),
        ("files", ("file2.txt", b"some file content")),
    ]
    response = client.post(
        "/api/v1/files/batch",
        files=files,
        params={"path": "/testfolder"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Folder /testfolder not found"}


def test_upload_filesize_limit(client, access_token):
    file_content = b"x" * (settings.SIZE_LIMIT)
    files = {"file": ("file.txt", file_content)}
    response = client.post(
        "/api/v1/files",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 413


def test_download_file(client, access_token, test_file):
    response = client.get(
        f"/api/v1/files{test_file['path']}/download",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200


def test_download_not_found(client, access_token):
    response = client.get(
        "/api/v1/files/random.jpg/download",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "File /random.jpg not found"}


def test_delete_file(client, access_token, test_file):
    response = client.delete(
        f"/api/v1/files{test_file['path']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "File deleted"}


def test_delete_file_not_found(client, access_token):
    response = client.delete(
        "/api/v1/files/random.jpg", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "File /random.jpg not found"}
