"""Traveler profile schemas with comprehensive validation."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class Gender(str, Enum):
    """Gender options for profile."""

    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class AgeRange(str, Enum):
    """Age range brackets."""

    EIGHTEEN_TO_TWENTY_FOUR = "18-24"
    TWENTY_FIVE_TO_THIRTY_FOUR = "25-34"
    THIRTY_FIVE_TO_FORTY_FOUR = "35-44"
    FORTY_FIVE_TO_FIFTY_FOUR = "45-54"
    FIFTY_FIVE_PLUS = "55+"


class LanguageProficiency(str, Enum):
    """Language proficiency levels."""

    NATIVE = "native"
    FLUENT = "fluent"
    CONVERSATIONAL = "conversational"
    BASIC = "basic"


class TravelStyle(str, Enum):
    """Travel style preferences."""

    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CULTURE = "culture"
    FOOD = "food"
    NIGHTLIFE = "nightlife"
    NATURE = "nature"
    BUDGET = "budget"
    LUXURY = "luxury"
    PHOTOGRAPHY = "photography"
    WELLNESS = "wellness"
    DIGITAL_NOMAD = "digital_nomad"


class AccommodationType(str, Enum):
    """Preferred accommodation types."""

    HOSTEL = "hostel"
    BUDGET_HOTEL = "budget_hotel"
    MID_RANGE_HOTEL = "mid_range_hotel"
    LUXURY_HOTEL = "luxury_hotel"
    AIRBNB = "airbnb"
    GUESTHOUSE = "guesthouse"
    CAMPING = "camping"
    RESORT = "resort"


class SocialStyle(str, Enum):
    """Social interaction preferences."""

    VERY_SOCIAL = "very_social"
    MODERATELY_SOCIAL = "moderately_social"
    SELECTIVE = "selective"
    PREFER_SOLO = "prefer_solo"


class ProfileVisibility(str, Enum):
    """Profile visibility settings."""

    PUBLIC = "public"
    CONNECTIONS_ONLY = "connections_only"
    PRIVATE = "private"


class MessagePermission(str, Enum):
    """Who can send messages."""

    ANYONE = "anyone"
    MATCHED_ONLY = "matched_only"
    CONNECTIONS_ONLY = "connections_only"
    NO_ONE = "no_one"


class LanguageSkill(BaseModel):
    """Language proficiency entry."""

    language: Annotated[str, Field(min_length=2, max_length=50)]
    proficiency: LanguageProficiency

    model_config = {"json_schema_extra": {"example": {"language": "Spanish", "proficiency": "conversational"}}}


class TravelPreferences(BaseModel):
    """Comprehensive travel preferences."""

    travel_styles: Annotated[list[TravelStyle], Field(min_length=1, max_length=5)]
    accommodation_types: Annotated[list[AccommodationType], Field(max_length=3)] = []
    budget_per_day_usd: Annotated[int | None, Field(ge=0, le=10000)] = None
    willing_to_share_accommodation: bool = False
    willing_to_share_transportation: bool = True
    dietary_restrictions: Annotated[list[str], Field(max_length=10)] = []
    accessibility_needs: Annotated[list[str], Field(max_length=10)] = []
    interests: Annotated[list[str], Field(max_length=20)] = []
    social_style: SocialStyle = SocialStyle.MODERATELY_SOCIAL
    prefer_guided_tours: bool | None = None
    prefer_off_beaten_path: bool | None = None
    early_bird_or_night_owl: Annotated[str | None, Field(pattern="^(early_bird|night_owl)$")] = None

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, v: list[str]) -> list[str]:
        """Ensure interests are not empty strings."""
        return [interest.strip() for interest in v if interest.strip()]

    model_config = {
        "json_schema_extra": {
            "example": {
                "travel_styles": ["adventure", "culture"],
                "accommodation_types": ["hostel", "airbnb"],
                "budget_per_day_usd": 75,
                "willing_to_share_accommodation": True,
                "willing_to_share_transportation": True,
                "dietary_restrictions": ["vegetarian"],
                "accessibility_needs": [],
                "interests": ["hiking", "photography", "local cuisine"],
                "social_style": "moderately_social",
                "prefer_guided_tours": False,
                "prefer_off_beaten_path": True,
                "early_bird_or_night_owl": "early_bird",
            }
        }
    }


class SafetyPreferences(BaseModel):
    """Safety and privacy preferences."""

    profile_visibility: ProfileVisibility = ProfileVisibility.PUBLIC
    allow_messages_from: MessagePermission = MessagePermission.MATCHED_ONLY
    share_exact_dates: bool = True
    share_accommodation_details: bool = False
    share_phone_number: bool = False
    share_social_media: bool = False
    require_verified_profiles: bool = True
    auto_decline_unverified: bool = False
    blocked_user_ids: Annotated[list[int], Field(max_length=100)] = []
    emergency_contact_name: Annotated[str | None, Field(max_length=100)] = None
    emergency_contact_phone: Annotated[str | None, Field(max_length=20)] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "profile_visibility": "public",
                "allow_messages_from": "matched_only",
                "share_exact_dates": True,
                "share_accommodation_details": False,
                "share_phone_number": False,
                "share_social_media": False,
                "require_verified_profiles": True,
                "auto_decline_unverified": False,
                "blocked_user_ids": [],
                "emergency_contact_name": "Jane Doe",
                "emergency_contact_phone": "+1-555-0100",
            }
        }
    }


class TravelerProfileBase(BaseModel):
    """Base traveler profile fields."""

    name: Annotated[str, Field(min_length=1, max_length=100)]
    bio: Annotated[str | None, Field(max_length=1000)] = None
    location: Annotated[str | None, Field(max_length=100)] = None
    age_range: AgeRange | None = None
    gender: Gender | None = None
    languages: Annotated[list[LanguageSkill], Field(max_length=10)] = []
    occupation: Annotated[str | None, Field(max_length=100)] = None
    travel_experience_years: Annotated[int | None, Field(ge=0, le=100)] = None
    countries_visited: Annotated[int | None, Field(ge=0, le=300)] = None
    avatar_url: Annotated[str | None, Field(max_length=500)] = None
    social_media_links: Annotated[dict[str, str], Field(max_length=5)] = {}

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        """Ensure bio is meaningful."""
        if v and len(v.strip()) < 10:
            raise ValueError("Bio must be at least 10 characters if provided")
        return v.strip() if v else None

    @field_validator("social_media_links")
    @classmethod
    def validate_social_links(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate social media links."""
        allowed_platforms = {"instagram", "facebook", "twitter", "linkedin", "website"}
        for platform in v.keys():
            if platform not in allowed_platforms:
                raise ValueError(f"Platform {platform} not allowed. Use: {allowed_platforms}")
        return v


