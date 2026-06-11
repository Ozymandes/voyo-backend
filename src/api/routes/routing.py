"""
VOYO Routing API Routes

Endpoints:
    GET  /api/v1/routing/distance-matrix — NxN travel time/distance matrix
    POST /api/v1/routing/isochrone       — Reachable area polygons
    GET  /api/v1/routing/route           — Turn-by-turn route with polyline
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.routes.auth import get_current_user, get_optional_user
from src.routing.valhalla_client import ValhallaClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/routing", tags=["routing"])

valhalla = ValhallaClient()


# ── Request / Response Models ─────────────────────────────────────────


class IsochroneRequest(BaseModel):
    """Request body for isochrone computation."""
    latitude: float = Field(..., ge=-90, le=90, description="Center latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Center longitude")
    ranges: List[int] = Field(
        default=[30, 60, 90],
        description="Time ranges in minutes",
    )
    profile: str = Field(
        default="auto",
        description="Travel profile: auto, pedestrian, bicycle",
    )


# ── Endpoints ─────────────────────────────────────────────────────────


@router.get("/distance-matrix")
async def distance_matrix(
    sources: str = Query(
        ...,
        description="Semicolon-separated lat,lng pairs. Example: 30.04,31.23;29.97,31.13",
    ),
    targets: Optional[str] = Query(
        default=None,
        description="Target coordinates (same format). Defaults to sources.",
    ),
    profile: str = Query(default="auto", description="auto, pedestrian, or bicycle"),
    user=Depends(get_current_user),
):
    """Get travel time/distance matrix between locations.

    Returns a 2D array where matrix[i][j] contains travel from source i
    to target j with ``distance`` (meters) and ``time`` (seconds).
    """
    try:
        src_coords = _parse_waypoints(sources)
        tgt_coords = _parse_waypoints(targets) if targets else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not src_coords:
        raise HTTPException(status_code=400, detail="No source coordinates provided")

    try:
        matrix = await valhalla.get_distance_matrix(src_coords, tgt_coords, profile)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    return {"matrix": matrix, "profile": profile}


@router.post("/isochrone")
async def isochrone(request: IsochroneRequest):
    """Get reachable area polygons from a point.

    This endpoint is public (used by map explorer for unauthenticated users).
    Returns GeoJSON polygons for each requested time range.
    """
    try:
        result = await valhalla.get_isochrone(
            center=(request.latitude, request.longitude),
            ranges=request.ranges,
            profile=request.profile,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return result


@router.get("/route")
async def get_route(
    waypoints: str = Query(
        ...,
        description="Semicolon-separated lat,lng pairs. Example: 30.04,31.23;29.97,31.13;30.01,31.18",
    ),
    profile: str = Query(default="auto", description="auto, pedestrian, or bicycle"),
):
    """Get turn-by-turn route with polyline geometry.

    Returns distance, time, and a decoded polyline of [lat, lng] pairs
    suitable for rendering on a map.
    """
    try:
        coords = _parse_waypoints(waypoints)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(coords) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 waypoints required for routing",
        )

    try:
        route = await valhalla.get_route(coords, profile)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return route


@router.get("/health")
async def routing_health():
    """Check if the routing services (Valhalla + VROOM) are running."""
    from src.routing.vroom_client import VROOMClient

    valhalla_ok = await valhalla.health_check()

    vroom_ok = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://localhost:8081/health")
            vroom_ok = resp.status_code == 200
    except Exception:
        pass

    return {
        "valhalla": "healthy" if valhalla_ok else "unavailable",
        "vroom": "healthy" if vroom_ok else "unavailable",
        "overall": "healthy" if (valhalla_ok and vroom_ok) else "degraded",
    }


# ── Helpers ───────────────────────────────────────────────────────────


def _parse_waypoints(text: str) -> List[tuple]:
    """Parse "lat1,lng1;lat2,lng2;..." into list of (lat, lng) tuples."""
    coords: List[tuple] = []
    for pair in text.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        parts = pair.split(",")
        if len(parts) != 2:
            raise ValueError(f"Invalid coordinate pair: '{pair}'. Expected lat,lng")
        try:
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
        except ValueError:
            raise ValueError(f"Invalid numbers in coordinate pair: '{pair}'")
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError(f"Coordinates out of range: lat={lat}, lng={lng}")
        coords.append((lat, lng))
    return coords
