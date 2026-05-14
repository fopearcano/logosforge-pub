from __future__ import annotations

from pydantic import BaseModel

from app.services.ai.prompts import manuscript_excerpt, parse_json_object
from app.services.ai.providers.base import ChatMessage, LLMProvider
from app.services.exports.base import ManuscriptExportBundle


class SemanticTagsResult(BaseModel):
    tags: list[str] = []


_SYSTEM_PROMPT = """FEATURE:semantic_tags
You are a cataloguer at a literary press. Given the manuscript
metadata and synopsis, propose 5–10 short semantic tags suitable for
faceted search. Use lower-case hyphenated forms. Prefer evergreen
terms (themes, periods, settings, modes) over plot specifics.

Respond as a single JSON object: {"tags": ["...", "..."]}"""


def run_semantic_tags(
    bundle: ManuscriptExportBundle, provider: LLMProvider
) -> SemanticTagsResult:
    response = provider.chat(
        messages=[
            ChatMessage(role="system", content=_SYSTEM_PROMPT),
            ChatMessage(role="user", content=manuscript_excerpt(bundle)),
        ],
        temperature=0.3,
        max_tokens=200,
    )
    parsed = parse_json_object(response.content) or {}
    raw = parsed.get("tags") or []
    if not isinstance(raw, list):
        raw = []
    return SemanticTagsResult(tags=[str(t).strip() for t in raw if str(t).strip()])
