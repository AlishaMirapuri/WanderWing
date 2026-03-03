# Activity Recommendation - Quick Start

## Installation

First, install the package with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Running Tests

### Unit Tests
```bash
pytest tests/unit/test_activity_recommender.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_activity_workflow.py -v
```

### All Tests
```bash
pytest tests/ -v
```

## Basic Usage Example

```python
from datetime import datetime, timedelta
from wanderwing.schemas.user import TravelerProfile, AgeRange
from wanderwing.schemas.trip_enhanced import (
    ParsedTravelerIntent,
    ActivityCategory,
    BudgetTier,
    PacePreference,
)
from wanderwing.services.activity_recommender import get_activity_recommender

# Setup
today = datetime.now().date()

# Two travelers going to Tokyo
profiles = [
    TravelerProfile(
        user_id="alice",
        age_range=AgeRange.AGE_25_34,
        verification_level=3,
        trust_score=0.85,
    ),
    TravelerProfile(
        user_id="bob",
        age_range=AgeRange.AGE_25_34,
        verification_level=2,
        trust_score=0.75,
    ),
]

intents = [
    ParsedTravelerIntent(
        primary_destination="Tokyo",
        overall_start_date=today,
        overall_end_date=today + timedelta(days=10),
        activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOURS],
        budget_tier=BudgetTier.MODERATE,
        pace_preference=PacePreference.MODERATE,
        traveling_solo=True,
        open_to_companions=True,
    ),
    ParsedTravelerIntent(
        primary_destination="Tokyo",
        overall_start_date=today + timedelta(days=2),
        overall_end_date=today + timedelta(days=12),
        activities=[ActivityCategory.HIKING, ActivityCategory.ADVENTURE_SPORTS],
        budget_tier=BudgetTier.MODERATE,
        pace_preference=PacePreference.FAST,
        traveling_solo=True,
        open_to_companions=True,
    ),
]

# Get recommendations
recommender = get_activity_recommender()
response = recommender.recommend(profiles, intents, limit=5)

# Print results
print(f"Destination: {response.destination}")
print(f"Date Range: {response.date_range}")
print(f"\nTop {len(response.recommendations)} Recommendations:\n")

for i, rec in enumerate(response.recommendations, 1):
    print(f"{i}. {rec.activity.name} (Score: {rec.score:.2f})")
    print(f"   Cost: {rec.estimated_cost_per_person}")
    print(f"   Duration: {rec.activity.duration_hours} hours")
    print(f"   Tags: {', '.join([t.value for t in rec.activity.tags])}")
    print(f"   Explanation: {rec.explanation}")
    print(f"   Meeting Suggestion: {rec.meeting_suggestion}")
    print()
```

## File Structure

```
wanderwing/
├── data/
│   ├── activities/
│   │   ├── tokyo.json          # Tokyo activities (12 activities)
│   │   ├── paris.json          # Paris activities (10 activities)
│   │   └── barcelona.json      # Barcelona activities (12 activities)
│   └── activity_repository.py  # Data loading and querying
│
├── src/wanderwing/
│   ├── schemas/
│   │   └── activity.py         # Activity, Recommendation schemas
│   │
│   └── services/
│       ├── activity_recommender.py      # Main recommendation engine
│       └── activity_llm_enhancer.py     # Optional LLM polish
│
└── tests/
    ├── unit/
    │   └── test_activity_recommender.py     # Unit tests (25+ tests)
    └── integration/
        └── test_activity_workflow.py        # Integration tests (30+ tests)
```

## Available Cities

- **Tokyo** (12 activities)
- **Paris** (10 activities)
- **Barcelona** (12 activities)

## Next Steps

1. Run tests to verify implementation
2. Review `ACTIVITY_RECOMMENDATIONS.md` for detailed documentation
3. Try different traveler combinations (budget travelers, culture lovers, etc.)
4. Add your own cities by creating new JSON files in `data/activities/`

## Common Use Cases

### Food Lovers
```python
activities=[ActivityCategory.FOOD_TOURS, ActivityCategory.LOCAL_EXPERIENCES]
```

### Adventure Seekers
```python
activities=[ActivityCategory.HIKING, ActivityCategory.ADVENTURE_SPORTS]
```

### Culture Enthusiasts
```python
activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS]
```

### Budget Backpackers
```python
budget_tier=BudgetTier.BUDGET
```

### Luxury Travelers
```python
budget_tier=BudgetTier.COMFORTABLE  # or LUXURY (if you add luxury activities)
```

## Troubleshooting

### No recommendations returned
- Check that the destination matches a city in `data/activities/`
- Verify budget tier isn't too restrictive
- Ensure travelers have overlapping dates

### Tests failing
- Make sure dependencies are installed: `pip install -e ".[dev]"`
- Check Python version >= 3.11

### Want to add custom activities
- Copy an existing JSON file from `data/activities/`
- Follow the schema (see `ACTIVITY_RECOMMENDATIONS.md`)
- Save with city name as filename (lowercase)
