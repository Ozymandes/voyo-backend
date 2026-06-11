"""
Profile Routes for VOYO API
User profile CRUD with JSONB merge support.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.routes.auth import get_current_user, AuthUser
from src.database.supabase_client import SupabaseClient, VOYODatabase

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── Module-level DB instances ─────────────────────────────────────────
# Reuse a single SupabaseClient / VOYODatabase per process.
# These are cheap to create (the underlying httpx session is pooled).
# They are NOT singletons — import-time instantiation is fine for a
# single-process FastAPI server.  For multi-worker deployments, each
# worker gets its own instance, which is the intended behaviour.

try:
    _supabase = SupabaseClient()
    _db = VOYODatabase()
except Exception as exc:
    logger.warning("Supabase client init failed: %s. Profile routes will 503.", exc)
    _supabase = None  # type: ignore[assignment]
    _db = None  # type: ignore[assignment]


def _require_db() -> VOYODatabase:
    """Raise 503 if the DB client couldn't initialise."""
    if _db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "database_unavailable",
                "message": "Database connection is not configured.",
            },
        )
    return _db


# ═══════════════════════════════════════════════════════════════════════
# Pydantic request / response models
# ═══════════════════════════════════════════════════════════════════════


class ProfileUpdateRequest(BaseModel):
    """Partial update of top-level profile fields."""

    full_name: Optional[str] = Field(None, max_length=100)
    home_country: Optional[str] = Field(None, max_length=50)
    age_range: Optional[str] = Field(
        None,
        description="One of: 18-24, 25-34, 35-44, 45-54, 55-64, 65+",
    )
    typical_companions: Optional[Dict[str, Any]] = None
    trips_per_year: Optional[int] = Field(None, ge=0, le=365)
    accommodation_type_preference: Optional[str] = None
    itinerary_pace: Optional[str] = Field(
        None,
        description="packed_schedule | balanced | slow_flexible",
    )
    planning_style: Optional[str] = Field(
        None,
        description="everything_pre_planned | mix_of_planned_spontaneous | mostly_spontaneous",
    )
    loved_trip_description: Optional[str] = None
    mobility_preference: Optional[str] = None
    comfort_level: Optional[str] = None
    favorite_cuisines: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    chronotype: Optional[str] = None
    trip_budget_estimate: Optional[float] = Field(None, ge=0)
    price_sensitivity: Optional[str] = Field(
        None, description="budget | moderate | luxury"
    )
    accessibility_needs: Optional[str] = None
    allow_long_term_profile: Optional[bool] = None


class PreferencesUpdateRequest(BaseModel):
    """
    Update only preference / interest fields.

    ``interest_scores`` and ``personal_interests`` are **merged** into the
    existing JSONB value — they never overwrite what's already stored.
    """

    interest_scores: Optional[Dict[str, Any]] = Field(
        None,
        description="Partial scores to merge, e.g. {\"history\": 0.9, \"food\": 0.7}",
    )
    personal_interests: Optional[Dict[str, Any]] = Field(
        None,
        description="Partial interests to merge, e.g. {\"museums\": true}",
    )
    itinerary_pace: Optional[str] = Field(
        None, description="packed_schedule | balanced | slow_flexible"
    )
    price_sensitivity: Optional[str] = Field(
        None, description="budget | moderate | luxury"
    )
    mobility_preference: Optional[str] = None
    trip_budget_estimate: Optional[float] = Field(None, ge=0)
    travel_style: Optional[Dict[str, Any]] = None
    planning_style: Optional[str] = Field(
        None,
        description="everything_pre_planned | mix_of_planned_spontaneous | mostly_spontaneous",
    )
    typical_companions: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    """Full profile payload returned to the client."""

    user_id: str
    full_name: Optional[str] = None
    home_country: Optional[str] = None
    age_range: Optional[str] = None
    typical_companions: Optional[Dict[str, Any]] = None
    trips_per_year: Optional[int] = None
    travel_style: Optional[Dict[str, Any]] = None
    accommodation_type_preference: Optional[str] = None
    interest_scores: Optional[Dict[str, Any]] = None
    itinerary_pace: Optional[str] = None
    planning_style: Optional[str] = None
    loved_trip_description: Optional[str] = None
    mobility_preference: Optional[str] = None
    comfort_level: Optional[str] = None
    favorite_cuisines: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    chronotype: Optional[str] = None
    trip_budget_estimate: Optional[float] = None
    price_sensitivity: Optional[str] = None
    accessibility_needs: Optional[str] = None
    personal_interests: Optional[Dict[str, Any]] = None
    allow_long_term_profile: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PreferencesResponse(BaseModel):
    """Only the preference / interest subset (what CLEO needs)."""

    interest_scores: Optional[Dict[str, Any]] = None
    personal_interests: Optional[Dict[str, Any]] = None
    itinerary_pace: Optional[str] = None
    price_sensitivity: Optional[str] = None
    mobility_preference: Optional[str] = None
    trip_budget_estimate: Optional[float] = None
    travel_style: Optional[Dict[str, Any]] = None
    planning_style: Optional[str] = None
    typical_companions: Optional[Dict[str, Any]] = None


