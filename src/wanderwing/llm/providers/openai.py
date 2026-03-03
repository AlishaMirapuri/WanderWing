"""OpenAI provider implementation."""

import json
from typing import Any, Literal

from openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from wanderwing.utils.config import Settings
from wanderwing.utils.logging import get_logger

from ..client import LLMResponse

logger = get_logger(__name__)


class OpenAIProvider:
    """OpenAI API provider."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
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
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else 0

        # Rough cost estimation (gpt-4-turbo pricing as of 2024)
        cost_usd = (tokens_used / 1000) * 0.01  # $0.01 per 1K tokens (simplified)

        logger.info(
            "OpenAI completion",
            extra={
                "llm_provider": "openai",
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
        response = await self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            response_format="json",
        )

        parsed = json.loads(response.content)

        if response_model:
            return response_model.model_validate(parsed)

        return parsed
