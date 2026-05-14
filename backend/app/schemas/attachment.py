from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import AttachmentKind
from app.schemas._common import TimestampedRead


class AttachmentPlaceholderCreate(BaseModel):
    """Create a metadata-only attachment record (no bytes on disk)."""

    manuscript_id: str
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(default="application/octet-stream", max_length=120)
    size_bytes: int = Field(default=0, ge=0)
    kind: AttachmentKind = AttachmentKind.OTHER
    description: Optional[str] = None


class AttachmentUpdate(BaseModel):
    kind: Optional[AttachmentKind] = None
    description: Optional[str] = None
    filename: Optional[str] = Field(default=None, min_length=1, max_length=255)


class AttachmentRead(TimestampedRead):
    manuscript_id: str
    uploader_id: Optional[str]
    uploader_name: Optional[str] = None
    filename: str
    content_type: str
    size_bytes: int
    kind: AttachmentKind
    storage_key: str
    sha256: Optional[str]
    description: Optional[str]
    is_placeholder: bool = False
