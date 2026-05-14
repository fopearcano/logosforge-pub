from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.services.ai.prompts import manuscript_excerpt, parse_json_object
from app.services.ai.providers.base import ChatMessage, LLMProvider
from app.services.exports.base import ManuscriptExportBundle


class ConsistencyIssue(BaseModel):
    kind: str  # e.g. "name" | "timeline" | "place" | "fact"
    where: Optional[str] = None
    description: str = ""


class ConsistencyCheckResult(BaseModel):
    issues: list[ConsistencyIssue] = []


_SYSTEM_PROMPT = """FEATURE:consistency_check
You are a narrative-consistency reader for a literary press.
Inspect the manuscript metadata, synopsis, and any editorial notes.
Surface 0–6 potential consistency issues. Each issue:

* kind: one of name / timeline / place / fact / continuity
* where: a short locator (chapter, paragraph, or 'unspecified')
* description: one sentence

If there are no concerns to surface, return an empty list.

Respond as a single JSON object: {"issues": [{"kind": "...", "where": "...", "description": "..."}]}"""


def run_consistency_check(
    bundle: ManuscriptExportBundle, provider: LLMProvider
) -> ConsistencyCheckResult:
    response = provider.chat(
        messages=[
            ChatMessage(role="system", content=_SYSTEM_PROMPT),
            ChatMessage(role="user", content=manuscript_excerpt(bundle)),
        ],
        temperature=0.4,
        max_tokens=420,
    )
    parsed = parse_json_object(response.content) or {}
    raw = parsed.get("issues") or []
    issues: list[ConsistencyIssue] = []
    if isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict):
                issues.append(
                    ConsistencyIssue(
                        kind=str(entry.get("kind", "fact")),
                        where=(
                            str(entry["where"])
                            if entry.get("where") is not None
                            else None
                        ),
                        description=str(entry.get("description", "")),
                    )
                )
    return ConsistencyCheckResult(issues=issues)
