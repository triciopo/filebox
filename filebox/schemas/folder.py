import datetime
from typing import Annotated

from pydantic import BaseModel, Field

path_regex = Annotated[
    str,
    Field(regex="^(?:\/(?:[\w\s]+\/)*[\w\s]+|\/)$", min_length=1, max_length=96),
]


class FolderBase(BaseModel):
    path: path_regex


class FolderBaseResponse(FolderBase):
    class Config:
        orm_mode = True


class FolderCreate(FolderBase):
    pass


class FolderUpdate(FolderBase):
    pass


class FolderInDBBase(FolderBase):
    class Config:
        orm_mode = True


class FolderInDB(FolderInDBBase):
    id: int
    owner_id: int
    created_at: datetime.date
    parent_id: int