class ProfileSummaryResponse(BaseModel):
    """Lightweight profile summary for UI chrome (avatar, sidebar)."""

    user_id: str
    full_name: Optional[str] = None
    avatar_initial: Optional[str] = None
    itinerary_pace: Optional[str] = None
    price_sensitivity: Optional[str] = None
    home_country: Optional[str] = None


class ErrorResponse(BaseModel):
    """Structured error envelope."""

    error: str
    message: str
    detail: Optional[Any] = None


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

# JSONB columns that must be merged, not replaced
_MERGE_JSONB_COLUMNS = {"interest_scores", "personal_interests"}


def _serialize_profile(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalise a Supabase row dict into a JSON-serialisable profile dict.

    Handles datetime objects and strips internal fields.
    """
    out: Dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out


def _default_profile(user_id: str) -> Dict[str, Any]:
    """
    Return a sensible default profile for users whose profile row
    hasn't been created yet (e.g. trigger hasn't fired).
    """
    return {
        "user_id": user_id,
        "full_name": None,
        "home_country": None,
        "age_range": None,
        "typical_companions": None,
        "trips_per_year": None,
        "travel_style": {},
        "accommodation_type_preference": None,
        "interest_scores": {},
        "itinerary_pace": "balanced",
        "planning_style": "mix_of_planned_spontaneous",
        "loved_trip_description": None,
        "mobility_preference": None,
        "comfort_level": None,
        "favorite_cuisines": None,
        "dietary_restrictions": None,
        "chronotype": None,
        "trip_budget_estimate": None,
        "price_sensitivity": "moderate",
        "accessibility_needs": None,
        "personal_interests": {},
        "allow_long_term_profile": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
    }


def _get_profile_row(db: VOYODatabase, user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch the raw profile row, returns None if not found."""
    return db.get_user_profile(user_id)


