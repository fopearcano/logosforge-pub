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


def _make_user(session: Session, *, email: str, role):
    from app.auth.security import hash_password
    from app.models import User

    user = User(
        email=email,
        full_name=email.split("@")[0].replace(".", " ").title(),
        role=role,
        hashed_password=hash_password("password"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _token_for(user) -> str:
    from app.auth.security import create_access_token

    token, _ = create_access_token(subject=user.id, role=user.role.value)
    return token


@pytest.fixture()
def admin_user(session: Session):
    from app.models import UserRole

    return _make_user(session, email="admin@logosforge.test", role=UserRole.ADMIN)


@pytest.fixture()
def editor_user(session: Session):
    from app.models import UserRole

    return _make_user(session, email="editor@logosforge.test", role=UserRole.EDITOR)


@pytest.fixture()
def admin_token(admin_user) -> str:
    return _token_for(admin_user)


@pytest.fixture()
def editor_token(editor_user) -> str:
    return _token_for(editor_user)


def _build_client(
    engine: Engine, monkeypatch: pytest.MonkeyPatch, *, token: str | None
) -> Iterator[TestClient]:
    """Build a fresh TestClient bound to the test engine, optionally authenticated.

    Each invocation produces an independent TestClient so callers requesting
    multiple role-specific clients in one test don't trample each other's
    Authorization header.
    """
    from app import db as db_module
    from app.main import app

    def _override() -> Iterator[Session]:
        with Session(engine) as s:
            yield s

    monkeypatch.setattr(db_module, "init_db", lambda: None)
    app.dependency_overrides[db_module.get_session] = _override

    with TestClient(app) as c:
        if token:
            c.headers["Authorization"] = f"Bearer {token}"
        yield c

    # Other client fixtures in the same test may still be active; only the
    # last one to tear down should clear the overrides.
    app.dependency_overrides.pop(db_module.get_session, None)


@pytest.fixture()
def anon_client(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    yield from _build_client(engine, monkeypatch, token=None)


@pytest.fixture()
def client(
    engine: Engine, monkeypatch: pytest.MonkeyPatch, admin_token: str
) -> Iterator[TestClient]:
    yield from _build_client(engine, monkeypatch, token=admin_token)


@pytest.fixture()
def editor_client(
    engine: Engine, monkeypatch: pytest.MonkeyPatch, editor_token: str
) -> Iterator[TestClient]:
    yield from _build_client(engine, monkeypatch, token=editor_token)
