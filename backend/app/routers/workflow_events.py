from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select

from app.auth import ADMIN_ONLY, AUTHED
from app.db import get_session
from app.models import Manuscript, User, WorkflowEvent
from app.schemas import WorkflowEventCreate, WorkflowEventRead, WorkflowEventUpdate
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/workflow-events", tags=["workflow_events"])


@router.get("", response_model=Page[WorkflowEventRead])
def list_workflow_events(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    manuscript_id: Optional[str] = Query(default=None),
) -> Page[WorkflowEventRead]:
    stmt = select(WorkflowEvent)
    if manuscript_id is not None:
        stmt = stmt.where(WorkflowEvent.manuscript_id == manuscript_id)
    stmt = stmt.order_by(WorkflowEvent.created_at.asc())

    items, total = paginate(session, stmt, params)
    return Page[WorkflowEventRead](
        items=[WorkflowEventRead.model_validate(i) for i in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{event_id}", response_model=WorkflowEventRead)
def get_workflow_event(
    event_id: str, session: Session = Depends(get_session)
) -> WorkflowEvent:
    return get_or_404(session, WorkflowEvent, event_id, name="WorkflowEvent")


@router.post(
    "",
    response_model=WorkflowEventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
)
def create_workflow_event(
    payload: WorkflowEventCreate, session: Session = Depends(get_session)
) -> WorkflowEvent:
    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    if payload.actor_id is not None:
        ensure_exists(session, User, payload.actor_id, name="User")
    event = WorkflowEvent(**payload.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.patch("/{event_id}", response_model=WorkflowEventRead, dependencies=AUTHED)
def update_workflow_event(
    event_id: str,
    payload: WorkflowEventUpdate,
    session: Session = Depends(get_session),
) -> WorkflowEvent:
    event = get_or_404(session, WorkflowEvent, event_id, name="WorkflowEvent")
    apply_patch(event, payload)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=ADMIN_ONLY,
)
def delete_workflow_event(
    event_id: str, session: Session = Depends(get_session)
):
    event = get_or_404(session, WorkflowEvent, event_id, name="WorkflowEvent")
    session.delete(event)
    session.commit()
