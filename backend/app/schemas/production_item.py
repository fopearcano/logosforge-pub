from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.models.enums import ProductionItemStatus, ProductionStage
from app.schemas._common import TimestampedRead


class ProductionItemCreate(BaseModel):
    manuscript_id: str
    assignee_id: Optional[str] = None
    stage: ProductionStage
    status: ProductionItemStatus = ProductionItemStatus.PENDING
    due_date: Optional[date] = None
    notes: Optional[str] = None


class ProductionItemUpdate(BaseModel):
    assignee_id: Optional[str] = None
    stage: Optional[ProductionStage] = None
    status: Optional[ProductionItemStatus] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None


class ProductionItemRead(TimestampedRead):
    manuscript_id: str
    assignee_id: Optional[str]
    stage: ProductionStage
    status: ProductionItemStatus
    due_date: Optional[date]
    notes: Optional[str]
