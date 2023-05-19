from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from filebox import storage
from filebox.core import queries
from filebox.core.auth import get_current_user
from filebox.core.database import get_db
from filebox.models.user import User
from filebox.schemas.user import UserBaseResponse, UserCreate, UserUpdate

user_router = APIRouter()


@user_router.get("/users", response_model=list[UserBaseResponse])
def get_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns a list of all users"""
    if not user.is_super_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return queries.get_users(db)


@user_router.get("/users/me", response_model=UserBaseResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently logged in user"""
    return current_user


@user_router.get("/users/{user_id}", response_model=UserBaseResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gets a single user by ID"""
    user = queries.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if not current_user.is_super_user and user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@user_router.post("/users/create", status_code=201, response_model=UserBaseResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    if queries.get_user_by_name(db, user_in.username):
        raise HTTPException(status_code=400, detail="User already exists")
    if queries.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already in use")
    return queries.create_user(db, user_in)


@user_router.put("/users/{user_id}", response_model=UserBaseResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing user by ID"""
    user = queries.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if not current_user.is_super_user and user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return queries.update_user(db, user_id, user_in)


@user_router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a user by ID and all associated files from storage."""
    if not current_user.is_super_user and user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not queries.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    files = queries.get_files_by_id(db, user_id)
    files_uuid = [file.uuid for file in files]
    await storage.delete_files(files_uuid)
    queries.delete_all_files(db, user_id)
    queries.delete_user(db, user_id)

    return {"success": True, "message": "User deleted"}
