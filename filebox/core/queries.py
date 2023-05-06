from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from filebox.models.file import File


def get_file(db: Session, uuid: UUID):
    """Fetch a file by its uuid."""
    return db.query(File).filter(File.uuid == uuid).first()


def get_files(db: Session, skip: int = 0, limit: int = 100):
    """Fetch all files."""
    return db.query(File).offset(skip).limit(limit).all()


def create_file(db: Session, uuid: UUID, name: str, size: str, content_type: str):
    """Creates a file."""
    file = File(
        uuid=uuid,
        name=name,
        size=size,
        content_type=content_type,
        created_at=date.today(),
    )
    db.add(file)
    db.commit()


def delete_file(db: Session, uuid: UUID):
    """Deletes a file."""
    file = db.get(File, uuid)
    db.delete(file)
    db.commit()
