"""Editorial workflow engine.

A small, deterministic state machine over `WorkflowStatus`. The service is the
single source of truth for which transitions are valid; the HTTP layer is a
thin adapter around it.
"""
from __future__ import annotations

from typing import Optional

from sqlmodel import Session

from app.models import Manuscript, User, WorkflowEvent
from app.models.enums import WorkflowStatus


class WorkflowError(Exception):
    """Raised when a transition is not allowed."""


# Allowed transitions. Each status maps to the set of statuses it can move to.
# Forward edges follow the canonical editorial path; selected backward edges
# allow returning to the previous stage for revisions. `archived` is reachable
# from every non-terminal stage so a manuscript can always be shelved.
TRANSITIONS: dict[WorkflowStatus, frozenset[WorkflowStatus]] = {
    WorkflowStatus.SUBMITTED: frozenset(
        {WorkflowStatus.UNDER_REVIEW, WorkflowStatus.REJECTED, WorkflowStatus.ARCHIVED}
    ),
    WorkflowStatus.UNDER_REVIEW: frozenset(
        {
            WorkflowStatus.ACCEPTED,
            WorkflowStatus.REJECTED,
            WorkflowStatus.SUBMITTED,
            WorkflowStatus.ARCHIVED,
        }
    ),
    WorkflowStatus.ACCEPTED: frozenset(
        {WorkflowStatus.DEVELOPMENT_EDITING, WorkflowStatus.ARCHIVED}
    ),
    WorkflowStatus.REJECTED: frozenset({WorkflowStatus.ARCHIVED}),
    WorkflowStatus.DEVELOPMENT_EDITING: frozenset(
        {
            WorkflowStatus.COPY_EDITING,
            WorkflowStatus.UNDER_REVIEW,
            WorkflowStatus.ARCHIVED,
        }
    ),
    WorkflowStatus.COPY_EDITING: frozenset(
        {
            WorkflowStatus.PROOFREADING,
            WorkflowStatus.DEVELOPMENT_EDITING,
            WorkflowStatus.ARCHIVED,
        }
    ),
    WorkflowStatus.PROOFREADING: frozenset(
        {WorkflowStatus.LAYOUT, WorkflowStatus.COPY_EDITING, WorkflowStatus.ARCHIVED}
    ),
    WorkflowStatus.LAYOUT: frozenset(
        {
            WorkflowStatus.COVER_DESIGN,
            WorkflowStatus.PROOFREADING,
            WorkflowStatus.ARCHIVED,
        }
    ),
    WorkflowStatus.COVER_DESIGN: frozenset(
        {WorkflowStatus.PREPRESS, WorkflowStatus.LAYOUT, WorkflowStatus.ARCHIVED}
    ),
    WorkflowStatus.PREPRESS: frozenset(
        {
            WorkflowStatus.PUBLISHED,
            WorkflowStatus.COVER_DESIGN,
            WorkflowStatus.ARCHIVED,
        }
    ),
    WorkflowStatus.PUBLISHED: frozenset({WorkflowStatus.ARCHIVED}),
    WorkflowStatus.ARCHIVED: frozenset(),
}


def allowed_next_states(current: WorkflowStatus) -> frozenset[WorkflowStatus]:
    return TRANSITIONS.get(current, frozenset())


def can_transition(current: WorkflowStatus, to: WorkflowStatus) -> bool:
    return to in allowed_next_states(current)


def transitions_map() -> dict[str, list[str]]:
    """Serialisable view of the full transition graph for clients."""
    return {
        current.value: sorted(s.value for s in allowed_next_states(current))
        for current in WorkflowStatus
    }


def transition(
    session: Session,
    manuscript: Manuscript,
    *,
    to_status: WorkflowStatus,
    actor: Optional[User],
    comment: Optional[str] = None,
) -> tuple[Manuscript, WorkflowEvent]:
    """Move a manuscript to a new status and record the event atomically."""
    if to_status == manuscript.status:
        raise WorkflowError(
            f"Manuscript is already in status '{manuscript.status.value}'."
        )
    if not can_transition(manuscript.status, to_status):
        raise WorkflowError(
            f"Transition from '{manuscript.status.value}' to "
            f"'{to_status.value}' is not allowed."
        )

    event = WorkflowEvent(
        manuscript_id=manuscript.id,
        actor_id=actor.id if actor is not None else None,
        from_status=manuscript.status,
        to_status=to_status,
        note=comment,
    )
    manuscript.status = to_status
    session.add(manuscript)
    session.add(event)
    session.commit()
    session.refresh(manuscript)
    session.refresh(event)
    return manuscript, event
