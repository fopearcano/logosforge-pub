from __future__ import annotations

from typing import Optional, Sequence

import httpx

from app.services.ai.providers.base import (
    ChatMessage,
    CompletionResult,
    LLMProvider,
)


class OpenAICompatibleProvider(LLMProvider):
    """Calls any backend that speaks ``POST /v1/chat/completions``.

    Works for OpenAI, OpenRouter, LM Studio, llama.cpp's server, and
    most Ollama deployments running the OpenAI shim.
    """

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        default_model: str,
        api_key: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.api_key = api_key
        self.timeout = timeout

    def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> CompletionResult:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body: dict[str, object] = {
            "model": model or self.default_model,
            "messages": [m.as_openai() for m in messages],
        }
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ValueError(
                f"Unexpected response shape from {self.name}: {data!r}"
            ) from exc

        return CompletionResult(
            content=content,
            model=str(data.get("model", body["model"])),
            provider=self.name,
            usage=data.get("usage"),
        )
