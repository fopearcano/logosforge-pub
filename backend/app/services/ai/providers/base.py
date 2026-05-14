from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Protocol, Sequence


ChatRole = Literal["system", "user", "assistant"]


@dataclass
class ChatMessage:
    role: ChatRole
    content: str

    def as_openai(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class CompletionResult:
    content: str
    model: str
    provider: str
    usage: Optional[dict] = field(default=None)


class LLMProvider(Protocol):
    """Anything that can answer a chat completion request.

    Implementations must be cheap to construct (so the registry can
    cache them) and synchronous. Concurrency is the route layer's
    concern.
    """

    name: str

    def chat(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> CompletionResult:
        ...
