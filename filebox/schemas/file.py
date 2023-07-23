import datetime

from pydantic import UUID4, BaseModel, ConfigDict

from filebox.schemas.types import FilePath


class FileBase(BaseModel):
    uuid: UUID4
    name: str
    path: FilePath
    folder_id: int
    size: int
    owner_id: int
    mime_type: str
    created_at: datetime.date


class FileBaseResponse(FileBase):
    model_config = ConfigDict(from_attributes=True)
