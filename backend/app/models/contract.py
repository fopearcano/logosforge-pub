from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import ContractStatus

if TYPE_CHECKING:
    from app.models.author import Author
    from app.models.manuscript import Manuscript


class Contract(BaseEntity, table=True):
    __tablename__ = "contracts"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    author_id: str = Field(foreign_key="authors.id", index=True)
    status: ContractStatus = Field(default=ContractStatus.DRAFT, index=True)
    advance_amount: Optional[Decimal] = Field(
        default=None,
        max_digits=12,
        decimal_places=2,
        ge=0,
    )
    royalty_rate: Optional[float] = Field(default=None, ge=0, le=1)
    currency: str = Field(default="USD", max_length=3)
    signed_at: Optional[datetime] = Field(default=None)
    terms: Optional[str] = Field(default=None)

    manuscript: "Manuscript" = Relationship(back_populates="contracts")
    author: "Author" = Relationship(back_populates="contracts")
