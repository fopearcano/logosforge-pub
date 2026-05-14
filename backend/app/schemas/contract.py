from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import ContractStatus
from app.schemas._common import TimestampedRead


class ContractCreate(BaseModel):
    manuscript_id: str
    author_id: str
    status: ContractStatus = ContractStatus.DRAFT
    advance_amount: Optional[Decimal] = Field(default=None, ge=0)
    royalty_rate: Optional[float] = Field(default=None, ge=0, le=1)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    signed_at: Optional[datetime] = None
    terms: Optional[str] = None


class ContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    advance_amount: Optional[Decimal] = Field(default=None, ge=0)
    royalty_rate: Optional[float] = Field(default=None, ge=0, le=1)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    signed_at: Optional[datetime] = None
    terms: Optional[str] = None


class ContractRead(TimestampedRead):
    manuscript_id: str
    author_id: str
    status: ContractStatus
    advance_amount: Optional[Decimal]
    royalty_rate: Optional[float]
    currency: str
    signed_at: Optional[datetime]
    terms: Optional[str]
