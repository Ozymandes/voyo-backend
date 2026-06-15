"""
Supabase Tool for CLEO — 3-Tier POI Search (Server-Side)
Cairo Local Expert & Operator

Tier 1: Name match via Supabase ``ilike``
Tier 2: Description + tag match via Supabase ``ilike`` (server-side,
        zero rows pulled into Python)
Tier 3: Category + region refinement filters

Future: Replace Tier 2 with pgvector embedding search (see
        config/sql/003_poi_search_vector.sql when ready).
"""

from typing import List, Dict, Optional
import logging

from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class SupabaseTool:
    """Three-tier POI search — all matching runs on the Supabase side.

    No more than ``limit`` rows ever leave the database.  Python only
    handles deduplication, region/category filtering on the result set
    (which is at most ``limit`` rows), and optional personalization
    re-ranking.
    """

    def __init__(self):
        self.db = SupabaseClient()
        logger.info("Supabase tool initialized (3-tier server-side search)")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_pois(
        self,
        query: str,
        region: Optional[str] = None,
        category: Optional[str] = None,
        user_profile: Optional[Dict] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Search POIs using a three-tier server-side strategy.

        1. Name match (Supabase ``ilike`` on name / name_arabic / address)
        2. Description + tags match (Supabase ``ilike`` on description)
        3. Category + region filters as refinements
        """
        try:
            results: List[Dict] = []

            # --- Tier 1: Name match ---
            name_matches = self._search_by_name(query, limit=limit)
            results.extend(name_matches)
            logger.debug(f"Tier 1 (name ilike): {len(name_matches)} hits for '{query}'")

            # --- Tier 2: Description / tag match (server-side) ---
            if len(results) < 3:
                broader = self._search_by_description(query, limit=limit)
                before = len(results)
                results = self._deduplicate(results + broader)
                logger.debug(f"Tier 2 (desc ilike): {len(results) - before} additional hits")

            # --- Tier 3: Region / category refinement ---
            if region:
                results = [p for p in results if self._matches_region(p, region)]
            if category:
                results = [p for p in results if self._matches_category(p, category)]

            # Personalize ranking when a profile is supplied
            if user_profile:
                results = self._personalize_ranking(results, user_profile)

            return [self._slim_for_llm(p) for p in results[:limit]]

        except Exception as e:
            logger.error(f"Error searching POIs: {e}")
            return []

    async def search_pois_async(
        self,
        query: str,
        region: Optional[str] = None,
        category: Optional[str] = None,
        user_profile: Optional[Dict] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Async wrapper — runs the synchronous search in a thread."""
        import asyncio
        return await asyncio.to_thread(
            self.search_pois, query, region, category, user_profile, limit
        )

    @staticmethod
    def _slim_for_llm(poi: Dict) -> Dict:
        """Project a full POI record into a compact summary for the LLM.

        The ReAct loop appends tool results back into the message history, so
        returning full records (Arabic names, address, opening_hours dicts,
        image-URL arrays) balloons the request past Groq's tokens-per-minute
        ceiling. The LLM only needs identity + a few decision-relevant fields
        to pick POIs; full detail is available via ``get_poi_details``.
        """
        desc = (poi.get("description") or "")
        if len(desc) > 140:
            desc = desc[:137].rstrip() + "…"
        return {
            "id": poi.get("id"),
            "name": poi.get("name", ""),
            "category": poi.get("category", ""),
            "city": poi.get("city") or poi.get("region_id"),
            "ticket_price": poi.get("ticket_price"),
            "currency": poi.get("currency"),
            "average_rating": poi.get("average_rating"),
            "description": desc,
        }

    def get_poi_details(self, poi_id: int) -> Optional[Dict]:
        """Get full POI record by ID."""
        try:
            pois = self.db.get_records("pois", filters={"id": int(poi_id)}, limit=1, use_admin=True)
            return pois[0] if pois else None
        except Exception as e:
            logger.error(f"Error getting POI details for id={poi_id}: {e}")
            return None

    def get_historical_significance(self, poi_id: int) -> Dict:
        """Return historical significance text and basic metadata for a POI."""
        try:
            poi = self.get_poi_details(poi_id)
            if poi:
                return {
                    "name": poi.get("name", ""),
                    "category": poi.get("category", ""),
                    "historical_significance": poi.get("historical_significance", ""),
                    "description": poi.get("description", ""),
                }
            return {"error": f"POI {poi_id} not found"}
        except Exception as e:
            logger.error(f"Error getting historical significance: {e}")
            return {"error": str(e)}

    def find_nearby_pois(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        limit: int = 10,
    ) -> List[Dict]:
        """Find POIs within ``radius_km`` using geodesic distance.

        Note: This is the one method that still fetches a wider set of
        POIs for client-side distance calc.  A future improvement should
        use Supabase's PostGIS ``ST_DWithin`` for server-side geo queries.
        """
        try:
            from geopy.distance import geodesic

            all_pois = self.db.get_records("pois", limit=1000, use_admin=True)
            nearby = []
            for poi in all_pois:
                try:
                    dist = geodesic(
                        (latitude, longitude),
                        (poi["latitude"], poi["longitude"]),
                    ).km
                    if dist <= radius_km:
                        poi["distance_km"] = round(dist, 2)
                        nearby.append(poi)
                except (KeyError, TypeError):
                    continue

            nearby.sort(key=lambda p: p["distance_km"])
            return nearby[:limit]

        except Exception as e:
            logger.error(f"Error finding nearby POIs: {e}")
            return []

    # ------------------------------------------------------------------
    # Tier implementations (all server-side)
    # ------------------------------------------------------------------

    def _search_by_name(self, query: str, limit: int = 10) -> List[Dict]:
        """Tier 1: Supabase ``ilike`` on name, name_arabic, address."""
        try:
            response = (
                self.db.admin_client.table("pois")
                .select("*")
                .eq("is_active", True)
                .or_(
                    f"name.ilike.%{query}%,"
                    f"name_arabic.ilike.%{query}%,"
                    f"address.ilike.%{query}%"
                )
                .limit(limit)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Tier 1 name search error: {e}")
            return []

    def _search_by_description(self, query: str, limit: int = 10) -> List[Dict]:
        """Tier 2: Supabase ``ilike`` on description + historical_significance.

        Runs entirely on the database side.  Individual words from the
        query are tried via ``or_`` so "King Tut exhibition" matches
        descriptions containing any of those terms.
        """
        try:
            # Build per-word ilike clauses for broader matching
            words = [w.strip() for w in query.split() if len(w.strip()) > 2]
            if not words:
                return []

            # Create OR clause: description ilike any word OR historical_significance ilike any word
            parts = []
            for word in words:
                parts.append(f"description.ilike.%{word}%")
                parts.append(f"historical_significance.ilike.%{word}%")

            or_clause = ",".join(parts)

            response = (
                self.db.admin_client.table("pois")
                .select("*")
                .eq("is_active", True)
                .or_(or_clause)
                .limit(limit)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Tier 2 description search error: {e}")
            return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate(pois: List[Dict]) -> List[Dict]:
        """Remove duplicate POIs by ID, preserving first-seen order."""
        seen: set = set()
        unique: List[Dict] = []
        for poi in pois:
            pid = poi.get("id")
            if pid not in seen:
                seen.add(pid)
                unique.append(poi)
        return unique

    @staticmethod
    def _matches_region(poi: Dict, region: str) -> bool:
        """Check if a POI belongs to the given region name."""
        region_name = poi.get("region_name", "")
        if not region_name:
            return True  # Can't filter — keep it
        return region.lower() in region_name.lower()

    @staticmethod
    def _matches_category(poi: Dict, category: str) -> bool:
        """Check if a POI matches the given category."""
        poi_cat = poi.get("category", "")
        return category.lower() in poi_cat.lower()

    def _personalize_ranking(self, pois: List[Dict], user_profile: Dict) -> List[Dict]:
        """Re-rank POIs based on user profile preferences."""
        interest_scores = user_profile.get("interest_scores", {})
        mobility = user_profile.get("mobility_preference", "")
        budget = user_profile.get("trip_budget_estimate", 0)

        scored: List[tuple] = []
        for poi in pois:
            score = 0.0

            category = poi.get("category", "").lower()
            for interest_key, weight in interest_scores.items():
                clean = interest_key.replace("_", " ")
                if clean in category or category in clean:
                    score += weight * 10

            if "limited" in mobility.lower() and poi.get("is_accessible", False):
                score += 20

            if budget > 0:
                ticket_price = poi.get("ticket_price", 0)
                if ticket_price and ticket_price <= budget * 0.2:
                    score += 10

            score += poi.get("popularity_score", 0) * 0.5
            scored.append((score, poi))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [poi for _, poi in scored]
