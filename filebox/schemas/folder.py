import datetime
from typing import Annotated, Optional, Union

from pydantic import BaseModel, ConfigDict, constr

from filebox.schemas.file import FileBaseResponse

FolderPath = Annotated[
    str,
    constr(pattern=r"^(?:\/(?:[\w\s]+\/)*[\w\s]+|\/)$", min_length=1, max_length=96),
]


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
