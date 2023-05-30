from datetime import date
import re
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
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


def create_file(
    db: Session,
    uuid: UUID,
    name: str,
    path: str,
    folder_id: int,
    size: int,
    owner_id: int,
    mime_type: str,
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
        mime_type=mime_type,
        created_at=date.today(),
    )
    db.add(file)
    db.commit()

    return file


def create_batch_files(
    db: Session,
    files: list,
    file_path: str,
    size: list[int],
    uuids: list,
    folder: int,
    usr_id: int,
):
    """Creates a list of files."""
    uploaded_files = []
    for i, file in enumerate(files):
        path = (
            file_path.rstrip("/")
            + "/"
            + str(re.sub(r'[\\/:"*?<>|]', "", file.filename))
        )
        if get_file_by_path(db, path, usr_id):
            raise HTTPException(status_code=409, detail=f"File {path} already exists")
        mime = file.content_type or "application/octet-stream"
        uploaded_files.append(
            create_file(
                db, uuids[i], file.filename, path, folder, size[i], usr_id, mime
            )
        )
    return uploaded_files


def delete_file(db: Session, uuid: UUID):
    """Deletes a file."""
    file = get_file(db, uuid)
    user = get_user(db, file.owner_id)
    user.used_space -= file.size
    db.delete(file)
    db.commit()


def get_files_by_folder_recursive(db: Session, folder_id: int):
    """Recursively fetch all files of a folder and its subfolders"""
    files = db.query(File).filter(File.folder_id == folder_id).all()
    subfolder_ids = db.query(Folder.id).filter(Folder.parent_id == folder_id).all()

    for (subfolder_id,) in subfolder_ids:
        subfolder_files = get_files_by_folder_recursive(db, subfolder_id)
        files.extend(subfolder_files)

    return files


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


def get_folder_by_path(db: Session, path: str, user_id: int):
    """Fetch a folder by its path."""
    return (
        db.query(Folder)
        .filter(Folder.owner_id == user_id)
        .filter(Folder.path == path)
        .first()
    )


def create_folder(db: Session, path: str, owner_id: int, parent_id: Optional[int]):
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


def create_parent_folders(db: Session, directories, user_id: int, parent_id: int):
    """Creates a list of parent folders."""
    for directory in directories:
        parent_path = "/".join(directories[: directories.index(directory)])
        if parent_path:
            parent_path_folder = get_folder_by_path(db, parent_path, user_id)
            if not parent_path_folder:
                new_folder = create_folder(db, parent_path, user_id, parent_id)
                parent_id = new_folder.id
            else:
                parent_id = parent_path_folder.id
    return parent_id


def delete_folder(db: Session, path: str, user_id: int):
    """Deletes a folder."""
    folder = get_folder_by_path(db, path, user_id)
    db.delete(folder)
    db.commit()
