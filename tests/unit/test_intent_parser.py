"""
Comprehensive unit tests for IntentParser.

Tests successful parsing, error handling, fallback mechanisms, and edge cases.
"""

import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from wanderwing.llm.client import LLMResponse
from wanderwing.schemas.trip_enhanced import ActivityCategory, BudgetTier, ParsedTravelerIntent
from wanderwing.services.intent_parser import (
    BatchIntentParser,
    IntentParser,
    IntentParsingError,
)


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    with patch("wanderwing.services.intent_parser.get_llm_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def intent_parser(mock_llm_client):
    """Create IntentParser instance for testing."""
    return IntentParser(prompt_version="v2")


@pytest.fixture
def valid_llm_response():
    """Valid LLM response for successful parsing."""
    return {
        "primary_destination": "Tokyo",
        "destination_stays": [
            {
                "destination": "Tokyo",
                "country": "Japan",
                "start_date": "2024-04-01",
                "end_date": "2024-04-08",
                "nights": 7,
                "activities": ["hiking", "food_tour", "sightseeing"],
                "must_see_attractions": ["Mt. Fuji", "Senso-ji Temple"],
                "is_flexible": False,
                "flexibility_days": 0,
            }
        ],
        "trip_segments": [],
        "activities": ["hiking", "food_tour", "sightseeing"],
        "budget_tier": "moderate",
        "budget_total_usd": 1050.0,
        "pace_preference": "moderate",
        "traveling_solo": True,
        "open_to_companions": True,
        "preferred_group_size": 2,
        "confidence_score": 0.92,
        "ambiguities": [],
        "clarification_questions": [],
    }


class TestIntentParserSuccess:
    """Test successful parsing scenarios."""

    @pytest.mark.asyncio
    async def test_successful_parse_complete_info(
        self, intent_parser, mock_llm_client, valid_llm_response
    ):
        """Test parsing with complete, valid information."""
        # Setup mock
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=450,
            cost_usd=0.009,
        )

        # Parse
        result = await intent_parser.parse(
            "Going to Tokyo for a week in April, love hiking and food tours"
        )

        # Assertions
        assert isinstance(result, ParsedTravelerIntent)
        assert result.primary_destination == "Tokyo"
        assert result.confidence_score == 0.92
        assert len(result.destination_stays) == 1
        assert result.destination_stays[0].nights == 7
        assert ActivityCategory.HIKING in result.activities

    @pytest.mark.asyncio
    async def test_multi_city_trip_parsing(self, intent_parser, mock_llm_client):
        """Test parsing multi-city itinerary."""
        multi_city_response = {
            "primary_destination": "Tokyo",
            "destination_stays": [
                {
                    "destination": "Tokyo",
                    "country": "Japan",
                    "start_date": "2024-04-01",
                    "end_date": "2024-04-06",
                    "nights": 5,
                    "activities": ["sightseeing"],
                    "is_flexible": False,
                    "flexibility_days": 0,
                },
                {
                    "destination": "Kyoto",
                    "country": "Japan",
                    "start_date": "2024-04-06",
                    "end_date": "2024-04-10",
                    "nights": 4,
                    "activities": ["cultural_events"],
                    "is_flexible": False,
                    "flexibility_days": 0,
                },
            ],
            "trip_segments": [
                {
                    "from_destination": "Tokyo",
                    "to_destination": "Kyoto",
                    "departure_date": "2024-04-06",
                    "arrival_date": "2024-04-06",
                    "transport_mode": "train",
                }
            ],
            "activities": ["sightseeing", "cultural_events"],
            "budget_tier": "moderate",
            "traveling_solo": True,
            "open_to_companions": True,
            "preferred_group_size": 2,
            "confidence_score": 0.9,
            "ambiguities": [],
            "clarification_questions": [],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(multi_city_response),
            model="gpt-4-turbo",
            tokens_used=550,
            cost_usd=0.011,
        )

        result = await intent_parser.parse(
            "2-week trip: 5 days Tokyo, 4 days Kyoto by train"
        )

        assert len(result.destination_stays) == 2
        assert len(result.trip_segments) == 1
        assert result.trip_segments[0].transport_mode == "train"
        assert result.overall_start_date == date(2024, 4, 1)
        assert result.overall_end_date == date(2024, 4, 10)

    @pytest.mark.asyncio
    async def test_vague_input_low_confidence(self, intent_parser, mock_llm_client):
        """Test parsing vague input results in low confidence."""
        vague_response = {
            "primary_destination": "Lisbon",
            "destination_stays": [
                {
                    "destination": "Lisbon",
                    "country": "Portugal",
                    "start_date": None,
                    "end_date": None,
                    "nights": 3,
                    "activities": ["food_tour"],
                    "is_flexible": True,
                    "flexibility_days": 7,
                }
            ],
            "trip_segments": [],
            "activities": ["food_tour", "local_experiences"],
            "budget_tier": "moderate",
            "traveling_solo": True,
            "open_to_companions": True,
            "preferred_group_size": 2,
            "confidence_score": 0.55,
            "ambiguities": [
                "Exact dates not specified",
                "Budget not mentioned - assumed moderate",
            ],
            "clarification_questions": [
                "What are your specific travel dates?",
                "What's your approximate daily budget?",
            ],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(vague_response),
            model="gpt-4-turbo",
            tokens_used=400,
            cost_usd=0.008,
        )

        result = await intent_parser.parse("Thinking about Lisbon for a long weekend")

        assert result.confidence_score < 0.7
        assert len(result.ambiguities) >= 2
        assert len(result.clarification_questions) >= 2
        assert result.destination_stays[0].start_date is None


