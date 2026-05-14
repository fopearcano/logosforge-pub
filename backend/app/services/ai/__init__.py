"""AI integration scaffolding.

Two layers live underneath this package:

* ``providers/`` — small abstraction over chat-completion HTTP backends.
  A ``DryRunProvider`` ships canned responses so the rest of the system
  works without network access; ``OpenAICompatibleProvider`` talks to
  anything that speaks the OpenAI ``POST /v1/chat/completions`` shape
  (LM Studio, OpenRouter, Ollama-via-openai-compat, etc.).
* ``features/`` — editorial features each compose a prompt from a
  manuscript bundle, call the provider, and parse the response into a
  typed result.
"""

from app.services.ai import features, providers
from app.services.ai.providers import (
    ChatMessage,
    CompletionResult,
    LLMProvider,
    get_provider,
)

__all__ = [
    "ChatMessage",
    "CompletionResult",
    "LLMProvider",
    "features",
    "get_provider",
    "providers",
]
