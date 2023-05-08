from datetime import date

from sqlalchemy import Column, Date, Integer, String

from filebox.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    created_at = Column(Date(), default=date.today())
