from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import ManuscriptLinkRole

if TYPE_CHECKING:
    from app.models.knowledge_entity import KnowledgeEntity
    from app.models.manuscript import Manuscript


class ManuscriptEntityLink(BaseEntity, table=True):
    """A typed relationship between a Manuscript and a KnowledgeEntity.

    The role tells the UI how to display the link — as a tag, a setting,
    a referenced work, etc. ``relevance`` (0–1) lets a future scoring
    pass rank tags by importance.
    """

    __tablename__ = "manuscript_entity_links"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    entity_id: str = Field(foreign_key="knowledge_entities.id", index=True)
    role: ManuscriptLinkRole = Field(
        default=ManuscriptLinkRole.TAGGED, index=True
    )
    relevance: Optional[float] = Field(default=None, ge=0, le=1)
    notes: Optional[str] = None

    manuscript: "Manuscript" = Relationship(back_populates="entity_links")
    entity: "KnowledgeEntity" = Relationship(back_populates="manuscript_links")
