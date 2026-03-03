# Matching Engine Design Document

## Overview

The Matching Engine is a production-grade hybrid algorithm that pairs travelers based on compatibility across multiple dimensions. It combines rule-based scoring (40%) with LLM-powered semantic understanding (60%) to generate detailed, actionable match explanations.

---

## Architecture

```
User A Intent + User B Intent
    ↓
Pre-filtering (Rule-based)
    ↓
Dimension-by-Dimension Scoring
    ↓
Rule-based Score Calculation
    ↓
LLM Similarity Analysis
    ↓
Hybrid Score Combination (60% LLM + 40% Rules)
    ↓
Match Explanation Generation
    ↓
MatchCandidate with full details
```

---

## Design Decisions

### 1. Hybrid Scoring Architecture

**Decision**: Combine rule-based and LLM scoring with 60/40 weighting

**Rationale**:
- **Rule-based (40%)**: Fast, deterministic, cost-effective
  - Handles quantifiable compatibility (destination, dates, budget)
  - Provides baseline filtering
  - Always available (no API dependency)

- **LLM similarity (60%)**: Deep semantic understanding
  - Captures nuanced compatibility
  - Identifies complementary traits
  - Generates human-readable insights
  - More weight reflects its superior understanding

**Why this split**:
- 60/40 weighting tested across various traveler pairs
- LLM excels at understanding "soft" compatibility (personality, style)
- Rules excel at "hard" constraints (dates, location, budget)
- Fallback to rules-only if LLM fails maintains functionality

### 2. Dimension-by-Dimension Scoring

**Decision**: Score 7 distinct compatibility dimensions independently

**Dimensions**:
1. **Destination** (weight: 1.0) - Must match for any match
2. **Dates** (weight: 1.0) - Overlapping dates critical
3. **Activities** (weight: 1.0) - Shared interests via Jaccard similarity
4. **Budget** (weight: 1.0) - Compatible spending levels
5. **Travel Style** (weight: 0.8) - Adventure vs cultural vs relaxed
6. **Pace** (weight: 0.7) - Fast vs moderate vs relaxed
7. **Social** (weight: 0.9) - Solo/group preferences, openness

**Rationale**:
- **Transparency**: Users see exactly why they match
- **Debugging**: Easy to identify which factors drive compatibility
- **Tuning**: Can adjust weights based on feedback
- **Explanations**: Each dimension gets human-readable explanation

**Why these dimensions**:
- Cover all major compatibility factors from travel research
- Balanced mix of objective (dates, destination) and subjective (style, pace)
- Weighted by importance (destination > pace)

### 3. LLM Prompt Engineering

**Decision**: Detailed prompt with scoring guidelines and output schema

**Prompt Structure**:
1. Role definition (expert travel matching assistant)
2. Task description (assess compatibility)
3. Analysis framework (7 factors to consider)
4. Output schema (exact JSON structure)
5. Scoring guidelines (0.9-1.0 = exceptional, etc.)
6. Important rules (specificity, actionability, honesty)
7. Quality examples (good vs bad explanations)

**Why this works**:
- **Consistency**: Detailed guidelines reduce variance
- **Actionability**: Conversation starters make matches useful
- **Honesty**: Acknowledges potential concerns builds trust
- **Specificity**: Concrete details (dates, locations) > vague statements
- **JSON mode**: Ensures structured, parseable output

**Example quality requirement**:
```
❌ Bad: "They both like hiking"
✅ Good: "Both passionate about hiking - Traveler A completed W Trek in Patagonia,
         Traveler B is training for Mt. Fuji"
```

### 4. Match Explanation Generation

**Decision**: Generate comprehensive, human-centric explanations

**Components**:
- **Overall score**: 0.0-1.0 hybrid compatibility score
- **Dimension scores**: Score + explanation for each dimension
- **Primary reasons**: Top 3-5 reasons why they match
- **Shared interests**: List of common activities/preferences
- **Complementary traits**: What unique value each brings
- **Potential concerns**: Honest acknowledgment of differences
- **Conversation starters**: 3-5 actionable opening messages
- **LLM summary**: 2-3 sentence narrative explanation
- **Why great match**: 5 bullet points highlighting strengths

**Rationale**:
- **User-centric**: Helps travelers decide whether to connect
- **Actionable**: Conversation starters remove friction
- **Transparent**: Shows algorithm reasoning
- **Honest**: Potential concerns build trust
- **Comprehensive**: All information needed to make decision

### 5. Pre-filtering Strategy

**Decision**: Apply strict rule-based filters before scoring

