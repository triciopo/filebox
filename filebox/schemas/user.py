import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserBase(BaseModel):
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
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

    @field_validator("password")
    @classmethod
    def pass_required(cls, password):
        if not password:
            raise ValueError("Password is required")
        return password


class UserUpdate(UserBase):
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def pass_required(cls, password):
        if not password:
            raise ValueError("Password is required")
        return password


class UserBaseResponse(UserBase):
    id: int
    storage_space: int
    used_space: int
    created_at: datetime.date
    model_config = ConfigDict(from_attributes=True)


class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserInDBBase):
    id: int
    hashed_password: str
    is_super_user: bool = False
