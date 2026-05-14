from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.security import hash_password
from app.models import (
    Author,
    EditorialNote,
    Manuscript,
    Review,
    User,
    WorkflowEvent,
)
from app.models.enums import (
    EditorialNoteKind,
    ReviewVerdict,
    UserRole,
    WorkflowStatus,
)


def _seed_full_manuscript(session: Session) -> Manuscript:
    editor = User(
        email="exporter@logosforge.test",
        full_name="House Editor",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    author = Author(
        full_name="Iris Aldoria",
        country="Portugal",
        biography="Essayist of inland seas.",
    )
    session.add_all([editor, author])
    session.commit()
    session.refresh(editor)
    session.refresh(author)

    m = Manuscript(
        title="The Salt Atlases",
        subtitle="A cartography of inland seas",
        synopsis="Twelve essays on the salt seas of Europe.",
        genre="Essays",
        language="en",
        word_count=68200,
        status=WorkflowStatus.PUBLISHED,
        author_id=author.id,
    )
    session.add(m)
    session.commit()
    session.refresh(m)

    session.add_all(
        [
            WorkflowEvent(
                manuscript_id=m.id,
                from_status=None,
                to_status=WorkflowStatus.SUBMITTED,
            ),
            WorkflowEvent(
                manuscript_id=m.id,
                actor_id=editor.id,
                from_status=WorkflowStatus.SUBMITTED,
                to_status=WorkflowStatus.UNDER_REVIEW,
                note="Routed to Helena.",
            ),
            Review(
                manuscript_id=m.id,
                reviewer_id=editor.id,
                verdict=ReviewVerdict.ACCEPT,
                summary="Original synthesis.",
                rating=5,
            ),
            EditorialNote(
                manuscript_id=m.id,
                author_user_id=editor.id,
                kind=EditorialNoteKind.STRUCTURAL,
                body="Re-order the chapters chronologically.",
                pinned=True,
            ),
        ]
    )
    session.commit()
    return m


def test_export_lists_formats(anon_client: TestClient) -> None:
    formats = anon_client.get("/api/exports/formats").json()
    by_format = {f["format"]: f for f in formats}
    assert "markdown" in by_format
    assert "json" in by_format
    assert by_format["markdown"]["extension"] == "md"
    assert by_format["json"]["media_type"] == "application/json"


def test_export_markdown_includes_metadata_and_history(
    anon_client: TestClient, session: Session
) -> None:
    m = _seed_full_manuscript(session)
    r = anon_client.get(f"/api/manuscripts/{m.id}/export?format=markdown")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/markdown")
    cd = r.headers.get("content-disposition", "")
    assert "the-salt-atlases.md" in cd

    body = r.text
    assert "# The Salt Atlases" in body
    assert "_A cartography of inland seas_" in body
    assert "## Metadata" in body
    assert "| Status |" in body
    assert "| Word count | 68,200 |" in body
    assert "## Synopsis" in body
    assert "Twelve essays" in body
    assert "## Workflow chronicle" in body
    assert "Under Review" in body
    assert "Routed to Helena." in body
    assert "## Reviews" in body
    assert "Accept" in body
    assert "Original synthesis." in body
    assert "## Editorial notes" in body
    assert "Structural" in body
    assert "Re-order the chapters chronologically." in body


def test_export_json_is_machine_readable(
    anon_client: TestClient, session: Session
) -> None:
    m = _seed_full_manuscript(session)
    r = anon_client.get(f"/api/manuscripts/{m.id}/export?format=json")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    cd = r.headers.get("content-disposition", "")
    assert "the-salt-atlases.json" in cd

    payload = json.loads(r.text)
    assert payload["schema_version"] == 1
    assert payload["manuscript"]["title"] == "The Salt Atlases"
    assert payload["manuscript"]["status"] == "published"
    assert payload["author"]["full_name"] == "Iris Aldoria"
    assert len(payload["workflow_history"]) == 2
    assert payload["workflow_history"][1]["to_status"] == "under_review"
    assert payload["workflow_history"][1]["actor_name"] == "House Editor"
    assert payload["reviews"][0]["verdict"] == "accept"
    assert payload["editorial_notes"][0]["pinned"] is True
    # exported_at must be a valid ISO datetime.
    datetime.fromisoformat(payload["exported_at"].replace("Z", "+00:00"))


def test_export_pdf_returns_not_implemented(
    anon_client: TestClient, session: Session
) -> None:
    m = _seed_full_manuscript(session)
    r = anon_client.get(f"/api/manuscripts/{m.id}/export?format=pdf")
    assert r.status_code == 501
    assert "pdf" in r.json()["detail"].lower()


def test_export_unknown_manuscript_returns_404(anon_client: TestClient) -> None:
    r = anon_client.get(
        "/api/manuscripts/no-such/export?format=markdown"
    )
    assert r.status_code == 404


def test_export_invalid_format_returns_422(
    anon_client: TestClient, session: Session
) -> None:
    m = _seed_full_manuscript(session)
    r = anon_client.get(f"/api/manuscripts/{m.id}/export?format=xml")
    assert r.status_code == 422
