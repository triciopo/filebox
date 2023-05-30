import datetime
from uuid import UUID

from pydantic import BaseModel, ConstrainedStr


class FilePath(ConstrainedStr):
    min_length = 1
    max_length = 96


class FileBase(BaseModel):
    uuid: UUID
    name: str
    path: FilePath
    folder_id: int
    size: int
    owner_id: int
    mime_type: str
    created_at: datetime.date


class FileBaseResponse(FileBase):
    class Config:
        orm_mode = True
