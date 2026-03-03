"""Unit tests for agent modules."""

import pytest
from unittest.mock import AsyncMock, patch

from wanderwing.agents.itinerary_extractor import extract_itinerary, validate_extraction
from wanderwing.schemas.trip import ParsedItinerary


@pytest.mark.asyncio
async def test_extract_itinerary_success(mock_llm_response):
    """Test successful itinerary extraction."""
    with patch("wanderwing.agents.itinerary_extractor.get_llm_client") as mock_client:
        mock_llm = AsyncMock()
        mock_llm.complete_structured.return_value = ParsedItinerary(**mock_llm_response)
        mock_client.return_value = mock_llm

        result = await extract_itinerary(
            "Going to Tokyo for 10 days in April, love hiking and food tours"
        )

        assert result.destination == "Tokyo"
        assert result.duration_days == 10
        assert "hiking" in result.activities


@pytest.mark.asyncio
async def test_validate_extraction():
    """Test itinerary validation."""
    parsed = ParsedItinerary(
        destination="Paris",
        start_date="2024-05-01",
        end_date="2024-05-10",
        confidence_score=0.8,
    )

    is_valid, errors = await validate_extraction(parsed)

    assert is_valid
    assert len(errors) == 0


@pytest.mark.asyncio
async def test_validate_extraction_with_errors():
    """Test validation catches errors."""
    parsed = ParsedItinerary(
        destination="",  # Missing destination
        confidence_score=0.3,  # Low confidence
    )

    is_valid, errors = await validate_extraction(parsed)

    assert not is_valid
    assert len(errors) > 0
    assert any("destination" in err.lower() for err in errors)
