from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.auth.security import hash_password
from app.models import Author, Manuscript, User, WorkflowEvent
from app.models.enums import UserRole, WorkflowStatus
from app.services import workflow
from app.services.workflow import WorkflowError


# ---------------------------------------------------------------------------
# Service-level tests (pure-Python, no HTTP).
# ---------------------------------------------------------------------------


def _build_manuscript(session: Session, status: WorkflowStatus) -> Manuscript:
    author = Author(full_name="Service Test Author")
    session.add(author)
    session.commit()
    session.refresh(author)
    m = Manuscript(title="Service Title", author_id=author.id, status=status)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


def _build_user(session: Session) -> User:
    u = User(
        email="actor@logosforge.test",
        full_name="Service Actor",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def test_transition_map_covers_every_status() -> None:
    for status_value in WorkflowStatus:
        assert status_value in workflow.TRANSITIONS


def test_archived_is_terminal() -> None:
    assert workflow.allowed_next_states(WorkflowStatus.ARCHIVED) == frozenset()


def test_transition_advances_status_and_records_event(session: Session) -> None:
    m = _build_manuscript(session, WorkflowStatus.SUBMITTED)
    actor = _build_user(session)

    updated, event = workflow.transition(
        session,
        m,
        to_status=WorkflowStatus.UNDER_REVIEW,
        actor=actor,
        comment="Routing to peer review.",
    )

    assert updated.status == WorkflowStatus.UNDER_REVIEW
    assert event.from_status == WorkflowStatus.SUBMITTED
    assert event.to_status == WorkflowStatus.UNDER_REVIEW
    assert event.actor_id == actor.id
    assert event.note == "Routing to peer review."

    history = session.exec(
        select(WorkflowEvent).where(WorkflowEvent.manuscript_id == m.id)
    ).all()
    assert len(history) == 1


def test_transition_rejects_disallowed_edge(session: Session) -> None:
    m = _build_manuscript(session, WorkflowStatus.SUBMITTED)
    with pytest.raises(WorkflowError, match="not allowed"):
        workflow.transition(
            session, m, to_status=WorkflowStatus.PUBLISHED, actor=None
        )


def test_transition_to_same_status_is_rejected(session: Session) -> None:
    m = _build_manuscript(session, WorkflowStatus.UNDER_REVIEW)
    with pytest.raises(WorkflowError, match="already in status"):
        workflow.transition(
            session, m, to_status=WorkflowStatus.UNDER_REVIEW, actor=None
        )


def test_transition_from_archived_blocked(session: Session) -> None:
    m = _build_manuscript(session, WorkflowStatus.ARCHIVED)
    with pytest.raises(WorkflowError, match="not allowed"):
        workflow.transition(
            session, m, to_status=WorkflowStatus.PUBLISHED, actor=None
        )


# ---------------------------------------------------------------------------
# HTTP-level tests.
# ---------------------------------------------------------------------------


def _author_via_api(client: TestClient) -> dict:
    r = client.post("/api/authors", json={"full_name": "Workflow Author"})
    assert r.status_code == 201, r.text
    return r.json()


def _manuscript_via_api(client: TestClient, author_id: str) -> dict:
    r = client.post(
        "/api/manuscripts",
        json={"title": "Workflow Title", "author_id": author_id},
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_transition_endpoint_happy_path(client: TestClient) -> None:
    author = _author_via_api(client)
    m = _manuscript_via_api(client, author["id"])

    r = client.post(
        f"/api/manuscripts/{m['id']}/transition",
        json={"to_status": "under_review", "comment": "Sent to reviewer."},
    )
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["manuscript_id"] == m["id"]
    assert body["status"] == "under_review"
    assert body["event"]["from_status"] == "submitted"
    assert body["event"]["to_status"] == "under_review"
    assert body["event"]["note"] == "Sent to reviewer."
    assert body["event"]["actor_id"]  # admin user from fixture
    assert body["event"]["actor_name"] == "Admin"
    assert "accepted" in body["allowed_next"]


def test_transition_endpoint_rejects_invalid_edge(client: TestClient) -> None:
    author = _author_via_api(client)
    m = _manuscript_via_api(client, author["id"])

    r = client.post(
        f"/api/manuscripts/{m['id']}/transition",
        json={"to_status": "published"},
    )
    assert r.status_code == 409
    assert "not allowed" in r.json()["detail"]


def test_transition_endpoint_rejects_same_status(client: TestClient) -> None:
    author = _author_via_api(client)
    m = _manuscript_via_api(client, author["id"])

    r = client.post(
        f"/api/manuscripts/{m['id']}/transition",
        json={"to_status": "submitted"},
    )
    assert r.status_code == 409
    assert "already in status" in r.json()["detail"]


def test_transition_endpoint_requires_authentication(
    anon_client: TestClient, session: Session
) -> None:
    m = _build_manuscript(session, WorkflowStatus.SUBMITTED)

    r = anon_client.post(
        f"/api/manuscripts/{m.id}/transition",
        json={"to_status": "under_review"},
    )
    assert r.status_code == 401


def test_transition_missing_manuscript_returns_404(client: TestClient) -> None:
    r = client.post(
        "/api/manuscripts/no-such-id/transition",
        json={"to_status": "under_review"},
    )
    assert r.status_code == 404


def test_manuscript_workflow_history_chronological(client: TestClient) -> None:
    author = _author_via_api(client)
    m = _manuscript_via_api(client, author["id"])

    for to_status in ("under_review", "accepted", "development_editing"):
        r = client.post(
            f"/api/manuscripts/{m['id']}/transition",
            json={"to_status": to_status},
        )
        assert r.status_code == 200, r.text

    r = client.get(f"/api/manuscripts/{m['id']}/workflow-events")
    assert r.status_code == 200
    events = r.json()
    assert len(events) == 3
    assert [e["to_status"] for e in events] == [
        "under_review",
        "accepted",
        "development_editing",
    ]
    assert events[0]["from_status"] == "submitted"
    assert events[-1]["from_status"] == "accepted"
    assert events[0]["actor_name"] is not None


def test_transitions_map_endpoint(anon_client: TestClient) -> None:
    r = anon_client.get("/api/workflow/transitions")
    assert r.status_code == 200
    body = r.json()

    assert set(body) == {s.value for s in WorkflowStatus}
    assert body["archived"] == []
    assert "under_review" in body["submitted"]
    assert "accepted" in body["under_review"]


def test_history_for_missing_manuscript_returns_404(anon_client: TestClient) -> None:
    r = anon_client.get("/api/manuscripts/missing/workflow-events")
    assert r.status_code == 404
