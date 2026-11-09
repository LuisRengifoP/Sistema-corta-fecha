from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM (SQLAlchemy 2.x)."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI: entrega una sesion y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
