from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import StreamStatus

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class ProductionRecord(BaseEntity, table=True):
    """Edition-level production summary, 1:1 with a Manuscript.

    Tracks identifiers (ISBN, release date) and the status of each format
    (print / ebook / audiobook) and stage (cover / layout / prepress) so
    a production manager has a single roll-up view per title.
    """

    __tablename__ = "production_records"

    manuscript_id: str = Field(foreign_key="manuscripts.id", unique=True, index=True)

    isbn: Optional[str] = Field(default=None, max_length=20, index=True)
    release_date: Optional[date] = Field(default=None, index=True)

    print_status: StreamStatus = Field(default=StreamStatus.NOT_PLANNED, index=True)
    ebook_status: StreamStatus = Field(default=StreamStatus.NOT_PLANNED, index=True)
    audiobook_status: StreamStatus = Field(default=StreamStatus.NOT_PLANNED, index=True)

    cover_status: StreamStatus = Field(default=StreamStatus.NOT_PLANNED, index=True)
    layout_status: StreamStatus = Field(default=StreamStatus.NOT_PLANNED, index=True)
    prepress_status: StreamStatus = Field(default=StreamStatus.NOT_PLANNED, index=True)

    notes: Optional[str] = None

    manuscript: "Manuscript" = Relationship(back_populates="production_record")
