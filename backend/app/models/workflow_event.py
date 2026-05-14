from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import WorkflowStatus

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class WorkflowEvent(BaseEntity, table=True):
    __tablename__ = "workflow_events"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    actor_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True)
    from_status: Optional[WorkflowStatus] = Field(default=None)
    to_status: WorkflowStatus = Field(index=True)
    note: Optional[str] = Field(default=None)

    manuscript: "Manuscript" = Relationship(back_populates="workflow_events")
    actor: Optional["User"] = Relationship(back_populates="workflow_events")
