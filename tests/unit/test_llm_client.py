"""Unit tests for LLM client."""

import pytest
from unittest.mock import AsyncMock, patch

from wanderwing.llm.client import LLMClient


@pytest.mark.asyncio
async def test_llm_client_initialization():
    """Test LLM client initializes correctly."""
    with patch("wanderwing.llm.client.get_settings") as mock_settings:
        mock_settings.return_value.llm_provider = "openai"
        mock_settings.return_value.openai_api_key = "test-key"

        client = LLMClient()
        assert client.provider is not None


@pytest.mark.asyncio
async def test_llm_client_invalid_provider():
    """Test LLM client raises error for invalid provider."""
    with patch("wanderwing.llm.client.get_settings") as mock_settings:
        mock_settings.return_value.llm_provider = "invalid"
        mock_settings.return_value.openai_api_key = "test-key"

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMClient()