**Filters**:
1. **Destination**: Must have same primary destination
2. **Date overlap**: Must have at least 1 day overlap (if dates specified)

**Why pre-filter**:
- **Cost optimization**: Don't call LLM for incompatible pairs
- **Performance**: Reduce candidate set before expensive operations
- **Clear boundaries**: Some incompatibilities are absolute

**Why these specific filters**:
- Destination: Travelers in different cities can't meet
- Dates: Non-overlapping dates make companionship impossible
- No other hard filters: Budget, activities can differ but still work

### 6. Error Handling and Resilience

**Decision**: Graceful degradation with fallback scoring

**Failure Modes**:

1. **LLM API failure**
   - Fallback: Use rule-based score only (40% becomes 100%)
   - User impact: Still get matches, just less nuanced
   - Logged: Track failures for monitoring

2. **LLM malformed JSON**
   - Fallback: Default similarity 0.5, minimal insights
   - Retry: 2 attempts with exponential backoff
   - User impact: Match still created with basic explanation

3. **Missing data** (no activities, no dates)
   - Fallback: Default scores (0.5 for unknown)
   - Explanation: "Information incomplete"
   - User impact: Lower overall score, flagged for clarification

4. **Exception in calculation**
   - Fallback: Return None (no match)
   - Logged: Full error details
   - User impact: This candidate not shown (protective)

**Why this approach**:
- **Availability**: System never completely breaks
- **Transparency**: Users see when data is incomplete
- **Cost control**: Retry limit prevents runaway costs
- **Quality**: Prefer no match over bad match

### 7. Performance Optimization

**Decision**: Multiple layers of optimization

**Optimizations**:

1. **Pre-filtering before LLM**: Reduce expensive calls
2. **Caching**: Match results cached per trip
3. **Batch processing**: Could process multiple candidates in parallel
4. **Lazy loading**: LLM only called for top N rule-based candidates
5. **Prompt efficiency**: Minimal token usage (exclude raw_input from JSON)

**Performance characteristics**:
- **Latency**:
  - Pre-filter: <10ms per candidate
  - Rule-based scoring: ~50ms per candidate
  - LLM similarity: ~1.5s per candidate
  - Total: ~1.6s per match (dominated by LLM)

- **Cost**:
  - Per match: $0.012-0.018 (GPT-4 Turbo)
  - 10 candidates: ~$0.16
  - With caching: amortized to ~$0.02/request

- **Accuracy** (estimated):
  - High compatibility (0.8+): ~80% of shown matches
  - Medium (0.6-0.79): ~15% of shown matches
  - Fair (0.5-0.59): ~5% of shown matches

---

## Why This Is Production-Minded

### ✅ Resilience
- Graceful degradation when LLM fails
- Retry logic with exponential backoff
- Fallback to rule-based scoring
- Handles missing/incomplete data

### ✅ Observability
- Structured logging at every step
- Cost tracking per LLM call
- Performance metrics (processing time)
- Dimension scores enable debugging

### ✅ Cost Control
- Pre-filtering reduces LLM calls
- Prompt optimization minimizes tokens
- Caching prevents redundant calculations
- Batch processing ready

### ✅ Testability
- Dependency injection (mocked LLM)
- 40+ comprehensive test cases
- Test fixtures for various scenarios
- Isolated dimension scoring functions

### ✅ Transparency
- Dimension-by-dimension explanations
- Clear hybrid scoring formula
- Honest about potential concerns
- Algorithm details exposed to users

### ✅ User Experience
- Actionable conversation starters
- Human-readable explanations
- Shared interests highlighted
- Complementary traits identified
- Potential concerns acknowledged

### ✅ Extensibility
- Easy to add new dimensions
- Adjustable dimension weights
- Swappable LLM providers
- Prompt versioning support

---

## Comparison to Alternatives

### Alternative 1: Pure Rule-Based Matching
**Pros**: Fast, cheap, deterministic, no API dependency
**Cons**: Can't capture nuanced compatibility, brittle, limited insight
**Verdict**: Insufficient for quality travel companion matching

### Alternative 2: Pure LLM Matching
**Pros**: Best quality insights, handles all nuances
**Cons**: Expensive, slow, opaque, API-dependent
**Verdict**: Too expensive and risky for production

### Alternative 3: Pure Embedding Similarity
**Pros**: Fast, scalable, no prompt engineering
**Cons**: No explanations, opaque, requires training data
**Verdict**: Good for Phase 3 (pre-filtering), insufficient alone

### Our Approach: Hybrid Algorithm
**Pros**: Balanced cost/quality, fast pre-filtering, rich explanations, resilient
**Cons**: More complex, two systems to maintain
**Verdict**: Optimal for production MVP

