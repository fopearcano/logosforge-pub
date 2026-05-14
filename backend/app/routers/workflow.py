from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from app.auth import AUTHED, get_current_user
from app.db import get_session
from app.models import Manuscript, User, WorkflowEvent
from app.models.enums import WorkflowStatus
from app.schemas import (
    TransitionRequest,
    TransitionResponse,
    WorkflowEventRead,
)
from app.services import workflow
from app.services.workflow import WorkflowError
from app.utils import ensure_exists, get_or_404

router = APIRouter(tags=["workflow"])


@router.get(
    "/workflow/transitions",
    response_model=dict[str, list[WorkflowStatus]],
    summary="Allowed transitions for every status",
)
def get_transitions_map() -> dict[str, list[str]]:
    return workflow.transitions_map()


@router.post(
    "/manuscripts/{manuscript_id}/transition",
    response_model=TransitionResponse,
    dependencies=AUTHED,
    summary="Transition a manuscript to a new workflow status",
)
def transition_manuscript(
    manuscript_id: str,
    payload: TransitionRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TransitionResponse:
    manuscript = get_or_404(session, Manuscript, manuscript_id, name="Manuscript")
    try:
        manuscript, event = workflow.transition(
            session,
            manuscript,
            to_status=payload.to_status,
            actor=user,
            comment=payload.comment,
        )
    except WorkflowError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    return TransitionResponse(
        manuscript_id=manuscript.id,
        status=manuscript.status,
        event=WorkflowEventRead.model_validate(event),
        allowed_next=sorted(workflow.allowed_next_states(manuscript.status)),
    )


@router.get(
    "/manuscripts/{manuscript_id}/workflow-events",
    response_model=list[WorkflowEventRead],
    summary="Chronological workflow history for a manuscript",
)
def get_manuscript_history(
    manuscript_id: str, session: Session = Depends(get_session)
) -> list[WorkflowEventRead]:
    ensure_exists(session, Manuscript, manuscript_id, name="Manuscript")
    events = list(
        session.exec(
            select(WorkflowEvent)
            .where(WorkflowEvent.manuscript_id == manuscript_id)
            .options(joinedload(WorkflowEvent.actor))
            .order_by(WorkflowEvent.created_at.asc())
        ).all()
    )
    return [WorkflowEventRead.model_validate(e) for e in events]
