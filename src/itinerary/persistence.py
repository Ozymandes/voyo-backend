"""
VOYO Itinerary Persistence — Supabase Save/Load

Handles saving optimized itineraries to Supabase (itineraries + itinerary_items
tables) and loading them back with enriched POI data.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class ItineraryPersistence:
    """Save/load itineraries to/from Supabase."""

    def __init__(self):
        self.db = SupabaseClient()

    async def save_optimized_itinerary(
        self,
        user_id: str,
        title: str,
        region_id: Optional[int],
        optimized_schedule: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Save the full itinerary to Supabase.

        1. Create itinerary record (status='current')
        2. Set any previous 'current' itinerary to 'archived'
        3. Create itinerary_items records from optimized schedule
        4. Return saved itinerary with IDs.
        """
        import asyncio

        # Archive previous current itinerary
        await asyncio.to_thread(self._archive_current, user_id)

        # Create itinerary record
        itinerary_data = {
            "user_id": user_id,
            "title": title,
            "region_id": region_id,
            "status": "current",
            "start_date": datetime.utcnow().isoformat(),
            "metadata": {
                "solver_status": optimized_schedule.get("optimization_metadata", {}).get("solver_status"),
                "computed_with": "vroom_v1.13",
            },
        }

        itinerary = await asyncio.to_thread(
            self.db.insert_record, "itineraries", itinerary_data, use_admin=True
        )

        if not itinerary:
            raise RuntimeError("Failed to create itinerary record")

        itinerary_id = itinerary.get("id") or itinerary[0].get("id") if isinstance(itinerary, list) else itinerary.get("id")

        # Create itinerary_items from the optimized schedule
        items: List[Dict[str, Any]] = []
        for day in optimized_schedule.get("days", []):
            day_number = day.get("day_number", 1)
            for stop in day.get("stops", []):
                item_data = {
                    "itinerary_id": itinerary_id,
                    "poi_id": stop.get("poi_id"),
                    "day_number": day_number,
                    "sequence": stop.get("sequence", 0),
                    "arrival_time": stop.get("arrival_time"),
                    "departure_time": stop.get("departure_time"),
                    "travel_to_next_minutes": stop.get("travel_to_next_minutes", 0),
                    "travel_to_next_km": stop.get("travel_to_next_km", 0),
                    "notes": stop.get("tip", ""),
                }
                items.append(item_data)

        # Batch insert items
        if items:
            await asyncio.to_thread(
                self.db.client.table("itinerary_items").insert(items).execute
            )

        logger.info(
            f"Saved itinerary {itinerary_id} for user {user_id} "
            f"with {len(items)} items across {len(optimized_schedule.get('days', []))} days"
        )

        # Return with the itinerary_id included
        result = optimized_schedule.copy()
        result["itinerary_id"] = itinerary_id
        result["title"] = title
        return result

    async def load_itinerary_with_routes(
        self,
        itinerary_id: int,
        user_id: str,
    ) -> Dict[str, Any]:
        """Load itinerary and generate Valhalla route polylines for map display."""
        import asyncio

        itinerary = await asyncio.to_thread(
            self._load_itinerary_record, itinerary_id, user_id
        )
        if not itinerary:
            return {}

        items = await asyncio.to_thread(
            self._load_itinerary_items, itinerary_id
        )

        # Enrich items with POI data
        poi_ids = list(set(item["poi_id"] for item in items))
        pois = await asyncio.to_thread(
            self._fetch_pois_by_ids, poi_ids
        )
        poi_lookup = {p["id"]: p for p in pois}

        # Build days structure
        days_map: Dict[int, List[Dict]] = {}
        for item in items:
            day = item["day_number"]
            if day not in days_map:
                days_map[day] = []
            poi = poi_lookup.get(item["poi_id"], {})
            days_map[day].append({
                "sequence": item["sequence"],
                "poi_id": item["poi_id"],
                "poi_name": poi.get("name", ""),
                "latitude": poi.get("latitude"),
                "longitude": poi.get("longitude"),
                "arrival_time": item.get("arrival_time"),
                "departure_time": item.get("departure_time"),
                "category": poi.get("category", ""),
                "ticket_price": float(poi.get("ticket_price") or 0),
                "tip": item.get("notes", ""),
                "travel_to_next_minutes": item.get("travel_to_next_minutes", 0),
                "travel_to_next_km": item.get("travel_to_next_km", 0),
            })

        days = []
        for day_num in sorted(days_map.keys()):
            stops = sorted(days_map[day_num], key=lambda s: s["sequence"])
            days.append({
                "day_number": day_num,
                "theme": "",
                "stops": stops,
            })

        return {
            "itinerary_id": itinerary_id,
            "title": itinerary.get("title", ""),
            "status": itinerary.get("status", ""),
            "days": days,
        }

    async def load_itinerary_raw(
        self, itinerary_id: int, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Load raw itinerary data (used by reoptimize)."""
        import asyncio

        itinerary = await asyncio.to_thread(
            self._load_itinerary_record, itinerary_id, user_id
        )
        if not itinerary:
            return None

        items = await asyncio.to_thread(
            self._load_itinerary_items, itinerary_id
        )

        return {**itinerary, "items": items}

    async def delete_itinerary(self, itinerary_id: int, user_id: str) -> bool:
        """Delete an itinerary and all its items."""
        import asyncio

        # Verify ownership
        record = await asyncio.to_thread(
            self._load_itinerary_record, itinerary_id, user_id
        )
        if not record:
            return False

        # Delete items first (CASCADE should handle this, but be explicit)
        await asyncio.to_thread(
            self.db.admin_client.table("itinerary_items")
            .delete()
            .eq("itinerary_id", itinerary_id)
            .execute
        )

        # Delete itinerary
        await asyncio.to_thread(
            self.db.admin_client.table("itineraries")
            .delete()
            .eq("id", itinerary_id)
            .execute
        )

        logger.info(f"Deleted itinerary {itinerary_id}")
        return True

    # ==================================================================
    # Internal
    # ==================================================================

    def _archive_current(self, user_id: str):
        """Set any current itinerary to 'archived'."""
        try:
            self.db.admin_client.table("itineraries").update(
                {"status": "archived"}
            ).eq("user_id", user_id).eq("status", "current").execute()
        except Exception as e:
            logger.warning(f"Could not archive current itinerary: {e}")

    def _load_itinerary_record(
        self, itinerary_id: int, user_id: str
    ) -> Optional[Dict]:
        """Load a single itinerary record, verifying user ownership."""
        try:
            records = self.db.get_records(
                "itineraries",
                filters={"id": itinerary_id, "user_id": user_id},
                use_admin=True,
                limit=1,
            )
            return records[0] if records else None
        except Exception as e:
            logger.error(f"Error loading itinerary {itinerary_id}: {e}")
            return None

    def _load_itinerary_items(self, itinerary_id: int) -> List[Dict]:
        """Load all items for an itinerary."""
        try:
            return self.db.get_records(
                "itinerary_items",
                filters={"itinerary_id": itinerary_id},
                use_admin=True,
            )
        except Exception as e:
            logger.error(f"Error loading items for itinerary {itinerary_id}: {e}")
            return []

    def _fetch_pois_by_ids(self, poi_ids: List[int]) -> List[Dict]:
        """Fetch POI records by IDs."""
        try:
            all_pois = self.db.get_records(
                "pois", filters={"is_active": True}, use_admin=True
            )
            return [p for p in all_pois if p.get("id") in poi_ids]
        except Exception as e:
            logger.error(f"Error fetching POIs: {e}")
            return []
