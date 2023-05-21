from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
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
def get_files(current_user: CurrentUser, db: DBSession) -> list[FileBaseResponse]:
    """Fetch all files"""
    if current_user.is_super_user:
        return queries.get_files(db)
    return queries.get_files_by_id(db, int(current_user.id))


@file_router.get("/files/{file_uuid}", response_model=FileBaseResponse)
def get_file(
    file_uuid: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> FileBaseResponse:
    """Fetch a file given an id"""
    file = queries.get_file(db, file_uuid)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    if not current_user.is_super_user and file.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    return file


@file_router.post("/files/upload", status_code=201, response_model=FileBaseResponse)
@limiter.limit("100/minute")
async def upload_file(
    request: Request,
    current_user: CurrentUser,
    db: DBSession,
    file: UploadFile = File(...),
) -> FileBaseResponse:
    """Upload a file"""
    content_type = file.content_type or "application/octet-stream"

    uuid = uuid4()
    Path(f"{settings.STORAGE_DIR}{uuid}").mkdir(parents=True, exist_ok=True)

    await storage.upload_file(uuid, file)
    size = await storage.get_file_size(file)

    return queries.create_file(
        db, uuid, str(file.filename), size, int(current_user.id), content_type
    )


@file_router.delete("/files/{file_uuid}", response_model=None)
async def delete_file(
    file_uuid: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete a file given an id"""
    file = queries.get_file(db, file_uuid)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    if file.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    await storage.delete_file(file_uuid)
    queries.delete_file(db, file_uuid)
    return {"success": True, "message": "File deleted"}


@file_router.get("/files/{file_uuid}/download", response_model=None)
async def download_file(
    file_uuid: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> FileResponse:
    """Download a file given an id"""
    file = await storage.get_file(file_uuid)
    file_db = queries.get_file(db, file_uuid)
    if not file or not file_db:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    if file_db.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    return FileResponse(
        file, filename=file_db.name, content_disposition_type="attachment"
    )
