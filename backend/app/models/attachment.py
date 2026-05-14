from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseEntity
from app.models.enums import AttachmentKind

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class Attachment(BaseEntity, table=True):
    """Metadata for a file attached to a manuscript.

    A real-upload record points to bytes on the configured storage
    backend via ``storage_key``. A placeholder record uses a
    ``placeholder:…`` key and has no underlying file — useful for
    planning what should eventually live in the archive.
    """

    __tablename__ = "attachments"

    manuscript_id: str = Field(foreign_key="manuscripts.id", index=True)
    uploader_id: Optional[str] = Field(
        default=None, foreign_key="users.id", index=True
    )

    filename: str = Field(max_length=255)
    content_type: str = Field(max_length=120)
    size_bytes: int = Field(default=0, ge=0)
    kind: AttachmentKind = Field(default=AttachmentKind.OTHER, index=True)

    storage_key: str = Field(max_length=300)
    sha256: Optional[str] = Field(default=None, max_length=64)

    description: Optional[str] = None

    manuscript: "Manuscript" = Relationship(back_populates="attachments")
    uploader: Optional["User"] = Relationship(back_populates="uploaded_attachments")

    @property
    def uploader_name(self) -> Optional[str]:
        return self.uploader.full_name if self.uploader is not None else None

    @property
    def is_placeholder(self) -> bool:
        return self.storage_key.startswith("placeholder:")
