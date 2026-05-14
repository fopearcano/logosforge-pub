from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.models.enums import (
    ContractStatus,
    EditorialNoteKind,
    ReviewVerdict,
    WorkflowStatus,
)


class ManuscriptHit(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    status: WorkflowStatus
    genre: Optional[str] = None
    author_id: str
    author_name: str


class AuthorHit(BaseModel):
    id: str
    full_name: str
    country: Optional[str] = None
    biography: Optional[str] = None


class ReviewHit(BaseModel):
    id: str
    manuscript_id: str
    manuscript_title: str
    verdict: ReviewVerdict
    summary: str
    rating: Optional[int] = None
    reviewer_name: Optional[str] = None


class NoteHit(BaseModel):
    id: str
    manuscript_id: str
    manuscript_title: str
    kind: EditorialNoteKind
    body: str
    pinned: bool
    author_user_name: Optional[str] = None


class ContractHit(BaseModel):
    id: str
    manuscript_id: str
    manuscript_title: str
    status: ContractStatus
    rights_territory: Optional[str] = None
    terms: Optional[str] = None


class SearchResults(BaseModel):
    query: str
    total: int
    manuscripts: list[ManuscriptHit]
    authors: list[AuthorHit]
    reviews: list[ReviewHit]
    editorial_notes: list[NoteHit]
    contracts: list[ContractHit]
