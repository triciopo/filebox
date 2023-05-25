import asyncio
from pathlib import Path
from typing import Optional
from uuid import UUID

import aiofiles.os
import aioshutil
from fastapi import HTTPException, UploadFile

from filebox.core.config import settings

STORAGE_DIR = settings.STORAGE_DIR


async def upload_file(uuid: UUID, file: UploadFile) -> None:
    """Upload a file to the storage"""
    file_path = f"{STORAGE_DIR}{uuid}/{uuid}{Path(str(file.filename)).suffix}"
    Path(f"{STORAGE_DIR}{uuid}").mkdir(parents=True, exist_ok=True)
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(10485760):  # 10MB
                await f.write(chunk)
    except OSError:
        raise HTTPException(status_code=500)


async def upload_files(uuids: list[UUID], files: list[UploadFile]) -> None:
    """Upload a list of files concurrently"""
    upload_tasks = [upload_file(uuid, file) for uuid, file in zip(uuids, files)]
    await asyncio.gather(*upload_tasks)


async def get_file(uuid: UUID) -> Optional[Path]:
    """Given a UUID, returns the Path of a file with that UUID in the storage"""
    file_path = Path(f"{STORAGE_DIR}{uuid}")
    for file in file_path.glob("*"):
        if Path(file).exists():
            return file
    return None


async def get_file_size(file: UploadFile) -> int:
    """Get the size of a file in bytes"""
    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)

    return file_size


async def get_files_size(files: list[UploadFile]) -> list[int]:
    tasks = [get_file_size(file) for file in files]
    sizes = await asyncio.gather(*tasks)

    return sizes


async def delete_file(uuid: UUID) -> None:
    """Deletes a file with the specified UUID"""
    await aioshutil.rmtree(f"{STORAGE_DIR}{uuid}")


async def delete_files(files: list[UUID]) -> None:
    """Deletes a list of files using the specified UUIDs"""
    delete_tasks = [delete_file(file) for file in files]
    await asyncio.gather(*delete_tasks)
