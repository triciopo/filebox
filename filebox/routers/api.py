from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import constr
from starlette.responses import FileResponse

from filebox import storage
from filebox.core import queries
from filebox.core.auth import CurrentUser
from filebox.core.config import settings
from filebox.core.database import DBSession
from filebox.rate_limiter import limiter
from filebox.schemas.file import FileBaseResponse

file_router = APIRouter()


@file_router.get("/")
def root() -> dict:
    """Main path"""
    return {"success": True}


@file_router.get("/files", response_model=list[FileBaseResponse])
def get_files(
    current_user: CurrentUser,
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
) -> list[FileBaseResponse]:
    """Fetch all files"""
    return queries.get_files_by_id(
        db,
        int(current_user.id),
        skip=skip,
        limit=limit,
    )


@file_router.get("/files{file_path:path}/download", response_model=None)
async def download_file(
    file_path: constr(regex="^\/(?:[\w\s]+\/)*[\w\s]+\.\w+$"),
    current_user: CurrentUser,
    db: DBSession,
) -> FileResponse:
    """Download a file given an path"""
    file_db = queries.get_file_by_path(db, file_path, current_user.id)
    if not file_db:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    file = await storage.get_file(file_db.uuid)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    if file_db.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    return FileResponse(
        file, filename=file_db.name, content_disposition_type="attachment"
    )


@file_router.get("/files{file_path:path}", response_model=FileBaseResponse)
def get_file(
    file_path: constr(regex="^\/(?:[\w\s]+\/)*[\w\s]+\.\w+$"),
    current_user: CurrentUser,
    db: DBSession,
) -> FileBaseResponse:
    """Fetch a file given an path"""
    file = queries.get_file_by_path(db, file_path, int(current_user.id))
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    if not current_user.is_super_user and file.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    return file


@file_router.post("/files", status_code=201, response_model=FileBaseResponse)
@limiter.limit("100/minute")
async def upload_file(
    request: Request,
    current_user: CurrentUser,
    db: DBSession,
    file_path: constr(regex="^(?:\/(?:[\w\s]+\/)*[\w\s]+|\/)$") = "/",
    file: UploadFile = File(...),
) -> FileBaseResponse:
    """Upload a file"""
    content_type = file.content_type or "application/octet-stream"
    uuid = uuid4()

    folder = queries.get_folder_by_path(db, file_path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=400, detail="Folder not found")
    if not file_path.endswith("/"):
        file_path += "/" + str(file.filename)
    else:
        file_path += str(file.filename)
    if queries.get_file_by_path(db, file_path, int(current_user.id)):
        raise HTTPException(status_code=400, detail="File already exists")
    size = await storage.get_file_size(file)
    current_user_used_space = queries.get_user_used_space(db, int(current_user.id))

    if size > settings.SIZE_LIMIT:
        raise HTTPException(status_code=413, detail="File size limit exceeded")
    if current_user_used_space + size > current_user.storage_space:
        raise HTTPException(status_code=413, detail="Storage space limit exceeded")
    await storage.upload_file(uuid, file)
    return queries.create_file(
        db,
        uuid,
        str(file.filename),
        file_path,
        folder.id,
        size,
        int(current_user.id),
        content_type,
    )


@file_router.post(
    "/files/batch", status_code=201, response_model=list[FileBaseResponse]
)
@limiter.limit("10/minute")
async def upload_batch(
    request: Request,
    current_user: CurrentUser,
    db: DBSession,
    file_path: constr(regex="^(?:\/(?:[\w\s]+\/)*[\w\s]+|\/)$") = "/",
    files: list[UploadFile] = File(...),
) -> list[FileBaseResponse]:
    """Upload a batch of files"""
    folder = queries.get_folder_by_path(db, file_path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=400, detail="Folder not found")
    current_user_used_space = queries.get_user_used_space(db, int(current_user.id))
    size = await storage.get_files_size(files)
    if current_user_used_space + sum(size) > current_user.storage_space:
        raise HTTPException(status_code=413, detail="Storage space limit exceeded")
    if sum(size) > settings.SIZE_LIMIT:
        raise HTTPException(status_code=413, detail="File size limit exceeded")
    uuids = [uuid4() for _ in range(len(files))]
    uploaded_files = []

    path = file_path
    for i, file in enumerate(files):
        if not file_path.endswith("/"):
            path += "/" + str(file.filename)
        else:
            path += str(file.filename)

        if queries.get_file_by_path(db, path, int(current_user.id)):
            raise HTTPException(status_code=400, detail=f"File {path} already exists")
        content_type = file.content_type or "application/octet-stream"
        uploaded_files.append(
            queries.create_file(
                db,
                uuids[i],
                str(file.filename),
                path,
                folder.id,
                size[i],
                int(current_user.id),
                content_type,
            )
        )
        path = file_path
    await storage.upload_files(uuids, files)
    return uploaded_files


@file_router.delete("/files{file_path:path}", response_model=None)
async def delete_file(
    file_path: constr(regex="^\/(?:[\w\s]+\/)*[\w\s]+\.\w+$"),
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete a file given an path"""
    file = queries.get_file_by_path(db, file_path, current_user.id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    if file.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
    await storage.delete_file(file.uuid)
    queries.delete_file(db, file.uuid)
    return {"success": True, "message": "File deleted"}
