from datetime import date

from sqlalchemy import Boolean, Column, Date, Integer, String

from filebox.core.config import settings
from filebox.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    email = Column(String)
    is_super_user = Column(Boolean, default=False)
    created_at = Column(Date(), default=date.today())
    storage_space = Column(Integer, default=settings.DEFAULT_STORAGE_SPACE)
    used_space = Column(Integer, default=0)
