from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.services.ai.prompts import manuscript_excerpt, parse_json_object
from app.services.ai.providers.base import ChatMessage, LLMProvider
from app.services.exports.base import ManuscriptExportBundle


class SummaryResult(BaseModel):
    one_line: Optional[str] = None
    summary: str = ""
    themes: list[str] = []


_SYSTEM_PROMPT = """FEATURE:summarize
You are an editorial assistant at a literary press.
Given the manuscript metadata and synopsis, write three things:

1. a one-line elevator pitch (≤ 14 words)
2. a short editorial summary (3–5 sentences)
3. up to five thematic tags (lower-case, hyphenated, no quotes)

Respond as a single JSON object with keys:
{"one_line": "...", "summary": "...", "themes": ["...", "..."]}"""


def run_summarize(
    bundle: ManuscriptExportBundle, provider: LLMProvider
) -> SummaryResult:
    response = provider.chat(
        messages=[
            ChatMessage(role="system", content=_SYSTEM_PROMPT),
            ChatMessage(role="user", content=manuscript_excerpt(bundle)),
        ],
        temperature=0.4,
        max_tokens=420,
    )
    parsed = parse_json_object(response.content) or {}
    themes = parsed.get("themes") or []
    if not isinstance(themes, list):
        themes = []
    return SummaryResult(
        one_line=parsed.get("one_line"),
        summary=str(parsed.get("summary") or response.content.strip()),
        themes=[str(t) for t in themes],
    )
