import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict

from filebox.schemas.file import FileBaseResponse
from filebox.schemas.types import FolderPath


class FolderBase(BaseModel):
    path: FolderPath


class FolderBaseResponse(FolderBase):
    model_config = ConfigDict(from_attributes=True)


class FolderCreate(FolderBase):
    pass


class FolderUpdate(FolderBase):
    pass


class FolderInDBBase(FolderBase):
    model_config = ConfigDict(from_attributes=True)


class FolderInDB(FolderInDBBase):
    id: int
    owner_id: int
    created_at: datetime.date
    parent_id: Optional[int] = None


class ListFolderResponse(BaseModel):
    folder: FolderBaseResponse
    items: dict[str, list[Union[FolderBaseResponse, FileBaseResponse]]]
