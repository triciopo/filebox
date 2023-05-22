import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    username: str
    email: EmailStr

    @validator("username")
    def username_validator(cls, name):
        if not name.isalnum():
            raise ValueError("Username must be alphanumeric")
        if len(name) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(name) > 20:
            raise ValueError("Username must be between 3 and 20 characters")

        return name


class UserCreate(UserBase):
    password: str

    @validator("password")
    def pass_required(cls, password):
        if not password:
            raise ValueError("Password is required")
        return password


class UserUpdate(UserBase):
    password: Optional[str]

    @validator("password")
    def pass_required(cls, password):
        if not password:
            raise ValueError("Password is required")
        return password


class UserBaseResponse(UserBase):
    id: int
    storage_space: int
    used_space: int
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
