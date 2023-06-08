from datetime import date
from typing import Optional, Sequence

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from filebox.models.file import File
from filebox.models.folder import Folder


async def get_folders_by_user_id(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> Sequence[Folder]:
    """Fetch all folders of a user"""
    result = await db.execute(
        select(Folder).where(Folder.owner_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_subfolders_by_id(
    db: AsyncSession, folder_id: int, skip: int = 0, limit: int = 100
) -> Sequence[Folder]:
    """Fetch all subfolders of a folder"""
    result = await db.execute(
        select(Folder).where(Folder.parent_id == folder_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_folder_by_path(
    db: AsyncSession, path: str, user_id: int
) -> Optional[Folder]:
    """Fetch a folder by its path."""
    result = await db.execute(
        select(Folder).where(and_(Folder.owner_id == user_id, Folder.path == path))
    )
    return result.scalar_one_or_none()


async def create_folder(
    db: AsyncSession, path: str, owner_id: int, parent_id: Optional[int]
) -> Folder:
    """Creates a folder."""
    folder = Folder(
        path=path,
        owner_id=owner_id,
        parent_id=parent_id,
        created_at=date.today(),
    )
    db.add(folder)
    await db.commit()

    return folder


async def create_parent_folders(
    db: AsyncSession, directories: list, user_id: int, parent_id: int
) -> int:
    """Creates a list of parent folders."""
    for directory in directories:
        parent_path = "/".join(directories[: directories.index(directory)])
        if parent_path:
            parent_path_folder = await get_folder_by_path(db, parent_path, user_id)
            if not parent_path_folder:
                new_folder = await create_folder(db, parent_path, user_id, parent_id)
                parent_id = int(new_folder.id)
            else:
                parent_id = int(parent_path_folder.id)
    return parent_id


async def delete_folder(db: AsyncSession, path: str, user_id: int) -> None:
    """Deletes a folder."""
    folder = await get_folder_by_path(db, path, user_id)
    if folder:
        await db.delete(folder)
        await db.commit()


async def get_files_by_folder_recursive(db: AsyncSession, folder_id: int) -> list:
    """Recursively fetch all files of a folder and its subfolders"""
    files_query = select(File).where(File.folder_id == folder_id)
    files_result = await db.execute(files_query)
    files = list(files_result.scalars().all())

    subfolder_query = select(Folder).where(Folder.parent_id == folder_id)
    subfolder_result = await db.execute(subfolder_query)
    subfolder_ids = subfolder_result.scalars().all()

    subfolder_files = []
    for subfolder in subfolder_ids:
        subfolder_files.extend(
            await get_files_by_folder_recursive(db, int(subfolder.id))
        )

    files.extend(subfolder_files)

    return files
