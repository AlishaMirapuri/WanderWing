"""Anthropic provider implementation."""

import json
from typing import Any, Literal

from anthropic import AsyncAnthropic
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from wanderwing.utils.config import Settings
from wanderwing.utils.logging import get_logger

from ..client import LLMResponse

logger = get_logger(__name__)


class AnthropicProvider:
    """Anthropic API provider."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        response_format: Literal["text", "json"] = "text",
    ) -> LLMResponse:
        """Generate completion."""
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self.client.messages.create(**kwargs)

        content = response.content[0].text if response.content else ""
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        # Rough cost estimation (Claude 3 pricing as of 2024)
        input_cost = (response.usage.input_tokens / 1000) * 0.003
        output_cost = (response.usage.output_tokens / 1000) * 0.015
        cost_usd = input_cost + output_cost

        logger.info(
            "Anthropic completion",
            extra={
                "llm_provider": "anthropic",
                "llm_tokens": tokens_used,
                "llm_cost": cost_usd,
            },
        )

        return LLMResponse(
            content=content,
            model=self.model,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
        )

    async def complete_structured(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.1,
    ) -> BaseModel | dict[str, Any]:
        """Generate structured output."""
        # Add JSON instruction to system prompt
        json_instruction = (
            "\n\nYou must respond with valid JSON only. No other text or explanation."
        )
        enhanced_system = (system_prompt or "") + json_instruction

        response = await self.complete(
            prompt=prompt,
            system_prompt=enhanced_system,
            temperature=temperature,
        )

        parsed = json.loads(response.content)

        if response_model:
            return response_model.model_validate(parsed)

        return parsed
