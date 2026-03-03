# Quick Start: Using WanderWing Schemas

## 📚 What You Have

### Schema Files (1,956 LOC)
- ✅ `schemas/profile.py` - Traveler profiles, preferences, safety settings
- ✅ `schemas/trip_enhanced.py` - Trips, destinations, parsed intent
- ✅ `schemas/match_enhanced.py` - Matching, explanations, compatibility
- ✅ `schemas/recommendation.py` - Activity recommendations
- ✅ `schemas/feedback_enhanced.py` - Feedback, ratings, reports
- ✅ `schemas/experiment.py` - A/B testing framework

### API Routes (1,115 LOC)
- ✅ `routes/profiles.py` - Profile CRUD (5 endpoints)
- ✅ `routes/intent.py` - Intent parsing (3 endpoints)
- ✅ `routes/matches_enhanced.py` - Matching (5 endpoints)
- ✅ `routes/recommendations_new.py` - Recommendations (4 endpoints)
- ✅ `routes/feedback_enhanced.py` - Feedback (5 endpoints)
- ✅ `routes/experiments_enhanced.py` - Experiments (5 endpoints)

### Tests (603 LOC)
- ✅ `tests/unit/test_schemas.py` - 40+ test cases
- ✅ Validation testing, edge cases, examples

---

## 🚀 Validate Schemas Work

```bash
cd /Users/amirapuri/wanderwing

# Run the validation script
python3 scripts/validate_schemas.py

# Expected output:
# ✅ Testing TravelerProfileCreate...
# ✅ Testing ParsedTravelerIntent...
# ✅ Testing MatchExplanation...
# ✅ Testing ActivityRecommendation...
# ✅ Testing FeedbackEvent...
# ✅ Testing ExperimentAssignment...
# ✅ ALL SCHEMAS VALIDATED SUCCESSFULLY!
```

---

## 📖 Schema Examples

### 1. Traveler Profile

```python
from wanderwing.schemas.profile import (
    TravelerProfileCreate,
    TravelPreferences,
    TravelStyle,
    LanguageSkill,
    LanguageProficiency
)

# Create a traveler profile
profile = TravelerProfileCreate(
    email="alice@example.com",
    password="SecurePass123",  # Must have uppercase, lowercase, digit
    name="Alice Chen",
    bio="Digital nomad who loves adventure travel and meeting new people.",
    age_range="25-34",
    languages=[
        LanguageSkill(
            language="English",
            proficiency=LanguageProficiency.NATIVE
        ),
        LanguageSkill(
            language="Spanish",
            proficiency=LanguageProficiency.CONVERSATIONAL
        ),
    ],
    preferences=TravelPreferences(
        travel_styles=[TravelStyle.ADVENTURE, TravelStyle.CULTURE],
        budget_per_day_usd=100,
        willing_to_share_accommodation=True,
        interests=["hiking", "photography", "local cuisine"],
        social_style="very_social",
    ),
)

# Validation happens automatically
print(profile.email)  # alice@example.com
print(profile.preferences.budget_per_day_usd)  # 100
```

### 2. Parsed Trip Intent

```python
from datetime import date
from wanderwing.schemas.trip_enhanced import (
    ParsedTravelerIntent,
    DestinationStay,
    ActivityCategory,
    BudgetTier,
)

# What LLM agent returns after parsing natural language
intent = ParsedTravelerIntent(
    raw_input="Planning a 2-week trip to Japan in April...",
    primary_destination="Tokyo",
    destination_stays=[
        DestinationStay(
            destination="Tokyo",
            country="Japan",
            start_date=date(2024, 4, 1),
            end_date=date(2024, 4, 8),
            nights=7,  # Must match date range!
            activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR],
            must_see_attractions=["Mt. Fuji", "Senso-ji Temple"],
        ),
        DestinationStay(
            destination="Kyoto",
            country="Japan",
            start_date=date(2024, 4, 8),
            end_date=date(2024, 4, 15),
            nights=7,
            activities=[ActivityCategory.SIGHTSEEING],
        ),
    ],
    budget_tier=BudgetTier.MODERATE,
    confidence_score=0.92,
    ambiguities=[],  # List things that need clarification
)

# Auto-calculated fields
print(intent.overall_start_date)  # 2024-04-01
print(intent.overall_end_date)    # 2024-04-15
print(intent.total_duration_days)  # 14
```

### 3. Match Explanation

