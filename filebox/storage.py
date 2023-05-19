import asyncio
from pathlib import Path
from uuid import UUID

import aiofiles
import aioshutil
from fastapi import HTTPException, UploadFile

from filebox.core.config import settings

STORAGE_DIR = settings.STORAGE_DIR


async def upload_file(uuid: UUID, file: UploadFile):
    file_size = 0
    file_path = f"{STORAGE_DIR}{uuid}/{uuid}{Path(file.filename).suffix}"
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(10485760):  # 10MB
                file_size += len(chunk)
                if file_size >= settings.SIZE_LIMIT:
                    raise HTTPException(status_code=413)
                await f.write(chunk)
    except OSError:
        raise HTTPException(status_code=500)


async def get_file(uuid: UUID):
    file_path = Path(f"{STORAGE_DIR}{uuid}")
    for file in file_path.glob("*"):
        if Path(file).exists():
            return file
    return None


async def get_file_size(file: UploadFile):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)

    return file_size


async def delete_file(uuid: UUID):
    await aioshutil.rmtree(f"{STORAGE_DIR}{uuid}")


async def delete_files(files: list[UUID]):
    delete_tasks = [delete_file(file) for file in files]
    await asyncio.gather(*delete_tasks)
