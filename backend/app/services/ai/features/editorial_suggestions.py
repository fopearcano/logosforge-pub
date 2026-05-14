from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.services.ai.prompts import manuscript_excerpt, parse_json_object
from app.services.ai.providers.base import ChatMessage, LLMProvider
from app.services.exports.base import ManuscriptExportBundle


class EditorialSuggestion(BaseModel):
    kind: str  # e.g. "structural" | "line" | "design"
    title: str
    rationale: Optional[str] = None


class EditorialSuggestionsResult(BaseModel):
    suggestions: list[EditorialSuggestion] = []


_SYSTEM_PROMPT = """FEATURE:editorial_suggestions
You are an editorial advisor at a literary press.
Read the manuscript metadata, synopsis, reviews, and notes, then offer
2–5 concrete suggestions. Each suggestion needs:

* kind: one of structural / line / pacing / design / production
* title: a short imperative phrase
* rationale: one or two sentences

Respond as a single JSON object:
{"suggestions": [{"kind": "...", "title": "...", "rationale": "..."}]}"""


def run_editorial_suggestions(
    bundle: ManuscriptExportBundle, provider: LLMProvider
) -> EditorialSuggestionsResult:
    response = provider.chat(
        messages=[
            ChatMessage(role="system", content=_SYSTEM_PROMPT),
            ChatMessage(role="user", content=manuscript_excerpt(bundle)),
        ],
        temperature=0.5,
        max_tokens=520,
    )
    parsed = parse_json_object(response.content) or {}
    raw = parsed.get("suggestions") or []
    suggestions: list[EditorialSuggestion] = []
    if isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict):
                suggestions.append(
                    EditorialSuggestion(
                        kind=str(entry.get("kind", "general")),
                        title=str(entry.get("title", "")),
                        rationale=(
                            str(entry["rationale"])
                            if entry.get("rationale") is not None
                            else None
                        ),
                    )
                )
    return EditorialSuggestionsResult(suggestions=suggestions)
