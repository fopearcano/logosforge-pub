from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import EditorialNoteKind
from app.schemas._common import TimestampedRead


class EditorialNoteCreate(BaseModel):
    manuscript_id: str
    author_user_id: str
    kind: EditorialNoteKind = EditorialNoteKind.GENERAL
    body: str = Field(min_length=1)
    pinned: bool = False


class EditorialNoteUpdate(BaseModel):
    kind: Optional[EditorialNoteKind] = None
    body: Optional[str] = Field(default=None, min_length=1)
    pinned: Optional[bool] = None


class EditorialNoteRead(TimestampedRead):
    manuscript_id: str
    author_user_id: str
    kind: EditorialNoteKind
    body: str
    pinned: bool
