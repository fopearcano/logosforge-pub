from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas._common import TimestampedRead


class AuthorCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    biography: Optional[str] = None


class AuthorUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    biography: Optional[str] = None


class AuthorRead(TimestampedRead):
    full_name: str
    email: Optional[str]
    country: Optional[str]
    biography: Optional[str]
