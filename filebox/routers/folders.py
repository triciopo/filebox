from fastapi import APIRouter, HTTPException

from filebox import storage
from filebox.core import queries
from filebox.core.auth import CurrentUser
from filebox.core.database import DBSession
from filebox.schemas.folder import FolderBaseResponse, FolderCreate, FolderPath

folder_router = APIRouter()


@folder_router.get("/folders", response_model=list[FolderBaseResponse])
def get_folders(
    current_user: CurrentUser,
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
) -> list[FolderBaseResponse]:
    """Fetch all folders"""
    return queries.get_folders_by_user_id(
        db,
        int(current_user.id),
        skip=skip,
        limit=limit,
    )


@folder_router.get("/folders{folder_path:path}", response_model=None)
def get_folder(
    folder_path: FolderPath,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Fetch a folder given a path"""
    folder = queries.get_folder_by_path(db, folder_path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    if folder.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Folder not found")
    subfolders = queries.get_subfolders_by_id(db, folder.id)
    files = queries.get_files_by_folder_id(db, folder.id)
    return {"folder": folder, "items": {"folders": subfolders, "files": files}}


@folder_router.post("/folders", status_code=201, response_model=FolderBaseResponse)
def create_folder(
    folder: FolderCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> FolderBaseResponse:
    """Create a new folder"""
    if queries.get_folder_by_path(db, folder.path, int(current_user.id)):
        raise HTTPException(status_code=409, detail="Folder already exists")

    # Remove spaces between slashes and split the path into individual directories
    cleaned_path = "/".join(word.strip() for word in folder.path.split("/"))
    directories = cleaned_path.split("/")
    parent_id = queries.get_folder_by_path(db, "/", int(current_user.id)).id

    id = queries.create_parent_folders(db, directories, int(current_user.id), parent_id)
    return queries.create_folder(db, cleaned_path, int(current_user.id), id)


@folder_router.delete("/folders{folder_path:path}", response_model=None)
async def delete_folder(
    folder_path: FolderPath,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete a folder"""
    folder = queries.get_folder_by_path(db, folder_path, int(current_user.id))
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    if folder.path == "/":
        raise HTTPException(status_code=404, detail="Cannot delete root folder")
    files = queries.get_files_by_folder_recursive(db, folder.id)
    files_to_delete = [file.uuid for file in files] if files else []

    queries.delete_folder(db, folder_path, int(current_user.id))
    await storage.delete_files(files_to_delete)
    return {"success": True, "message": "Folder deleted"}
