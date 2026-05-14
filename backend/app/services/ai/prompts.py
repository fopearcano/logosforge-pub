"""Shared prompt-building helpers.

Each feature builds on a single ``manuscript_excerpt`` formatter so the
information any model sees about a manuscript is consistent across
features.
"""
from __future__ import annotations

import json
from typing import Optional

from app.services.exports.base import ManuscriptExportBundle


_MAX_SYNOPSIS = 1200  # characters; the bundle's synopsis is often short
_MAX_REVIEWS = 5
_MAX_NOTES = 5


def manuscript_excerpt(bundle: ManuscriptExportBundle) -> str:
    """A compact, structured snapshot of a manuscript for the prompt body.

    Kept deliberately short so the prompt doesn't balloon past common
    context windows. Heavier passes can build their own excerpts.
    """
    m = bundle.manuscript
    lines: list[str] = []
    lines.append(f"TITLE: {m.title}")
    if m.subtitle:
        lines.append(f"SUBTITLE: {m.subtitle}")
    if bundle.author:
        lines.append(f"AUTHOR: {bundle.author.full_name}")
        if bundle.author.country:
            lines.append(f"AUTHOR_COUNTRY: {bundle.author.country}")
    lines.append(f"STATUS: {m.status.value}")
    if m.genre:
        lines.append(f"GENRE: {m.genre}")
    lines.append(f"LANGUAGE: {m.language}")
    if m.word_count is not None:
        lines.append(f"WORD_COUNT: {m.word_count}")
    if m.synopsis:
        synopsis = m.synopsis.strip()
        if len(synopsis) > _MAX_SYNOPSIS:
            synopsis = synopsis[:_MAX_SYNOPSIS].rstrip() + "…"
        lines.append("SYNOPSIS:")
        lines.append(synopsis)

    if bundle.reviews:
        lines.append("")
        lines.append(f"REVIEWS ({len(bundle.reviews)} on file):")
        for r in bundle.reviews[:_MAX_REVIEWS]:
            reviewer = r.reviewer.full_name if r.reviewer else "anonymous"
            rating = f" · {r.rating}/5" if r.rating is not None else ""
            lines.append(
                f"- [{r.verdict.value}{rating}] {reviewer}: {_clip(r.summary, 240)}"
            )

    if bundle.editorial_notes:
        lines.append("")
        lines.append(f"EDITORIAL NOTES ({len(bundle.editorial_notes)} on file):")
        for n in bundle.editorial_notes[:_MAX_NOTES]:
            lines.append(
                f"- [{n.kind.value}] {_clip(n.body, 240)}"
            )

    return "\n".join(lines)


def _clip(text: str, limit: int) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def parse_json_object(content: str) -> Optional[dict]:
    """Permissive JSON extractor.

    LLMs commonly answer with prose surrounding a JSON object. Try the
    raw content first; if that fails, look for the first balanced
    ``{...}`` block. Returns ``None`` when nothing parses.
    """
    text = content.strip()
    try:
        result = json.loads(text)
        return result if isinstance(result, dict) else None
    except (json.JSONDecodeError, TypeError):
        pass

    # Heuristic: find a balanced JSON object somewhere in the text.
    start = text.find("{")
    while start != -1:
        depth = 0
        for idx in range(start, len(text)):
            ch = text[idx]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : idx + 1]
                    try:
                        result = json.loads(candidate)
                        if isinstance(result, dict):
                            return result
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None
