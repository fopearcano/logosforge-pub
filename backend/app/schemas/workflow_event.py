from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.models.enums import WorkflowStatus
from app.schemas._common import TimestampedRead


class WorkflowEventCreate(BaseModel):
    manuscript_id: str
    actor_id: Optional[str] = None
    from_status: Optional[WorkflowStatus] = None
    to_status: WorkflowStatus
    note: Optional[str] = None


class WorkflowEventUpdate(BaseModel):
    note: Optional[str] = None


class WorkflowEventRead(TimestampedRead):
    manuscript_id: str
    actor_id: Optional[str]
    from_status: Optional[WorkflowStatus]
    to_status: WorkflowStatus
    note: Optional[str]
