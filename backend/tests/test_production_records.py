from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Author, Manuscript
from app.models.enums import WorkflowStatus


def _author_and_manuscript(session: Session, title: str = "Sample") -> tuple[Author, Manuscript]:
    author = Author(full_name="Test Author")
    session.add(author)
    session.commit()
    session.refresh(author)
    m = Manuscript(
        title=title,
        author_id=author.id,
        status=WorkflowStatus.ACCEPTED,
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    return author, m


def test_record_crud_lifecycle(client: TestClient, session: Session) -> None:
    _, manuscript = _author_and_manuscript(session)

    created = client.post(
        "/api/production-records",
        json={
            "manuscript_id": manuscript.id,
            "isbn": "978-0-00-000001-1",
            "release_date": str(date.today() + timedelta(days=60)),
            "print_status": "pending",
            "cover_status": "in_progress",
        },
    )
    assert created.status_code == 201, created.text
    record = created.json()
    assert record["isbn"] == "978-0-00-000001-1"
    assert record["print_status"] == "pending"
    assert record["cover_status"] == "in_progress"
    # Other streams default to not_planned.
    assert record["audiobook_status"] == "not_planned"

    record_id = record["id"]

    fetched = client.get(f"/api/production-records/{record_id}").json()
    assert fetched["manuscript_id"] == manuscript.id

    by_ms = client.get(
        f"/api/production-records/by-manuscript/{manuscript.id}"
    ).json()
    assert by_ms["id"] == record_id

    patched = client.patch(
        f"/api/production-records/{record_id}",
        json={"print_status": "complete", "isbn": None},
    ).json()
    assert patched["print_status"] == "complete"
    assert patched["isbn"] is None

    deleted = client.delete(f"/api/production-records/{record_id}")
    assert deleted.status_code == 204
    missing = client.get(f"/api/production-records/{record_id}")
    assert missing.status_code == 404


def test_create_requires_existing_manuscript(client: TestClient) -> None:
    r = client.post(
        "/api/production-records",
        json={"manuscript_id": "no-such-manuscript"},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Manuscript not found"


def test_create_prevents_duplicate_per_manuscript(
    client: TestClient, session: Session
) -> None:
    _, manuscript = _author_and_manuscript(session)
    first = client.post(
        "/api/production-records",
        json={"manuscript_id": manuscript.id},
    )
    assert first.status_code == 201
    second = client.post(
        "/api/production-records",
        json={"manuscript_id": manuscript.id},
    )
    assert second.status_code == 409


def test_create_requires_auth(
    anon_client: TestClient, session: Session
) -> None:
    _, manuscript = _author_and_manuscript(session)
    r = anon_client.post(
        "/api/production-records",
        json={"manuscript_id": manuscript.id},
    )
    assert r.status_code == 401


def test_delete_requires_admin(
    editor_client: TestClient, client: TestClient, session: Session
) -> None:
    _, manuscript = _author_and_manuscript(session)
    created = client.post(
        "/api/production-records",
        json={"manuscript_id": manuscript.id},
    ).json()
    refused = editor_client.delete(f"/api/production-records/{created['id']}")
    assert refused.status_code == 403


def test_list_filters_by_release_window_and_returns_manuscript_context(
    client: TestClient, session: Session
) -> None:
    today = date.today()
    _, m1 = _author_and_manuscript(session, "Near Release")
    _, m2 = _author_and_manuscript(session, "Far Release")
    _, m3 = _author_and_manuscript(session, "Unscheduled")

    client.post(
        "/api/production-records",
        json={
            "manuscript_id": m1.id,
            "release_date": str(today + timedelta(days=10)),
        },
    )
    client.post(
        "/api/production-records",
        json={
            "manuscript_id": m2.id,
            "release_date": str(today + timedelta(days=200)),
        },
    )
    client.post(
        "/api/production-records",
        json={"manuscript_id": m3.id},  # no release_date
    )

    # Has-release-date filter.
    with_dates = client.get(
        "/api/production-records?has_release_date=true"
    ).json()
    assert with_dates["total"] == 2
    titles = [r["manuscript_title"] for r in with_dates["items"]]
    # Sorted soonest first.
    assert titles == ["Near Release", "Far Release"]
    # Manuscript context denormalised.
    assert with_dates["items"][0]["author_name"] == "Test Author"
    assert with_dates["items"][0]["manuscript_status"] == "accepted"

    # Date-range filter excludes the far one.
    near = client.get(
        f"/api/production-records?release_from={today}&release_to={today + timedelta(days=30)}"
    ).json()
    assert near["total"] == 1
    assert near["items"][0]["manuscript_title"] == "Near Release"

    # has_release_date=false returns only the unscheduled one.
    unscheduled = client.get(
        "/api/production-records?has_release_date=false"
    ).json()
    assert unscheduled["total"] == 1
    assert unscheduled["items"][0]["manuscript_title"] == "Unscheduled"


def test_by_manuscript_404_when_no_record(
    anon_client: TestClient, session: Session
) -> None:
    _, manuscript = _author_and_manuscript(session)
    r = anon_client.get(
        f"/api/production-records/by-manuscript/{manuscript.id}"
    )
    assert r.status_code == 404
