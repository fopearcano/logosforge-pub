"""Domain models for LOGOSFORGE.

Importing this package registers every SQLModel table with the shared
metadata registry, so `init_db()` can materialise them against the
configured database engine.
"""
from app.models.author import Author
from app.models.contract import Contract
from app.models.editorial_note import EditorialNote
from app.models.enums import (
    ContractStatus,
    EditorialNoteKind,
    ProductionItemStatus,
    ProductionStage,
    ReviewVerdict,
    UserRole,
    WorkflowStatus,
)
from app.models.manuscript import Manuscript
from app.models.production_item import ProductionItem
from app.models.review import Review
from app.models.user import User
from app.models.workflow_event import WorkflowEvent

__all__ = [
    "Author",
    "Contract",
    "ContractStatus",
    "EditorialNote",
    "EditorialNoteKind",
    "Manuscript",
    "ProductionItem",
    "ProductionItemStatus",
    "ProductionStage",
    "Review",
    "ReviewVerdict",
    "User",
    "UserRole",
    "WorkflowEvent",
    "WorkflowStatus",
]
