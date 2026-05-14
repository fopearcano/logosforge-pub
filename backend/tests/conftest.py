from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture()
def engine() -> Iterator[Engine]:
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
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
