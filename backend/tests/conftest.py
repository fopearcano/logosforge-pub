from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture()
def engine() -> Iterator[Engine]:
    # Shared single-connection in-memory SQLite so every Session sees the
    # same database (separate connections normally yield separate :memory:s).
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    import app.models  # noqa: F401  (register tables)

    SQLModel.metadata.create_all(eng)
    try:
        yield eng
    finally:
        SQLModel.metadata.drop_all(eng)
        eng.dispose()


@pytest.fixture()
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as s:
        yield s


@pytest.fixture()
def client(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    from app import db as db_module
    from app.main import app

    def _override_get_session() -> Iterator[Session]:
        with Session(engine) as s:
            yield s

    # Prevent lifespan from touching the configured engine / on-disk file.
    monkeypatch.setattr(db_module, "init_db", lambda: None)

    app.dependency_overrides[db_module.get_session] = _override_get_session
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
