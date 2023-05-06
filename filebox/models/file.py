import uuid
from datetime import date

from sqlalchemy import Column, Date, Integer, String, Uuid

from filebox.core.database import Base


class File(Base):
    __tablename__ = "files"
    uuid = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    size = Column(Integer)
    content_type = Column(String)
    created_at = Column(Date(), default=date.today())
