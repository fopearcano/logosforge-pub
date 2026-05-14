from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import (
    EntityKind,
    ManuscriptLinkRole,
    RelationshipKind,
)
from app.schemas._common import TimestampedRead


# --- entity ---------------------------------------------------------------


class KnowledgeEntityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: Optional[str] = Field(default=None, max_length=220)
    kind: EntityKind = EntityKind.THEME
    description: Optional[str] = None
    extras: Optional[str] = None  # JSON-encoded text


class KnowledgeEntityUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    slug: Optional[str] = Field(default=None, max_length=220)
    kind: Optional[EntityKind] = None
    description: Optional[str] = None
    extras: Optional[str] = None


class KnowledgeEntityRead(TimestampedRead):
    name: str
    slug: str
    kind: EntityKind
    description: Optional[str]
    extras: Optional[str]


# --- relationship ---------------------------------------------------------


class KnowledgeRelationshipCreate(BaseModel):
    source_id: str
    target_id: str
    kind: RelationshipKind = RelationshipKind.RELATED_TO
    weight: Optional[float] = Field(default=None, ge=0, le=1)
    description: Optional[str] = None


class KnowledgeRelationshipUpdate(BaseModel):
    kind: Optional[RelationshipKind] = None
    weight: Optional[float] = Field(default=None, ge=0, le=1)
    description: Optional[str] = None


class KnowledgeRelationshipRead(TimestampedRead):
    source_id: str
    target_id: str
    kind: RelationshipKind
    weight: Optional[float]
    description: Optional[str]


class KnowledgeRelationshipDetail(KnowledgeRelationshipRead):
    """Edge plus the names of its endpoints for direct rendering."""

    source_name: Optional[str] = None
    source_kind: Optional[EntityKind] = None
    target_name: Optional[str] = None
    target_kind: Optional[EntityKind] = None


# --- manuscript link ------------------------------------------------------


class ManuscriptEntityLinkCreate(BaseModel):
    manuscript_id: str
    entity_id: str
    role: ManuscriptLinkRole = ManuscriptLinkRole.TAGGED
    relevance: Optional[float] = Field(default=None, ge=0, le=1)
    notes: Optional[str] = None


class ManuscriptEntityLinkUpdate(BaseModel):
    role: Optional[ManuscriptLinkRole] = None
    relevance: Optional[float] = Field(default=None, ge=0, le=1)
    notes: Optional[str] = None


class ManuscriptEntityLinkRead(TimestampedRead):
    manuscript_id: str
    entity_id: str
    role: ManuscriptLinkRole
    relevance: Optional[float]
    notes: Optional[str]
    entity_name: Optional[str] = None
    entity_kind: Optional[EntityKind] = None
    entity_slug: Optional[str] = None


# --- neighborhood ---------------------------------------------------------


class NeighborhoodNode(BaseModel):
    id: str
    name: str
    slug: str
    kind: EntityKind
    distance: int  # 0 for root


class NeighborhoodEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    kind: RelationshipKind
    weight: Optional[float] = None
    description: Optional[str] = None


class NeighborhoodResult(BaseModel):
    root_id: str
    depth: int
    nodes: list[NeighborhoodNode]
    edges: list[NeighborhoodEdge]
