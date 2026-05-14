from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import ProductionItemStatus, ProductionStage

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ProductionItem(BaseEntity, table=True):
    __tablename__ = "production_items"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    assignee_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True)
    stage: ProductionStage = Field(index=True)
    status: ProductionItemStatus = Field(default=ProductionItemStatus.PENDING, index=True)
    due_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None)

    manuscript: "Manuscript" = Relationship(back_populates="production_items")
    assignee: Optional["User"] = Relationship(back_populates="production_assignments")

    @property
    def assignee_name(self) -> Optional[str]:
        return self.assignee.full_name if self.assignee is not None else None
