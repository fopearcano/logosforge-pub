from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.db import get_session
from app.models import (
    Author,
    Contract,
    EditorialNote,
    Manuscript,
    Review,
)
from app.models.enums import WorkflowStatus
from app.schemas.search import (
    AuthorHit,
    ContractHit,
    ManuscriptHit,
    NoteHit,
    ReviewHit,
    SearchResults,
)

router = APIRouter(prefix="/search", tags=["search"])


def _year_bounds(year: int) -> tuple[datetime, datetime]:
    return datetime(year, 1, 1), datetime(year + 1, 1, 1)


def _apply_manuscript_filters(stmt, status, genre, year, author_id):
    if status is not None:
        stmt = stmt.where(Manuscript.status == status)
    if genre is not None:
        stmt = stmt.where(Manuscript.genre == genre)
    if year is not None:
        start, end = _year_bounds(year)
        stmt = stmt.where(Manuscript.created_at >= start, Manuscript.created_at < end)
    if author_id is not None:
        stmt = stmt.where(Manuscript.author_id == author_id)
    return stmt


@router.get(
    "",
    response_model=SearchResults,
    summary="Search across manuscripts, authors, reviews, notes, and contracts",
)
def search(
    q: str = Query(..., min_length=1, description="Search term"),
    status: Optional[WorkflowStatus] = Query(default=None),
    genre: Optional[str] = Query(default=None),
    year: Optional[int] = Query(default=None, ge=1900, le=2999),
    author_id: Optional[str] = Query(default=None),
    rights_territory: Optional[str] = Query(default=None),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> SearchResults:
    pattern = f"%{q}%"

    # Manuscripts
    m_stmt = (
        select(Manuscript)
        .options(selectinload(Manuscript.author))
        .where(
            or_(
                Manuscript.title.ilike(pattern),
                Manuscript.subtitle.ilike(pattern),
                Manuscript.synopsis.ilike(pattern),
                Manuscript.genre.ilike(pattern),
            )
        )
    )
    m_stmt = _apply_manuscript_filters(m_stmt, status, genre, year, author_id)
    manuscripts = list(
        session.exec(m_stmt.order_by(Manuscript.title.asc()).limit(limit)).all()
    )

    # Authors — name / biography / country
    a_stmt = select(Author).where(
        or_(
            Author.full_name.ilike(pattern),
            Author.biography.ilike(pattern),
            Author.country.ilike(pattern),
        )
    )
    if author_id is not None:
        a_stmt = a_stmt.where(Author.id == author_id)
    authors = list(
        session.exec(a_stmt.order_by(Author.full_name.asc()).limit(limit)).all()
    )

    # Reviews
    r_stmt = (
        select(Review)
        .join(Manuscript, Review.manuscript_id == Manuscript.id)
        .options(
            selectinload(Review.manuscript),
            selectinload(Review.reviewer),
        )
        .where(Review.summary.ilike(pattern))
    )
    r_stmt = _apply_manuscript_filters(r_stmt, status, genre, year, author_id)
    reviews = list(
        session.exec(r_stmt.order_by(Review.created_at.desc()).limit(limit)).all()
    )

    # Editorial notes
    n_stmt = (
        select(EditorialNote)
        .join(Manuscript, EditorialNote.manuscript_id == Manuscript.id)
        .options(
            selectinload(EditorialNote.manuscript),
            selectinload(EditorialNote.author_user),
        )
        .where(EditorialNote.body.ilike(pattern))
    )
    n_stmt = _apply_manuscript_filters(n_stmt, status, genre, year, author_id)
    notes = list(
        session.exec(n_stmt.order_by(EditorialNote.created_at.desc()).limit(limit)).all()
    )

    # Contracts — match terms or rights_territory; filter on territory if given.
    c_stmt = (
        select(Contract)
        .join(Manuscript, Contract.manuscript_id == Manuscript.id)
        .options(selectinload(Contract.manuscript))
        .where(
            or_(
                Contract.terms.ilike(pattern),
                Contract.rights_territory.ilike(pattern),
            )
        )
    )
    c_stmt = _apply_manuscript_filters(c_stmt, status, genre, year, author_id)
    if rights_territory is not None:
        c_stmt = c_stmt.where(Contract.rights_territory == rights_territory)
    contracts = list(
        session.exec(c_stmt.order_by(Contract.created_at.desc()).limit(limit)).all()
    )

    manuscript_hits = [
        ManuscriptHit(
            id=m.id,
            title=m.title,
            subtitle=m.subtitle,
            status=m.status,
            genre=m.genre,
            author_id=m.author_id,
            author_name=m.author.full_name,
        )
        for m in manuscripts
    ]
    author_hits = [
        AuthorHit(
            id=a.id,
            full_name=a.full_name,
            country=a.country,
            biography=a.biography,
        )
        for a in authors
    ]
    review_hits = [
        ReviewHit(
            id=r.id,
            manuscript_id=r.manuscript_id,
            manuscript_title=r.manuscript.title,
            verdict=r.verdict,
            summary=r.summary,
            rating=r.rating,
            reviewer_name=r.reviewer.full_name if r.reviewer is not None else None,
        )
        for r in reviews
    ]
    note_hits = [
        NoteHit(
            id=n.id,
            manuscript_id=n.manuscript_id,
            manuscript_title=n.manuscript.title,
            kind=n.kind,
            body=n.body,
            pinned=n.pinned,
            author_user_name=n.author_user.full_name if n.author_user is not None else None,
        )
        for n in notes
    ]
    contract_hits = [
        ContractHit(
            id=c.id,
            manuscript_id=c.manuscript_id,
            manuscript_title=c.manuscript.title,
            status=c.status,
            rights_territory=c.rights_territory,
            terms=c.terms,
        )
        for c in contracts
    ]

    total = (
        len(manuscript_hits)
        + len(author_hits)
        + len(review_hits)
        + len(note_hits)
        + len(contract_hits)
    )

    return SearchResults(
        query=q,
        total=total,
        manuscripts=manuscript_hits,
        authors=author_hits,
        reviews=review_hits,
        editorial_notes=note_hits,
        contracts=contract_hits,
    )
