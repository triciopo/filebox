from datetime import date
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from filebox.core.auth import get_hashed_password
from filebox.models.file import File
from filebox.models.folder import Folder
from filebox.models.user import User
from filebox.schemas.user import UserCreate, UserUpdate


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
    db: Session,
    uuid: UUID,
    name: str,
    path: str,
    folder_id: int,
    size: int,
    owner_id: int,
    content_type: str,
):
    """Creates a file."""
    user = get_user(db, owner_id)
    user.used_space += size

    file = File(
        uuid=uuid,
        name=name,
        path=path,
        folder_id=folder_id,
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
    file = get_file(db, uuid)
    user = get_user(db, file.owner_id)
    user.used_space -= file.size
    db.delete(file)
    db.commit()


def get_user(db: Session, id: int):
    """Fetch a user by its id."""
    return db.query(User).filter(User.id == id).first()


def get_user_by_name(db: Session, username: str):
    """Fetch a user by its name."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """Fetch a user by its email."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Fetch all users."""
    return db.query(User).offset(skip).limit(limit).all()


def get_user_used_space(db: Session, id: int):
    """Fetch the used storage space of a user"""
    return (
        db.query(File)
        .filter(File.owner_id == id)
        .with_entities(func.coalesce(func.sum(File.size), 0))
        .scalar()
    )


def create_user(db: Session, usr: UserCreate):
    """Creates a user."""
    user = User(
        username=usr.username,
        hashed_password=get_hashed_password(usr.password),
        email=usr.email,
        created_at=date.today(),
    )
    db.add(user)
    db.commit()

    return user


def update_user(db: Session, id: int, usr: UserUpdate):
    """Updates a user."""
    user = get_user(db, id)
    if usr.username:
        user.username = usr.username
    if usr.password:
        user.hashed_password = get_hashed_password(usr.password)
    if usr.email:
        user.email = usr.email
    db.commit()

    return user


def delete_user(db: Session, id: int):
    """Deletes a user."""
    user = db.get(User, id)
    db.delete(user)
    db.commit()


def get_folders_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Fetch all folders of a user"""
    return (
        db.query(Folder)
        .filter(Folder.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_subfolders_by_id(db: Session, folder_id: int, skip: int = 0, limit: int = 100):
    """Fetch all subfolders of a folder"""
    return (
        db.query(Folder)
        .filter(Folder.parent_id == folder_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_files_by_folder_id(
    db: Session, folder_id: int, skip: int = 0, limit: int = 100
):
    """Fetch all files of a folder"""
    return (
        db.query(File)
        .filter(File.folder_id == folder_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_file_by_path(db: Session, path: str, user_id):
    """Fetch a file by its path."""
    return (
        db.query(File)
        .filter(File.owner_id == user_id)
        .filter(File.path == path)
        .first()
    )


def get_folder_by_path(db: Session, path: str, user_id: int):
    """Fetch a folder by its path."""
    return (
        db.query(Folder)
        .filter(Folder.owner_id == user_id)
        .filter(Folder.path == path)
        .first()
    )


def create_folder(db: Session, path: str, owner_id: int, parent_id: int):
    """Creates a folder."""
    folder = Folder(
        path=path,
        owner_id=owner_id,
        parent_id=parent_id,
        created_at=date.today(),
    )
    db.add(folder)
    db.commit()

    return folder


def delete_folder(db: Session, path: str, user_id: int):
    """Deletes a folder."""
    folder = get_folder_by_path(db, path, user_id)
    db.delete(folder)
    db.commit()