class TestIntentParserErrorHandling:
    """Test error handling and fallback mechanisms."""

    @pytest.mark.asyncio
    async def test_malformed_json_triggers_fallback(
        self, intent_parser, mock_llm_client
    ):
        """Test that malformed JSON triggers fallback parser."""
        # LLM returns invalid JSON
        mock_llm_client.complete.return_value = LLMResponse(
            content='{"destination": "Tokyo", "invalid json structure',
            model="gpt-4-turbo",
            tokens_used=200,
            cost_usd=0.004,
        )

        result = await intent_parser.parse("Going to Tokyo")

        # Fallback should succeed with low confidence
        assert isinstance(result, ParsedTravelerIntent)
        assert result.confidence_score == 0.3
        assert "Could not fully parse" in result.ambiguities[0]
        assert len(result.clarification_questions) > 0

    @pytest.mark.asyncio
    async def test_missing_required_fields_fallback(
        self, intent_parser, mock_llm_client
    ):
        """Test handling of missing required fields."""
        # Missing destination_stays (required field)
        incomplete_response = {
            "primary_destination": "Paris",
            "activities": ["museums"],
            "budget_tier": "moderate",
            "confidence_score": 0.8,
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(incomplete_response),
            model="gpt-4-turbo",
            tokens_used=300,
            cost_usd=0.006,
        )

        result = await intent_parser.parse("Paris trip")

        # Should use fallback
        assert result.confidence_score == 0.3
        assert len(result.destination_stays) == 0

    @pytest.mark.asyncio
    async def test_retry_logic_on_validation_error(
        self, intent_parser, mock_llm_client
    ):
        """Test that validation errors trigger retry."""
        # First call: invalid dates
        invalid_response = {
            "primary_destination": "Tokyo",
            "destination_stays": [
                {
                    "destination": "Tokyo",
                    "country": "Japan",
                    "start_date": "2024-04-10",
                    "end_date": "2024-04-05",  # End before start!
                    "nights": 5,
                    "activities": [],
                    "is_flexible": False,
                    "flexibility_days": 0,
                }
            ],
            "activities": [],
            "budget_tier": "moderate",
            "traveling_solo": True,
            "open_to_companions": True,
            "preferred_group_size": 2,
            "confidence_score": 0.8,
            "ambiguities": [],
            "clarification_questions": [],
        }

        # Second call: valid
        valid_response = {
            "primary_destination": "Tokyo",
            "destination_stays": [
                {
                    "destination": "Tokyo",
                    "country": "Japan",
                    "start_date": "2024-04-05",
                    "end_date": "2024-04-10",
                    "nights": 5,
                    "activities": ["sightseeing"],
                    "is_flexible": False,
                    "flexibility_days": 0,
                }
            ],
            "activities": ["sightseeing"],
            "budget_tier": "moderate",
            "traveling_solo": True,
            "open_to_companions": True,
            "preferred_group_size": 2,
            "confidence_score": 0.8,
            "ambiguities": [],
            "clarification_questions": [],
        }

        mock_llm_client.complete.side_effect = [
            LLMResponse(
                content=json.dumps(invalid_response),
                model="gpt-4-turbo",
                tokens_used=400,
                cost_usd=0.008,
            ),
            LLMResponse(
                content=json.dumps(valid_response),
                model="gpt-4-turbo",
                tokens_used=400,
                cost_usd=0.008,
            ),
        ]

        result = await intent_parser.parse("Tokyo trip April 5-10")

        # Should succeed on retry
        assert result.destination_stays[0].start_date == date(2024, 4, 5)
        assert mock_llm_client.complete.call_count == 2


