"""
VOYO VROOM Client — Async Vehicle Routing Problem Solver

Translates POI lists into VROOM problem definitions, sends them to the
self-hosted VROOM Docker container, and parses the solution into VOYO's
itinerary format.
"""

import logging
from datetime import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

from src.routing.valhalla_client import ValhallaClient
from src.routing.poi_adapter import POIAdapter

logger = logging.getLogger(__name__)

DEFAULT_VROOM_URL = "http://localhost:8081"


class VROOMClient:
    """Async client for VROOM optimization engine."""

    def __init__(
        self,
        base_url: str = DEFAULT_VROOM_URL,
        valhalla: Optional[ValhallaClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=60.0)
        self.valhalla = valhalla or ValhallaClient()
        self.adapter = POIAdapter()

    # ==================================================================
    # Public API
    # ==================================================================

    async def optimize_itinerary(
        self,
        pois: List[Dict[str, Any]],
        hotel: Optional[Tuple[float, float]] = None,
        days: int = 1,
        daily_start: str = "09:00",
        daily_end: str = "18:00",
        profile: str = "auto",
    ) -> Dict[str, Any]:
        """Build VROOM problem and solve it.

        Maps itinerary planning to Vehicle Routing Problem:
        - Each day = one "vehicle" with time window [start, end]
        - Each POI = one "job" with service time and time windows
        - Hotel = vehicle start/end location
        - Objective: minimize total travel time while respecting constraints

        Args:
            pois: POI records with latitude, longitude, average_visit_duration,
                  opening_hours, etc.
            hotel: Optional (lat, lng) of accommodation.
            days: Number of trip days.
            daily_start: HH:MM start time each day.
            daily_end: HH:MM end time each day.
            profile: "auto", "pedestrian", or "bicycle".

        Returns:
            Optimized itinerary in the MASTER_PLAN.md integration contract format.
        """
        if not pois:
            return {"days": [], "optimization_metadata": {"solver_status": "EMPTY"}}

        # 1. Build location list (hotel first if present, then POIs)
        all_locations: List[Tuple[float, float]] = []
        if hotel:
            all_locations.append(hotel)
        for poi in pois:
            all_locations.append((poi["latitude"], poi["longitude"]))

        # 2. Get distance matrix from Valhalla
        try:
            matrix = await self.valhalla.get_distance_matrix(
                all_locations, all_locations, profile
            )
        except RuntimeError as e:
            logger.error(f"Failed to get distance matrix: {e}")
            raise

        # 3. Build VROOM problem
        problem = self._build_vroom_problem(
            pois=pois,
            matrix=matrix,
            hotel=hotel,
            days=days,
            daily_start=daily_start,
            daily_end=daily_end,
            profile=profile,
        )

        # 4. Send to VROOM solver
        try:
            resp = await self.client.post(
                f"{self.base_url}",
                json=problem,
            )
            resp.raise_for_status()
            solution = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"VROOM solver error: {e}")
            raise RuntimeError(
                f"VROOM optimization failed: {e}. "
                "Is Docker running? Run: docker-compose up -d"
            ) from e

        # 5. Parse solution into itinerary format
        return self._parse_solution(solution, pois, matrix, hotel)

    # ==================================================================
    # Problem Building
    # ==================================================================

    def _build_vroom_problem(
        self,
        pois: List[Dict[str, Any]],
        matrix: List[List[Dict[str, Any]]],
        hotel: Optional[Tuple[float, float]],
        days: int,
        daily_start: str,
        daily_end: str,
        profile: str,
    ) -> Dict[str, Any]:
        """Transform POIs + constraints into a VROOM problem JSON."""

        hotel_offset = 1 if hotel else 0

        # Convert time strings to seconds from midnight
        start_seconds = self._time_to_seconds(daily_start)
        end_seconds = self._time_to_seconds(daily_end)

        # VROOM uses OSRM-style profile names, not Valhalla costing names.
        # Our pipeline standardizes on Valhalla's (auto/pedestrian/bicycle);
        # map them here so the solver accepts the request. Without this,
        # VROOM returns 400 "Invalid profile: auto" and the whole /plan
        # pipeline silently falls back to unscheduled — the root cause of
        # the sparse-output bug partner QA found.
        vroom_profile = {"auto": "car", "pedestrian": "foot",
                         "bicycle": "bike"}.get(profile, "car")

        # ── Vehicles (one per day) ────────────────────────────────
        # VROOM with a custom matrix requires EVERY location (vehicle
        # start/end AND job) to supply BOTH a matrix index (`start_index` /
        # `location_index`) AND a coordinate array (`start` / `location`).
        # The index drives the duration/distance lookup; the coordinate
        # drives route geometry. Omitting either is a 400. Without a hotel
        # anchor, each day-vehicle starts/ends at the first POI's location.
        vehicles: List[Dict[str, Any]] = []
        for day_idx in range(days):
            if hotel:
                anchor_idx = 0
                anchor_coord = [hotel[1], hotel[0]]  # [lon, lat]
            elif pois:
                anchor_idx = 1  # matrix index 1 = first POI (0 reserved for hotel when present)
                anchor_coord = [pois[0]["longitude"], pois[0]["latitude"]]
            else:
                continue
            vehicles.append({
                "id": day_idx,
                "time_window": [start_seconds, end_seconds],
                "profile": vroom_profile,
                "start_index": anchor_idx,
                "end_index": anchor_idx,
                "start": anchor_coord,
                "end": anchor_coord,
            })

        # ── Jobs (one per POI) ────────────────────────────────────
        jobs: List[Dict[str, Any]] = []
        for poi_idx, poi in enumerate(pois):
            location_idx = poi_idx + hotel_offset

            service_seconds = (poi.get("average_visit_duration") or 60) * 60
            if "adjusted_visit_duration" in poi:
                service_seconds = poi["adjusted_visit_duration"] * 60

            job: Dict[str, Any] = {
                "id": poi.get("id", poi_idx + 1),
                "location_index": location_idx,
                "location": [poi["longitude"], poi["latitude"]],
                "service": service_seconds,
                "description": poi.get("name", f"POI {poi_idx}"),
            }

            # Add time windows from opening hours. Skip any window where
            # end <= start (e.g. a venue open until 2 AM that parses as
            # [32400, 0] — midnight rollover) — VROOM rejects those and
            # they were causing the live planner to drop POIs / fail. The
            # venue is still visitable within the vehicle's day window.
            time_windows = self.adapter.parse_opening_hours_to_seconds(
                poi.get("opening_hours")
            )
            sane_windows = [
                tw for tw in time_windows
                if len(tw) == 2 and tw[1] > tw[0]
            ]
            if sane_windows:
                job["time_windows"] = sane_windows

            jobs.append(job)

        # ── Duration matrix (seconds) ─────────────────────────────
        durations: List[List[int]] = []
        for row in matrix:
            durations.append([int(cell["time"]) for cell in row])

        # ── Distance matrix (meters) ──────────────────────────────
        distances: List[List[int]] = []
        for row in matrix:
            distances.append([int(cell["distance"]) for cell in row])

        return {
            "vehicles": vehicles,
            "jobs": jobs,
            # Matrix MUST be keyed by the same profile name the vehicles use
            # (VROOM's car/foot/bike, not Valhalla's auto/pedestrian/bicycle).
            # Mismatch here is a silent 400.
            "matrices": {
                vroom_profile: {
                    "durations": durations,
                    "distances": distances,
                }
            },
        }

    # ==================================================================
    # Solution Parsing
    # ==================================================================

    def _parse_solution(
        self,
        vroom_output: Dict[str, Any],
        pois: List[Dict[str, Any]],
        matrix: List[List[Dict[str, Any]]],
        hotel: Optional[Tuple[float, float]],
    ) -> Dict[str, Any]:
        """Transform VROOM solution into the VOYO itinerary contract.

        VROOM returns:
            {
                "code": 0,
                "routes": [{ "vehicle": 0, "steps": [...] }],
                "unassigned": [...]
            }

        We transform into the format defined in MASTER_PLAN.md.
        """
        poi_lookup = {poi.get("id"): poi for poi in pois}
        hotel_offset = 1 if hotel else 0
        unassigned_ids = [u.get("job") for u in vroom_output.get("unassigned", [])]

        days: List[Dict[str, Any]] = []
        total_travel_minutes = 0
        total_service_minutes = 0
        total_cost_egp = 0.0

        for route in vroom_output.get("routes", []):
            day_number = route["vehicle"] + 1
            stops: List[Dict[str, Any]] = []

            for step in route.get("steps", []):
                if step.get("type") != "job":
                    continue

                job_id = step.get("job")
                poi = poi_lookup.get(job_id, {})

                arrival = step.get("arrival", 0)
                service = step.get("service", 0)
                departure = step.get("departure", arrival + service)

                # Find the next step to calculate travel. VROOM's solution
                # steps report `location` as a [lon, lat] array AND
                # `location_index` as the matrix index. We need the INDEX to
                # look up the duration/distance cell.
                travel_to_next_minutes = 0
                travel_to_next_km = 0.0
                steps = route.get("steps", [])
                step_idx = steps.index(step)
                if step_idx + 1 < len(steps):
                    next_step = steps[step_idx + 1]
                    if next_step.get("type") in ("job", "end"):
                        next_location = next_step.get("location_index",
                                                      step.get("location_index", 0))
                        curr_location = step.get("location_index", 0)
                        if (isinstance(curr_location, int)
                                and isinstance(next_location, int)
                                and curr_location < len(matrix)
                                and next_location < len(matrix[curr_location])):
                            cell = matrix[curr_location][next_location]
                            travel_to_next_minutes = round(cell["time"] / 60, 1)
                            travel_to_next_km = round(cell["distance"] / 1000, 1)

                price = float(poi.get("ticket_price") or 0)

                stops.append({
                    "sequence": len(stops) + 1,
                    "poi_id": job_id,
                    "poi_name": poi.get("name", f"POI {job_id}"),
                    "latitude": poi.get("latitude"),
                    "longitude": poi.get("longitude"),
                    "arrival_time": self._seconds_to_time_str(arrival),
                    "departure_time": self._seconds_to_time_str(departure),
                    "service_duration": round(service / 60),
                    "travel_to_next_minutes": travel_to_next_minutes,
                    "travel_to_next_km": travel_to_next_km,
                    "category": poi.get("category", ""),
                    "ticket_price": price,
                    "tip": self._generate_tip(poi),
                })

                total_travel_minutes += travel_to_next_minutes
                service_min = round(service / 60)
                total_service_minutes += service_min
                total_cost_egp += price

            days.append({
                "day_number": day_number,
                "theme": "",  # filled by ItineraryEngine in Phase 2B
                "stops": stops,
                "total_travel_minutes": round(total_travel_minutes),
                "total_service_minutes": round(total_service_minutes),
                "total_cost_egp": round(total_cost_egp, 2),
            })

        return {
            "days": days,
            "optimization_metadata": {
                "solver_status": self._vroom_code_to_status(vroom_output.get("code", -1)),
                "total_cost_function": vroom_output.get("cost", 0),
                "unassigned": unassigned_ids,
                "computed_with": "vroom_v1.13",
            },
        }

    # ==================================================================
    # Helpers
    # ==================================================================

    @staticmethod
    def _time_to_seconds(time_str: str) -> int:
        """Convert HH:MM to seconds from midnight."""
        try:
            parts = time_str.split(":")
            return int(parts[0]) * 3600 + int(parts[1]) * 60
        except (ValueError, IndexError):
            return 32400  # default 09:00

    @staticmethod
    def _seconds_to_time_str(seconds: int) -> str:
        """Convert seconds from midnight to HH:MM string."""
        seconds = max(0, int(seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def _vroom_code_to_status(code: int) -> str:
        """Map VROOM return codes to human-readable status."""
        status_map = {
            0: "OPTIMAL",
            1: "HEURISTIC",
            2: "PARTIAL",
            3: "TIMEOUT",
        }
        return status_map.get(code, f"UNKNOWN({code})")

    @staticmethod
    def _generate_tip(poi: Dict[str, Any]) -> str:
        """Generate a brief practical tip for a POI."""
        duration = poi.get("average_visit_duration") or 60
        price = float(poi.get("ticket_price") or 0)

        if duration >= 180:
            return "Allow plenty of time — this is a major attraction"
        if price == 0:
            return "Free entry — great for a budget stop"
        if price > 300:
            return "Consider booking tickets in advance"
        return "Check opening hours before visiting"

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()
        await self.valhalla.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
