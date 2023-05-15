import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    username: str
    email: EmailStr

    @validator("username")
    def username_required(cls, v):
        if not v:
            raise ValueError("Username is required")
        return v


class UserCreate(UserBase):
    password: str

    @validator("password")
    def pass_required(cls, v):
        if not v:
            raise ValueError("Password is required")
        return v


class UserUpdate(UserBase):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

    @validator("password")
    def pass_required(cls, v):
        if not v:
            raise ValueError("Password is required")
        return v


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
