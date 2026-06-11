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
    cleo_response = await agent.process_message(
        user_message=request.message,
        user_id=user["user_id"],
    )

    return {
        "message": cleo_response,
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
