"""
VOYO OSRM Table Client — Async distance/duration matrix proxy

Thin async client over the OSRM HTTP ``/table`` endpoint. Powers the
``POST /api/v1/routing/table`` route, which returns an origin→destinations
travel matrix for the Flutter consumer.

OSRM runs as the ``voyo-osrm`` Docker container on port 5000 (see
docker-compose.yml). VROOM reaches it as host ``osrm`` on the compose
network; the backend, running on the host, uses ``localhost:5000`` — the
same convention as ``DEFAULT_VALHALLA_URL`` and ``DEFAULT_VROOM_URL``.

VOYO profiles (``auto``/``pedestrian``/``bicycle`` — Valhalla costing
names used throughout the routing package) are mapped to OSRM's own
router profiles (``car``/``foot``/``bike``) so the public API stays
consistent.
"""

import logging
from typing import Any, Dict, List, Tuple

import httpx

logger = logging.getLogger(__name__)

# Default OSRM URL — matches the 5000:5000 port map in docker-compose.yml.
DEFAULT_OSRM_URL = "http://localhost:5000"

# VOYO (Valhalla costing) profile → OSRM URL profile.
_OSRM_PROFILES = {
    "auto": "car",
    "pedestrian": "foot",
    "bicycle": "bike",
}


class OSRMTableError(RuntimeError):
    """Raised when OSRM is unreachable or returns an error response.

    The API route converts this into an HTTP 503 so callers never see a
    crash or a hang.
    """


class OSRMTableClient:
    """Async client for the OSRM ``/table/v1/{profile}`` endpoint."""

    def __init__(self, base_url: str = DEFAULT_OSRM_URL, timeout: float = 30.0):
        # The bounded timeout guarantees we never hang on an unreachable OSRM.
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=timeout)

    async def get_table(
        self,
        origin: Tuple[float, float],
        destinations: List[Tuple[float, float]],
        profile: str = "auto",
    ) -> List[Dict[str, Any]]:
        """Return an origin→destinations distance + duration matrix.

        Args:
            origin: ``(lat, lng)`` of the single origin point.
            destinations: ordered list of ``(lat, lng)`` destination points.
            profile: VOYO profile (``"auto"``, ``"pedestrian"``, ``"bicycle"``).

        Returns:
            A list aligned to ``destinations`` order:
            ``[{"index": 0, "distance_m": 1234.5, "duration_s": 240.0}, ...]``
            Unreachable cells (OSRM returns ``null``) are reported as ``0.0``.

        Raises:
            OSRMTableError: if OSRM is unreachable or returns an error.
        """
        osrm_profile = _OSRM_PROFILES.get(profile, "car")

        # OSRM expects lng,lat in the URL path. Origin is coordinate index 0;
        # each destination is index 1..N.
        coord_str = ";".join(
            [_fmt_coord(origin)] + [_fmt_coord(d) for d in destinations]
        )
        params = {
            "sources": "0",
            "destinations": ";".join(str(i) for i in range(1, len(destinations) + 1)),
            "annotations": "duration,distance",
        }
        url = f"{self.base_url}/table/v1/{osrm_profile}/{coord_str}"

        try:
            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"OSRM table request failed: {e}")
            raise OSRMTableError(
                f"OSRM table request failed: {e}. "
                "Is Docker running? Run: docker-compose up -d"
            ) from e

        if data.get("code") != "Ok":
            msg = data.get("message", "unknown OSRM error")
            logger.error(f"OSRM table returned error code: {msg}")
            raise OSRMTableError(f"OSRM table error: {msg}")

        # With a single source the matrix is 1×N; row 0 is the origin.
        distances = data.get("distances") or [[]]
        durations = data.get("durations") or [[]]
        distance_row = distances[0] if distances else []
        duration_row = durations[0] if durations else []

        return [
            {
                "index": i,
                "distance_m": _safe_num(distance_row, i),
                "duration_s": _safe_num(duration_row, i),
            }
            for i in range(len(destinations))
        ]

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def _fmt_coord(point: Tuple[float, float]) -> str:
    """Format a ``(lat, lng)`` point as an OSRM ``lng,lat`` path segment."""
    lat, lng = point
    return f"{lng},{lat}"


def _safe_num(row: List[Any], idx: int) -> float:
    """Pull a numeric value from an OSRM matrix row.

    OSRM reports unreachable cells as ``null``; we coerce those to ``0.0``
    (matching the ``or 0`` convention in ``valhalla_client``).
    """
    if idx >= len(row):
        return 0.0
    val = row[idx]
    if val is None:
        return 0.0
    return round(float(val), 1)