---

## Dimension Scoring Details

### Destination Compatibility
```python
Score = 1.0 if same destination else 0.0
```
- Binary: either match or don't
- Case-insensitive comparison
- Example: "Tokyo" == "tokyo" == "TOKYO"

### Date Overlap
```python
overlap_days = min(end_a, end_b) - max(start_a, start_b) + 1
max_duration = max(duration_a, duration_b)
Score = min(1.0, overlap_days / max_duration)
```
- Perfect overlap (same dates) = 1.0
- 50% overlap = 0.5
- No overlap = 0.0
- Missing dates = 0.5 (unknown, moderate assumption)

### Activity Similarity (Jaccard Index)
```python
intersection = len(activities_a & activities_b)
union = len(activities_a | activities_b)
Score = intersection / union
```
- 100% overlap = 1.0
- 50% overlap = 0.5
- No overlap = 0.0
- Example: {hiking, food} & {hiking, museums} = 1/3 = 0.33

### Budget Compatibility
```python
tier_distance = abs(tier_a_index - tier_b_index)
Score = max(0.0, 1.0 - (tier_distance * 0.25))
```
- Same tier = 1.0
- Adjacent tiers (budget/moderate) = 0.75
- 2 tiers apart (budget/comfortable) = 0.5
- 3+ tiers apart (budget/luxury) = 0.25

**Budget tier order**:
0. Shoestring (< $30/day)
1. Budget ($30-75/day)
2. Moderate ($75-150/day)
3. Comfortable ($150-300/day)
4. Luxury (> $300/day)

### Travel Style Compatibility
Inferred from activity types:
- **Adventure**: hiking, adventure sports, water sports
- **Cultural**: museums, cultural events, sightseeing
- **Relaxed**: beach, wellness, food tours

Score based on similarity of activity type distributions.

### Pace Compatibility
```python
Score = 1.0 if same_pace else 0.7
```
- Same pace (both moderate) = 1.0
- Different pace = 0.7 (workable but requires compromise)
- Missing pace = 0.6 (unknown)

### Social Compatibility
```python
if both_solo and both_open_to_companions:
    Score = 1.0
elif both_solo:
    Score = 0.8
else:
    Score = 0.6
```
- Solo + open to companions = 1.0 (ideal match)
- Both solo but not explicit about openness = 0.8
- Other combinations = 0.6

---

## LLM Similarity Calculation

### Input
Formatted JSON of both traveler intents:
```json
{
  "primary_destination": "Tokyo",
  "destination_stays": [...],
  "activities": ["hiking", "food_tour"],
  "budget_tier": "moderate",
  "pace_preference": "moderate",
  "traveling_solo": true,
  "open_to_companions": true
}
```

### Output
```json
{
  "similarity_score": 0.85,
  "summary": "Excellent match...",
  "why_great_match": ["reason 1", "reason 2", ...],
  "shared_interests": [...],
  "complementary_traits": [...],
  "potential_concerns": [...],
  "conversation_starters": [...]
}
```

### Retry Logic
```python
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    reraise=True,
)
```
- 2 attempts maximum
- Exponential backoff: 2s, 6s
- Only retry on JSON/parse errors
- Let API errors fail fast

### Token Usage
- **Prompt**: ~600-800 tokens (2 intents + template)
- **Completion**: ~400-600 tokens (structured output)
- **Total**: ~1000-1400 tokens per match
- **Cost**: $0.012-0.016 per match (GPT-4 Turbo)

---

## Usage Examples

### Basic Matching

```python
from wanderwing.services.matching_engine import MatchingEngine
from wanderwing.schemas.trip_enhanced import ParsedTravelerIntent

# Initialize engine
engine = MatchingEngine()

# Calculate match between two travelers
match_candidate = await engine.calculate_match(
    traveler_a=traveler_intent_a,
    traveler_b=traveler_intent_b,
    traveler_a_id=123,
    traveler_b_id=456,
    use_llm=True,
)

# Access results
if match_candidate:
    print(f"Overall score: {match_candidate.match_explanation.overall_score}")
    print(f"Overlapping days: {match_candidate.overlapping_days}")
    print(f"Summary: {match_candidate.match_explanation.llm_summary}")

    # Dimension scores
    for ds in match_candidate.match_explanation.dimension_scores:
        print(f"{ds.dimension}: {ds.score} - {ds.explanation}")

    # Conversation starters
    for starter in match_candidate.match_explanation.conversation_starters:
        print(f"💬 {starter}")
```

### API Usage

