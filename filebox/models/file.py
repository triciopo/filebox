import uuid
from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Uuid

from filebox.core.database import Base


class File(Base):
    __tablename__ = "files"
    uuid = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    path = Column(String)
    folder_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"))
    size = Column(Integer)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_type = Column(String)
    created_at = Column(Date(), default=date.today())