def _upsert_profile(db: VOYODatabase, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert a new profile or update the existing one.

    For JSONB columns listed in ``_MERGE_JSONB_COLUMNS``, the new data is
    merged with whatever is currently stored.
    """
    # Separate mergeable JSONB fields from plain fields
    merge_data = {}
    plain_data = {}
    for key, value in data.items():
        if value is None:
            continue
        if key in _MERGE_JSONB_COLUMNS and isinstance(value, dict):
            merge_data[key] = value
        else:
            plain_data[key] = value

    # First, try to read the existing profile
    existing = _get_profile_row(db, user_id)

    if existing is None:
        # No row at all — insert a fresh profile.
        # Merge data becomes the initial JSONB value.
        insert_payload = {
            "user_id": user_id,
            "interest_scores": merge_data.get("interest_scores", {}),
            "personal_interests": merge_data.get("personal_interests", {}),
            "itinerary_pace": plain_data.get("itinerary_pace", "balanced"),
            "planning_style": plain_data.get(
                "planning_style", "mix_of_planned_spontaneous"
            ),
            "travel_style": plain_data.get("travel_style", {}),
            "price_sensitivity": plain_data.get("price_sensitivity", "moderate"),
        }
        # Carry over any other plain fields
        for k, v in plain_data.items():
            if k not in insert_payload:
                insert_payload[k] = v

        result = db.create_user_profile(user_id, insert_payload)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "profile_create_failed",
                    "message": "Failed to create user profile.",
                },
            )
        return result

    # ── Row exists — apply updates ────────────────────────────────────
    # Merge JSONB columns
    for col, new_vals in merge_data.items():
        current = existing.get(col, {})
        if not isinstance(current, dict):
            current = {}
        merged = {**current, **new_vals}
        plain_data[col] = merged  # treat as a normal update now

    if not plain_data:
        # Nothing to update (all values were None)
        return existing

    result = db.update_user_profile(user_id, plain_data)
    if result is None:
        # The admin client update may have failed due to RLS — try admin
        result = db.db.update_record(
            "user_profiles",
            record_id=user_id,
            data=plain_data,
            id_column="user_id",
            use_admin=True,
        )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "profile_update_failed",
                "message": "Failed to update user profile.",
            },
        )
    return result


# ═══════════════════════════════════════════════════════════════════════
# Route handlers
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get current user's full profile",
)
async def get_profile(user: AuthUser = Depends(get_current_user)):
    """
    Returns the authenticated user's full profile.
    If no profile row exists yet, returns defaults (does NOT 404).
    """
    db = _require_db()
    raw = _get_profile_row(db, user["user_id"])

    if raw is None:
        return _default_profile(user["user_id"])

    return _serialize_profile(raw)


@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Update profile fields",
)
async def update_profile(
    body: ProfileUpdateRequest,
    user: AuthUser = Depends(get_current_user),
):
    """
    Partial-update of profile fields.  Only fields present in the request
    body are touched; omitted fields are left unchanged.

    For ``interest_scores`` and ``personal_interests`` (if sent), the
    values are **merged** into the existing JSONB, not overwritten.
    """
    db = _require_db()

    # Pydantic .model_dump(exclude_none=True) gives us only the fields
    # the client actually sent.
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        # Nothing to update — just return current profile
        raw = _get_profile_row(db, user["user_id"])
        if raw is None:
            return _default_profile(user["user_id"])
        return _serialize_profile(raw)

    result = _upsert_profile(db, user["user_id"], update_data)
    return _serialize_profile(result)


@router.get(
    "/profile/preferences",
    response_model=PreferencesResponse,
    summary="Get preference fields for CLEO",
)
async def get_preferences(user: AuthUser = Depends(get_current_user)):
    """
    Returns only the preference/interest fields that CLEO uses for
    personalization.  Returns defaults if no profile exists.
    """
    db = _require_db()
    raw = _get_profile_row(db, user["user_id"])

    if raw is None:
        defaults = _default_profile(user["user_id"])
        return {
            k: defaults.get(k)
            for k in PreferencesResponse.model_fields
        }

    return {
        k: raw.get(k)
        for k in PreferencesResponse.model_fields
    }


@router.put(
    "/profile/preferences",
    response_model=PreferencesResponse,
    summary="Update preference fields (CLEO / onboarding)",
)
async def update_preferences(
    body: PreferencesUpdateRequest,
    user: AuthUser = Depends(get_current_user),
):
    """
    Update preference/interest fields.  ``interest_scores`` and
    ``personal_interests`` are **merged** with existing values.

    This is the endpoint CLEO's ``UserProfileManager`` and the Flutter
    onboarding flow should call.
    """
    db = _require_db()

    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raw = _get_profile_row(db, user["user_id"])
        if raw is None:
            defaults = _default_profile(user["user_id"])
            return {k: defaults.get(k) for k in PreferencesResponse.model_fields}
        return {k: raw.get(k) for k in PreferencesResponse.model_fields}

    result = _upsert_profile(db, user["user_id"], update_data)

    # Return only the preference subset
    return {k: result.get(k) for k in PreferencesResponse.model_fields}


@router.get(
    "/profile/summary",
    response_model=ProfileSummaryResponse,
    summary="Lightweight profile summary",
)
async def get_profile_summary(user: AuthUser = Depends(get_current_user)):
    """
    Minimal profile data for UI chrome (avatar initial, sidebar).

    Returns defaults if no profile row exists.
    """
    db = _require_db()
    raw = _get_profile_row(db, user["user_id"])

    if raw is None:
        defaults = _default_profile(user["user_id"])
        name = defaults.get("full_name") or ""
        return {
            "user_id": user["user_id"],
            "full_name": name or None,
            "avatar_initial": name[0].upper() if name else None,
            "itinerary_pace": defaults.get("itinerary_pace"),
            "price_sensitivity": defaults.get("price_sensitivity"),
            "home_country": defaults.get("home_country"),
        }

    name = raw.get("full_name") or ""
    return {
        "user_id": user["user_id"],
        "full_name": name or None,
        "avatar_initial": name[0].upper() if name else None,
        "itinerary_pace": raw.get("itinerary_pace"),
        "price_sensitivity": raw.get("price_sensitivity"),
        "home_country": raw.get("home_country"),
    }
