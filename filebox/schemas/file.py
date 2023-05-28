import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

path_regex = Annotated[
    str,
    Field(regex="^\/(?:[\w\s]+\/)*[\w\s]+\.\w+$", min_length=1, max_length=96),
]


class FileBase(BaseModel):
    uuid: UUID
    name: str
    path: path_regex
    folder_id: int
    size: int
    owner_id: int
    content_type: str
    created_at: datetime.date


class FileBaseResponse(FileBase):
    class Config:
        orm_mode = True
