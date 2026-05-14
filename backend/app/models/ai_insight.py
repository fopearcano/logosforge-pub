from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import AIFeature

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class AIInsight(BaseEntity, table=True):
    """A cached AI feature result for a manuscript.

    The payload is stored as JSON-encoded text; the feature schema layer
    is the source of truth for its shape. Multiple insights can exist
    per (manuscript, feature) — the latest is the canonical one.
    """

    __tablename__ = "ai_insights"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    feature: AIFeature = Field(index=True)
    provider: str = Field(max_length=80)
    model: Optional[str] = Field(default=None, max_length=160)
    payload: str = Field(default="{}")

    manuscript: "Manuscript" = Relationship(back_populates="ai_insights")
