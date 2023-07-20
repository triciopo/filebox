import datetime
from typing import Annotated

from pydantic import UUID4, BaseModel, ConfigDict, constr

FilePath = Annotated[str, constr(min_length=1, max_length=96)]


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
