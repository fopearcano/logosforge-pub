from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import WorkflowStatus
from app.schemas._common import TimestampedRead


class ManuscriptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    synopsis: Optional[str] = None
    genre: Optional[str] = Field(default=None, max_length=100)
    language: str = Field(default="en", max_length=10)
    word_count: Optional[int] = Field(default=None, ge=0)
    status: WorkflowStatus = Field(default=WorkflowStatus.SUBMITTED)
    author_id: str


class ManuscriptUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    synopsis: Optional[str] = None
    genre: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, max_length=10)
    word_count: Optional[int] = Field(default=None, ge=0)
    status: Optional[WorkflowStatus] = None


class ManuscriptRead(TimestampedRead):
    title: str
    subtitle: Optional[str]
    synopsis: Optional[str]
    genre: Optional[str]
    language: str
    word_count: Optional[int]
    status: WorkflowStatus
    author_id: str
