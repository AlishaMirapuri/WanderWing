"""User-related Pydantic schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


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


class BudgetTier(str, Enum):
    """Budget tier classification."""

    BUDGET = "budget"
    MODERATE = "moderate"
    COMFORTABLE = "comfortable"
    LUXURY = "luxury"


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    travel_styles: list[TravelStyle] = Field(default_factory=list)
    budget_tier: BudgetTier = Field(default=BudgetTier.MODERATE)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    travel_styles: list[TravelStyle] | None = None
    budget_tier: BudgetTier | None = None


class User(UserBase):
    """Full user schema."""

    id: int
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SafetyPreferences(BaseModel):
    """User safety and privacy preferences."""

    profile_visibility: str = Field(default="public")  # public, connections_only, private
    allow_messages_from: str = Field(default="matched")  # anyone, matched, connections
    share_exact_dates: bool = Field(default=True)
    share_accommodation: bool = Field(default=False)
