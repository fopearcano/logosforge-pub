"""Provider abstraction tests.

The dry-run provider is exercised end-to-end; the OpenAI-compatible
provider has its HTTP call mocked so we never touch the network.
"""
from __future__ import annotations

import json

import httpx
import pytest

from app.services.ai.providers import (
    ChatMessage,
    DryRunProvider,
    KNOWN_PROVIDERS,
    OpenAICompatibleProvider,
    PROVIDER_DEFAULTS,
    get_provider,
    reset_provider_cache,
)


# --- dry-run ------------------------------------------------------------


def test_dry_run_returns_feature_specific_payloads() -> None:
    p = DryRunProvider()
    summary = p.chat([ChatMessage("system", "FEATURE:summarize ...")])
    assert "themes" in summary.content
    assert json.loads(summary.content)["themes"]

    tags = p.chat([ChatMessage("system", "FEATURE:semantic_tags ...")])
    assert "tags" in tags.content

    style = p.chat([ChatMessage("system", "FEATURE:style_analysis ...")])
    assert "voice" in style.content


def test_dry_run_falls_back_to_generic_payload() -> None:
    p = DryRunProvider()
    res = p.chat([ChatMessage("system", "no feature tag here")])
    assert "Dry-run AI provider" in res.content


def test_dry_run_records_provider_and_model() -> None:
    res = DryRunProvider().chat(
        [ChatMessage("system", "FEATURE:summarize")], model="my-stub"
    )
    assert res.provider == "dry_run"
    assert res.model == "my-stub"
    assert res.usage is None


# --- openai-compatible (mocked HTTP) ------------------------------------


def test_openai_compatible_builds_request_and_parses_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict = {}

    class _MockResponse:
        status_code = 200

        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self._payload

    def fake_post(url, *, headers, json, timeout):  # noqa: A002 (shadow ok in mock)
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return _MockResponse(
            {
                "model": "gpt-4o-mini",
                "choices": [
                    {"message": {"role": "assistant", "content": "hello"}}
                ],
                "usage": {"prompt_tokens": 4, "completion_tokens": 1},
            }
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    provider = OpenAICompatibleProvider(
        name="openai",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
        api_key="sk-test",
        timeout=5.0,
    )
    result = provider.chat(
        [
            ChatMessage("system", "be brief"),
            ChatMessage("user", "hi"),
        ],
        temperature=0.5,
        max_tokens=64,
    )

    # Request shape
    assert captured["url"] == "https://api.openai.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert captured["headers"]["Content-Type"] == "application/json"
    body = captured["json"]
    assert body["model"] == "gpt-4o-mini"
    assert body["temperature"] == 0.5
    assert body["max_tokens"] == 64
    assert body["messages"] == [
        {"role": "system", "content": "be brief"},
        {"role": "user", "content": "hi"},
    ]
    assert captured["timeout"] == 5.0

    # Parsed response
    assert result.content == "hello"
    assert result.model == "gpt-4o-mini"
    assert result.provider == "openai"
    assert result.usage == {"prompt_tokens": 4, "completion_tokens": 1}


def test_openai_compatible_raises_on_unexpected_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Empty:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": []}

    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _Empty())

    provider = OpenAICompatibleProvider(
        name="x", base_url="http://x/v1", default_model="m"
    )
    with pytest.raises(ValueError):
        provider.chat([ChatMessage("user", "hi")])


# --- registry / settings -----------------------------------------------


def test_registry_returns_dry_run_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "ai_provider", "dry_run")
    reset_provider_cache()
    p = get_provider()
    assert p.name == "dry_run"


def test_registry_builds_openai_compatible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "ai_provider", "openrouter")
    monkeypatch.setattr(settings, "ai_base_url", None)  # fall back to default
    monkeypatch.setattr(settings, "ai_model", "anthropic/claude-3.5-sonnet")
    monkeypatch.setattr(settings, "ai_api_key", "or-test")
    reset_provider_cache()
    p = get_provider()
    assert p.name == "openrouter"
    assert getattr(p, "base_url") == PROVIDER_DEFAULTS["openrouter"]
    assert getattr(p, "default_model") == "anthropic/claude-3.5-sonnet"


def test_registry_requires_base_url_for_openai_compatible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "ai_provider", "openai_compatible")
    monkeypatch.setattr(settings, "ai_base_url", None)
    reset_provider_cache()
    with pytest.raises(ValueError):
        get_provider()


def test_registry_rejects_unknown_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "ai_provider", "intuition")
    reset_provider_cache()
    with pytest.raises(ValueError):
        get_provider()


def test_known_providers_includes_each_documented_backend() -> None:
    assert "dry_run" in KNOWN_PROVIDERS
    assert "openai" in KNOWN_PROVIDERS
    assert "openrouter" in KNOWN_PROVIDERS
    assert "lm_studio" in KNOWN_PROVIDERS
