"""
VOYO Recommendations API Routes

Endpoints:
    GET /api/v1/recommendations        — Personalized POI recommendations
    GET /api/v1/recommendations/context — CLEO context string for chat session
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from src.api.routes.auth import get_current_user
from src.recommendations.engine import RecommendationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("")
async def get_recommendations(
    limit: int = Query(default=12, ge=1, le=50, description="Max POIs to return"),
    region_id: Optional[int] = Query(default=None, description="Filter by region ID"),
    exclude: Optional[str] = Query(
        default=None, description="Comma-separated POI IDs to exclude"
    ),
    user=Depends(get_current_user),
):
    """Get personalized POI recommendations.

    Called by Flutter home screen on app launch. Returns scored,
    diversified POI list with match reasons explaining why each was
    recommended.

    Requires a valid Supabase JWT (Bearer token).
    """
    exclude_ids: List[int] = []
    if exclude:
        try:
            exclude_ids = [int(x.strip()) for x in exclude.split(",") if x.strip()]
        except ValueError:
            # Invalid exclude param — just ignore it
            logger.warning(f"Invalid exclude parameter: {exclude}")

    engine = RecommendationEngine()
    recommendations = await engine.get_recommendations(
        user_id=user["user_id"],
        limit=limit,
        region_id=region_id,
        exclude_poi_ids=exclude_ids or None,
    )
    return {"recommendations": recommendations}


@router.get("/context")
async def get_recommendation_context(user=Depends(get_current_user)):
    """Get CLEO context string for chat session initialization.

    Called when user opens CLEO chat. Returns a concise text summary
    of the user's preferences and recent chat topics that CLEO can
    use to personalize responses immediately.
    """
    engine = RecommendationEngine()
    context = await engine.get_cleo_context(user["user_id"])
    return {"context": context}