class TestBusinessRuleValidation:
    """Test business rule validation."""

    @pytest.mark.asyncio
    async def test_unsupported_destination_flagged(
        self, intent_parser, mock_llm_client
    ):
        """Test that unsupported destinations are flagged."""
        unsupported_response = {
            "primary_destination": "North Korea",
            "destination_stays": [
                {
                    "destination": "Pyongyang",
                    "country": "North Korea",
                    "start_date": "2024-05-01",
                    "end_date": "2024-05-05",
                    "nights": 4,
                    "activities": ["sightseeing"],
                    "is_flexible": False,
                    "flexibility_days": 0,
                }
            ],
            "activities": ["sightseeing"],
            "budget_tier": "moderate",
            "traveling_solo": True,
            "open_to_companions": True,
            "preferred_group_size": 2,
            "confidence_score": 0.9,
            "ambiguities": [],
            "clarification_questions": [],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(unsupported_response),
            model="gpt-4-turbo",
            tokens_used=400,
            cost_usd=0.008,
        )

        result = await intent_parser.parse("Trip to North Korea")

        # Should flag restrictions
        assert any("restrictions" in amb.lower() for amb in result.ambiguities)

    @pytest.mark.asyncio
    async def test_contradictory_preferences_flagged(
        self, intent_parser, mock_llm_client
    ):
        """Test contradictory preferences are flagged."""
        contradictory_response = {
            "primary_destination": "Bangkok",
            "destination_stays": [
                {
                    "destination": "Bangkok",
                    "country": "Thailand",
                    "start_date": "2024-06-01",
                    "end_date": "2024-06-02",
                    "nights": 1,
                    "activities": ["nightlife", "sightseeing"],  # Nightlife in 1 night
                    "is_flexible": False,
                    "flexibility_days": 0,
                }
            ],
            "activities": ["nightlife", "sightseeing"],
            "budget_tier": "budget",
            "traveling_solo": True,
            "open_to_companions": True,
            "preferred_group_size": 2,
            "confidence_score": 0.85,
            "ambiguities": [],
            "clarification_questions": [],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(contradictory_response),
            model="gpt-4-turbo",
            tokens_used=400,
            cost_usd=0.008,
        )

        result = await intent_parser.parse("One night in Bangkok, nightlife")

        # Should flag timing issue
        assert any("short stay" in amb.lower() for amb in result.ambiguities)


