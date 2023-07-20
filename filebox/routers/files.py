import uuid
from typing import Sequence

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from starlette.responses import FileResponse

from filebox import storage
from filebox.core.auth import CurrentUser
from filebox.core.database import DBSession
from filebox.models import file
from filebox.rate_limiter import limiter
from filebox.schemas.file import FileBaseResponse, FilePath
from filebox.schemas.folder import FolderPath
from filebox.services import files as service
from filebox.services import folders as folder_service
from filebox.services import users as user_service

file_router = APIRouter()


@file_router.get("/")
async def root() -> dict:
    """Main path"""
    return {"success": True}


@file_router.get("/files", response_model=list[FileBaseResponse])
async def get_files(
    current_user: CurrentUser,
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[file.File]:
    """Fetch all files"""
    return await service.get_files_by_id(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
    )


@file_router.get("/files{file_path:path}/download")
async def download_file(
    file_path: FilePath,
    current_user: CurrentUser,
    db: DBSession,
) -> FileResponse:
    """Download a file given a path"""
    file_db = await service.get_file_by_path(db, file_path, int(current_user.id))
    if not file_db:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    file = await storage.get_file(file_db.uuid)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    return FileResponse(
        file, filename=file_db.name, content_disposition_type="attachment"
    )


@file_router.get("/files{file_path:path}", response_model=FileBaseResponse)
async def get_file(
    file_path: FilePath,
    current_user: CurrentUser,
    db: DBSession,
) -> FileBaseResponse:
    """Fetch a file given an path"""
    file = await service.get_file_by_path(db, file_path, int(current_user.id))
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    return file


@file_router.post("/files", status_code=201, response_model=FileBaseResponse)
@limiter.limit("100/minute")
async def upload_file(
    request: Request,
    current_user: CurrentUser,
    db: DBSession,
    path: FolderPath = FolderPath("/"),
    file: UploadFile = File(...),
) -> FileBaseResponse:
    """Upload a file"""
    mime_type = file.content_type or "application/octet-stream"
    id = uuid.uuid4()

    folder = await folder_service.get_folder_by_path(db, path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=404, detail=f"Folder {path} not found")
    full_path = str(path).rstrip("/") + "/" + str(file.filename)
    if await service.get_file_by_path(db, full_path, int(current_user.id)):
        raise HTTPException(status_code=409, detail="File already exists")
    size = await storage.get_file_size(file)
    current_user_used_space = await user_service.get_user_used_space(
        db, current_user.id
    )

    if current_user_used_space + size > current_user.storage_space:
        raise HTTPException(status_code=413, detail="Storage space limit exceeded")
    await storage.upload_file(id, file)
    return await service.create_file(
        db,
        id,
        str(file.filename),
        full_path,
        folder.id,
        size,
        current_user.id,
        mime_type,
    )


@file_router.post(
    "/files/batch", status_code=201, response_model=list[FileBaseResponse]
)
@limiter.limit("2/minute")
async def upload_batch(
    request: Request,
    current_user: CurrentUser,
    db: DBSession,
    path: FolderPath = FolderPath("/"),
    files: list[UploadFile] = File(...),
) -> list[file.File]:
    """Upload a batch of files"""
    folder = await folder_service.get_folder_by_path(db, path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=404, detail=f"Folder {path} not found")
    current_user_used_space = await user_service.get_user_used_space(
        db, current_user.id
    )
    size = await storage.get_files_size(files)
    if current_user_used_space + sum(size) > current_user.storage_space:
        raise HTTPException(status_code=413, detail="Storage space limit exceeded")
    uuids = [uuid.uuid4() for _ in range(len(files))]

    await storage.upload_files(uuids, files)
    return await service.create_batch_files(
        db, files, path, size, uuids, folder.id, current_user.id
    )


@file_router.delete("/files{file_path:path}")
async def delete_file(
    file_path: FilePath,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete a file given an path"""
    file = await service.get_file_by_path(db, file_path, current_user.id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    await storage.delete_file(file.uuid)
    await service.delete_file(db, file.uuid)
    return {"success": True, "message": "File deleted"}
