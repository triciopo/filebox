from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from filebox.core import queries
from filebox.core.database import get_db
from filebox.schemas.user import UserBaseResponse, UserCreate

user_router = APIRouter()


@user_router.get("/users", response_model=list[UserBaseResponse])
async def get_users(db: Session = Depends(get_db)):
    return queries.get_users(db)


@user_router.get("/users/{user_id}", response_model=UserBaseResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = queries.get_user(db, user_id)
    if not user:
        raise HTTPException(404, detail=f"User {user_id} not found")
    return user


@user_router.post("/users/create", status_code=201, response_model=UserBaseResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if queries.get_user_by_name(db, user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    return queries.create_user(db, user)


@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not queries.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    queries.delete_user(db, user_id)
    return {"success": True, "message": "User deleted"}
