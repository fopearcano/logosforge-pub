from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import EditorialNoteKind

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class EditorialNote(BaseEntity, table=True):
    __tablename__ = "editorial_notes"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    author_user_id: str = Field(foreign_key="users.id", index=True)
    kind: EditorialNoteKind = Field(default=EditorialNoteKind.GENERAL, index=True)
    body: str
    pinned: bool = Field(default=False)

    manuscript: "Manuscript" = Relationship(back_populates="editorial_notes")
    author_user: "User" = Relationship(back_populates="editorial_notes")

    @property
    def author_user_name(self) -> Optional[str]:
        return self.author_user.full_name if self.author_user is not None else None
