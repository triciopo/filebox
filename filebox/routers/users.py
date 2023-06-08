from typing import Optional, Sequence

from fastapi import APIRouter, HTTPException

from filebox import storage
from filebox.core.auth import CurrentUser
from filebox.core.database import DBSession
from filebox.models.user import User
from filebox.schemas.user import UserBaseResponse, UserCreate, UserUpdate
from filebox.services import files as file_service
from filebox.services import folders as folder_service
from filebox.services import users as service

user_router = APIRouter()


@user_router.get("/users", response_model=list[UserBaseResponse])
async def get_users(
    current_user: CurrentUser,
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[User]:
    """Returns a list of all users"""
    if not current_user.is_super_user:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return await service.get_users(db, skip=skip, limit=limit)


@user_router.get("/users/me", response_model=UserBaseResponse)
async def get_me(current_user: CurrentUser) -> User:
    """Returns the currently logged in user"""
    return current_user


@user_router.get("/users/{user_id}", response_model=UserBaseResponse)
async def get_user(
    user_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> User:
    """Gets a single user by ID"""
    user = await service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if not current_user.is_super_user and user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@user_router.post("/users", status_code=201, response_model=UserBaseResponse)
async def create_user(user_in: UserCreate, db: DBSession) -> User:
    """Create a new user"""
    if await service.get_user_by_name(db, user_in.username):
        raise HTTPException(status_code=400, detail="User already exists")
    if await service.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already in use")
    user = await service.create_user(db, user_in)
    await folder_service.create_folder(db, "/", user.id, None)
    return user


@user_router.put("/users/{user_id}", response_model=UserBaseResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> Optional[User]:
    """Update an existing user by ID"""
    user = await service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if not current_user.is_super_user and user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await service.update_user(db, user_id, user_in)


@user_router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete a user by ID and all associated files from storage."""
    if not current_user.is_super_user and user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not await service.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    files = await file_service.get_files_by_id(db, user_id)
    files_uuid = [file.uuid for file in files]
    await storage.delete_files(files_uuid)
    await service.delete_user(db, user_id)

    return {"success": True, "message": "User deleted"}
