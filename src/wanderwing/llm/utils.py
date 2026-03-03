"""LLM utility functions."""

from functools import lru_cache
from typing import Any


@lru_cache(maxsize=100)
def cached_prompt(prompt_key: str, **kwargs: Any) -> str:
    """Cache formatted prompts to reduce redundant LLM calls."""
    # Placeholder for prompt caching logic
    return prompt_key


def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars ≈ 1 token)."""
    return len(text) // 4


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximate token limit."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
