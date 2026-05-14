from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import RelationshipKind

if TYPE_CHECKING:
    from app.models.knowledge_entity import KnowledgeEntity


class KnowledgeRelationship(BaseEntity, table=True):
    """A typed, directional edge between two ``KnowledgeEntity`` nodes.

    Edges may carry a ``weight`` (0–1) so the UI / future scoring can
    distinguish a passing reference from a defining link. The schema
    permits multiple edges of different kinds between the same pair.
    """

    __tablename__ = "knowledge_relationships"

    source_id: str = Field(foreign_key="knowledge_entities.id", index=True)
    target_id: str = Field(foreign_key="knowledge_entities.id", index=True)
    kind: RelationshipKind = Field(
        default=RelationshipKind.RELATED_TO, index=True
    )
    weight: Optional[float] = Field(default=None, ge=0, le=1)
    description: Optional[str] = None

    source: "KnowledgeEntity" = Relationship(
        back_populates="outgoing_relationships",
        sa_relationship_kwargs={
            "foreign_keys": "[KnowledgeRelationship.source_id]"
        },
    )
    target: "KnowledgeEntity" = Relationship(
        back_populates="incoming_relationships",
        sa_relationship_kwargs={
            "foreign_keys": "[KnowledgeRelationship.target_id]"
        },
    )
