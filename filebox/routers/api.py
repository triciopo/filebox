from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from filebox import storage
from filebox.core import queries
from filebox.core.auth import get_current_user
from filebox.core.config import settings
from filebox.core.database import Base, engine, get_db
from filebox.models.user import User
from filebox.rate_limiter import limiter
from filebox.schemas.file import FileBaseResponse

Base.metadata.create_all(bind=engine)

file_router = APIRouter()


@file_router.get("/")
def root():
    """Main path"""
    return {"success": True}


@file_router.get("/files", response_model=list[FileBaseResponse])
def get_files(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch all files"""
    if user.is_super_user:
        return queries.get_files(db)
    return queries.get_files_by_id(db, user.id)


@file_router.get("/files/{file_uuid}", response_model=FileBaseResponse)
def get_file(
    file_uuid: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch a file given an id"""
    file = queries.get_file(db, file_uuid)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    if not user.is_super_user and file.owner_id != user.id:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    return file


@file_router.post("/files/upload", status_code=201, response_model=FileBaseResponse)
@limiter.limit("100/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a file"""
    content_type = file.content_type or "application/octet-stream"

    uuid = uuid4()
    Path(f"{settings.STORAGE_DIR}{uuid}").mkdir(parents=True, exist_ok=True)

    await storage.upload_file(uuid, file)
    size = await storage.get_file_size(file)

    return queries.create_file(db, uuid, file.filename, size, user.id, content_type)


@file_router.delete("/files/{file_uuid}", response_model=None)
async def delete_file(
    file_uuid: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a file given an id"""
    file = queries.get_file(db, file_uuid)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    if file.owner_id != user.id:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    await storage.delete_file(file_uuid)
    queries.delete_file(db, file_uuid)
    return {"success": True, "message": "File deleted"}


@file_router.get("/files/{file_uuid}/download", response_model=None)
async def download_file(
    file_uuid: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a file given an id"""
    file = await storage.get_file(file_uuid)
    file_db = queries.get_file(db, file_uuid)
    if not file or not file_db:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    if file_db.owner_id != user.id:
        raise HTTPException(status_code=404, detail=f"File {file_uuid} not found")
    return FileResponse(
        file, filename=file_db.name, content_disposition_type="attachment"
    )
