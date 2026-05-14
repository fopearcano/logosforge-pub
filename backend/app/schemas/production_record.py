from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import StreamStatus, WorkflowStatus
from app.schemas._common import TimestampedRead


class ProductionRecordCreate(BaseModel):
    manuscript_id: str
    isbn: Optional[str] = Field(default=None, max_length=20)
    release_date: Optional[date] = None
    print_status: StreamStatus = StreamStatus.NOT_PLANNED
    ebook_status: StreamStatus = StreamStatus.NOT_PLANNED
    audiobook_status: StreamStatus = StreamStatus.NOT_PLANNED
    cover_status: StreamStatus = StreamStatus.NOT_PLANNED
    layout_status: StreamStatus = StreamStatus.NOT_PLANNED
    prepress_status: StreamStatus = StreamStatus.NOT_PLANNED
    notes: Optional[str] = None


class ProductionRecordUpdate(BaseModel):
    isbn: Optional[str] = Field(default=None, max_length=20)
    release_date: Optional[date] = None
    print_status: Optional[StreamStatus] = None
    ebook_status: Optional[StreamStatus] = None
    audiobook_status: Optional[StreamStatus] = None
    cover_status: Optional[StreamStatus] = None
    layout_status: Optional[StreamStatus] = None
    prepress_status: Optional[StreamStatus] = None
    notes: Optional[str] = None


class ProductionRecordRead(TimestampedRead):
    manuscript_id: str
    isbn: Optional[str]
    release_date: Optional[date]
    print_status: StreamStatus
    ebook_status: StreamStatus
    audiobook_status: StreamStatus
    cover_status: StreamStatus
    layout_status: StreamStatus
    prepress_status: StreamStatus
    notes: Optional[str]


class ProductionRecordDetail(ProductionRecordRead):
    """Read schema enriched with manuscript context for board + calendar."""

    manuscript_title: str
    manuscript_status: WorkflowStatus
    author_name: Optional[str] = None
