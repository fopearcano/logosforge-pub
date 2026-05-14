"""Payload validation across the public CRUD surface.

We trust Pydantic to enforce the constraints we declared on the schemas
— these tests pin those declarations so they don't quietly drift.
"""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.security import hash_password
from app.models import Author, Manuscript, User
from app.models.enums import UserRole, WorkflowStatus


def _author(session: Session) -> Author:
    a = Author(full_name="A")
    session.add(a)
    session.commit()
    session.refresh(a)
    return a


def _editor(session: Session) -> User:
    u = User(
        email="ed-validation@logosforge.test",
        full_name="Ed",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def _manuscript(session: Session) -> Manuscript:
    a = _author(session)
    m = Manuscript(title="T", author_id=a.id, status=WorkflowStatus.SUBMITTED)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


# --- author --------------------------------------------------------------


def test_author_full_name_required(client: TestClient) -> None:
    r = client.post("/api/authors", json={"full_name": ""})
    assert r.status_code == 422


def test_author_full_name_too_long(client: TestClient) -> None:
    r = client.post("/api/authors", json={"full_name": "x" * 250})
    assert r.status_code == 422


# --- manuscript ----------------------------------------------------------


def test_manuscript_word_count_must_be_non_negative(
    client: TestClient, session: Session
) -> None:
    a = _author(session)
    r = client.post(
        "/api/manuscripts",
        json={"title": "Negative", "author_id": a.id, "word_count": -1},
    )
    assert r.status_code == 422


def test_manuscript_status_must_be_known_value(
    client: TestClient, session: Session
) -> None:
    a = _author(session)
    r = client.post(
        "/api/manuscripts",
        json={"title": "Bad status", "author_id": a.id, "status": "no_such_status"},
    )
    assert r.status_code == 422


def test_manuscript_title_too_long(
    client: TestClient, session: Session
) -> None:
    a = _author(session)
    r = client.post(
        "/api/manuscripts",
        json={"title": "x" * 350, "author_id": a.id},
    )
    assert r.status_code == 422


# --- review --------------------------------------------------------------


def test_review_rating_upper_bound(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    u = _editor(session)
    r = client.post(
        "/api/reviews",
        json={
            "manuscript_id": m.id,
            "reviewer_id": u.id,
            "verdict": "accept",
            "summary": "ok",
            "rating": 7,
        },
    )
    assert r.status_code == 422


def test_review_rating_lower_bound(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    u = _editor(session)
    r = client.post(
        "/api/reviews",
        json={
            "manuscript_id": m.id,
            "reviewer_id": u.id,
            "verdict": "accept",
            "summary": "ok",
            "rating": 0,
        },
    )
    assert r.status_code == 422


def test_review_summary_required(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    u = _editor(session)
    r = client.post(
        "/api/reviews",
        json={
            "manuscript_id": m.id,
            "reviewer_id": u.id,
            "verdict": "accept",
            "summary": "",
        },
    )
    assert r.status_code == 422


# --- contract ------------------------------------------------------------


def test_contract_royalty_rate_upper_bound(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    a = m.author_id
    r = client.post(
        "/api/contracts",
        json={
            "manuscript_id": m.id,
            "author_id": a,
            "royalty_rate": 1.5,
        },
    )
    assert r.status_code == 422


def test_contract_advance_must_be_non_negative(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    r = client.post(
        "/api/contracts",
        json={
            "manuscript_id": m.id,
            "author_id": m.author_id,
            "advance_amount": "-1",
        },
    )
    assert r.status_code == 422


def test_contract_currency_must_be_three_chars(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    r = client.post(
        "/api/contracts",
        json={
            "manuscript_id": m.id,
            "author_id": m.author_id,
            "currency": "DOLLARS",
        },
    )
    assert r.status_code == 422


# --- transition ----------------------------------------------------------


def test_transition_to_same_status_is_409(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    r = client.post(
        f"/api/manuscripts/{m.id}/transition",
        json={"to_status": "submitted"},
    )
    assert r.status_code == 409
    assert "already" in r.json()["detail"].lower()


def test_invalid_transition_is_409(
    client: TestClient, session: Session
) -> None:
    m = _manuscript(session)
    r = client.post(
        f"/api/manuscripts/{m.id}/transition",
        json={"to_status": "published"},
    )
    assert r.status_code == 409
    assert "not allowed" in r.json()["detail"].lower()
