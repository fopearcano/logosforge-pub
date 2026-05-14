from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.enums import AIFeature
from app.schemas._common import TimestampedRead


class AIRunResponse(BaseModel):
    """Returned by every AI feature endpoint."""

    feature: AIFeature
    provider: str
    model: Optional[str] = None
    generated_at: datetime
    insight_id: str
    result: dict[str, Any]


class AIInsightRead(TimestampedRead):
    manuscript_id: str
    feature: AIFeature
    provider: str
    model: Optional[str] = None
    payload: dict[str, Any] = {}


class AIProviderInfo(BaseModel):
    """Public description of the configured AI backend."""

    provider: str
    model: str
    base_url: Optional[str] = None
    is_live: bool  # False when the dry-run provider is in use


class AIProviderListing(BaseModel):
    active: AIProviderInfo
    known: list[str]
