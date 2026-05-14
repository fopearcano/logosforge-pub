from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


def _engine_kwargs() -> dict:
    kwargs: dict = {"echo": settings.database_echo}
    if settings.database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


engine: Engine = create_engine(settings.database_url, **_engine_kwargs())


def init_db() -> None:
    """Create database schema. Imports model modules so SQLModel sees them."""
    from app import models  # noqa: F401  (registers metadata)

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
