from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from filebox import storage
from filebox.core import queries
from filebox.core.config import settings
from filebox.core.database import Base, engine, get_db
from filebox.rate_limiter import limiter
from filebox.schemas.file import FileBaseResponse

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/")
async def root():
    """Main path"""
    return {"success": True}


@router.get("/files", response_model=list[FileBaseResponse])
async def get_files(db: Session = Depends(get_db)):
    """Fetch all files"""
    return queries.get_files(db)


@router.get("/files/{file_uuid}", response_model=FileBaseResponse)
async def get_file(file_uuid: UUID, db: Session = Depends(get_db)):
    """Fetch a file given an id"""

    result = queries.get_file(db, file_uuid)
    if not result:
        raise HTTPException(404, detail=f"File {file_uuid} not found")
    return result


@router.post("/files/upload", status_code=201, response_model=FileBaseResponse)
@limiter.limit("100/minute")
async def upload_file(
    request: Request, file: UploadFile, db: Session = Depends(get_db)
):
    """Upload file and save it on the files folder"""

    uuid = uuid4()
    Path(f"{settings.STORAGE_DIR}{uuid}").mkdir(parents=True, exist_ok=True)

    await storage.upload_file(uuid, file)
    size = await storage.get_file_size(file)

    return queries.create_file(db, uuid, file.filename, size, file.content_type)


@router.delete("/files/{file_uuid}", response_model=None)
async def delete_file(file_uuid: UUID, db: Session = Depends(get_db)):
    """Delete a file given an id"""

    if await storage.get_file(file_uuid) is not None:
        await storage.delete_file(file_uuid)
    else:
        raise HTTPException(404, detail=f"File {file_uuid} not found")

    queries.delete_file(db, file_uuid)
    return {"success": True, "message": "File deleted"}


@router.get("/files/{file_uuid}/download", response_model=None)
async def download_file(file_uuid: UUID):
    """Download file from the API"""

    file = await storage.get_file(file_uuid)
    if file is None:
        raise HTTPException(404, detail=f"File {file_uuid} not found")
    return FileResponse(file)
