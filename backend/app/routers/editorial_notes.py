from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import EditorialNote, Manuscript, User
from app.models.enums import EditorialNoteKind
from app.schemas import EditorialNoteCreate, EditorialNoteRead, EditorialNoteUpdate
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/editorial-notes", tags=["editorial_notes"])


@router.get("", response_model=Page[EditorialNoteRead])
def list_editorial_notes(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    manuscript_id: Optional[str] = Query(default=None),
    author_user_id: Optional[str] = Query(default=None),
    kind: Optional[EditorialNoteKind] = Query(default=None),
    pinned: Optional[bool] = Query(default=None),
) -> Page[EditorialNoteRead]:
    stmt = select(EditorialNote)
    if manuscript_id is not None:
        stmt = stmt.where(EditorialNote.manuscript_id == manuscript_id)
    if author_user_id is not None:
        stmt = stmt.where(EditorialNote.author_user_id == author_user_id)
    if kind is not None:
        stmt = stmt.where(EditorialNote.kind == kind)
    if pinned is not None:
        stmt = stmt.where(EditorialNote.pinned == pinned)
    stmt = stmt.order_by(EditorialNote.created_at.desc())

    items, total = paginate(session, stmt, params)
    return Page[EditorialNoteRead](
        items=[EditorialNoteRead.model_validate(i) for i in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{note_id}", response_model=EditorialNoteRead)
def get_editorial_note(
    note_id: str, session: Session = Depends(get_session)
) -> EditorialNote:
    return get_or_404(session, EditorialNote, note_id, name="EditorialNote")


@router.post("", response_model=EditorialNoteRead, status_code=status.HTTP_201_CREATED)
def create_editorial_note(
    payload: EditorialNoteCreate, session: Session = Depends(get_session)
) -> EditorialNote:
    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    ensure_exists(session, User, payload.author_user_id, name="User")
    note = EditorialNote(**payload.model_dump())
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.patch("/{note_id}", response_model=EditorialNoteRead)
def update_editorial_note(
    note_id: str,
    payload: EditorialNoteUpdate,
    session: Session = Depends(get_session),
) -> EditorialNote:
    note = get_or_404(session, EditorialNote, note_id, name="EditorialNote")
    apply_patch(note, payload)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_editorial_note(
    note_id: str, session: Session = Depends(get_session)
):
    note = get_or_404(session, EditorialNote, note_id, name="EditorialNote")
    session.delete(note)
    session.commit()
