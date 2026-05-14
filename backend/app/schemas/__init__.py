"""Pydantic schemas used for request/response payloads."""

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
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.schemas.workflow_event import (
    WorkflowEventCreate,
    WorkflowEventRead,
    WorkflowEventUpdate,
)

__all__ = [
    "AuthorCreate",
    "AuthorRead",
    "AuthorUpdate",
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
    "ReviewCreate",
    "ReviewRead",
    "ReviewUpdate",
    "WorkflowEventCreate",
    "WorkflowEventRead",
    "WorkflowEventUpdate",
]
