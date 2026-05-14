"""Service-level workflow tests.

These exercise app.services.workflow without going through the HTTP
layer — they assert the transition graph is what we documented and
that the side effects (manuscript update + WorkflowEvent insertion)
land in the same database session.
"""
from __future__ import annotations

import pytest
from sqlmodel import Session, select

from app.auth.security import hash_password
from app.models import Author, Manuscript, User, WorkflowEvent
from app.models.enums import UserRole, WorkflowStatus
from app.services import workflow


# --- transition graph ---------------------------------------------------


def test_archived_is_terminal() -> None:
    assert workflow.allowed_next_states(WorkflowStatus.ARCHIVED) == frozenset()


def test_canonical_path_is_allowed() -> None:
    canonical = [
        (WorkflowStatus.SUBMITTED, WorkflowStatus.UNDER_REVIEW),
        (WorkflowStatus.UNDER_REVIEW, WorkflowStatus.ACCEPTED),
        (WorkflowStatus.ACCEPTED, WorkflowStatus.DEVELOPMENT_EDITING),
        (WorkflowStatus.DEVELOPMENT_EDITING, WorkflowStatus.COPY_EDITING),
        (WorkflowStatus.COPY_EDITING, WorkflowStatus.PROOFREADING),
        (WorkflowStatus.PROOFREADING, WorkflowStatus.LAYOUT),
        (WorkflowStatus.LAYOUT, WorkflowStatus.COVER_DESIGN),
        (WorkflowStatus.COVER_DESIGN, WorkflowStatus.PREPRESS),
        (WorkflowStatus.PREPRESS, WorkflowStatus.PUBLISHED),
        (WorkflowStatus.PUBLISHED, WorkflowStatus.ARCHIVED),
    ]
    for current, nxt in canonical:
        assert workflow.can_transition(current, nxt), (current, nxt)


def test_long_jumps_are_blocked() -> None:
    # A submitted manuscript cannot leap straight to publication.
    assert not workflow.can_transition(
        WorkflowStatus.SUBMITTED, WorkflowStatus.PUBLISHED
    )
    # Nor can a manuscript be re-submitted after being published.
    assert not workflow.can_transition(
        WorkflowStatus.PUBLISHED, WorkflowStatus.SUBMITTED
    )


def test_archive_is_reachable_from_every_state() -> None:
    for state in WorkflowStatus:
        if state == WorkflowStatus.ARCHIVED:
            continue
        assert WorkflowStatus.ARCHIVED in workflow.allowed_next_states(state), state


def test_transitions_map_returns_string_serialised_graph() -> None:
    raw = workflow.transitions_map()
    assert raw["submitted"]
    assert "under_review" in raw["submitted"]
    assert raw["archived"] == []


# --- transition() side effects -----------------------------------------


def _seed(session: Session) -> tuple[Manuscript, User]:
    user = User(
        email="actor@logosforge.test",
        full_name="Actor",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    author = Author(full_name="Author")
    session.add_all([user, author])
    session.commit()
    session.refresh(user)
    session.refresh(author)
    manuscript = Manuscript(
        title="Subject",
        author_id=author.id,
        status=WorkflowStatus.SUBMITTED,
    )
    session.add(manuscript)
    session.commit()
    session.refresh(manuscript)
    return manuscript, user


def test_transition_updates_status_and_records_event(session: Session) -> None:
    manuscript, user = _seed(session)
    updated, event = workflow.transition(
        session,
        manuscript,
        to_status=WorkflowStatus.UNDER_REVIEW,
        actor=user,
        comment="Routed to acquisitions.",
    )
    assert updated.status == WorkflowStatus.UNDER_REVIEW
    assert event.from_status == WorkflowStatus.SUBMITTED
    assert event.to_status == WorkflowStatus.UNDER_REVIEW
    assert event.actor_id == user.id
    assert event.note == "Routed to acquisitions."

    # The event is persisted, not just returned in memory.
    rows = session.exec(
        select(WorkflowEvent).where(WorkflowEvent.manuscript_id == manuscript.id)
    ).all()
    assert len(rows) == 1


def test_transition_allows_no_actor(session: Session) -> None:
    manuscript, _ = _seed(session)
    _, event = workflow.transition(
        session,
        manuscript,
        to_status=WorkflowStatus.UNDER_REVIEW,
        actor=None,
    )
    assert event.actor_id is None


def test_transition_to_same_status_is_rejected(session: Session) -> None:
    manuscript, user = _seed(session)
    with pytest.raises(workflow.WorkflowError) as exc:
        workflow.transition(
            session,
            manuscript,
            to_status=WorkflowStatus.SUBMITTED,
            actor=user,
        )
    assert "already" in str(exc.value).lower()


def test_transition_along_disallowed_edge_is_rejected(session: Session) -> None:
    manuscript, user = _seed(session)
    with pytest.raises(workflow.WorkflowError) as exc:
        workflow.transition(
            session,
            manuscript,
            to_status=WorkflowStatus.PUBLISHED,
            actor=user,
        )
    assert "not allowed" in str(exc.value).lower()
    # The manuscript stays put when the transition is rejected.
    assert manuscript.status == WorkflowStatus.SUBMITTED
    assert (
        session.exec(
            select(WorkflowEvent).where(
                WorkflowEvent.manuscript_id == manuscript.id
            )
        ).all()
        == []
    )
