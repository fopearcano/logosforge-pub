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
