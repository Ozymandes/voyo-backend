"""
Google Places API Scraper
Enhances POI data with photos, reviews, and detailed information
"""

import os
import logging
import json
import time
import math
from typing import List, Dict, Any, Optional, Tuple
import requests

from .base_scraper import BaseScraper, POIData, POICategory
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class GooglePlacesScraper(BaseScraper):
    """Google Places API scraper for POI enhancement"""

    def __init__(self, region_name: str, region_bounds: Optional[Dict] = None):
        super().__init__(region_name, region_bounds)
        load_dotenv()

        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise ValueError("Google Places API key not found in environment variables")

        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.text_search_url = f"{self.base_url}/textsearch/json"
        self.nearby_search_url = f"{self.base_url}/nearbysearch/json"
        self.details_url = f"{self.base_url}/details/json"
        self.photos_url = f"{self.base_url}/photo"

        # Google Places API limits
        self.max_requests_per_day = 100000  # Free tier limit
        self.requests_per_second = 10
        self.requests_made_today = 0

    def search_places_by_text(self, query: str, region_bounds: Dict, limit: int = 20) -> List[Dict]:
        """Search for places using text search within region bounds"""
        try:
            # Construct location bias parameter
            bounds_str = f"{region_bounds['min_lat']},{region_bounds['min_lon']}|{region_bounds['max_lat']},{region_bounds['max_lon']}"

            params = {
                "query": query,
                "locationbias": f"rectangle:{bounds_str}",
                "key": self.api_key,
                "language": "en",
                "region": "eg",
                "radius": "50000"  # 50km radius
            }

            logger.info(f"Searching Google Places for: {query}")
            response = self.make_request(self.text_search_url, params=params)

            if not response:
                return []

            data = response.json()
            if data.get("status") == "OK":
                places = data.get("results", [])[:limit]
                logger.info(f"Found {len(places)} places for query: {query}")
                return places
            else:
                logger.error(f"Google Places API error: {data.get('status')} - {data.get('error_message', '')}")
                return []

        except Exception as e:
            logger.error(f"Error in Google Places text search: {str(e)}")
            return []

    def search_places_nearby(self, lat: float, lon: float, radius: int = 5000, place_type: str = "tourist_attraction") -> List[Dict]:
        """Search for places near specific coordinates"""
        try:
            params = {
                "location": f"{lat},{lon}",
                "radius": radius,
                "type": place_type,
                "key": self.api_key,
                "language": "en",
                "region": "eg"
            }

            logger.info(f"Searching near {lat},{lon} for {place_type}")
            response = self.make_request(self.nearby_search_url, params=params)

            if not response:
                return []

            data = response.json()
            if data.get("status") == "OK":
                places = data.get("results", [])
                logger.info(f"Found {len(places)} nearby places")
                return places
            else:
                logger.error(f"Google Places nearby search error: {data.get('status')}")
                return []

        except Exception as e:
            logger.error(f"Error in Google Places nearby search: {str(e)}")
            return []

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific place"""
        try:
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,rating,reviews,photos,geometry,opening_hours,price_level,website,phone_number,types,user_ratings_total",
                "key": self.api_key,
                "language": "en"
            }

            response = self.make_request(self.details_url, params=params)

            if not response:
                return None

            data = response.json()
            if data.get("status") == "OK":
                return data.get("result")
            else:
                logger.error(f"Google Places details error: {data.get('status')}")
                return None

        except Exception as e:
            logger.error(f"Error getting place details for {place_id}: {str(e)}")
            return None

    def get_photo_url(self, photo_reference: str, max_width: int = 800) -> Optional[str]:
        """Get photo URL from photo reference"""
        try:
            params = {
                "maxwidth": max_width,
                "photoreference": photo_reference,
                "key": self.api_key
            }

            # This returns the actual image URL
            response = self.make_request(self.photos_url, params=params, allow_redirects=False)

            if response and response.status_code == 302:
                return response.headers.get("Location")
            else:
                # Try to get the URL directly
                url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"
                return url

        except Exception as e:
            logger.error(f"Error getting photo URL: {str(e)}")
            return None

    def enhance_poi_data(self, pois: List[POIData]) -> List[POIData]:
        """Enhance existing POI data with Google Places information"""
        enhanced_pois = []

        for i, poi in enumerate(pois):
            logger.info(f"Enhancing POI {i+1}/{len(pois)}: {poi.name}")

            try:
                # Search for matching place
                search_results = self.search_places_nearby(
                    poi.latitude, poi.longitude,
                    radius=1000,
                    place_type="tourist_attraction"
                )

                if not search_results:
                    # Try broader search with default Cairo bounds
                    cairo_bounds = {"min_lat": 29.7, "max_lat": 30.3, "min_lon": 31.0, "max_lon": 31.6}
                    search_results = self.search_places_by_text(
                        poi.name, cairo_bounds, limit=5
                    )

                # Find best match
                best_match = self._find_best_match(poi, search_results)

                if best_match:
                    # Get detailed information
                    place_details = self.get_place_details(best_match.get("place_id"))
                    if place_details:
                        enhanced_poi = self._merge_poi_data(poi, place_details)
                        enhanced_pois.append(enhanced_poi)
                    else:
                        enhanced_pois.append(poi)
                else:
                    enhanced_pois.append(poi)

                # Rate limiting between requests (free tier: 10 requests/second)
                time.sleep(0.2)  # Conservative: 5 requests/second

            except Exception as e:
                logger.error(f"Error enhancing POI {poi.name}: {str(e)}")
                enhanced_pois.append(poi)

        logger.info(f"Enhanced {len(enhanced_pois)} POIs with Google Places data")
        return enhanced_pois

    def _find_best_match(self, poi: POIData, search_results: List[Dict]) -> Optional[Dict]:
        """Find the best matching place from search results"""
        if not search_results:
            return None

        best_match = None
        best_score = 0

        for result in search_results:
            score = 0

            # Name similarity
            result_name = result.get("name", "").lower()
            poi_name = poi.name.lower()

            if result_name == poi_name:
                score += 100
            elif poi_name in result_name or result_name in poi_name:
                score += 50

            # Distance check
            if "geometry" in result:
                location = result["geometry"]["location"]
                distance = self._calculate_distance(
                    poi.latitude, poi.longitude,
                    location["lat"], location["lng"]
                )

                if distance < 0.1:  # Less than 100 meters
                    score += 50
                elif distance < 0.5:  # Less than 500 meters
                    score += 25
                elif distance < 1.0:  # Less than 1 km
                    score += 10

            # Rating bonus (places with ratings are more likely to be important)
            if result.get("rating"):
                score += 20

            if score > best_score:
                best_score = score
                best_match = result

        # Only return match if it's reasonably close (distance < 2km)
        if best_match and best_score >= 50:
            return best_match

        return None

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        # Haversine formula
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (math.sin(dlat/2)**2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def _merge_poi_data(self, poi: POIData, place_details: Dict) -> POIData:
        """Merge Google Places data with existing POI data"""
        # Enhance basic information
        if place_details.get("formatted_address"):
            poi.address = place_details["formatted_address"]

        if place_details.get("formatted_phone_number"):
            poi.phone_number = place_details["formatted_phone_number"]

        if place_details.get("website"):
            poi.website_url = place_details["website"]

        # Enhanced ratings
        if place_details.get("rating"):
            poi.average_rating = float(place_details["rating"])

        if place_details.get("user_ratings_total"):
            poi.total_reviews = int(place_details["user_ratings_total"])

        # Price information
        if place_details.get("price_level"):
            price_mapping = {0: 0, 1: 25, 2: 100, 3: 250, 4: 500}  # EGP estimates
            price_level = place_details["price_level"]
            if price_level in price_mapping:
                poi.ticket_price = price_mapping[price_level]

        # Photos
        photos = place_details.get("photos", [])
        if photos:
            photo_urls = []
            for photo in photos[:5]:  # Limit to first 5 photos
                photo_url = self.get_photo_url(photo["photo_reference"])
                if photo_url:
                    photo_urls.append(photo_url)
            poi.image_urls = photo_urls

        # Opening hours
        if place_details.get("opening_hours"):
            opening_hours = place_details["opening_hours"]
            if opening_hours.get("periods"):
                periods = opening_hours["periods"]
                hours_dict = {
                    "open_now": opening_hours.get("open_now", False),
                    "periods": []
                }

                for period in periods:
                    day_period = {
                        "open": period["open"]["time"],
                        "close": period["close"]["time"],
                        "day": period["open"]["day"]
                    }
                    hours_dict["periods"].append(day_period)

                poi.opening_hours = hours_dict

        # Enhanced description (concatenate with existing)
        if place_details.get("types"):
            types_info = ", ".join(place_details["types"])
            if poi.description:
                poi.description = f"{poi.description} Types: {types_info}"
            else:
                poi.description = f"Types: {types_info}"

        # Add Google Places source
        poi.source = f"{poi.source or ''} + Google Places".strip()
        if not poi.source:
            poi.source = "Google Places"

        return poi

    def scrape_pois(self, limit: Optional[int] = None) -> List[POIData]:
        """Google Places is primarily used for enhancement, not primary scraping"""
        # This method is implemented for consistency with BaseScraper
        # but Google Places is mainly used to enhance OSM data
        logger.info("Google Places scraper called - will enhance existing data")
        return []

    def search_popular_pois(self, limit: int = 20) -> List[POIData]:
        """Search for popular POIs in the region"""
        logger.info(f"Searching for popular POIs in {self.region_name}")

        # Get region center
        bounds = self.get_region_bounds()
        center_lat = (bounds["min_lat"] + bounds["max_lat"]) / 2
        center_lon = (bounds["min_lon"] + bounds["max_lon"]) / 2

        # Search queries for different types of POIs
        search_queries = [
            "museum",
            "historical site",
            "tourist attraction",
            "temple",
            "monument",
            "park",
            "restaurant"
        ]

        all_places = []
        for query in search_queries:
            try:
                places = self.search_places_by_text(query, bounds, limit=limit//len(search_queries))
                all_places.extend(places)
                logger.info(f"Found {len(places)} places for query: {query}")
            except Exception as e:
                logger.error(f"Error searching for {query}: {str(e)}")

        logger.info(f"Total places found: {len(all_places)}")

        # Convert to POIData objects
        pois = []
        for place in all_places:
            try:
                if "geometry" in place:
                    location = place["geometry"]["location"]
                    poi = POIData(
                        name=place.get("name", ""),
                        description=place.get("vicinity", ""),
                        latitude=location["lat"],
                        longitude=location["lng"],
                        average_rating=place.get("rating"),
                        total_reviews=place.get("user_ratings_total", 0),
                        source="Google Places",
                        source_id=place.get("place_id")
                    )

                    # Add photos
                    photos = place.get("photos", [])
                    if photos:
                        photo_urls = []
                        for photo in photos[:3]:
                            photo_url = self.get_photo_url(photo["photo_reference"])
                            if photo_url:
                                photo_urls.append(photo_url)
                        poi.image_urls = photo_urls

                    if self.validate_poi_data(poi):
                        pois.append(poi)

            except Exception as e:
                logger.error(f"Error converting place to POI: {str(e)}")

        logger.info(f"Successfully converted {len(pois)} places to POI objects")
        return pois