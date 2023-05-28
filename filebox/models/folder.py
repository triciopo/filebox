from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String

from filebox.core.database import Base


class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    created_at = Column(Date(), default=date.today())
