"""Pydantic schemas used for request/response payloads."""

from app.schemas.attachment import (
    AttachmentPlaceholderCreate,
    AttachmentRead,
    AttachmentUpdate,
)
from app.schemas.auth import CurrentUserRead, TokenResponse
from app.schemas.author import AuthorCreate, AuthorRead, AuthorUpdate
from app.schemas.contract import ContractCreate, ContractRead, ContractUpdate
from app.schemas.editorial_note import (
    EditorialNoteCreate,
    EditorialNoteRead,
    EditorialNoteUpdate,
)
from app.schemas.manuscript import ManuscriptCreate, ManuscriptRead, ManuscriptUpdate
from app.schemas.production_item import (
    ProductionItemCreate,
    ProductionItemRead,
    ProductionItemUpdate,
)
from app.schemas.production_record import (
    ProductionRecordCreate,
    ProductionRecordDetail,
    ProductionRecordRead,
    ProductionRecordUpdate,
)
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.schemas.workflow_event import (
    TransitionRequest,
    TransitionResponse,
    WorkflowEventCreate,
    WorkflowEventRead,
    WorkflowEventUpdate,
)

__all__ = [
    "AttachmentPlaceholderCreate",
    "AttachmentRead",
    "AttachmentUpdate",
    "AuthorCreate",
    "AuthorRead",
    "AuthorUpdate",
    "CurrentUserRead",
    "TokenResponse",
    "ContractCreate",
    "ContractRead",
    "ContractUpdate",
    "EditorialNoteCreate",
    "EditorialNoteRead",
    "EditorialNoteUpdate",
    "ManuscriptCreate",
    "ManuscriptRead",
    "ManuscriptUpdate",
    "ProductionItemCreate",
    "ProductionItemRead",
    "ProductionItemUpdate",
    "ProductionRecordCreate",
    "ProductionRecordDetail",
    "ProductionRecordRead",
    "ProductionRecordUpdate",
    "ReviewCreate",
    "ReviewRead",
    "ReviewUpdate",
    "TransitionRequest",
    "TransitionResponse",
    "WorkflowEventCreate",
    "WorkflowEventRead",
    "WorkflowEventUpdate",
]
