from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.editorial_note import EditorialNote
    from app.models.production_item import ProductionItem
    from app.models.review import Review
    from app.models.workflow_event import WorkflowEvent


class User(BaseEntity, table=True):
    __tablename__ = "users"

    email: str = Field(max_length=255, index=True, unique=True)
    hashed_password: str = Field(max_length=255)
    full_name: str = Field(max_length=200)
    role: UserRole = Field(default=UserRole.EDITOR, index=True)
    is_active: bool = Field(default=True)

    reviews: list["Review"] = Relationship(back_populates="reviewer")
    workflow_events: list["WorkflowEvent"] = Relationship(back_populates="actor")
    editorial_notes: list["EditorialNote"] = Relationship(back_populates="author_user")
    production_assignments: list["ProductionItem"] = Relationship(back_populates="assignee")
