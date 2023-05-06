import datetime
from uuid import UUID

from pydantic import BaseModel


class FileBase(BaseModel):
    uuid: UUID
    name: str
    size: int
    content_type: str
    created_at: datetime.date


class FileBaseResponse(FileBase):
    class Config:
        orm_mode = True
