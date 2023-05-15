from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from filebox.core import queries
from filebox.core.auth import get_current_user
from filebox.core.database import get_db
from filebox.models.user import User
from filebox.schemas.user import UserBaseResponse, UserCreate, UserUpdate

user_router = APIRouter()


@user_router.get("/users", response_model=list[UserBaseResponse])
def get_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.is_super_user:
        return queries.get_users(db)
    raise HTTPException(status_code=401, detail="Not authenticated")


@user_router.get("/users/{user_id}", response_model=UserBaseResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = queries.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if user_id == current_user.id or current_user.is_super_user:
        return user
    raise HTTPException(status_code=404, detail=f"User {user_id} not found")


@user_router.post("/users/create", status_code=201, response_model=UserBaseResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if queries.get_user_by_name(db, user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    if queries.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already in use")
    return queries.create_user(db, user)


@user_router.put("/users/{user_id}", response_model=UserBaseResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = queries.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if current_user.is_super_user or current_user.id == user_id:
        return queries.update_user(db, user_id, user_in)
    raise HTTPException(status_code=401, detail="Not authenticated")


@user_router.delete("/users/{user_id}")
def delete_user(
    user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user.is_super_user:
        if not queries.get_user(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")
        queries.delete_user(db, user_id)
        return {"success": True, "message": "User deleted"}

    raise HTTPException(status_code=401, detail="Not authenticated")
