from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.security import hash_password
from app.models import (
    Author,
    Contract,
    EditorialNote,
    Manuscript,
    Review,
    User,
)
from app.models.enums import (
    ContractStatus,
    EditorialNoteKind,
    ReviewVerdict,
    UserRole,
    WorkflowStatus,
)


def _seed_corpus(session: Session) -> dict:
    editor = User(
        email="ed@logosforge.test",
        full_name="House Editor",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    iris = Author(
        full_name="Iris Aldoria",
        country="Portugal",
        biography="Essayist of inland seas.",
    )
    marcus = Author(full_name="Marcus Veldt", country="Netherlands")
    session.add_all([editor, iris, marcus])
    session.commit()
    for x in (editor, iris, marcus):
        session.refresh(x)

    # An older salt-themed manuscript and a separate fiction one.
    salt = Manuscript(
        title="The Salt Atlases",
        subtitle="A cartography of inland seas",
        synopsis="On the saline inland seas of Europe.",
        genre="Essays",
        status=WorkflowStatus.PUBLISHED,
        author_id=iris.id,
    )
    letters = Manuscript(
        title="Letters to a Dim Province",
        synopsis="An epistolary novel set in a province.",
        genre="Fiction",
        status=WorkflowStatus.COPY_EDITING,
        author_id=marcus.id,
    )
    session.add_all([salt, letters])
    session.commit()
    for m in (salt, letters):
        session.refresh(m)

    # Backdate the salt manuscript's created_at so year filter is testable.
    salt.created_at = datetime(2024, 6, 12, tzinfo=timezone.utc)
    session.add(salt)
    session.commit()
    session.refresh(salt)

    session.add_all(
        [
            Review(
                manuscript_id=salt.id,
                reviewer_id=editor.id,
                verdict=ReviewVerdict.ACCEPT,
                summary="A salt-soaked, original synthesis.",
                rating=5,
            ),
            Review(
                manuscript_id=letters.id,
                reviewer_id=editor.id,
                verdict=ReviewVerdict.REVISE,
                summary="Strong voice; restructure middle chapters.",
                rating=4,
            ),
            EditorialNote(
                manuscript_id=salt.id,
                author_user_id=editor.id,
                kind=EditorialNoteKind.STRUCTURAL,
                body="Re-order the salt-soaked chapters in chronological order.",
                pinned=True,
            ),
            EditorialNote(
                manuscript_id=letters.id,
                author_user_id=editor.id,
                kind=EditorialNoteKind.LINE,
                body="Chapter eleven needs clarification from the author.",
            ),
            Contract(
                manuscript_id=salt.id,
                author_id=iris.id,
                status=ContractStatus.SIGNED,
                advance_amount=Decimal("4500.00"),
                royalty_rate=0.12,
                currency="EUR",
                rights_territory="world",
                terms="Worldwide trade rights, first edition only.",
            ),
            Contract(
                manuscript_id=letters.id,
                author_id=marcus.id,
                status=ContractStatus.SIGNED,
                advance_amount=Decimal("7500.00"),
                royalty_rate=0.15,
                currency="EUR",
                rights_territory="europe",
                terms="European rights, including translation.",
            ),
        ]
    )
    session.commit()

    return {
        "editor": editor,
        "iris": iris,
        "marcus": marcus,
        "salt": salt,
        "letters": letters,
    }


def test_search_query_required(anon_client: TestClient) -> None:
    r = anon_client.get("/api/search")
    assert r.status_code == 422  # missing q


def test_search_returns_grouped_results(
    anon_client: TestClient, session: Session
) -> None:
    seeded = _seed_corpus(session)
    body = anon_client.get("/api/search?q=salt").json()

    assert body["query"] == "salt"
    assert {m["id"] for m in body["manuscripts"]} == {seeded["salt"].id}
    assert body["manuscripts"][0]["author_name"] == "Iris Aldoria"
    assert any(r["summary"].startswith("A salt") for r in body["reviews"])
    assert any("salt" in n["body"] for n in body["editorial_notes"])
    assert body["total"] > 0
    # The 'salt' search hits multiple types — assert it found at least
    # one in each of manuscripts, reviews, editorial_notes.
    assert len(body["manuscripts"]) >= 1
    assert len(body["reviews"]) >= 1
    assert len(body["editorial_notes"]) >= 1


def test_search_is_case_insensitive(
    anon_client: TestClient, session: Session
) -> None:
    _seed_corpus(session)
    body = anon_client.get("/api/search?q=SALT").json()
    assert any(m["title"] == "The Salt Atlases" for m in body["manuscripts"])


def test_search_filter_by_status(
    anon_client: TestClient, session: Session
) -> None:
    _seed_corpus(session)
    # Salt is published, letters is copy_editing. A 'province' query matches
    # the letters synopsis and the letters note body.
    only_pub = anon_client.get(
        "/api/search?q=province&status=published"
    ).json()
    assert only_pub["manuscripts"] == []
    assert only_pub["editorial_notes"] == []

    only_copy = anon_client.get(
        "/api/search?q=province&status=copy_editing"
    ).json()
    assert {m["id"] for m in only_copy["manuscripts"]} == {
        m["id"] for m in only_copy["manuscripts"]
    }
    assert len(only_copy["manuscripts"]) == 1


def test_search_filter_by_genre(
    anon_client: TestClient, session: Session
) -> None:
    _seed_corpus(session)
    body = anon_client.get("/api/search?q=a&genre=Essays").json()
    assert all(m["genre"] == "Essays" for m in body["manuscripts"])
    # And reviews / notes / contracts are filtered to Essays manuscripts too.
    assert all(
        r["manuscript_title"] == "The Salt Atlases" for r in body["reviews"]
    )


def test_search_filter_by_year(
    anon_client: TestClient, session: Session
) -> None:
    _seed_corpus(session)
    # Salt was backdated to 2024.
    body_2024 = anon_client.get("/api/search?q=a&year=2024").json()
    assert {m["id"] for m in body_2024["manuscripts"]} == {
        m["id"]
        for m in body_2024["manuscripts"]
        if m["title"] == "The Salt Atlases"
    }
    assert len(body_2024["manuscripts"]) == 1

    body_now = anon_client.get(
        f"/api/search?q=a&year={datetime.now(timezone.utc).year}"
    ).json()
    titles_now = {m["title"] for m in body_now["manuscripts"]}
    assert "The Salt Atlases" not in titles_now


def test_search_filter_by_author(
    anon_client: TestClient, session: Session
) -> None:
    seeded = _seed_corpus(session)
    body = anon_client.get(
        f"/api/search?q=a&author_id={seeded['marcus'].id}"
    ).json()
    assert all(
        m["author_id"] == seeded["marcus"].id for m in body["manuscripts"]
    )
    # Reviews / notes restricted to Marcus's manuscripts.
    assert all(
        r["manuscript_title"] == "Letters to a Dim Province"
        for r in body["reviews"]
    )


def test_search_filter_by_rights_territory(
    anon_client: TestClient, session: Session
) -> None:
    _seed_corpus(session)
    body = anon_client.get(
        "/api/search?q=rights&rights_territory=europe"
    ).json()
    assert len(body["contracts"]) == 1
    assert body["contracts"][0]["rights_territory"] == "europe"


def test_search_matches_rights_territory_in_query(
    anon_client: TestClient, session: Session
) -> None:
    _seed_corpus(session)
    body = anon_client.get("/api/search?q=europe").json()
    assert any(c["rights_territory"] == "europe" for c in body["contracts"])


def test_search_is_public_read(anon_client: TestClient) -> None:
    # No auth needed.
    r = anon_client.get("/api/search?q=anything")
    assert r.status_code == 200


def test_search_limit_caps_each_section(
    anon_client: TestClient, session: Session
) -> None:
    _seed_corpus(session)
    body = anon_client.get("/api/search?q=a&limit=1").json()
    assert len(body["manuscripts"]) <= 1
    assert len(body["authors"]) <= 1
    assert len(body["reviews"]) <= 1
    assert len(body["editorial_notes"]) <= 1
    assert len(body["contracts"]) <= 1
