from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.services.ai.prompts import manuscript_excerpt, parse_json_object
from app.services.ai.providers.base import ChatMessage, LLMProvider
from app.services.exports.base import ManuscriptExportBundle


class StyleAnalysisResult(BaseModel):
    register: Optional[str] = None
    voice: Optional[str] = None
    rhythm: Optional[str] = None
    concerns: list[str] = []


_SYSTEM_PROMPT = """FEATURE:style_analysis
You are a stylistic reader for a literary press.
Read the manuscript synopsis and any editorial notes, then describe:

1. register (one short clause)
2. voice (one short clause)
3. rhythm (one short clause)
4. concerns: a short list of 1–4 stylistic risks worth surfacing

Respond as a single JSON object with keys:
{"register": "...", "voice": "...", "rhythm": "...", "concerns": ["..."]}"""


def run_style_analysis(
    bundle: ManuscriptExportBundle, provider: LLMProvider
) -> StyleAnalysisResult:
    response = provider.chat(
        messages=[
            ChatMessage(role="system", content=_SYSTEM_PROMPT),
            ChatMessage(role="user", content=manuscript_excerpt(bundle)),
        ],
        temperature=0.5,
        max_tokens=420,
    )
    parsed = parse_json_object(response.content) or {}
    concerns = parsed.get("concerns") or []
    if not isinstance(concerns, list):
        concerns = []
    return StyleAnalysisResult(
        register=parsed.get("register"),
        voice=parsed.get("voice"),
        rhythm=parsed.get("rhythm"),
        concerns=[str(c) for c in concerns],
    )
