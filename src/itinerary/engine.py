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
