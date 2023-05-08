import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    username: str
    created_at: datetime.date


class UserCreate(UserBase):
    password: str


class UserBaseResponse(UserBase):
    class Config:
        orm_mode = True


class UserInDBBase(UserBase):
    class Config:
        orm_mode = True


class UserInDB(UserInDBBase):
    hashed_password: str
