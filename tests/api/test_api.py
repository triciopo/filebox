import os
import uuid

from filebox.core.config import settings


def test_root(client):
    response = client.get("/api/v1")
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_get_file(client, access_token):
    file_content = b"some file content"
    files = {"file": ("file.txt", file_content)}
    file_post = client.post(
        "/api/v1/files/upload",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    file_id = file_post.json()["uuid"]

    response = client.get(
        f"/api/v1/files/{file_id}", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200


def test_get_files(client, access_token):
    response = client.get(
        "/api/v1/files", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200


def test_get_random(client, access_token):
    id = uuid.uuid4()
    response = client.get(
        f"/api/v1/files/{id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File {id} not found"}


def test_upload_file(client, access_token):
    file_content = b"some file content"
    files = {"file": ("file.txt", file_content)}
    response = client.post(
        "/api/v1/files/upload",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    file_id = response.json()["uuid"]

    assert response.status_code == 201
    assert f"{file_id}.txt" in os.listdir(f"{settings.STORAGE_DIR}{file_id}")


def test_upload_filesize_limit(client, access_token):
    file_content = b"x" * (settings.SIZE_LIMIT)
    files = {"file": ("file.txt", file_content)}
    response = client.post(
        "/api/v1/files/upload",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 413


def test_download_file(client, access_token):
    file_content = b"some file content"
    files = {"file": ("file.txt", file_content)}
    file_id = client.post(
        "/api/v1/files/upload",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()["uuid"]

    response = client.get(
        f"/api/v1/files/{file_id}/download",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200


def test_download_not_found(client, access_token):
    id = uuid.uuid4()
    response = client.get(
        f"/api/v1/files/{id}/download",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File {id} not found"}


def test_delete_file(client, access_token):
    file_content = b"some file content"
    files = {"file": ("file.txt", file_content)}
    file_id = client.post(
        "/api/v1/files/upload",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()["uuid"]

    response = client.delete(
        f"/api/v1/files/{file_id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "File deleted"}


def test_delete_file_not_found(client, access_token):
    id = uuid.uuid4()
    response = client.delete(
        f"/api/v1/files/{id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"File {id} not found"}
