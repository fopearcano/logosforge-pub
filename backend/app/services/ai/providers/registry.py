from __future__ import annotations

from app.config import settings
from app.services.ai.providers.base import LLMProvider
from app.services.ai.providers.dry_run import DryRunProvider
from app.services.ai.providers.openai_compat import OpenAICompatibleProvider


PROVIDER_DEFAULTS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "lm_studio": "http://localhost:1234/v1",
    # ``openai_compatible`` is the catch-all for anything else; the
    # caller must supply AI_BASE_URL explicitly.
}

KNOWN_PROVIDERS = ("dry_run", *PROVIDER_DEFAULTS.keys(), "openai_compatible")


_cache: dict[str, LLMProvider] = {}


def reset_provider_cache() -> None:
    """Clear the cached provider. Useful in tests."""
    _cache.clear()


def _build_provider() -> LLMProvider:
    kind = (settings.ai_provider or "dry_run").lower()

    if kind == "dry_run":
        return DryRunProvider()

    if kind in PROVIDER_DEFAULTS or kind == "openai_compatible":
        base_url = settings.ai_base_url or PROVIDER_DEFAULTS.get(kind)
        if not base_url:
            raise ValueError(
                f"AI provider '{kind}' requires AI_BASE_URL to be set."
            )
        return OpenAICompatibleProvider(
            name=kind,
            base_url=base_url,
            default_model=settings.ai_model,
            api_key=settings.ai_api_key,
            timeout=settings.ai_request_timeout,
        )

    raise ValueError(
        f"Unknown AI provider: {kind!r}. "
        f"Expected one of: {', '.join(KNOWN_PROVIDERS)}."
    )


def get_provider() -> LLMProvider:
    """Return the configured provider, cached per process."""
    key = settings.ai_provider
    if key not in _cache:
        _cache[key] = _build_provider()
    return _cache[key]
