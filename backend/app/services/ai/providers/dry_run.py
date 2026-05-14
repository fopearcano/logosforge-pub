from __future__ import annotations

import json
from typing import Optional, Sequence

from app.services.ai.providers.base import (
    ChatMessage,
    CompletionResult,
    LLMProvider,
)


# Each feature embeds a tag in its system prompt; the dry-run provider
# pattern-matches the tag and returns deterministic JSON the feature
# parser can ingest.  This keeps the full call → parse cycle exercised
# without network access.
_CANNED_PAYLOADS: dict[str, dict] = {
    "FEATURE:summarize": {
        "one_line": "A quiet, archival workshop novel.",
        "summary": (
            "A short editorial summary placeholder. Connect a real "
            "provider (LM Studio, OpenAI, OpenRouter, …) to replace "
            "this with grounded text."
        ),
        "themes": ["archive", "labour", "letters"],
    },
    "FEATURE:style_analysis": {
        "register": "literary · restrained",
        "voice": "third-person, past tense, dry humour in long sentences",
        "rhythm": "long → short → long; comma-led parentheticals throughout",
        "concerns": [
            "Long opening paragraphs may slow the first chapter.",
            "Dialogue tags occasionally telegraph the next emotion.",
        ],
    },
    "FEATURE:editorial_suggestions": {
        "suggestions": [
            {
                "kind": "structural",
                "title": "Compress the central correspondence",
                "rationale": "The middle third loses momentum across letters 8–14.",
            },
            {
                "kind": "line",
                "title": "Tighten chapter three",
                "rationale": "Two paragraphs restate the same image.",
            },
        ]
    },
    "FEATURE:semantic_tags": {
        "tags": ["epistolary", "provincial-life", "20th-century", "memory", "letters"],
    },
    "FEATURE:consistency_check": {
        "issues": [
            {
                "kind": "name",
                "where": "ch. 4 vs ch. 11",
                "description": "Character spelled 'Iren' early and 'Iryn' later.",
            }
        ]
    },
}

_DEFAULT_PAYLOAD = {
    "note": (
        "Dry-run AI provider · canned response. Configure AI_PROVIDER + "
        "AI_BASE_URL to call a real backend."
    )
}


class DryRunProvider(LLMProvider):
    """A deterministic stub provider that never leaves the process.

    The default in development, in tests, and whenever AI_PROVIDER is
    unset.
    """

    name = "dry_run"

    def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> CompletionResult:
        joined = "\n".join(m.content for m in messages)
        payload = _DEFAULT_PAYLOAD
        for tag, canned in _CANNED_PAYLOADS.items():
            if tag in joined:
                payload = canned
                break

        return CompletionResult(
            content=json.dumps(payload, ensure_ascii=False),
            model=model or "stub",
            provider=self.name,
            usage=None,
        )
