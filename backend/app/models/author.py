from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity

if TYPE_CHECKING:
    from app.models.contract import Contract
    from app.models.manuscript import Manuscript


class Author(BaseEntity, table=True):
    __tablename__ = "authors"

    full_name: str = Field(max_length=200, index=True)
    email: Optional[str] = Field(default=None, max_length=255, index=True)
    country: Optional[str] = Field(default=None, max_length=100)
    biography: Optional[str] = Field(default=None)

    manuscripts: list["Manuscript"] = Relationship(back_populates="author")
    contracts: list["Contract"] = Relationship(back_populates="author")
