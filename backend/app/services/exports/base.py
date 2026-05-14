from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Protocol

from app.models import (
    Author,
    EditorialNote,
    Manuscript,
    Review,
    WorkflowEvent,
)


@dataclass
class ManuscriptExportBundle:
    """Everything an exporter needs to render a manuscript.

    Held by value so exporters can be exercised in isolation from a
    Session — the route layer materialises the bundle once.
    """

    manuscript: Manuscript
    author: Optional[Author]
    workflow_events: list[WorkflowEvent]
    reviews: list[Review]
    editorial_notes: list[EditorialNote]


class Exporter(Protocol):
    """Render a bundle into bytes for download.

    `body` is whatever bytes the response carries. `media_type` is the
    HTTP Content-Type. `extension` is the suggested filename suffix
    (no leading dot).
    """

    media_type: str
    extension: str

    def render(self, bundle: ManuscriptExportBundle) -> bytes:
        ...


_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def slugify_for_filename(value: str) -> str:
    slug = _SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug or "manuscript"
