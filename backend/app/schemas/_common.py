from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for read schemas — populates from SQLModel attribute access."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedRead(ORMModel):
    id: str
    created_at: datetime
    updated_at: datetime
