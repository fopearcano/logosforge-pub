from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Author, Manuscript
from app.models.enums import WorkflowStatus
from app.schemas import ManuscriptCreate, ManuscriptRead, ManuscriptUpdate
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/manuscripts", tags=["manuscripts"])


@router.get("", response_model=Page[ManuscriptRead])
def list_manuscripts(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    status_: Optional[WorkflowStatus] = Query(
        default=None, alias="status", description="Filter by workflow status"
    ),
    genre: Optional[str] = Query(default=None, description="Filter by genre (exact match)"),
    author_id: Optional[str] = Query(default=None, description="Filter by author id"),
) -> Page[ManuscriptRead]:
    stmt = select(Manuscript)
    if status_ is not None:
        stmt = stmt.where(Manuscript.status == status_)
    if genre is not None:
        stmt = stmt.where(Manuscript.genre == genre)
    if author_id is not None:
        stmt = stmt.where(Manuscript.author_id == author_id)
    stmt = stmt.order_by(Manuscript.created_at.desc())

    items, total = paginate(session, stmt, params)
    return Page[ManuscriptRead](
        items=[ManuscriptRead.model_validate(i) for i in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{manuscript_id}", response_model=ManuscriptRead)
def get_manuscript(
    manuscript_id: str, session: Session = Depends(get_session)
) -> Manuscript:
    return get_or_404(session, Manuscript, manuscript_id, name="Manuscript")


@router.post("", response_model=ManuscriptRead, status_code=status.HTTP_201_CREATED)
def create_manuscript(
    payload: ManuscriptCreate, session: Session = Depends(get_session)
) -> Manuscript:
    ensure_exists(session, Author, payload.author_id, name="Author")
    manuscript = Manuscript(**payload.model_dump())
    session.add(manuscript)
    session.commit()
    session.refresh(manuscript)
    return manuscript


@router.patch("/{manuscript_id}", response_model=ManuscriptRead)
def update_manuscript(
    manuscript_id: str,
    payload: ManuscriptUpdate,
    session: Session = Depends(get_session),
) -> Manuscript:
    manuscript = get_or_404(session, Manuscript, manuscript_id, name="Manuscript")
    apply_patch(manuscript, payload)
    session.add(manuscript)
    session.commit()
    session.refresh(manuscript)
    return manuscript


@router.delete("/{manuscript_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manuscript(
    manuscript_id: str, session: Session = Depends(get_session)
):
    manuscript = get_or_404(session, Manuscript, manuscript_id, name="Manuscript")
    session.delete(manuscript)
    session.commit()
