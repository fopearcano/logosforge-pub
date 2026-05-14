from __future__ import annotations

from typing import TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.sql import Select
from sqlmodel import Session, SQLModel, select

from app.utils.pagination import PageParams

ModelT = TypeVar("ModelT", bound=SQLModel)


def get_or_404(session: Session, model: type[ModelT], id: str, *, name: str | None = None) -> ModelT:
    obj = session.get(model, id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name or model.__name__} not found",
        )
    return obj


def ensure_exists(session: Session, model: type[SQLModel], id: str, *, name: str | None = None) -> None:
    if session.get(model, id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name or model.__name__} not found",
        )


def paginate(
    session: Session,
    stmt: Select,
    params: PageParams,
) -> tuple[list, int]:
    total = session.exec(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    ).one()
    items = list(session.exec(stmt.offset(params.skip).limit(params.limit)).all())
    return items, total


def apply_patch(obj: SQLModel, payload: BaseModel) -> None:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
