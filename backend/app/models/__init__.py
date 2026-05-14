"""Domain models for LOGOSFORGE.

Importing this package registers every SQLModel table with the shared
metadata registry, so `init_db()` can materialise them against the
configured database engine.
"""
from app.models.ai_insight import AIInsight
from app.models.attachment import Attachment
from app.models.author import Author
from app.models.contract import Contract
from app.models.editorial_note import EditorialNote
from app.models.enums import (
    AIFeature,
    AttachmentKind,
    ContractStatus,
    EditorialNoteKind,
    EntityKind,
    ExportFormat,
    ManuscriptLinkRole,
    ProductionItemStatus,
    ProductionStage,
    RelationshipKind,
    ReviewVerdict,
    StreamStatus,
    UserRole,
    WorkflowStatus,
)
from app.models.knowledge_entity import KnowledgeEntity
from app.models.knowledge_relationship import KnowledgeRelationship
from app.models.manuscript import Manuscript
from app.models.manuscript_entity_link import ManuscriptEntityLink
from app.models.production_item import ProductionItem
from app.models.production_record import ProductionRecord
from app.models.review import Review
from app.models.user import User
from app.models.workflow_event import WorkflowEvent

__all__ = [
    "AIFeature",
    "AIInsight",
    "Attachment",
    "AttachmentKind",
    "Author",
    "EntityKind",
    "KnowledgeEntity",
    "KnowledgeRelationship",
    "ManuscriptEntityLink",
    "ManuscriptLinkRole",
    "RelationshipKind",
    "Contract",
    "ContractStatus",
    "EditorialNote",
    "EditorialNoteKind",
    "ExportFormat",
    "Manuscript",
    "ProductionItem",
    "ProductionItemStatus",
    "ProductionRecord",
    "ProductionStage",
    "Review",
    "ReviewVerdict",
    "StreamStatus",
    "User",
    "UserRole",
    "WorkflowEvent",
    "WorkflowStatus",
]
