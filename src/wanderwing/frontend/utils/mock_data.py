"""
Mock data generators for WanderWing frontend demo.

Provides realistic sample data for testing and demonstration.
"""

import random
from datetime import datetime, timedelta


def generate_parsed_intent(raw_text):
    """
    Generate a mock parsed intent from raw text.

    In production, this would call the actual intent parser.
    """
    # Extract destination (simple keyword matching for demo)
    destinations = ["Tokyo", "Paris", "Barcelona", "London", "New York"]
    destination = next((d for d in destinations if d.lower() in raw_text.lower()), "Tokyo")

    # Extract dates (mock - assumes "in April" or similar)
    today = datetime.now().date()
    start_date = today + timedelta(days=30)
    end_date = start_date + timedelta(days=random.randint(5, 14))

    # Extract activities (keyword matching)
    activity_keywords = {
        "hiking": "HIKING",
        "hike": "HIKING",
        "food": "FOOD_TOURS",
        "museum": "MUSEUMS",
        "culture": "CULTURAL_EVENTS",
        "beach": "BEACHES",
        "adventure": "ADVENTURE_SPORTS",
        "shopping": "SHOPPING",
        "nightlife": "NIGHTLIFE",
    }

    detected_activities = []
    for keyword, activity in activity_keywords.items():
        if keyword in raw_text.lower():
            detected_activities.append(activity)

    if not detected_activities:
        detected_activities = ["SIGHTSEEING", "LOCAL_EXPERIENCES"]

    # Extract budget (keyword matching)
    budget = "MODERATE"
    if "budget" in raw_text.lower() or "cheap" in raw_text.lower():
        budget = "BUDGET"
    elif "luxury" in raw_text.lower() or "expensive" in raw_text.lower():
        budget = "COMFORTABLE"

    # Extract pace
    pace = "MODERATE"
    if "fast" in raw_text.lower() or "quick" in raw_text.lower():
        pace = "FAST"
    elif "relaxed" in raw_text.lower() or "slow" in raw_text.lower():
        pace = "RELAXED"

    return {
        "primary_destination": destination,
        "overall_start_date": start_date.strftime("%Y-%m-%d"),
        "overall_end_date": end_date.strftime("%Y-%m-%d"),
        "duration_days": (end_date - start_date).days,
        "activities": detected_activities,
        "budget_tier": budget,
        "pace_preference": pace,
        "traveling_solo": True,
        "open_to_companions": True,
        "accommodation_type": "HOSTEL" if budget == "BUDGET" else "HOTEL",
        "confidence_score": 0.85,
    }


def generate_mock_matches(user_profile, parsed_intent, num_matches=5):
    """Generate mock match results."""
    destinations = [parsed_intent["primary_destination"]]

    matches = []
    names = ["Alice", "Bob", "Charlie", "Diana", "Erik", "Fiona", "Grace", "Henry"]
    used_names = []

    for i in range(num_matches):
        # Pick a unique name
        available_names = [n for n in names if n not in used_names]
        if not available_names:
            break

        name = random.choice(available_names)
        used_names.append(name)

        # Generate compatibility score (higher for first matches)
        base_score = 0.85 - (i * 0.08)
        score = base_score + random.uniform(-0.05, 0.05)
        score = max(0.4, min(1.0, score))

        # Determine shared activities
        shared_activities = parsed_intent["activities"][:random.randint(2, len(parsed_intent["activities"]))]

        # Generate match data
        match = {
            "match_id": f"match_{i+1}",
            "name": name,
            "age_range": random.choice(["UNDER_25", "AGE_25_34", "AGE_35_44"]),
            "verification_level": random.randint(1, 4),
            "trust_score": round(random.uniform(0.65, 0.95), 2),
            "overall_score": round(score, 2),
            "component_scores": {
                "destination": 1.0,
                "date_overlap": round(random.uniform(0.7, 1.0), 2),
                "activity_similarity": round(random.uniform(0.5, 0.9), 2),
                "budget_compatibility": round(random.uniform(0.75, 1.0), 2),
                "pace_compatibility": round(random.uniform(0.7, 1.0), 2),
                "social_compatibility": 1.0,
                "age_compatibility": round(random.uniform(0.8, 1.0), 2),
            },
            "shared_activities": shared_activities,
            "reasons": [
                "SAME_DESTINATION",
                "OVERLAPPING_DATES",
                "SHARED_INTEREST",
                "COMPATIBLE_BUDGET",
            ],
            "explanation": f"{name} is traveling to {parsed_intent['primary_destination']} during the same dates and shares your interest in {', '.join(shared_activities[:2])}. Great budget compatibility and similar travel pace.",
            "confidence": round(random.uniform(0.7, 0.9), 2),
            "safety_flags": [] if random.random() > 0.2 else ["NEW_USER"],
        }

        matches.append(match)

    # Sort by score
    matches.sort(key=lambda m: m["overall_score"], reverse=True)

    return matches


