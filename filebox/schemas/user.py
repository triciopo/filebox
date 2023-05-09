import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserBaseResponse(UserBase):
    id: int
    created_at: datetime.date

    class Config:
        orm_mode = True


class UserInDBBase(UserBase):
    class Config:
        orm_mode = True


class UserInDB(UserInDBBase):
    id: int
    hashed_password: str
    is_super_user: bool = False
