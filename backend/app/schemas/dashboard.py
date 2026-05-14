from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import (
    ProductionItemStatus,
    ProductionStage,
    ReviewVerdict,
    WorkflowStatus,
)


class StatusCount(BaseModel):
    status: WorkflowStatus
    count: int


class ActiveReviewSummary(BaseModel):
    manuscript_id: str
    manuscript_title: str
    author_name: str
    review_count: int
    latest_verdict: Optional[ReviewVerdict] = None
    latest_review_at: Optional[datetime] = None


class UpcomingRelease(BaseModel):
    manuscript_id: str
    title: str
    author_name: str
    status: WorkflowStatus
    next_due: Optional[date] = None
    open_production_items: int


class DeadlineEntry(BaseModel):
    production_item_id: str
    manuscript_id: str
    manuscript_title: str
    stage: ProductionStage
    status: ProductionItemStatus
    assignee_name: Optional[str] = None
    due_date: date
    days_until: int


class ActivityEntry(BaseModel):
    event_id: str
    manuscript_id: str
    manuscript_title: str
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    from_status: Optional[WorkflowStatus] = None
    to_status: WorkflowStatus
    note: Optional[str] = None
    occurred_at: datetime