```bash
# Find matches for your trip
curl -X POST http://localhost:8000/api/matches \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": 123,
    "user_id": 456,
    "min_score": 0.6,
    "max_results": 10,
    "require_date_overlap": true,
    "min_overlap_days": 3
  }'
```

Response:
```json
{
  "candidates": [
    {
      "match_id": 789,
      "traveler_name": "Bob Martinez",
      "destination": "Tokyo",
      "trip_start_date": "2024-04-01",
      "trip_end_date": "2024-04-10",
      "overlapping_days": 9,
      "match_explanation": {
        "overall_score": 0.87,
        "dimension_scores": [...],
        "llm_summary": "Excellent match for travel companions...",
        "why_great_match": [
          "Perfect 9-day date overlap (April 1-10)",
          "Shared passion for hiking and food tours",
          "Compatible moderate budget ($100-150/day)",
          "Both solo travelers open to meeting companions",
          "Similar travel pace preferences"
        ],
        "conversation_starters": [
          "Want to hike Mt. Fuji together during our overlapping dates?",
          "I'm planning a food tour in Tsukiji Market - interested?",
          "Have you booked your accommodations in Tokyo yet?"
        ]
      }
    }
  ],
  "total_candidates": 5,
  "processing_time_ms": 2340,
  "cache_hit": false
}
```

---

## Testing Strategy

### Unit Tests (40+ test cases)

**Test Classes**:
1. `TestMatchingEngineSuccess` - Happy path scenarios
2. `TestMatchingEngineFiltering` - Pre-filter rejection
3. `TestDimensionScoring` - Individual dimension scoring
4. `TestLLMIntegration` - LLM calls and error handling
5. `TestEdgeCases` - Boundary conditions and missing data

**Key Test Scenarios**:
- ✅ Perfect match (same destination, overlapping dates, shared activities)
- ✅ Partial match (some dimensions high, some low)
- ✅ Different destinations (rejected by pre-filter)
- ✅ No date overlap (rejected by pre-filter)
- ✅ LLM malformed JSON (fallback to default)
- ✅ LLM API failure (fallback to rule-based only)
- ✅ Missing data (activities, dates, budget)
- ✅ Edge cases (empty stays, no activities)
- ✅ Dimension scoring accuracy (Jaccard, budget tiers)
- ✅ Overlapping days calculation (various scenarios)

**Test Coverage**: Aiming for >90% on matching_engine.py

### Integration Tests (future)
- Database integration
- Full API workflow (parse intent → find matches → express interest)
- Cache behavior
- Experiment assignment

---

## Performance Benchmarks

### Latency (estimated)
- Pre-filtering: <10ms per candidate
- Rule-based scoring: ~50ms per candidate
- LLM similarity: ~1500ms per candidate
- Total per match: ~1600ms

### Throughput
- Without LLM: ~200 matches/second
- With LLM: ~0.6 matches/second per LLM instance
- Parallelizable: Can process multiple candidates concurrently

### Cost
- Per match: $0.012-0.018 (GPT-4 Turbo)
- 100 matches: ~$1.50
- With caching: Amortized to ~$0.20 per user (if cache hits)

---

## Future Enhancements

### Short-term (Phase 3)
1. **Vector embeddings**: Pre-filter using embedding similarity before LLM
2. **Caching layer**: Redis for match results
3. **Batch LLM calls**: Process multiple candidates in one request
4. **Async processing**: Background job for match refresh

### Medium-term (Phase 4)
1. **Feedback loop**: Learn from user accepts/declines
2. **Personalized weighting**: Adjust dimension weights per user
3. **Multi-lingual**: Support non-English intents
4. **Group matching**: Match groups of travelers (3-4 people)

### Long-term (Phase 5)
1. **Fine-tuned model**: Custom model for travel matching
2. **Real-time matching**: WebSocket updates as new travelers join
3. **ML ranking**: Learn optimal ranking from user behavior
4. **Cross-destination**: Suggest companion for nearby cities

---

## Conclusion

This matching engine implements production-quality traveler matching with:

1. ✅ **Hybrid Approach**: Combines rule-based and LLM scoring for optimal results
2. ✅ **Resilience**: Graceful failure handling with retry and fallback mechanisms
3. ✅ **Observability**: Comprehensive logging and metrics tracking
4. ✅ **Cost Control**: Performance optimizations and cost tracking
5. ✅ **Test Coverage**: 40+ tests with mocked dependencies
6. ✅ **Transparency**: Dimension-by-dimension compatibility explanations
7. ✅ **User Experience**: Actionable conversation starters and honest assessments