```python
from wanderwing.schemas.match_enhanced import (
    MatchExplanation,
    DimensionScore,
    CompatibilityDimension,
    MatchReason,
)

# Detailed explanation of why two travelers match
explanation = MatchExplanation(
    overall_score=0.87,
    dimension_scores=[
        DimensionScore(
            dimension=CompatibilityDimension.DESTINATION,
            score=1.0,
            explanation="Both traveling to Tokyo",
            contributing_factors=["Tokyo"],
        ),
        DimensionScore(
            dimension=CompatibilityDimension.ACTIVITIES,
            score=0.85,
            explanation="5 out of 6 activities match",
            contributing_factors=["hiking", "food_tour", "sightseeing"],
        ),
    ],
    primary_reasons=[
        MatchReason.SAME_DESTINATION,
        MatchReason.OVERLAPPING_DATES,
        MatchReason.SHARED_ACTIVITIES,
    ],
    shared_interests=["hiking", "food tours", "photography"],
    complementary_traits=["One has local language skills"],
    llm_summary="Alice and Bob are an excellent match...",
    why_great_match=[
        "Perfect date overlap (April 1-10)",
        "Shared passion for hiking and food",
        "Complementary skills (photography + language)",
    ],
    conversation_starters=[
        "What's your dream hike around Tokyo?",
        "Have you planned any specific food tours?",
    ],
    rule_based_score=0.82,
    llm_similarity_score=0.91,
    hybrid_weight_llm=0.6,
    hybrid_weight_rules=0.4,
)

# Access detailed breakdown
for dim_score in explanation.dimension_scores:
    print(f"{dim_score.dimension.value}: {dim_score.score:.0%}")
```

### 4. Activity Recommendation

```python
from wanderwing.schemas.recommendation import (
    ActivityRecommendation,
    RecommendationType,
    DifficultyLevel,
    CostRange,
)

# LLM-generated activity recommendation
rec = ActivityRecommendation(
    title="Sunrise Hike to Mount Takao Summit",
    description="Start early to catch spectacular sunrise...",
    recommendation_type=RecommendationType.SHARED_ACTIVITY,
    activity_category="hiking",
    location="Mount Takao, Hachioji, Tokyo",
    difficulty_level=DifficultyLevel.MODERATE,
    duration_hours=3.5,
    cost_range=CostRange.BUDGET,
    cost_per_person_usd=12.0,
    ideal_group_size=2,
    cost_savings_if_shared=8.0,  # Save $8 by sharing taxi
    best_time_of_day="Early morning (4:30 AM start)",
    advance_booking_required=False,
    why_recommended=[
        "Both travelers love hiking",
        "Matches 'early bird' preference",
        "Budget-friendly activity",
        "Great for photography",
        "Can share taxi cost to trailhead",
    ],
    matches_interests=["hiking", "photography", "nature"],
    confidence_score=0.94,
)
```

### 5. Feedback Event

```python
from wanderwing.schemas.feedback_enhanced import (
    FeedbackEvent,
    FeedbackEventType,
    FeedbackSentiment,
)

# Track user feedback
event = FeedbackEvent(
    event_type=FeedbackEventType.MATCH_RATING,
    user_id=123,
    match_id=456,
    rating=5,
    sentiment=FeedbackSentiment.VERY_POSITIVE,
    comment="Amazing travel companion! We had such a great time...",
    tags=["great_match", "would_travel_again", "helpful"],
    metadata={
        "match_score": 0.87,
        "days_traveled_together": 9,
        "activities_completed": 12,
    },
)
```

### 6. Experiment Assignment

```python
from wanderwing.schemas.experiment import (
    ExperimentAssignment,
    ConversionType,
)

# A/B test tracking
assignment = ExperimentAssignment(
    experiment_name="itinerary_extraction_prompt_v2",
    variant_name="treatment",  # or "control"
    user_id=123,
    converted=True,
    conversion_type=ConversionType.INTENT_PARSED,
    conversion_value=1.0,
    assignment_method="deterministic_hash",
    metadata={
        "prompt_version": "v2",
        "model": "gpt-4-turbo",
    },
)
```

---

## 🔍 Validation Examples

### Valid Profile

```python
from pydantic import ValidationError

# ✅ This works
profile = TravelerProfileCreate(
    email="alice@example.com",
    password="SecurePass123",
    name="Alice Chen",
    bio="Digital nomad with 10+ years travel experience.",
    preferences=TravelPreferences(
        travel_styles=[TravelStyle.ADVENTURE],
    ),
)
```

