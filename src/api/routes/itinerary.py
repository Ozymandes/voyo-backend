"""
VOYO Itinerary API Routes

Endpoints:
    POST /api/v1/itinerary/curate      — LLM curates POI IDs (proxied to CLEO)
    POST /api/v1/itinerary/optimize    — VROOM optimizes curated POIs into schedule
    POST /api/v1/itinerary             — Create/save new itinerary
    GET  /api/v1/itinerary/{id}        — Get full itinerary with enriched POI data
    PUT  /api/v1/itinerary/{id}/reoptimize — Re-run VROOM after manual edits
    GET  /api/v1/itinerary/current     — Get user's active/current itinerary
    DELETE /api/v1/itinerary/{id}      — Delete an itinerary
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.routes.auth import get_current_user
from src.itinerary.engine import ItineraryEngine
from src.itinerary.persistence import ItineraryPersistence
from src.itinerary.safarny_planner import SafarnyPlanner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/itinerary", tags=["itinerary"])


# ── Request / Response Models ─────────────────────────────────────────


class CurateRequest(BaseModel):
    """Request for CLEO to curate POI IDs."""
    message: str = Field(..., min_length=2, description="User's natural language trip request")
    region: Optional[str] = None
    days: int = Field(default=1, ge=1, le=14)


class OptimizeRequest(BaseModel):
    """Request to run VROOM optimization on POI IDs."""
    poi_ids: List[int] = Field(..., min_length=1, max_length=50, description="POI IDs to optimize")
    days: int = Field(default=1, ge=1, le=14)
    hotel_location: Optional[List[float]] = Field(
        default=None,
        description="Hotel [lat, lng] for start/end of each day",
    )
    daily_start: str = Field(default="09:00")
    daily_end: str = Field(default="18:00")
    travel_profile: str = Field(default="auto")
    pace: str = Field(default="balanced")


class PlanTripRequest(BaseModel):
    """Structured trip profile for the grounded Safarny planner.

    Mirrors the Flutter ``TripProfile``. All scheduling intelligence is
    deterministic (recommendation engine + VROOM); the LLM only selects +
    writes copy from a DB-filtered candidate set — so this endpoint never
    fabricates POIs, prices, or times.
    """
    title: Optional[str] = None
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    travelers: int = Field(default=2, ge=1, le=20)
    budget_tier: str = Field(default="moderate")  # budget|moderate|luxury
    pace: str = Field(default="balanced")  # packed_schedule|balanced|slow_flexible
    companions: str = Field(default="couple")  # solo|couple|family|friends
    interests: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    hotel_location: Optional[List[float]] = None


class CreateItineraryRequest(BaseModel):
    """Request to save an optimized itinerary."""
    title: str = Field(..., min_length=1, max_length=200)
    region_id: Optional[int] = None
    optimized_schedule: Dict[str, Any]


class ReoptimizeRequest(BaseModel):
    """Request to reoptimize after manual edits."""
    added_poi_ids: Optional[List[int]] = None
    removed_poi_ids: Optional[List[int]] = None
    hotel_location: Optional[List[float]] = None
    days: int = Field(default=1, ge=1, le=14)
    pace: str = Field(default="balanced")


class PreviewAddRequest(BaseModel):
    """Request for a dry-run feasibility check before adding a POI.

    The user wants to add ``candidate_poi_id`` to an existing itinerary.
    We run the real VROOM solver on (existing + candidate) and report
    whether it fits, where it fits best, and whether anything gets displaced.
    Nothing is persisted — the caller saves via the normal flow on confirm.
    """
    itinerary_id: int
    candidate_poi_id: int
    preferred_day: Optional[int] = Field(
        default=None, ge=1, description="Day the user picked, if any"
    )
    hotel_location: Optional[List[float]] = None
    days: Optional[int] = Field(default=None, ge=1, le=14)
    daily_start: str = "09:00"
    daily_end: str = "18:00"
    travel_profile: str = "auto"
    pace: str = "balanced"


# ── Endpoints ─────────────────────────────────────────────────────────


@router.post("/curate")
async def curate_pois(request: CurateRequest, user=Depends(get_current_user)):
    """Step 1: CLEO curates POI IDs based on user request.

    Returns POI IDs with reasoning. The Flutter app then sends these
    to /optimize for scheduling.
    """
    from src.cleo.cleo_agent import CleoAgent

    agent = CleoAgent()
    # Ask CLEO to curate — it uses its tools to search POIs and pick relevant ones
    cleo_result = await agent.process_message(
        user_message=request.message,
        user_id=user["user_id"],
    )

    return {
        "message": cleo_result.text,
        "request": {
            "region": request.region,
            "days": request.days,
        },
    }


@router.post("/optimize")
async def optimize(request: OptimizeRequest, user=Depends(get_current_user)):
    """Step 2: Run VROOM optimization on curated POI IDs.

    Returns full optimized itinerary schedule with arrival/departure times,
    travel segments, and costs.
    """
    engine = ItineraryEngine()

    hotel = None
    if request.hotel_location and len(request.hotel_location) == 2:
        hotel = (request.hotel_location[0], request.hotel_location[1])

    try:
        result = await engine.generate(
            poi_ids=request.poi_ids,
            user_id=user["user_id"],
            days=request.days,
            hotel_location=hotel,
            daily_start=request.daily_start,
            daily_end=request.daily_end,
            travel_profile=request.travel_profile,
            pace=request.pace,
        )
    except RuntimeError as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    return result


@router.post("/plan")
async def plan_trip(request: PlanTripRequest, user=Depends(get_current_user)):
    """Grounded Safarny itinerary planner.

    The deterministic trip-planning endpoint: takes a structured trip profile
    (dates, budget, pace, interests, companions, notes) and returns a
    Safarny-shaped JSON itinerary where every POI, price, and time traces to
    either the database or the VROOM optimizer — never the LLM's training
    data. The LLM's only role is selection + vivid copy.

    Pipeline: recommendation engine pre-filters POIs → LLM selects per-day
    from that set + writes copy → VROOM assigns real arrival/departure times.
    Each stage degrades gracefully (Groq down → recommendation-engine
    fallback; VROOM down → unscheduled stops with null times).
    """
    planner = SafarnyPlanner()
    profile = request.model_dump()
    try:
        result = await planner.plan(
            profile=profile,
            user_id=user["user_id"],
            hotel_location=request.hotel_location,
        )
    except Exception as e:
        logger.error(f"/itinerary/plan failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Could not generate itinerary: {e}",
        )
    return result


@router.post("/preview-add")
async def preview_add(request: PreviewAddRequest, user=Depends(get_current_user)):
    """Dry-run feasibility check: can this POI be added to the trip, and where?

    Runs the real VROOM solver on the existing itinerary + candidate (no
    persistence). Returns a verdict — feasible / recommended day / displaced
    POIs / human reason — so the client can say so, recommend placement, or
    turn the add down honestly instead of silently over-packing a day.
    """
    engine = ItineraryEngine()

    hotel = None
    if request.hotel_location and len(request.hotel_location) == 2:
        hotel = (request.hotel_location[0], request.hotel_location[1])

    try:
        result = await engine.preview_add(
            itinerary_id=request.itinerary_id,
            user_id=user["user_id"],
            candidate_poi_id=request.candidate_poi_id,
            preferred_day=request.preferred_day,
            hotel_location=hotel,
            days=request.days,
            daily_start=request.daily_start,
            daily_end=request.daily_end,
            travel_profile=request.travel_profile,
            pace=request.pace,
        )
    except ValueError as e:
        # Itinerary not found / doesn't belong to the user.
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        # Routing backend (VROOM/OSRM) unreachable.
        logger.error(f"preview-add failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    return result


@router.post("")
async def create_itinerary(request: CreateItineraryRequest, user=Depends(get_current_user)):
    """Step 3: Save optimized itinerary to Supabase.

    Writes to `itineraries` and `itinerary_items` tables.
    """
    persistence = ItineraryPersistence()

    try:
        saved = await persistence.save_optimized_itinerary(
            user_id=user["user_id"],
            title=request.title,
            region_id=request.region_id,
            optimized_schedule=request.optimized_schedule,
        )
    except Exception as e:
        logger.error(f"Failed to save itinerary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save itinerary: {e}")

    return saved


@router.get("/current")
async def get_current_itinerary(user=Depends(get_current_user)):
    """Get user's active/current itinerary."""
    import asyncio
    from src.database.supabase_client import SupabaseClient

    db = SupabaseClient()

    try:
        records = await asyncio.to_thread(
            db.get_records,
            "itineraries",
            filters={"user_id": user["user_id"], "status": "current"},
            use_admin=True,
            limit=1,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not records:
        return {"itinerary": None}

    itinerary_id = records[0]["id"]
    persistence = ItineraryPersistence()
    full = await persistence.load_itinerary_with_routes(itinerary_id, user["user_id"])
    return {"itinerary": full}


@router.get("/{itinerary_id}")
async def get_itinerary(itinerary_id: int, user=Depends(get_current_user)):
    """Get full itinerary with enriched POI data."""
    persistence = ItineraryPersistence()
    result = await persistence.load_itinerary_with_routes(itinerary_id, user["user_id"])

    if not result:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    return result


@router.put("/{itinerary_id}/reoptimize")
async def reoptimize(
    itinerary_id: int,
    request: ReoptimizeRequest,
    user=Depends(get_current_user),
):
    """Re-run VROOM after manual edits (add/remove stops).

    Keeps user's explicit changes, reoptimizes ordering and timing.
    """
    engine = ItineraryEngine()

    hotel = None
    if request.hotel_location and len(request.hotel_location) == 2:
        hotel = (request.hotel_location[0], request.hotel_location[1])

    try:
        result = await engine.reoptimize_after_edit(
            itinerary_id=itinerary_id,
            user_id=user["user_id"],
            added_poi_ids=request.added_poi_ids,
            removed_item_ids=request.removed_poi_ids,
            hotel_location=hotel,
            days=request.days,
            pace=request.pace,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return result


@router.delete("/{itinerary_id}")
async def delete_itinerary(itinerary_id: int, user=Depends(get_current_user)):
    """Delete an itinerary and all its items."""
    persistence = ItineraryPersistence()
    deleted = await persistence.delete_itinerary(itinerary_id, user["user_id"])

    if not deleted:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    return {"status": "deleted", "itinerary_id": itinerary_id}
