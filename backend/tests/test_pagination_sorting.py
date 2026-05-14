"""Pagination edge cases and sort behaviour."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Author, Manuscript
from app.models.enums import WorkflowStatus


def _seed_authors(session: Session, n: int) -> None:
    # Prefix with index so the alphabetic order is predictable.
    session.add_all(
        Author(full_name=f"{chr(ord('A') + (i % 26))}{i:03d}", country="X")
        for i in range(n)
    )
    session.commit()


# --- pagination edges ---------------------------------------------------


def test_skip_beyond_total_returns_empty_items(
    anon_client: TestClient, session: Session
) -> None:
    _seed_authors(session, 3)
    body = anon_client.get("/api/authors?skip=999&limit=10").json()
    assert body["total"] == 3
    assert body["items"] == []
    assert body["skip"] == 999
    assert body["limit"] == 10


def test_zero_limit_is_rejected(anon_client: TestClient) -> None:
    r = anon_client.get("/api/authors?limit=0")
    assert r.status_code == 422


def test_limit_above_cap_is_rejected(anon_client: TestClient) -> None:
    r = anon_client.get("/api/authors?limit=500")
    assert r.status_code == 422


def test_negative_skip_is_rejected(anon_client: TestClient) -> None:
    r = anon_client.get("/api/authors?skip=-1")
    assert r.status_code == 422


def test_default_limit_when_unspecified(
    anon_client: TestClient, session: Session
) -> None:
    _seed_authors(session, 2)
    body = anon_client.get("/api/authors").json()
    assert body["limit"] == 50  # documented default
    assert body["skip"] == 0


# --- sort ---------------------------------------------------------------


def test_authors_sort_by_name_asc_default(
    anon_client: TestClient, session: Session
) -> None:
    session.add_all(
        [
            Author(full_name="Zalman"),
            Author(full_name="Aldoria"),
            Author(full_name="Marcus"),
        ]
    )
    session.commit()

    body = anon_client.get("/api/authors").json()
    names = [a["full_name"] for a in body["items"]]
    assert names == sorted(names)


def test_authors_sort_dir_desc(
    anon_client: TestClient, session: Session
) -> None:
    session.add_all([Author(full_name=name) for name in ("A", "M", "Z")])
    session.commit()
    body = anon_client.get("/api/authors?sort_dir=desc").json()
    assert [a["full_name"] for a in body["items"]] == ["Z", "M", "A"]


def test_authors_sort_by_unknown_field_is_rejected(
    anon_client: TestClient,
) -> None:
    r = anon_client.get("/api/authors?sort_by=email")
    assert r.status_code == 422


def test_manuscripts_sort_by_title(
    anon_client: TestClient, session: Session
) -> None:
    a = Author(full_name="Author")
    session.add(a)
    session.commit()
    session.refresh(a)
    session.add_all(
        [
            Manuscript(title="C", author_id=a.id, status=WorkflowStatus.SUBMITTED),
            Manuscript(title="A", author_id=a.id, status=WorkflowStatus.SUBMITTED),
            Manuscript(title="B", author_id=a.id, status=WorkflowStatus.SUBMITTED),
        ]
    )
    session.commit()

    body = anon_client.get(
        "/api/manuscripts?sort_by=title&sort_dir=asc"
    ).json()
    assert [m["title"] for m in body["items"]] == ["A", "B", "C"]


def test_manuscripts_sort_dir_must_be_asc_or_desc(
    anon_client: TestClient,
) -> None:
    r = anon_client.get("/api/manuscripts?sort_dir=sideways")
    assert r.status_code == 422
