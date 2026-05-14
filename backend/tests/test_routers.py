from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.security import hash_password
from app.models import Author, Manuscript, User
from app.models.enums import UserRole, WorkflowStatus


def _make_author(client: TestClient, name: str = "Test Author") -> dict:
    r = client.post("/api/authors", json={"full_name": name, "country": "Atlantis"})
    assert r.status_code == 201, r.text
    return r.json()


def _make_manuscript(
    client: TestClient,
    author_id: str,
    *,
    title: str = "An Untitled Folio",
    genre: str | None = "Essays",
    status: str = "submitted",
) -> dict:
    payload = {"title": title, "author_id": author_id, "status": status}
    if genre is not None:
        payload["genre"] = genre
    r = client.post("/api/manuscripts", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def test_author_crud_lifecycle(client: TestClient) -> None:
    created = _make_author(client, "Iris Aldoria")
    author_id = created["id"]
    assert created["full_name"] == "Iris Aldoria"
    assert created["country"] == "Atlantis"

    listed = client.get("/api/authors").json()
    assert listed["total"] == 1
    assert listed["items"][0]["id"] == author_id
    assert listed["skip"] == 0
    assert listed["limit"] == 50

    fetched = client.get(f"/api/authors/{author_id}")
    assert fetched.status_code == 200
    assert fetched.json()["full_name"] == "Iris Aldoria"

    patched = client.patch(
        f"/api/authors/{author_id}", json={"country": "Portugal"}
    )
    assert patched.status_code == 200
    assert patched.json()["country"] == "Portugal"
    assert patched.json()["full_name"] == "Iris Aldoria"

    deleted = client.delete(f"/api/authors/{author_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/authors/{author_id}")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Author not found"


def test_create_author_validation_rejects_empty_name(client: TestClient) -> None:
    r = client.post("/api/authors", json={"full_name": ""})
    assert r.status_code == 422


def test_manuscript_create_requires_existing_author(client: TestClient) -> None:
    r = client.post(
        "/api/manuscripts",
        json={"title": "Ghost Title", "author_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Author not found"


def test_manuscript_filtering(client: TestClient) -> None:
    a1 = _make_author(client, "Author One")
    a2 = _make_author(client, "Author Two")

    _make_manuscript(client, a1["id"], title="Essays A", genre="Essays", status="submitted")
    _make_manuscript(client, a1["id"], title="Essays B", genre="Essays", status="published")
    _make_manuscript(client, a2["id"], title="Fiction A", genre="Fiction", status="submitted")

    by_status = client.get("/api/manuscripts?status=submitted").json()
    assert by_status["total"] == 2
    assert {m["title"] for m in by_status["items"]} == {"Essays A", "Fiction A"}

    by_genre = client.get("/api/manuscripts?genre=Essays").json()
    assert by_genre["total"] == 2
    assert {m["title"] for m in by_genre["items"]} == {"Essays A", "Essays B"}

    by_author = client.get(f"/api/manuscripts?author_id={a2['id']}").json()
    assert by_author["total"] == 1
    assert by_author["items"][0]["title"] == "Fiction A"

    combined = client.get(
        f"/api/manuscripts?author_id={a1['id']}&genre=Essays&status=published"
    ).json()
    assert combined["total"] == 1
    assert combined["items"][0]["title"] == "Essays B"


def test_manuscript_patch_status_and_404(client: TestClient) -> None:
    author = _make_author(client)
    m = _make_manuscript(client, author["id"])

    patched = client.patch(
        f"/api/manuscripts/{m['id']}", json={"status": "under_review"}
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "under_review"

    missing = client.patch(
        "/api/manuscripts/no-such", json={"status": "accepted"}
    )
    assert missing.status_code == 404


def test_pagination_envelope_respects_skip_and_limit(client: TestClient) -> None:
    author = _make_author(client, "Prolific")
    for i in range(5):
        _make_manuscript(client, author["id"], title=f"Title {i:02d}", genre=None)

    page = client.get("/api/manuscripts?skip=2&limit=2").json()
    assert page["total"] == 5
    assert page["skip"] == 2
    assert page["limit"] == 2
    assert len(page["items"]) == 2


def test_pagination_rejects_invalid_limit(client: TestClient) -> None:
    r = client.get("/api/manuscripts?limit=0")
    assert r.status_code == 422


def test_review_workflow_full_chain(
    client: TestClient, session: Session
) -> None:
    # Reviews need a User; users are only created via seed/session in this build.
    reviewer = User(
        email="reviewer@logosforge.test",
        full_name="Test Reviewer",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    session.add(reviewer)
    session.commit()
    session.refresh(reviewer)

    author = _make_author(client)
    manuscript = _make_manuscript(client, author["id"])

    created = client.post(
        "/api/reviews",
        json={
            "manuscript_id": manuscript["id"],
            "reviewer_id": reviewer.id,
            "verdict": "accept",
            "summary": "Strong.",
            "rating": 4,
        },
    )
    assert created.status_code == 201
    review_id = created.json()["id"]

    listed = client.get(
        f"/api/reviews?manuscript_id={manuscript['id']}"
    ).json()
    assert listed["total"] == 1

    patched = client.patch(
        f"/api/reviews/{review_id}", json={"rating": 5}
    ).json()
    assert patched["rating"] == 5

    bad = client.post(
        "/api/reviews",
        json={
            "manuscript_id": manuscript["id"],
            "reviewer_id": "nonexistent",
            "verdict": "accept",
            "summary": "x",
        },
    )
    assert bad.status_code == 404
    assert bad.json()["detail"] == "User not found"


def test_workflow_event_with_null_actor(
    client: TestClient, session: Session
) -> None:
    author = Author(full_name="Direct Insert")
    session.add(author)
    session.commit()
    session.refresh(author)
    manuscript = _make_manuscript(client, author.id)

    created = client.post(
        "/api/workflow-events",
        json={
            "manuscript_id": manuscript["id"],
            "to_status": WorkflowStatus.SUBMITTED.value,
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["actor_id"] is None
    assert body["to_status"] == "submitted"


def test_contract_create_and_filter(client: TestClient, session: Session) -> None:
    author = _make_author(client)
    manuscript = _make_manuscript(client, author["id"])

    r = client.post(
        "/api/contracts",
        json={
            "manuscript_id": manuscript["id"],
            "author_id": author["id"],
            "advance_amount": "1500.00",
            "royalty_rate": 0.12,
            "currency": "EUR",
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["currency"] == "EUR"

    by_author = client.get(f"/api/contracts?author_id={author['id']}").json()
    assert by_author["total"] == 1

    by_status = client.get("/api/contracts?status=signed").json()
    assert by_status["total"] == 0


def test_production_item_create_and_update(
    client: TestClient, session: Session
) -> None:
    designer = User(
        email="designer@logosforge.test",
        full_name="Designer",
        role=UserRole.PRODUCTION_MANAGER,
        hashed_password=hash_password("password"),
    )
    session.add(designer)
    session.commit()
    session.refresh(designer)

    author = _make_author(client)
    manuscript = _make_manuscript(client, author["id"])

    created = client.post(
        "/api/production-items",
        json={
            "manuscript_id": manuscript["id"],
            "assignee_id": designer.id,
            "stage": "layout",
        },
    )
    assert created.status_code == 201
    item = created.json()
    assert item["status"] == "pending"

    moved = client.patch(
        f"/api/production-items/{item['id']}", json={"status": "in_progress"}
    ).json()
    assert moved["status"] == "in_progress"


def test_editorial_note_lifecycle(client: TestClient, session: Session) -> None:
    user = User(
        email="copy@logosforge.test",
        full_name="Copy",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    author = _make_author(client)
    manuscript = _make_manuscript(client, author["id"])

    created = client.post(
        "/api/editorial-notes",
        json={
            "manuscript_id": manuscript["id"],
            "author_user_id": user.id,
            "kind": "line",
            "body": "Trim chapter four.",
            "pinned": True,
        },
    )
    assert created.status_code == 201
    note_id = created.json()["id"]

    pinned_only = client.get("/api/editorial-notes?pinned=true").json()
    assert pinned_only["total"] == 1

    deleted = client.delete(f"/api/editorial-notes/{note_id}")
    assert deleted.status_code == 204