class TravelerProfileCreate(TravelerProfileBase):
    """Schema for creating a traveler profile."""

    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
    preferences: TravelPreferences
    safety_preferences: SafetyPreferences = SafetyPreferences()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "alice.chen@example.com",
                "password": "SecurePass123",
                "name": "Alice Chen",
                "bio": "Digital nomad and adventure seeker. Love hiking, trying local street food, and meeting fellow travelers. Always up for spontaneous adventures!",
                "location": "San Francisco, CA",
                "age_range": "25-34",
                "gender": "female",
                "languages": [
                    {"language": "English", "proficiency": "native"},
                    {"language": "Mandarin", "proficiency": "conversational"},
                ],
                "occupation": "Software Engineer",
                "travel_experience_years": 8,
                "countries_visited": 23,
                "preferences": {
                    "travel_styles": ["adventure", "culture", "food"],
                    "accommodation_types": ["hostel", "airbnb"],
                    "budget_per_day_usd": 100,
                    "willing_to_share_accommodation": True,
                    "willing_to_share_transportation": True,
                    "dietary_restrictions": [],
                    "interests": ["hiking", "photography", "local cuisine", "temples"],
                    "social_style": "very_social",
                    "prefer_off_beaten_path": True,
                },
                "safety_preferences": {
                    "profile_visibility": "public",
                    "allow_messages_from": "matched_only",
                    "share_exact_dates": True,
                    "require_verified_profiles": True,
                },
            }
        }
    }


class TravelerProfileUpdate(BaseModel):
    """Schema for updating a traveler profile."""

    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    bio: Annotated[str | None, Field(max_length=1000)] = None
    location: Annotated[str | None, Field(max_length=100)] = None
    age_range: AgeRange | None = None
    gender: Gender | None = None
    languages: Annotated[list[LanguageSkill] | None, Field(max_length=10)] = None
    occupation: Annotated[str | None, Field(max_length=100)] = None
    travel_experience_years: Annotated[int | None, Field(ge=0, le=100)] = None
    countries_visited: Annotated[int | None, Field(ge=0, le=300)] = None
    avatar_url: Annotated[str | None, Field(max_length=500)] = None
    preferences: TravelPreferences | None = None
    safety_preferences: SafetyPreferences | None = None


class TravelerProfile(TravelerProfileBase):
    """Full traveler profile response."""

    id: int
    email: EmailStr
    preferences: TravelPreferences
    safety_preferences: SafetyPreferences
    is_verified: bool = False
    verification_level: Annotated[int, Field(ge=0, le=5)] = 0
    is_active: bool = True
    trust_score: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    total_trips: int = 0
    total_connections: int = 0
    joined_date: datetime
    last_active: datetime

    model_config = {"from_attributes": True}


class TravelerProfilePublic(BaseModel):
    """Public-facing traveler profile (limited fields for privacy)."""

    id: int
    name: str
    bio: str | None
    location: str | None
    age_range: AgeRange | None
    gender: Gender | None
    languages: list[LanguageSkill]
    travel_experience_years: int | None
    countries_visited: int | None
    avatar_url: str | None
    travel_styles: list[TravelStyle]
    is_verified: bool
    verification_level: int
    trust_score: float
    total_trips: int
    total_connections: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 123,
                "name": "Alice Chen",
                "bio": "Digital nomad and adventure seeker...",
                "location": "San Francisco, CA",
                "age_range": "25-34",
                "gender": "female",
                "languages": [{"language": "English", "proficiency": "native"}],
                "travel_experience_years": 8,
                "countries_visited": 23,
                "avatar_url": "https://example.com/avatars/alice.jpg",
                "travel_styles": ["adventure", "culture", "food"],
                "is_verified": True,
                "verification_level": 3,
                "trust_score": 0.87,
                "total_trips": 15,
                "total_connections": 42,
            }
        }
    }
