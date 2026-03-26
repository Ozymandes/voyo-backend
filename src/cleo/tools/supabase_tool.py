"""
Supabase Tool for CLEO
Personalized POI queries based on user profile
"""

from typing import List, Dict, Optional
from src.database.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)

class SupabaseTool:
    """Personalized Supabase queries for CLEO"""

    def __init__(self):
        """Initialize Supabase tool"""
        self.db = SupabaseClient()
        logger.info("Supabase tool initialized")

    def search_pois(
        self,
        query: str,
        region: Optional[str] = None,
        category: Optional[str] = None,
        user_profile: Optional[Dict] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search POIs with personalization

        Args:
            query: Search query string
            region: Optional region filter
            category: Optional category filter
            user_profile: Optional user profile for personalization
            limit: Maximum number of results

        Returns:
            List of POI dictionaries
        """
        try:
            # Build query filters
            filters = {}

            if region:
                # Get region ID
                regions = self.db.get_records("regions", filters={"name": region})
                if regions:
                    filters["region_id"] = regions[0]["id"]

            if category:
                filters["category"] = category

            # Search POIs (get more for personalization)
            pois = self.db.get_records("pois", filters=filters, limit=limit * 3)

            # Filter by query keywords if no exact matches
            if query and len(pois) < limit:
                query_lower = query.lower()
                # Extract keywords from query
                keywords = ['cairo', 'giza', 'luxor', 'aswan', 'alexandria', 'sinai',
                           'mosque', 'temple', 'museum', 'pyramid', 'citadel', 'market',
                           'bazaar', 'church', 'historical', 'cultural', 'natural']

                matching_pois = []
                for poi in pois:
                    poi_text = f"{poi.get('name', '')} {poi.get('description', '')} {poi.get('category', '')}".lower()
                    if any(keyword in query_lower and keyword in poi_text for keyword in keywords):
                        matching_pois.append(poi)

                if matching_pois:
                    pois = matching_pois

            # Personalize ranking if profile provided
            if user_profile:
                pois = self._personalize_ranking(pois, user_profile)

            return pois[:limit]

        except Exception as e:
            logger.error(f"Error searching POIs: {e}")
            return []

    def get_poi_details(self, poi_id: str) -> Optional[Dict]:
        """
        Get detailed POI information

        Args:
            poi_id: POI identifier

        Returns:
            POI dictionary or None
        """
        try:
            pois = self.db.get_records("pois", filters={"id": poi_id}, limit=1)
            return pois[0] if pois else None

        except Exception as e:
            logger.error(f"Error getting POI details: {e}")
            return None

    def get_historical_significance(self, poi_id: str) -> str:
        """
        Get historical significance for educational content

        Args:
            poi_id: POI identifier

        Returns:
            Historical significance text
        """
        try:
            poi = self.get_poi_details(poi_id)
            if poi:
                return poi.get("historical_significance", "")
            return ""

        except Exception as e:
            logger.error(f"Error getting historical significance: {e}")
            return ""

    def find_nearby_pois(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find POIs near a location

        Args:
            latitude: Starting latitude
            longitude: Starting longitude
            radius_km: Search radius in kilometers
            limit: Maximum results

        Returns:
            List of nearby POIs with distance
        """
        try:
            from geopy.distance import geodesic

            # Get all POIs (will filter by distance)
            all_pois = self.db.get_records("pois", limit=1000)

            nearby = []
            for poi in all_pois:
                try:
                    distance = geodesic(
                        (latitude, longitude),
                        (poi["latitude"], poi["longitude"])
                    ).km

                    if distance <= radius_km:
                        poi["distance_km"] = round(distance, 2)
                        nearby.append(poi)

                except KeyError:
                    # Skip POIs without coordinates
                    continue

            # Sort by distance
            nearby.sort(key=lambda p: p["distance_km"])

            return nearby[:limit]

        except Exception as e:
            logger.error(f"Error finding nearby POIs: {e}")
            return []

    def _personalize_ranking(self, pois: List[Dict], user_profile: Dict) -> List[Dict]:
        """
        Re-rank POIs based on user profile

        Args:
            pois: List of POI dictionaries
            user_profile: User profile with preferences

        Returns:
            Re-ranked list of POIs
        """
        interest_scores = user_profile.get("interest_scores", {})
        mobility = user_profile.get("mobility_preference", "")
        budget = user_profile.get("trip_budget_estimate", 0)

        scored_pois = []

        for poi in pois:
            score = 0

            # Match category to interests
            category = poi.get("category", "").lower()
            if category in interest_scores:
                score += interest_scores[category] * 10

            # Consider mobility
            if "limited" in mobility.lower():
                if poi.get("is_accessible", False):
                    score += 20

            # Consider budget (ticket price as % of daily budget)
            if budget > 0:
                ticket_price = poi.get("ticket_price", 0)
                if ticket_price and ticket_price <= budget * 0.2:
                    score += 10

            # Consider popularity
            score += poi.get("popularity_score", 0) * 5

            scored_pois.append((score, poi))

        # Sort by score (highest first)
        scored_pois.sort(key=lambda x: x[0], reverse=True)

        return [poi for score, poi in scored_pois]
