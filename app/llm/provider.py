from typing import Protocol


class LLMProvider(Protocol):
    """Future optional adapter for OpenAI, Claude, or local models; no provider is used in v1."""

    def complete(self, prompt: str) -> str: ...
