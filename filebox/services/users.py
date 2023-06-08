from datetime import date
from typing import Optional, Sequence

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import filebox.core.auth as auth
from filebox.models.file import File
from filebox.models.user import User
from filebox.schemas.user import UserCreate, UserUpdate


async def get_user(db: AsyncSession, id: int) -> Optional[User]:
    """Fetch a user by its id."""
    result = await db.execute(select(User).where(User.id == id))
    return result.scalar_one_or_none()


async def get_user_by_name(db: AsyncSession, username: str) -> Optional[User]:
    """Fetch a user by its name."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Fetch a user by its email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[User]:
    """Fetch all users."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user_used_space(db: AsyncSession, id: int) -> int:
    """Fetch the used storage space of a user"""
    result = await db.execute(select(func.sum(File.size)).where(File.owner_id == id))
    return result.scalar_one() or 0


async def create_user(db: AsyncSession, usr: UserCreate) -> User:
    """Creates a user."""
    user = User(
        username=usr.username,
        hashed_password=auth.get_hashed_password(usr.password),
        email=usr.email,
        created_at=date.today(),
    )
    db.add(user)
    await db.commit()

    return user


async def update_user(db: AsyncSession, id: int, usr: UserUpdate) -> Optional[User]:
    """Updates a user."""
    user = await get_user(db, id)
    if user:
        if usr.username:
            user.username = usr.username
        if usr.password:
            user.hashed_password = auth.get_hashed_password(usr.password)
        if usr.email:
            user.email = usr.email
        await db.commit()

    return user


async def delete_user(db: AsyncSession, id: int) -> None:
    """Deletes a user."""
    user = await get_user(db, id)
    if user:
        await db.delete(user)
        await db.commit()
