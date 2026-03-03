"""Unified LLM client abstraction."""

from typing import Any, Literal

from pydantic import BaseModel

from wanderwing.utils.config import get_settings
from wanderwing.utils.logging import get_logger

from .providers.anthropic import AnthropicProvider
from .providers.openai import OpenAIProvider

logger = get_logger(__name__)


class LLMResponse(BaseModel):
    """Standardized LLM response."""

    content: str
    model: str
    tokens_used: int
    cost_usd: float
    metadata: dict[str, Any] = {}


class LLMClient:
    """Unified interface for LLM providers."""

    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings

        # Initialize provider
        if settings.llm_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self.provider = OpenAIProvider(settings)
        elif settings.llm_provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            self.provider = AnthropicProvider(settings)
        else:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

        logger.info(f"Initialized LLM client with provider: {settings.llm_provider}")

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: Literal["text", "json"] = "text",
    ) -> LLMResponse:
        """Generate completion from prompt."""
        return await self.provider.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature or self.settings.llm_temperature,
            max_tokens=max_tokens or self.settings.llm_max_tokens,
            response_format=response_format,
        )

    async def complete_structured(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float | None = None,
    ) -> BaseModel | dict[str, Any]:
        """Generate structured output (JSON mode or function calling)."""
        return await self.provider.complete_structured(
            prompt=prompt,
            system_prompt=system_prompt,
            response_model=response_model,
            temperature=temperature or self.settings.llm_temperature,
        )


# Global client instance
_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
