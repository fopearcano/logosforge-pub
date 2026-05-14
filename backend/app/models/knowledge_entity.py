from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import EntityKind

if TYPE_CHECKING:
    from app.models.knowledge_relationship import KnowledgeRelationship
    from app.models.manuscript_entity_link import ManuscriptEntityLink


class KnowledgeEntity(BaseEntity, table=True):
    """A node in the editorial knowledge graph.

    Entities are typed (character, place, theme, motif, …) and carry a
    canonical ``slug`` for stable cross-referencing. ``extras`` holds a
    JSON-encoded payload for ad-hoc semantic metadata that doesn't yet
    warrant its own column.
    """

    __tablename__ = "knowledge_entities"

    kind: EntityKind = Field(default=EntityKind.THEME, index=True)
    name: str = Field(max_length=200, index=True)
    slug: str = Field(max_length=220, unique=True, index=True)
    description: Optional[str] = None
    extras: Optional[str] = Field(default=None)  # JSON-encoded text

    outgoing_relationships: list["KnowledgeRelationship"] = Relationship(
        back_populates="source",
        sa_relationship_kwargs={
            "foreign_keys": "[KnowledgeRelationship.source_id]"
        },
    )
    incoming_relationships: list["KnowledgeRelationship"] = Relationship(
        back_populates="target",
        sa_relationship_kwargs={
            "foreign_keys": "[KnowledgeRelationship.target_id]"
        },
    )
    manuscript_links: list["ManuscriptEntityLink"] = Relationship(
        back_populates="entity"
    )
