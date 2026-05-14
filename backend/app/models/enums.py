from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    PRODUCTION_MANAGER = "production_manager"
    MARKETING = "marketing"
    ARCHIVE_READER = "archive_reader"


class WorkflowStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEVELOPMENT_EDITING = "development_editing"
    COPY_EDITING = "copy_editing"
    PROOFREADING = "proofreading"
    LAYOUT = "layout"
    COVER_DESIGN = "cover_design"
    PREPRESS = "prepress"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ReviewVerdict(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    TERMINATED = "terminated"


class ProductionStage(str, Enum):
    LAYOUT = "layout"
    COVER_DESIGN = "cover_design"
    PREPRESS = "prepress"
    PRINTING = "printing"


class ProductionItemStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class EditorialNoteKind(str, Enum):
    GENERAL = "general"
    STRUCTURAL = "structural"
    LINE = "line"
    DESIGN = "design"
    PRODUCTION = "production"


class StreamStatus(str, Enum):
    """Status of a single production stream (format or stage)."""

    NOT_PLANNED = "not_planned"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETE = "complete"


class AttachmentKind(str, Enum):
    """Categories of file attached to a manuscript."""

    MANUSCRIPT_DRAFT = "manuscript_draft"
    EDITOR_MARKED_COPY = "editor_marked_copy"
    COVER_ARTWORK = "cover_artwork"
    PROOF = "proof"
    CONTRACT_SCAN = "contract_scan"
    OTHER = "other"


class ExportFormat(str, Enum):
    """Available manuscript export formats."""

    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"  # registered placeholder — implementation pending


class AIFeature(str, Enum):
    """The editorial AI features exposed at /api/ai/manuscripts/..."""

    SUMMARIZE = "summarize"
    STYLE_ANALYSIS = "style_analysis"
    EDITORIAL_SUGGESTIONS = "editorial_suggestions"
    SEMANTIC_TAGS = "semantic_tags"
    CONSISTENCY_CHECK = "consistency_check"


class EntityKind(str, Enum):
    """Kinds of node in the editorial knowledge graph."""

    CHARACTER = "character"
    PLACE = "place"
    THEME = "theme"
    MOTIF = "motif"
    ORGANIZATION = "organization"
    WORK = "work"
    PERSON = "person"
    PERIOD = "period"
    OTHER = "other"


class RelationshipKind(str, Enum):
    """Typed edges between knowledge entities."""

    RELATED_TO = "related_to"
    INFLUENCES = "influences"
    DESCENDS_FROM = "descends_from"
    CONTRASTS_WITH = "contrasts_with"
    INHABITS = "inhabits"
    AUTHORED = "authored"
    PART_OF = "part_of"
    SIBLING_OF = "sibling_of"
    MENTOR_OF = "mentor_of"
    ADAPTS = "adapts"
    OTHER = "other"


class ManuscriptLinkRole(str, Enum):
    """How a manuscript relates to a knowledge entity."""

    TAGGED = "tagged"
    FEATURES = "features"
    REFERENCES = "references"
    SET_IN = "set_in"
    DERIVED_FROM = "derived_from"
    OTHER = "other"
