from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum

from app.services.exports.base import Exporter, ManuscriptExportBundle


def _default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Cannot serialise {type(value).__name__}")


def _manuscript(m) -> dict:
    return {
        "id": m.id,
        "title": m.title,
        "subtitle": m.subtitle,
        "synopsis": m.synopsis,
        "genre": m.genre,
        "language": m.language,
        "word_count": m.word_count,
        "status": m.status,
        "created_at": m.created_at,
        "updated_at": m.updated_at,
    }


def _author(a) -> dict | None:
    if a is None:
        return None
    return {
        "id": a.id,
        "full_name": a.full_name,
        "country": a.country,
        "biography": a.biography,
        "email": a.email,
    }


def _event(e) -> dict:
    return {
        "id": e.id,
        "from_status": e.from_status,
        "to_status": e.to_status,
        "actor_id": e.actor_id,
        "actor_name": e.actor.full_name if e.actor else None,
        "note": e.note,
        "occurred_at": e.created_at,
    }


def _review(r) -> dict:
    return {
        "id": r.id,
        "verdict": r.verdict,
        "summary": r.summary,
        "rating": r.rating,
        "reviewer_id": r.reviewer_id,
        "reviewer_name": r.reviewer.full_name if r.reviewer else None,
        "created_at": r.created_at,
    }


def _note(n) -> dict:
    return {
        "id": n.id,
        "kind": n.kind,
        "body": n.body,
        "pinned": n.pinned,
        "author_user_id": n.author_user_id,
        "author_user_name": n.author_user.full_name if n.author_user else None,
        "created_at": n.created_at,
    }


class JSONExporter:
    media_type = "application/json"
    extension = "json"

    def render(self, bundle: ManuscriptExportBundle) -> bytes:
        payload = {
            "exported_at": datetime.now(timezone.utc),
            "schema_version": 1,
            "manuscript": _manuscript(bundle.manuscript),
            "author": _author(bundle.author),
            "workflow_history": [_event(e) for e in bundle.workflow_events],
            "reviews": [_review(r) for r in bundle.reviews],
            "editorial_notes": [_note(n) for n in bundle.editorial_notes],
        }
        return json.dumps(
            payload, default=_default, indent=2, ensure_ascii=False
        ).encode("utf-8")
