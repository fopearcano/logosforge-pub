from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import (
    EditorialNote,
    Manuscript,
    Review,
    WorkflowEvent,
)
from app.services.exports.base import ManuscriptExportBundle


def build_bundle(session: Session, manuscript_id: str) -> ManuscriptExportBundle:
    manuscript = session.exec(
        select(Manuscript)
        .where(Manuscript.id == manuscript_id)
        .options(selectinload(Manuscript.author))
    ).first()
    if manuscript is None:
        raise HTTPException(status_code=404, detail="Manuscript not found")

    workflow_events = list(
        session.exec(
            select(WorkflowEvent)
            .where(WorkflowEvent.manuscript_id == manuscript_id)
            .options(selectinload(WorkflowEvent.actor))
            .order_by(WorkflowEvent.created_at.asc())
        ).all()
    )

    reviews = list(
        session.exec(
            select(Review)
            .where(Review.manuscript_id == manuscript_id)
            .options(selectinload(Review.reviewer))
            .order_by(Review.created_at.asc())
        ).all()
    )

    editorial_notes = list(
        session.exec(
            select(EditorialNote)
            .where(EditorialNote.manuscript_id == manuscript_id)
            .options(selectinload(EditorialNote.author_user))
            .order_by(
                EditorialNote.pinned.desc(),
                EditorialNote.created_at.desc(),
            )
        ).all()
    )

    return ManuscriptExportBundle(
        manuscript=manuscript,
        author=manuscript.author,
        workflow_events=workflow_events,
        reviews=reviews,
        editorial_notes=editorial_notes,
    )
