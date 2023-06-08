import re
from datetime import date
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from filebox.models.file import File
from filebox.services import users


async def get_file(db: AsyncSession, uuid: UUID) -> Optional[File]:
    """Fetch a file by its uuid."""
    return await db.get(File, uuid)


async def get_files_by_id(
    db: AsyncSession, id: int, skip: int = 0, limit: int = 100
) -> Sequence[File]:
    """Fetch all files from a user"""
    result = await db.execute(
        select(File).where(File.owner_id == id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_files_by_folder_id(
    db: AsyncSession, folder_id: int, skip: int = 0, limit: int = 100
) -> Sequence[File]:
    """Fetch all files of a folder"""
    result = await db.execute(
        select(File).where(File.folder_id == folder_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_file_by_path(db: AsyncSession, path: str, user_id: int) -> Optional[File]:
    """Fetch a file by its path."""
    result = await db.execute(
        select(File).where(and_(File.owner_id == user_id, File.path == path))
    )
    return result.scalar_one_or_none()


async def create_file(
    db: AsyncSession,
    uuid: UUID,
    name: str,
    path: str,
    folder_id: int,
    size: int,
    owner_id: int,
    mime_type: str,
) -> File:
    """Creates a file."""
    user = await users.get_user(db, owner_id)
    if user:
        user.used_space += size

    file = File(
        uuid=uuid,
        name=name,
        path=path,
        folder_id=folder_id,
        size=size,
        owner_id=owner_id,
        mime_type=mime_type,
        created_at=date.today(),
    )
    db.add(file)
    await db.commit()

    return file


async def create_batch_files(
    db: AsyncSession,
    files: Sequence,
    file_path: str,
    sizes: list[int],
    uuids: list,
    folder: int,
    user_id: int,
) -> list[File]:
    """Creates a list of files."""
    uploaded_files = []
    created_files = []
    for file, size, uuid in zip(files, sizes, uuids):
        name = file.filename
        filename = re.sub(r'[\\/:"*?<>|]', "", name)
        path = f"{file_path.rstrip('/')}/{filename}"
        if await get_file_by_path(db, path, user_id):
            raise HTTPException(status_code=409, detail=f"{path} already exists")
        mime = file.content_type or "application/octet-stream"
        uploaded_files.append((uuid, name, path, folder, size, user_id, mime))

    for file_data in uploaded_files:
        created_file = await create_file(db, *file_data)
        created_files.append(created_file)

    return created_files


async def delete_file(db: AsyncSession, uuid: UUID) -> None:
    """Deletes a file."""
    file = await get_file(db, uuid)
    if file:
        user = await users.get_user(db, int(file.owner_id))
        if user:
            user.used_space -= file.size or 0
            await db.delete(file)
            await db.commit()