### Invalid Profile (Examples)

```python
# ❌ Weak password
try:
    profile = TravelerProfileCreate(
        email="alice@example.com",
        password="weak",  # No uppercase, no digit
        name="Alice",
        preferences=TravelPreferences(travel_styles=[TravelStyle.ADVENTURE]),
    )
except ValidationError as e:
    print(e.errors())
    # "Password must contain at least one uppercase letter"
    # "Password must contain at least one digit"

# ❌ Bio too short
try:
    profile = TravelerProfileCreate(
        email="alice@example.com",
        password="SecurePass123",
        name="Alice",
        bio="Short",  # Less than 10 chars
        preferences=TravelPreferences(travel_styles=[TravelStyle.ADVENTURE]),
    )
except ValidationError as e:
    print(e.errors())
    # "Bio must be at least 10 characters if provided"

# ❌ No travel styles
try:
    preferences = TravelPreferences(
        travel_styles=[],  # Must have at least 1
    )
except ValidationError as e:
    print(e.errors())
    # "List should have at least 1 item"
```

### Date Validation

```python
# ❌ End date before start date
try:
    stay = DestinationStay(
        destination="Tokyo",
        country="Japan",
        start_date=date(2024, 4, 10),
        end_date=date(2024, 4, 5),  # Before start!
        nights=5,
    )
except ValidationError as e:
    print(e.errors())
    # "end_date must be after start_date"

# ❌ Nights don't match dates
try:
    stay = DestinationStay(
        destination="Tokyo",
        country="Japan",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 6),
        nights=10,  # Should be 5!
    )
except ValidationError as e:
    print(e.errors())
    # "nights (10) doesn't match date range (5 nights)"
```

---

## 📊 Schema Summary

| Schema | Purpose | Key Models | Enums |
|--------|---------|------------|-------|
| profile.py | User profiles | TravelerProfile, TravelPreferences, SafetyPreferences | TravelStyle (12), Gender, AgeRange, etc. |
| trip_enhanced.py | Trip planning | ParsedTravelerIntent, DestinationStay, TripSegment | ActivityCategory (18), BudgetTier (5), TransportMode (9) |
| match_enhanced.py | Matching | MatchExplanation, MatchCandidate, DimensionScore | MatchStatus (7), CompatibilityDimension (9) |
| recommendation.py | Activities | ActivityRecommendation | RecommendationType (5), DifficultyLevel (4) |
| feedback_enhanced.py | Feedback | FeedbackEvent, MatchRating, UserReport | FeedbackEventType (14), ReportReason (8) |
| experiment.py | A/B testing | ExperimentAssignment, ExperimentMetrics | ExperimentStatus (5), ConversionType (8) |

---

## 🧪 Running Tests

```bash
# All schema tests
pytest tests/unit/test_schemas.py -v

# Specific test class
pytest tests/unit/test_schemas.py::TestProfileSchemas -v

# Test with coverage
pytest tests/unit/test_schemas.py --cov=src/wanderwing/schemas

# Run validation script
python3 scripts/validate_schemas.py
```

---

## 📝 Next: Implementation Checklist

1. ✅ **Schemas defined** (COMPLETE)
2. ✅ **API routes stubbed** (COMPLETE)
3. ✅ **Tests written** (COMPLETE)
4. ⏳ **Database models** (TODO - create SQLAlchemy models)
5. ⏳ **LLM agents** (TODO - implement intent parser, matcher)
6. ⏳ **Route implementation** (TODO - wire up actual logic)
7. ⏳ **Frontend integration** (TODO - update Streamlit to use schemas)

---

## 💡 Tips

1. **Import from schemas package**: `from wanderwing.schemas.profile import TravelerProfile`
2. **Use `.model_dump()` for JSON**: `profile.model_dump()`
3. **Use `.model_validate()` to parse**: `Profile.model_validate(dict_data)`
4. **Check examples**: Every schema has `json_schema_extra["example"]`
5. **Validation errors are helpful**: `except ValidationError as e: print(e.errors())`

---

## 🎯 Key Features

✅ **Data Modeling** - Comprehensive schemas with validation rules
✅ **Type Safety** - Full Pydantic + mypy support throughout
✅ **API Design** - RESTful endpoints with complete documentation
✅ **Test Coverage** - 40+ test cases covering edge cases
✅ **AI Integration** - LLM workflows with confidence scoring
✅ **Safety & Privacy** - Verification, trust scoring, and user safety features
