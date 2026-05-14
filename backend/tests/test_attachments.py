from __future__ import annotations

import io

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Author, Manuscript
from app.models.enums import WorkflowStatus


def _seed_manuscript(session: Session, title: str = "Folio") -> Manuscript:
    a = Author(full_name="Test Author")
    session.add(a)
    session.commit()
    session.refresh(a)
    m = Manuscript(title=title, author_id=a.id, status=WorkflowStatus.ACCEPTED)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


def test_placeholder_lifecycle(client: TestClient, session: Session) -> None:
    m = _seed_manuscript(session)

    created = client.post(
        "/api/attachments",
        json={
            "manuscript_id": m.id,
            "filename": "draft-v1.docx",
            "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size_bytes": 102400,
            "kind": "manuscript_draft",
            "description": "First complete draft.",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["is_placeholder"] is True
    assert body["storage_key"].startswith("placeholder:")
    assert body["uploader_name"]  # denormalised name present

    listed = client.get(f"/api/attachments?manuscript_id={m.id}").json()
    assert listed["total"] == 1
    assert listed["items"][0]["filename"] == "draft-v1.docx"

    patched = client.patch(
        f"/api/attachments/{body['id']}",
        json={"description": "Revised first complete draft."},
    ).json()
    assert patched["description"] == "Revised first complete draft."

    # Placeholder download returns 410.
    gone = client.get(f"/api/attachments/{body['id']}/download")
    assert gone.status_code == 410


def test_placeholder_requires_existing_manuscript(client: TestClient) -> None:
    r = client.post(
        "/api/attachments",
        json={"manuscript_id": "no-such", "filename": "x.bin"},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Manuscript not found"


def test_placeholder_requires_auth(
    anon_client: TestClient, session: Session
) -> None:
    m = _seed_manuscript(session)
    r = anon_client.post(
        "/api/attachments",
        json={"manuscript_id": m.id, "filename": "x.bin"},
    )
    assert r.status_code == 401


def test_delete_requires_admin(
    editor_client: TestClient, client: TestClient, session: Session
) -> None:
    m = _seed_manuscript(session)
    created = client.post(
        "/api/attachments",
        json={"manuscript_id": m.id, "filename": "doomed.bin"},
    ).json()
    refused = editor_client.delete(f"/api/attachments/{created['id']}")
    assert refused.status_code == 403


def test_upload_writes_bytes_and_streams_back(
    client: TestClient, session: Session, monkeypatch, tmp_path
) -> None:
    from app.services import storage as storage_mod

    # Point the cached storage at a temp path scoped to this test.
    monkeypatch.setattr(
        storage_mod, "_storage", storage_mod.LocalFileStorage(tmp_path)
    )

    m = _seed_manuscript(session)
    payload = b"Hello, archive!\n"
    response = client.post(
        "/api/attachments/upload",
        data={
            "manuscript_id": m.id,
            "kind": "manuscript_draft",
            "description": "Hand-typed sample.",
        },
        files={"file": ("draft.txt", io.BytesIO(payload), "text/plain")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["is_placeholder"] is False
    assert body["size_bytes"] == len(payload)
    assert body["sha256"]
    assert body["filename"] == "draft.txt"
    assert body["storage_key"].startswith("attachments/")

    # The file lives on the temp storage root.
    on_disk = tmp_path / body["storage_key"]
    assert on_disk.read_bytes() == payload

    download = client.get(f"/api/attachments/{body['id']}/download")
    assert download.status_code == 200
    assert download.content == payload
    # Content-Disposition uses the original filename.
    assert "draft.txt" in download.headers.get("content-disposition", "")
