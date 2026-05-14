from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


def page_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
) -> PageParams:
    return PageParams(skip=skip, limit=limit)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
