from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import ReviewVerdict
from app.schemas._common import TimestampedRead


class ReviewCreate(BaseModel):
    manuscript_id: str
    reviewer_id: str
    verdict: ReviewVerdict
    summary: str = Field(min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class ReviewUpdate(BaseModel):
    verdict: Optional[ReviewVerdict] = None
    summary: Optional[str] = Field(default=None, min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class ReviewRead(TimestampedRead):
    manuscript_id: str
    reviewer_id: str
    verdict: ReviewVerdict
    summary: str
    rating: Optional[int]
