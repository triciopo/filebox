from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from filebox.core.config import settings


def get_db_url(env):
    if env == "tests":
        return "sqlite:///./test.db"
    return f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"


SQLALCHEMY_DATABASE_URL = get_db_url(settings.ENV)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()
