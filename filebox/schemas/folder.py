import datetime
from typing import Optional

from pydantic import BaseModel, ConstrainedStr


class FolderPath(ConstrainedStr):
    regex = "^(?:\/(?:[\w\s]+\/)*[\w\s]+|\/)$"
    min_length = 1
    max_length = 96


class FolderBase(BaseModel):
    path: FolderPath


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
    parent_id: Optional[int]
