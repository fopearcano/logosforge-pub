from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import ReviewVerdict

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class Review(BaseEntity, table=True):
    __tablename__ = "reviews"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    reviewer_id: str = Field(foreign_key="users.id", index=True)
    verdict: ReviewVerdict = Field(index=True)
    summary: str
    rating: Optional[int] = Field(default=None, ge=1, le=5)

    manuscript: "Manuscript" = Relationship(back_populates="reviews")
    reviewer: "User" = Relationship(back_populates="reviews")
