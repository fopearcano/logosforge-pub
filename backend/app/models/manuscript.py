from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import WorkflowStatus

if TYPE_CHECKING:
    from app.models.ai_insight import AIInsight
    from app.models.attachment import Attachment
    from app.models.author import Author
    from app.models.contract import Contract
    from app.models.editorial_note import EditorialNote
    from app.models.manuscript_entity_link import ManuscriptEntityLink
    from app.models.production_item import ProductionItem
    from app.models.production_record import ProductionRecord
    from app.models.review import Review
    from app.models.workflow_event import WorkflowEvent


class Manuscript(BaseEntity, table=True):
    __tablename__ = "manuscripts"

    title: str = Field(max_length=300, index=True)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    synopsis: Optional[str] = Field(default=None)
    genre: Optional[str] = Field(default=None, max_length=100, index=True)
    language: str = Field(default="en", max_length=10)
    word_count: Optional[int] = Field(default=None, ge=0)
    status: WorkflowStatus = Field(default=WorkflowStatus.SUBMITTED, index=True)

    author_id: str = Field(foreign_key="authors.id", index=True)
    author: "Author" = Relationship(back_populates="manuscripts")

    reviews: list["Review"] = Relationship(back_populates="manuscript")
    workflow_events: list["WorkflowEvent"] = Relationship(back_populates="manuscript")
    contracts: list["Contract"] = Relationship(back_populates="manuscript")
    production_items: list["ProductionItem"] = Relationship(back_populates="manuscript")
    editorial_notes: list["EditorialNote"] = Relationship(back_populates="manuscript")
    production_record: Optional["ProductionRecord"] = Relationship(
        back_populates="manuscript",
        sa_relationship_kwargs={"uselist": False},
    )
    attachments: list["Attachment"] = Relationship(back_populates="manuscript")
    ai_insights: list["AIInsight"] = Relationship(back_populates="manuscript")
    entity_links: list["ManuscriptEntityLink"] = Relationship(
        back_populates="manuscript"
    )