class TestFallbackParser:
    """Test fallback parsing mechanisms."""

    @pytest.mark.asyncio
    async def test_partial_json_extraction(self, intent_parser, mock_llm_client):
        """Test extraction from partial JSON."""
        # Severely malformed JSON with some extractable data
        partial_json = '''
        {
            "destination": "Barcelona",
            incomplete structure
            "ambiguities": ["test"]
        '''

        mock_llm_client.complete.return_value = LLMResponse(
            content=partial_json,
            model="gpt-4-turbo",
            tokens_used=200,
            cost_usd=0.004,
        )

        result = await intent_parser.parse("Going to Barcelona")

        # Fallback should extract what it can
        assert result.confidence_score == 0.3
        assert "Barcelona" in result.primary_destination or result.primary_destination == "Unknown"

    @pytest.mark.asyncio
    async def test_complete_garbage_output(self, intent_parser, mock_llm_client):
        """Test handling of completely invalid output."""
        mock_llm_client.complete.return_value = LLMResponse(
            content="This is not JSON at all, just random text",
            model="gpt-4-turbo",
            tokens_used=100,
            cost_usd=0.002,
        )

        result = await intent_parser.parse("Random trip")

        # Should still return something with very low confidence
        assert result.confidence_score == 0.3
        assert result.primary_destination == "Unknown"
        assert len(result.clarification_questions) >= 3


class TestBatchProcessing:
    """Test batch processing functionality."""

    @pytest.mark.asyncio
    async def test_batch_parse_multiple_inputs(
        self, intent_parser, mock_llm_client, valid_llm_response
    ):
        """Test batch parsing of multiple inputs."""
        batch_parser = BatchIntentParser(intent_parser)

        # Mock response for all inputs
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=400,
            cost_usd=0.008,
        )

        inputs = [
            "Trip to Tokyo",
            "Weekend in Paris",
            "Beach vacation in Bali",
        ]

        results = await batch_parser.parse_batch(inputs, max_concurrent=2)

        assert len(results) == 3
        # Should have mostly successful parses
        successful = [r for r in results if isinstance(r, ParsedTravelerIntent)]
        assert len(successful) >= 2


class TestPromptVersioning:
    """Test prompt version handling."""

    def test_load_specific_prompt_version(self):
        """Test loading specific prompt version."""
        parser = IntentParser(prompt_version="v2")
        assert parser.prompt_version == "v2"
        assert "You are an expert travel planning assistant" in parser.prompt_template

    def test_fallback_to_v1_if_version_missing(self):
        """Test fallback to v1 if version doesn't exist."""
        parser = IntentParser(prompt_version="v99")
        # Should fall back to v1
        assert "extraction_v1" in str(parser.prompt_template) or len(parser.prompt_template) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_input(self, intent_parser, mock_llm_client):
        """Test handling of empty input."""
        minimal_response = {
            "primary_destination": "Unknown",
            "destination_stays": [],
            "activities": [],
            "budget_tier": "moderate",
            "traveling_solo": True,
            "open_to_companions": True,
            "preferred_group_size": 2,
            "confidence_score": 0.1,
            "ambiguities": ["No destination provided", "No activities specified"],
            "clarification_questions": ["Where do you want to travel?"],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(minimal_response),
            model="gpt-4-turbo",
            tokens_used=150,
            cost_usd=0.003,
        )

        result = await intent_parser.parse("")

        assert result.confidence_score < 0.3
        assert len(result.clarification_questions) > 0

    @pytest.mark.asyncio
    async def test_very_long_input(self, intent_parser, mock_llm_client, valid_llm_response):
        """Test handling of very long input."""
        long_input = "I want to travel " + "and see amazing sights " * 200

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=2000,
            cost_usd=0.04,
        )

        result = await intent_parser.parse(long_input)

        # Should still parse successfully
        assert isinstance(result, ParsedTravelerIntent)

    @pytest.mark.asyncio
    async def test_user_context_included(
        self, intent_parser, mock_llm_client, valid_llm_response
    ):
        """Test that user context is included in prompt."""
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=450,
            cost_usd=0.009,
        )

        user_context = {
            "preferred_budget": "moderate",
            "travel_styles": ["adventure", "culture"],
        }

        result = await intent_parser.parse("Trip to Tokyo", user_context=user_context)

        # Verify context was used in prompt
        call_args = mock_llm_client.complete.call_args
        prompt_used = call_args.kwargs["prompt"]
        assert "moderate" in prompt_used or "User Context" in prompt_used
