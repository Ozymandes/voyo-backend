"""
VOYO Itinerary Engine — Neuro-Symbolic Planning Orchestrator

Bridges CLEO's creative curation with VROOM's deterministic optimization.
No LLM calls — this module handles pure logistics:

  1. Fetch POI data from Supabase
  2. Apply pace adjustments to visit durations
  3. Build and solve VROOM problem
  4. Enrich schedule with POI details and travel segments
  5. Generate day themes and calculate costs
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.database.supabase_client import SupabaseClient
from src.routing.vroom_client import VROOMClient
from src.routing.valhalla_client import ValhallaClient

logger = logging.getLogger(__name__)

# Pace multipliers for visit duration and max stops per day
PACE_CONFIG = {
    "slow_flexible": {"multiplier": 1.5, "max_stops": 3},
    "balanced": {"multiplier": 1.0, "max_stops": 5},
    "packed_schedule": {"multiplier": 0.75, "max_stops": 7},
}


class ItineraryEngine:
    """Orchestrates the full itinerary generation pipeline:
    POI IDs -> Supabase lookup -> VROOM optimization -> enriched schedule.
    """

    def __init__(self):
        self.db = SupabaseClient()
        self.vroom = VROOMClient()
        self.valhalla = ValhallaClient()

    async def generate(
        self,
        poi_ids: List[int],
        user_id: str,
        days: int = 1,
        hotel_location: Optional[Tuple[float, float]] = None,
        daily_start: str = "09:00",
        daily_end: str = "18:00",
        travel_profile: str = "auto",
        pace: str = "balanced",
    ) -> Dict[str, Any]:
        """Full pipeline: fetch -> adjust -> optimize -> enrich.

        Args:
            poi_ids: List of POI database IDs (curated by CLEO or user).
            user_id: For profile lookup (pace, mobility, budget).
            days: Number of trip days.
            hotel_location: Optional (lat, lng) of accommodation.
            daily_start/end: Active hours each day (HH:MM).
            travel_profile: "auto", "pedestrian", etc.
            pace: "packed_schedule" | "balanced" | "slow_flexible".

        Returns:
            Itinerary in the MASTER_PLAN.md integration contract format.
        """
        # 1. Fetch POI data
        pois = await self._fetch_pois(poi_ids)
        if not pois:
            return {"days": [], "optimization_metadata": {"solver_status": "NO_POIS"}}

        # 2. Apply pace adjustments
        pace_config = PACE_CONFIG.get(pace, PACE_CONFIG["balanced"])
        pois = self._apply_pace(pois, pace_config)

        # 3. Run VROOM optimization
        optimized = await self.vroom.optimize_itinerary(
            pois=pois,
            hotel=hotel_location,
            days=days,
            daily_start=daily_start,
            daily_end=daily_end,
            profile=travel_profile,
        )

        # 4. Enrich with POI details
        enriched = self._enrich_schedule(optimized, pois)

        # 5. Calculate costs
        enriched["total_cost_egp"] = self._calculate_costs(pois)

        # 6. Generate day themes
        enriched = self._generate_day_themes(enriched, pois)

        return enriched

    async def reoptimize_after_edit(
        self,
        itinerary_id: int,
        user_id: str,
        added_poi_ids: Optional[List[int]] = None,
        removed_item_ids: Optional[List[int]] = None,
        hotel_location: Optional[Tuple[float, float]] = None,
        days: int = 1,
        pace: str = "balanced",
    ) -> Dict[str, Any]:
        """Re-run optimization after user manually edits the itinerary.

        Loads the existing itinerary, applies additions/removals,
        then re-optimizes ordering and timing.
        """
        from src.itinerary.persistence import ItineraryPersistence

        persistence = ItineraryPersistence()
        existing = await persistence.load_itinerary_raw(itinerary_id, user_id)

        if not existing:
            raise ValueError(f"Itinerary {itinerary_id} not found")

        # Collect existing POI IDs from the itinerary
        existing_poi_ids = [
            item["poi_id"] for item in existing.get("items", [])
        ]

        # Apply removals
        if removed_item_ids:
            removed_set = set(removed_item_ids)
            existing_poi_ids = [pid for pid in existing_poi_ids if pid not in removed_set]

        # Apply additions
        if added_poi_ids:
            existing_poi_ids.extend(added_poi_ids)

        # Deduplicate while preserving order
        seen = set()
        unique_ids = []
        for pid in existing_poi_ids:
            if pid not in seen:
                seen.add(pid)
                unique_ids.append(pid)

        return await self.generate(
            poi_ids=unique_ids,
            user_id=user_id,
            days=days,
            hotel_location=hotel_location,
            pace=pace,
        )

    async def preview_add(
        self,
        itinerary_id: int,
        user_id: str,
        candidate_poi_id: int,
        preferred_day: Optional[int] = None,
        hotel_location: Optional[Tuple[float, float]] = None,
        days: Optional[int] = None,
        daily_start: str = "09:00",
        daily_end: str = "18:00",
        travel_profile: str = "auto",
        pace: str = "balanced",
    ) -> Dict[str, Any]:
        """Dry-run feasibility check: "can this POI be added, and where?"

        Loads the existing itinerary's POIs, adds the candidate, and runs the
        real VROOM solver (no heuristic). Because VROOM models each day as a
        vehicle with a time window and POIs carry opening-hours windows, the
        solver's verdict is honest road-network + time-budget feasibility:

          * candidate in ``unassigned`` → **infeasible** (trip at capacity,
            or POI unreachable in any day's window / opening hours).
          * candidate assigned to a vehicle/day → that's the **recommended**
            day. May differ from the user's preferred day — e.g. an Aswan
            POI won't land on a Cairo day no matter the preference.
          * any previously-assigned POI that becomes unassigned → **displaced**
            by the candidate (the day got too full).

        Nothing is persisted — the caller still saves via the normal flow
        once the user confirms. (Honest routing: this is the whole point of
        running a real optimizer instead of a haversine guess.)
        """
        from src.itinerary.persistence import ItineraryPersistence

        persistence = ItineraryPersistence()
        existing = await persistence.load_itinerary_raw(itinerary_id, user_id)
        if not existing:
            raise ValueError(f"Itinerary {itinerary_id} not found")

        existing_poi_ids = [item["poi_id"] for item in existing.get("items", [])]
        # Existing per-POI day assignment, used to detect displacement.
        prior_day_by_poi: Dict[int, int] = {
            item["poi_id"]: int(item.get("day_number", 0))
            for item in existing.get("items", [])
            if item.get("poi_id") is not None
        }

        # If the caller didn't pass a day count, infer from the existing plan.
        if days is None:
            days = max([1, *prior_day_by_poi.values()])

        # Simulate the addition (deduped — if the POI is already on the trip,
        # there's nothing to add; we still report that honestly).
        already_on_trip = candidate_poi_id in existing_poi_ids
        all_ids = existing_poi_ids + ([] if already_on_trip else [candidate_poi_id])

        optimized = await self.generate(
            poi_ids=all_ids,
            user_id=user_id,
            days=days,
            hotel_location=hotel_location,
            daily_start=daily_start,
            daily_end=daily_end,
            travel_profile=travel_profile,
            pace=pace,
        )

        meta = optimized.get("optimization_metadata", {})
        unassigned: List[int] = list(meta.get("unassigned", []) or [])

        # Where did VROOM place the candidate?
        recommended_day: Optional[int] = None
        for day in optimized.get("days", []):
            for stop in day.get("stops", []):
                if stop.get("poi_id") == candidate_poi_id:
                    recommended_day = int(day.get("day_number", 0))
                    break
            if recommended_day is not None:
                break

        feasible = candidate_poi_id not in unassigned and recommended_day is not None

        # Displacement = existing POIs that WERE assigned but are now unassigned.
        displaced = [
            {"poi_id": pid, "day_was": prior_day_by_poi[pid]}
            for pid in unassigned
            if pid != candidate_poi_id and pid in prior_day_by_poi
        ]

        preferred_feasible = (
            feasible and (preferred_day is None or recommended_day == preferred_day)
        )

        # Path B — deterministic placement. Walk the VROOM-optimized schedule
        # to extract exactly where the candidate landed: its arrival time
        # (the suggested clock slot), and the POIs immediately before/after
        # it so the UI can say "between X and Y". This is what lets the
        # planner stop offering a fabricated clock grid and instead commit
        # the POI at the route-optimal time VROOM actually computed.
        placement = self._extract_placement(
            optimized, candidate_poi_id, recommended_day
        )

        return {
            "feasible": feasible,
            "already_on_trip": already_on_trip,
            "recommended_day": recommended_day,
            "preferred_day": preferred_day,
            "preferred_day_feasible": preferred_feasible,
            "displaced_pois": displaced,
            "candidate_placement": placement,
            "solver_status": meta.get("solver_status", "UNKNOWN"),
            "reason": self._explain_preview(
                feasible=feasible,
                already_on_trip=already_on_trip,
                recommended_day=recommended_day,
                preferred_day=preferred_day,
                displaced=displaced,
            ),
            "preview": optimized,
        }

    @staticmethod
    def _extract_placement(
        optimized: Dict, candidate_poi_id: int, recommended_day: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """Pull the candidate's VROOM-assigned slot + neighbours from the preview.

        Returns ``None`` when the candidate wasn't placed (infeasible). On
        success returns ``{arrival_time, sequence, previous_name, next_name,
        day_stops_count}`` — everything the client needs to render "CLEO
        suggests ~2:00 PM, between the Egyptian Museum and Khan el-Khalili".
        """
        if recommended_day is None:
            return None
        for day in optimized.get("days", []):
            if int(day.get("day_number", 0)) != recommended_day:
                continue
            stops = day.get("stops", [])
            for idx, stop in enumerate(stops):
                if stop.get("poi_id") != candidate_poi_id:
                    continue
                prev_stop = stops[idx - 1] if idx > 0 else None
                next_stop = stops[idx + 1] if idx + 1 < len(stops) else None
                return {
                    "arrival_time": stop.get("arrival_time"),
                    "departure_time": stop.get("departure_time"),
                    "sequence": stop.get("sequence"),
                    "previous_name": (prev_stop or {}).get("poi_name"),
                    "next_name": (next_stop or {}).get("poi_name"),
                    "day_stops_count": len(stops),
                }
        return None

    @staticmethod
    def _explain_preview(
        *,
        feasible: bool,
        already_on_trip: bool,
        recommended_day: Optional[int],
        preferred_day: Optional[int],
        displaced: List[Dict[str, Any]],
    ) -> str:
        """One human sentence summarizing the verdict, in VOYO voice."""
        if already_on_trip:
            return "This place is already on your trip."
        if not feasible:
            return (
                "This won't fit on any day of your current trip — every day is "
                "at capacity or the opening hours don't align. Try removing a "
                "stop or extending a day's hours."
            )
        names = lambda n: f"Day {n}"
        if displaced:
            disp_str = ", ".join(
                f"Day {d['day_was']}" for d in displaced
            )
            return (
                f"Fits on {names(recommended_day)}, but adding it crowds the day "
                f"— another stop would be pushed off ({disp_str}). Add it anyway, "
                "or pick a different day."
            )
        if preferred_day is not None and recommended_day != preferred_day:
            return (
                f"Your Day {preferred_day} can't take it, but it fits naturally "
                f"on {names(recommended_day)} — less travel, better pacing."
            )
        return f"Fits cleanly on {names(recommended_day)}."

    # ==================================================================
    # Internal Methods
    # ==================================================================

    async def _fetch_pois(self, poi_ids: List[int]) -> List[Dict[str, Any]]:
        """Fetch full POI records from Supabase by IDs."""
        import asyncio
        try:
            pois = await asyncio.to_thread(
                self._fetch_pois_sync, poi_ids
            )
            return pois
        except Exception as e:
            logger.error(f"Error fetching POIs: {e}")
            return []

    def _fetch_pois_sync(self, poi_ids: List[int]) -> List[Dict[str, Any]]:
        """Synchronous POI fetch."""
        all_pois = self.db.get_records("pois", filters={"is_active": True}, use_admin=True)
        poi_map = {p["id"]: p for p in all_pois}
        return [poi_map[pid] for pid in poi_ids if pid in poi_map]

    @staticmethod
    def _apply_pace(pois: List[Dict], pace_config: Dict) -> List[Dict]:
        """Adjust visit durations and daily capacity based on pace."""
        multiplier = pace_config["multiplier"]

        for poi in pois:
            base_duration = poi.get("average_visit_duration") or 60
            poi["adjusted_visit_duration"] = max(15, int(base_duration * multiplier))

        return pois

    @staticmethod
    def _enrich_schedule(optimized: Dict, pois: List[Dict]) -> Dict:
        """Add POI details (name, category, image, tip) to each stop."""
        poi_lookup = {p["id"]: p for p in pois}

        for day in optimized.get("days", []):
            for stop in day.get("stops", []):
                poi = poi_lookup.get(stop.get("poi_id"), {})
                stop["image_url"] = (poi.get("image_urls") or [None])[0] if poi.get("image_urls") else None
                stop["description"] = (poi.get("description") or "")[:200]
                stop["address"] = poi.get("address", "")
                stop["tags"] = poi.get("tags", [])

        return optimized

    @staticmethod
    def _calculate_costs(pois: List[Dict]) -> float:
        """Sum ticket prices for all POIs in the itinerary."""
        total = sum(float(p.get("ticket_price") or 0) for p in pois)
        return round(total, 2)

    @staticmethod
    def _generate_day_themes(schedule: Dict, pois: List[Dict]) -> Dict:
        """Generate human-readable day themes from POI categories."""
        category_labels = {
            "historical": "Ancient Wonders",
            "cultural": "Cultural Treasures",
            "religious": "Sacred Heritage",
            "natural": "Natural Beauty",
            "entertainment": "Fun & Adventure",
            "dining": "Culinary Journey",
        }

        poi_lookup = {p["id"]: p for p in pois}

        for day in schedule.get("days", []):
            categories = []
            for stop in day.get("stops", []):
                poi = poi_lookup.get(stop.get("poi_id"), {})
                cat = (poi.get("category") or "").lower()
                if cat and cat not in categories:
                    categories.append(cat)

            if categories:
                primary = category_labels.get(categories[0], categories[0].title())
                if len(categories) > 1:
                    secondary = category_labels.get(categories[1], categories[1].title())
                    day["theme"] = f"{primary} & {secondary}"
                else:
                    day["theme"] = primary
            else:
                day["theme"] = f"Day {day.get('day_number', 1)}"

        return schedule
