from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


database_url = (
    "mysql+pymysql://"
    f"{quote_plus(settings.db_user)}:"
    f"{quote_plus(settings.db_password)}@"
    f"{settings.db_host}:{settings.db_port}/"
    f"{quote_plus(settings.db_name)}"
    "?charset=utf8mb4"
)

engine = create_engine(
    database_url,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_database():
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()