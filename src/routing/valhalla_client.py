"""
VOYO Valhalla Client — Async routing, distance matrices, and isochrones

Communicates with a self-hosted Valhalla instance running in Docker.
Gracefully handles the case where Docker is not running.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

# Default Valhalla URL (matches docker-compose.yml)
DEFAULT_VALHALLA_URL = "http://localhost:8002"


class ValhallaClient:
    """Async client for self-hosted Valhalla routing engine."""

    def __init__(self, base_url: str = DEFAULT_VALHALLA_URL):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def health_check(self) -> bool:
        """Check if Valhalla is running and has tile data loaded."""
        try:
            resp = await self.client.get(f"{self.base_url}/status")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    # ==================================================================
    # Distance Matrix
    # ==================================================================

    async def get_distance_matrix(
        self,
        sources: List[Tuple[float, float]],
        targets: Optional[List[Tuple[float, float]]] = None,
        profile: str = "auto",
    ) -> List[List[Dict[str, Any]]]:
        """Get distance + time matrix between all source-target pairs.

        Args:
            sources: List of (lat, lng) coordinate pairs.
            targets: Optional separate target list. If None, uses sources
                     (square NxN matrix).
            profile: "auto", "pedestrian", or "bicycle".

        Returns:
            matrix[i][j] = {"distance": meters, "time": seconds}
        """
        if targets is None:
            targets = sources

        # Build Valhalla matrix request
        body = {
            "sources": [
                {"lat": lat, "lon": lng} for lat, lng in sources
            ],
            "targets": [
                {"lat": lat, "lon": lng} for lat, lng in targets
            ],
            "costing": profile,
        }

        try:
            resp = await self.client.post(
                f"{self.base_url}/sources_to_targets", json=body
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"Valhalla distance matrix error: {e}")
            raise RuntimeError(
                f"Valhalla distance matrix request failed: {e}. "
                "Is Docker running? Run: docker-compose up -d"
            ) from e

        # Parse Valhalla response into our format
        raw_matrix = data.get("sources_to_targets", [])
        matrix: List[List[Dict[str, Any]]] = []

        for i, row in enumerate(raw_matrix):
            matrix_row: List[Dict[str, Any]] = []
            for j, cell in enumerate(row):
                entry = cell.get("distance", cell) if isinstance(cell, dict) else {}
                # Valhalla returns distance in km and time in seconds
                dist_km = entry.get("distance", 0) or 0
                time_sec = entry.get("time", 0) or 0
                matrix_row.append({
                    "distance": round(dist_km * 1000, 1),  # km → meters
                    "time": round(time_sec, 1),
                })
            matrix.append(matrix_row)

        return matrix

    # ==================================================================
    # Turn-by-Turn Route
    # ==================================================================

    async def get_route(
        self,
        waypoints: List[Tuple[float, float]],
        profile: str = "auto",
    ) -> Dict[str, Any]:
        """Get turn-by-turn route with polyline geometry.

        Args:
            waypoints: Ordered list of (lat, lng) stops.
            profile: "auto", "pedestrian", or "bicycle".

        Returns:
            {
                "distance": meters,
                "time": seconds,
                "polyline": [[lat, lng], ...],
                "legs": [{"distance": m, "time": s, "summary": "..."}, ...]
            }
        """
        if len(waypoints) < 2:
            raise ValueError("At least 2 waypoints required for routing")

        body = {
            "locations": [
                {"lat": lat, "lon": lng} for lat, lng in waypoints
            ],
            "costing": profile,
            "directions_options": {"units": "kilometers"},
        }

        try:
            resp = await self.client.post(
                f"{self.base_url}/route", json=body
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"Valhalla route error: {e}")
            raise RuntimeError(
                f"Valhalla route request failed: {e}. "
                "Is Docker running? Run: docker-compose up -d"
            ) from e

        trip = data.get("trip", {})
        legs_raw = trip.get("legs", [])

        # Extract full polyline from all legs
        polyline: List[List[float]] = []
        legs: List[Dict[str, Any]] = []

        for leg in legs_raw:
            leg_dist = leg.get("summary", {}).get("length", 0) or 0  # km
            leg_time = leg.get("summary", {}).get("time", 0) or 0  # seconds

            # Decode Valhalla shape (polyline6 encoding)
            shape = leg.get("shape", "")
            decoded = self._decode_polyline6(shape)
            polyline.extend(decoded)

            legs.append({
                "distance": round(leg_dist * 1000, 1),  # km → m
                "time": round(leg_time, 1),
                "summary": leg.get("summary", {}).get("text", ""),
            })

        total_dist = trip.get("summary", {}).get("length", 0) or 0
        total_time = trip.get("summary", {}).get("time", 0) or 0

        return {
            "distance": round(total_dist * 1000, 1),
            "time": round(total_time, 1),
            "polyline": polyline,
            "legs": legs,
        }

    # ==================================================================
    # Isochrone (Reachable Area)
    # ==================================================================

    async def get_isochrone(
        self,
        center: Tuple[float, float],
        ranges: Optional[List[int]] = None,
        profile: str = "auto",
    ) -> Dict[str, Any]:
        """Get reachable area polygons for given time ranges.

        Args:
            center: (lat, lng) center point.
            ranges: List of time ranges in minutes, e.g. [30, 60, 90].
            profile: "auto", "pedestrian", or "bicycle".

        Returns:
            {
                "center": {"latitude": ..., "longitude": ...},
                "profile": "auto",
                "polygons": [
                    {"time_minutes": 30, "geojson": {...}},
                    ...
                ],
                "reachable_pois": [...]  # populated by caller if needed
            }
        """
        if ranges is None:
            ranges = [30, 60, 90]

        body = {
            "locations": [
                {"lat": center[0], "lon": center[1]}
            ],
            "costing": profile,
            "contours": [{"time": r, "color": f"{r:02x}6040"} for r in ranges],
            "polygons": True,
        }

        try:
            resp = await self.client.post(
                f"{self.base_url}/isochrone", json=body
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"Valhalla isochrone error: {e}")
            raise RuntimeError(
                f"Valhalla isochrone request failed: {e}. "
                "Is Docker running? Run: docker-compose up -d"
            ) from e

        polygons: List[Dict[str, Any]] = []
        features = data.get("features", [])

        # Match features to the requested time ranges
        for i, feature in enumerate(features):
            time_min = ranges[i] if i < len(ranges) else ranges[-1]
            polygons.append({
                "time_minutes": time_min,
                "geojson": feature,
            })

        return {
            "center": {"latitude": center[0], "longitude": center[1]},
            "profile": profile,
            "polygons": polygons,
            "reachable_pois": [],  # populated by the route handler if POI data available
        }

    # ==================================================================
    # Polyline Decoding
    # ==================================================================

    @staticmethod
    def _decode_polyline6(encoded: str) -> List[List[float]]:
        """Decode Valhalla's polyline6 (precision factor 1e6) encoding.

        Returns list of [lat, lng] coordinate pairs.
        """
        if not encoded:
            return []

        points: List[List[float]] = []
        index = 0
        lat = 0
        lng = 0

        while index < len(encoded):
            # Decode latitude
            result = 0
            shift = 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            if result & 1:
                result = ~result
            result >>= 1
            lat += result * 1e-6

            # Decode longitude
            result = 0
            shift = 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            if result & 1:
                result = ~result
            result >>= 1
            lng += result * 1e-6

            points.append([round(lat, 6), round(lng, 6)])

        return points

    # ==================================================================
    # Cleanup
    # ==================================================================

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
