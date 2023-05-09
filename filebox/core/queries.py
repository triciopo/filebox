from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from filebox.core.auth import get_hashed_password
from filebox.models.file import File
from filebox.models.user import User
from filebox.schemas.user import UserCreate


def get_file(db: Session, uuid: UUID):
    """Fetch a file by its uuid."""
    return db.query(File).filter(File.uuid == uuid).first()


def get_files(db: Session, skip: int = 0, limit: int = 100):
    """Fetch all files."""
    return db.query(File).offset(skip).limit(limit).all()


def get_files_by_id(db: Session, id: int, skip: int = 0, limit: int = 100):
    """Fetch all files from a user"""
    return db.query(File).filter(File.owner_id == id).offset(skip).limit(limit).all()


def create_file(
    db: Session, uuid: UUID, name: str, size: str, owner_id: int, content_type: str
):
    """Creates a file."""
    file = File(
        uuid=uuid,
        name=name,
        size=size,
        owner_id=owner_id,
        content_type=content_type,
        created_at=date.today(),
    )
    db.add(file)
    db.commit()

    return file


def delete_file(db: Session, uuid: UUID):
    """Deletes a file."""
    file = db.get(File, uuid)
    db.delete(file)
    db.commit()


def delete_all_files(db: Session, id: int, skip: int = 0, limit: int = 100):
    """Deletes all files belonging to an ID."""
    files = db.query(File).filter(File.owner_id == id).all()
    for file in files:
        db.delete(file)
    db.commit()


def get_user(db: Session, id: int):
    """Fetch a user by its id."""
    return db.query(User).filter(User.id == id).first()


def get_user_by_name(db: Session, username: str):
    """Fetch a user by its name."""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Fetch all users."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, usr: UserCreate):
    """Creates a user."""
    user = User(
        username=usr.username,
        hashed_password=get_hashed_password(usr.password),
        created_at=date.today(),
    )
    db.add(user)
    db.commit()

    return user


def delete_user(db: Session, id: int):
    """Deletes a user."""
    user = db.get(User, id)
    db.delete(user)
    db.commit()
