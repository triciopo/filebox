from typing import Sequence

from fastapi import APIRouter, HTTPException

from filebox import storage
from filebox.core.auth import CurrentUser
from filebox.core.database import DBSession
from filebox.models.folder import Folder
from filebox.schemas.folder import (
    FolderBaseResponse,
    FolderCreate,
    FolderPath,
    ListFolderResponse,
)
from filebox.services import files as file_service
from filebox.services import folders as service

folder_router = APIRouter()


@folder_router.get("/folders", response_model=list[FolderBaseResponse])
async def get_folders(
    current_user: CurrentUser,
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Folder]:
    """Fetch all folders"""
    return await service.get_folders_by_user_id(
        db, int(current_user.id), skip=skip, limit=limit
    )


@folder_router.get("/folders{path:path}", response_model=ListFolderResponse)
async def get_folder(
    path: FolderPath,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, object]:
    """Fetch a folder given a path"""
    folder = await service.get_folder_by_path(db, path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    subfolders = await service.get_subfolders_by_id(db, folder.id)
    files = await file_service.get_files_by_folder_id(db, folder.id)
    return {"folder": folder, "items": {"folders": subfolders, "files": files}}


@folder_router.post("/folders", status_code=201, response_model=FolderBaseResponse)
async def create_folder(
    folder: FolderCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> FolderBaseResponse:
    """Create a new folder"""
    if await service.get_folder_by_path(db, folder.path, int(current_user.id)):
        raise HTTPException(status_code=409, detail="Folder already exists")

    # Remove spaces between slashes and split the path into individual directories
    cleaned_path = "/".join(word.strip() for word in folder.path.split("/"))
    directories = cleaned_path.split("/")
    parent = await service.get_folder_by_path(db, "/", int(current_user.id))

    id = await service.create_parent_folders(
        db, directories, int(current_user.id), parent.id
    )
    return await service.create_folder(db, cleaned_path, int(current_user.id), id)


@folder_router.delete("/folders{path:path}")
async def delete_folder(
    path: FolderPath,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete a folder"""
    folder = await service.get_folder_by_path(db, path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    if folder.path == "/":
        raise HTTPException(status_code=403, detail="Cannot delete root folder")
    files = await service.get_files_by_folder_recursive(db, folder.id)
    files_to_delete = [file.uuid for file in files] if files else []

    await service.delete_folder(db, path, int(current_user.id))
    await storage.delete_files(files_to_delete)
    return {"success": True, "message": "Folder deleted"}