def generate_mock_activities(match_data, parsed_intent, num_activities=5):
    """Generate mock activity recommendations."""
    destination = parsed_intent["primary_destination"]

    # Activity templates by destination
    activity_templates = {
        "Tokyo": [
            {
                "name": "Mount Fuji Day Hike",
                "description": "Day trip to Mt. Fuji with guided trail to 5th station. Stunning views, moderate difficulty.",
                "tags": ["outdoors", "adventure"],
                "cost": "$50-100",
                "duration": "10 hours",
            },
            {
                "name": "Tsukiji Food Market Tour",
                "description": "Explore Tokyo's famous fish market. Sample fresh sushi, tamagoyaki, and street food.",
                "tags": ["food", "local-experience"],
                "cost": "$20-50",
                "duration": "3 hours",
            },
            {
                "name": "Meiji Shrine Visit",
                "description": "Peaceful Shinto shrine surrounded by forest. Free entry, cultural immersion.",
                "tags": ["culture", "introvert-friendly", "low-cost"],
                "cost": "Free",
                "duration": "1.5 hours",
            },
            {
                "name": "Shibuya Izakaya Hopping",
                "description": "Experience Tokyo's izakaya culture. Visit 3-4 local spots, try sake and small plates.",
                "tags": ["food", "nightlife", "local-experience"],
                "cost": "$20-50",
                "duration": "3.5 hours",
            },
            {
                "name": "teamLab Borderless Museum",
                "description": "Immersive digital art experience with interactive installations.",
                "tags": ["culture", "introvert-friendly"],
                "cost": "$20-50",
                "duration": "2 hours",
            },
        ],
        "Paris": [
            {
                "name": "Louvre Museum",
                "description": "World's largest art museum. Home to Mona Lisa and 35,000+ artworks.",
                "tags": ["culture", "educational"],
                "cost": "$20-50",
                "duration": "3.5 hours",
            },
            {
                "name": "Eiffel Tower Picnic",
                "description": "Buy fresh bread, cheese, and wine. Picnic at Champ de Mars with tower views.",
                "tags": ["food", "outdoors", "low-cost"],
                "cost": "$5-20",
                "duration": "2 hours",
            },
            {
                "name": "Montmartre Walking Tour",
                "description": "Explore artistic Montmartre: Sacré-Cœur, Place du Tertre, cobblestone streets.",
                "tags": ["culture", "local-experience"],
                "cost": "Free",
                "duration": "2.5 hours",
            },
        ],
        "Barcelona": [
            {
                "name": "Sagrada Família",
                "description": "Gaudí's iconic basilica. Breathtaking architecture with skip-the-line tickets.",
                "tags": ["culture", "educational"],
                "cost": "$20-50",
                "duration": "2 hours",
            },
            {
                "name": "Gothic Quarter Tapas Tour",
                "description": "Visit 4-5 authentic tapas bars. Sample patatas bravas, jamón, pan con tomate.",
                "tags": ["food", "local-experience"],
                "cost": "$20-50",
                "duration": "3 hours",
            },
            {
                "name": "Barceloneta Beach",
                "description": "City beach. Swim, sunbathe, or grab fresh seafood at chiringuito.",
                "tags": ["outdoors", "low-cost"],
                "cost": "Free",
                "duration": "3 hours",
            },
        ],
    }

    # Get activities for destination
    activities_pool = activity_templates.get(destination, activity_templates["Tokyo"])
    selected_activities = random.sample(activities_pool, min(num_activities, len(activities_pool)))

    # Generate recommendations
    recommendations = []
    for i, activity in enumerate(selected_activities):
        score = 0.85 - (i * 0.05) + random.uniform(-0.03, 0.03)
        score = max(0.5, min(1.0, score))

        # Find shared interests
        shared_interests = []
        for act in parsed_intent["activities"]:
            act_lower = act.lower()
            if "food" in act_lower and "food" in activity["tags"]:
                shared_interests.append("Food Tours")
            elif "hiking" in act_lower and "outdoors" in activity["tags"]:
                shared_interests.append("Hiking")
            elif "culture" in act_lower and "culture" in activity["tags"]:
                shared_interests.append("Cultural Events")

        if not shared_interests:
            shared_interests = ["Sightseeing"]

        rec = {
            "activity_id": f"activity_{i+1}",
            "name": activity["name"],
            "description": activity["description"],
            "tags": activity["tags"],
            "cost": activity["cost"],
            "duration": activity["duration"],
            "score": round(score, 2),
            "shared_interests": shared_interests,
            "explanation": f"{activity['description']} Great match for your shared interest in {', '.join(shared_interests)}.",
            "meeting_suggestion": f"Would you be interested in trying {activity['name']} together? I've heard great things about it.",
        }

        recommendations.append(rec)

    return recommendations


def generate_dashboard_metrics():
    """Generate mock dashboard metrics."""
    return {
        "total_matches": random.randint(450, 550),
        "match_acceptance_rate": round(random.uniform(0.62, 0.72), 2),
        "avg_feedback_score": round(random.uniform(4.1, 4.6), 1),
        "parse_success_rate": round(random.uniform(0.88, 0.94), 2),
        "active_users": random.randint(180, 220),
    }


def generate_acceptance_rate_by_day(days=30):
    """Generate mock acceptance rate trend data."""
    data = []
    base_rate = 0.65

    for i in range(days):
        date = (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d")
        rate = base_rate + random.uniform(-0.1, 0.15)
        rate = max(0.4, min(0.9, rate))

        data.append({
            "date": date,
            "acceptance_rate": round(rate, 3),
        })

    return data


def generate_feedback_by_variant():
    """Generate mock feedback scores by UX variant."""
    return [
        {"variant": "Variant A (Current)", "avg_score": round(random.uniform(4.0, 4.3), 2), "count": random.randint(80, 120)},
        {"variant": "Variant B (New UI)", "avg_score": round(random.uniform(4.3, 4.7), 2), "count": random.randint(70, 110)},
        {"variant": "Variant C (Experimental)", "avg_score": round(random.uniform(3.8, 4.2), 2), "count": random.randint(40, 60)},
    ]


def generate_parse_success_over_time(weeks=12):
    """Generate mock parse success rate over time."""
    data = []
    base_rate = 0.85

    for i in range(weeks):
        week = f"Week {i+1}"
        rate = base_rate + (i * 0.01) + random.uniform(-0.03, 0.03)
        rate = max(0.75, min(0.95, rate))

        data.append({
            "week": week,
            "success_rate": round(rate, 3),
        })

    return data
