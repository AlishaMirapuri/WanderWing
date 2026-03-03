"""Evaluate and compare different prompt versions."""

import asyncio
import json
from pathlib import Path

from wanderwing.agents.itinerary_extractor import extract_itinerary
from wanderwing.schemas.trip import ParsedItinerary


# Test cases for prompt evaluation
TEST_CASES = [
    {
        "input": "Going to Tokyo for 10 days in April, love hiking and trying local food",
        "expected": {
            "destination": "Tokyo",
            "duration_days": 10,
            "has_activities": True,
        },
    },
    {
        "input": "2-week backpacking trip through Southeast Asia starting in Bangkok",
        "expected": {
            "destination": "Bangkok",
            "duration_days": 14,
        },
    },
    {
        "input": "Weekend getaway to Paris next month, interested in art museums",
        "expected": {
            "destination": "Paris",
        },
    },
    {
        "input": "Planning a luxury beach resort stay in Bali for relaxation",
        "expected": {
            "destination": "Bali",
            "budget_tier": "luxury",
        },
    },
]


async def evaluate_extraction(test_case: dict) -> dict:
    """
    Evaluate itinerary extraction on a test case.

    Args:
        test_case: Test case with input and expected output

    Returns:
        Evaluation results
    """
    user_input = test_case["input"]
    expected = test_case["expected"]

    try:
        result = await extract_itinerary(user_input)

        # Check expectations
        matches = []
        misses = []

        if "destination" in expected:
            if result.destination.lower() == expected["destination"].lower():
                matches.append("destination")
            else:
                misses.append(
                    f"destination (expected: {expected['destination']}, got: {result.destination})"
                )

        if "duration_days" in expected:
            if result.duration_days == expected["duration_days"]:
                matches.append("duration_days")
            else:
                misses.append(
                    f"duration_days (expected: {expected['duration_days']}, got: {result.duration_days})"
                )

        if "has_activities" in expected:
            if expected["has_activities"] and result.activities:
                matches.append("has_activities")
            elif not expected["has_activities"] and not result.activities:
                matches.append("has_activities")
            else:
                misses.append("has_activities")

        if "budget_tier" in expected:
            if result.budget_tier.lower() == expected["budget_tier"].lower():
                matches.append("budget_tier")
            else:
                misses.append(
                    f"budget_tier (expected: {expected['budget_tier']}, got: {result.budget_tier})"
                )

        return {
            "input": user_input,
            "success": len(misses) == 0,
            "matches": matches,
            "misses": misses,
            "confidence": result.confidence_score,
            "result": result.model_dump(),
        }

    except Exception as e:
        return {
            "input": user_input,
            "success": False,
            "error": str(e),
        }


async def main() -> None:
    """Main evaluation function."""
    print("Prompt Evaluation Suite")
    print("=" * 50)
    print()

    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"Test Case {i}: {test_case['input'][:60]}...")
        result = await evaluate_extraction(test_case)
        results.append(result)

        if result["success"]:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
            if "misses" in result:
                for miss in result["misses"]:
                    print(f"    - {miss}")

        print()

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    success_rate = (passed / total * 100) if total > 0 else 0

    print("=" * 50)
    print(f"Results: {passed}/{total} passed ({success_rate:.1f}%)")
    print()

    # Save results
    output_path = Path("data/prompt_evaluation_results.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Detailed results saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
