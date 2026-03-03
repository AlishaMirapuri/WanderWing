"""Traveler profile API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from wanderwing.api.dependencies import get_current_user_id
from wanderwing.schemas.profile import (
    TravelerProfile,
    TravelerProfileCreate,
    TravelerProfilePublic,
    TravelerProfileUpdate,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=TravelerProfile, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: TravelerProfileCreate,
) -> TravelerProfile:
    """
    Create a new traveler profile.

    This endpoint creates a complete traveler profile including:
    - Basic information (name, bio, location)
    - Travel preferences (styles, budget, activities)
    - Safety preferences (privacy, verification requirements)
    - Language skills

    Password must meet security requirements:
    - At least 8 characters
    - Contains uppercase, lowercase, and digit

    Returns the created profile with assigned ID.
    """
    # TODO: Implement profile creation
    # 1. Validate password strength
    # 2. Hash password
    # 3. Create user in database
    # 4. Return profile (without password)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile creation not yet implemented",
    )


@router.get("/{profile_id}", response_model=TravelerProfilePublic)
async def get_profile(
    profile_id: int,
    user_id: int = Depends(get_current_user_id),
) -> TravelerProfilePublic:
    """
    Get a traveler profile by ID.

    Returns public-facing profile information based on user's privacy settings.

    If viewing own profile, returns full details.
    If viewing another user's profile, respects their privacy settings:
    - Public: All non-sensitive fields
    - Connections only: Limited to connected users
    - Private: Only basic info
    """
    # TODO: Implement profile retrieval
    # 1. Check if profile exists
    # 2. Check privacy settings
    # 3. Filter fields based on requester relationship
    # 4. Return appropriate profile view
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile retrieval not yet implemented",
    )


@router.patch("/{profile_id}", response_model=TravelerProfile)
async def update_profile(
    profile_id: int,
    profile_data: TravelerProfileUpdate,
    user_id: int = Depends(get_current_user_id),
) -> TravelerProfile:
    """
    Update a traveler profile.

    Only the profile owner can update their profile.
    Partial updates are supported - only send fields that should change.

    Returns the updated profile.
    """
    # TODO: Implement profile update
    # 1. Verify ownership (user_id matches profile owner)
    # 2. Validate updated fields
    # 3. Update database
    # 4. Return updated profile
    if profile_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update own profile",
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile update not yet implemented",
    )


@router.get("/{profile_id}/verification-status")
async def get_verification_status(
    profile_id: int,
    user_id: int = Depends(get_current_user_id),
) -> dict:
    """
    Get profile verification status and requirements.

    Returns:
    - Current verification level (0-5)
    - Trust score
    - Verified attributes (email, phone, ID, etc.)
    - Next steps to increase verification level
    """
    # TODO: Implement verification status retrieval
    return {
        "profile_id": profile_id,
        "verification_level": 0,
        "trust_score": 0.5,
        "verified_attributes": [],
        "next_steps": [
            "Verify email address",
            "Add profile photo",
            "Connect social media account",
        ],
    }


@router.post("/{profile_id}/verify-email")
async def verify_email(
    profile_id: int,
    verification_code: str,
    user_id: int = Depends(get_current_user_id),
) -> dict:
    """
    Verify email address with code sent to email.

    This increases verification level and trust score.
    """
    # TODO: Implement email verification
    # 1. Check verification code
    # 2. Update verified status
    # 3. Increase verification level
    # 4. Update trust score
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email verification not yet implemented",
    )
