"""
OpenStreetMap Overpass API Scraper
Extracts POI data from OpenStreetMap for Egyptian regions
"""

import logging
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from .base_scraper import BaseScraper, POIData, POICategory

logger = logging.getLogger(__name__)

class OSMScraper(BaseScraper):
    """OpenStreetMap scraper using Overpass API"""

    def __init__(self, region_name: str, region_bounds: Optional[Dict] = None):
        super().__init__(region_name, region_bounds)
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.regions_config = self._get_regions_config()

    def _get_regions_config(self) -> Dict[str, Dict[str, Any]]:
        """Get specific configuration for each Egyptian region"""
        return {
            "Cairo": {
                "focus_categories": [
                    "tourism=museum", "tourism=attraction", "tourism=artwork",
                    "historic=archaeological_site", "historic=monument",
                    "amenity=restaurant", "amenity=cafe", "shop=mall",
                    "leisure=park", "historic=castle"
                ],
                "important_tags": ["Egyptian Museum", "Khan el-Khalili", "Citadel", "Cairo Tower"]
            },
            "Giza": {
                "focus_categories": [
                    "tourism=museum", "tourism=attraction",
                    "historic=archaeological_site", "historic=monument",
                    "historic=castle", "tourism=zoo"
                ],
                "important_tags": ["Pyramids", "Sphinx", "Memphis", "Saqqara"]
            },
            "Alexandria": {
                "focus_categories": [
                    "tourism=museum", "tourism=attraction", "historic=monument",
                    "amenity=restaurant", "amenity=cafe", "tourism=gallery",
                    "historic=castle", "leisure=park"
                ],
                "important_tags": ["Bibliotheca", "Citadel", "Montazah", "Corniche"]
            },
            "Luxor": {
                "focus_categories": [
                    "tourism=museum", "tourism=attraction",
                    "historic=archaeological_site", "historic=monument",
                    "historic=temple", "historic=tomb"
                ],
                "important_tags": ["Karnak", "Valley of Kings", "Luxor Temple", "Hatshepsut"]
            },
            "Aswan": {
                "focus_categories": [
                    "tourism=museum", "tourism=attraction",
                    "historic=archaeological_site", "historic=monument",
                    "historic=temple", "tourism=wildlife_hide"
                ],
                "important_tags": ["Philae", "Abu Simbel", "Nubian Museum", "Elephantine"]
            },
            "Hurghada": {
                "focus_categories": [
                    "tourism=attraction", "tourism=museum",
                    "amenity=restaurant", "amenity=cafe", "tourism=hotel",
                    "leisure=beach_resort", "tourism=wildlife_hide"
                ],
                "important_tags": ["Marina", "Old Town", "Giftun", "El Gouna"]
            },
            "Marsa Alam": {
                "focus_categories": [
                    "tourism=attraction", "tourism=wildlife_hide",
                    "amenity=restaurant", "tourism=hotel",
                    "leisure=beach_resort", "tourism=marine_park"
                ],
                "important_tags": ["Port Ghalib", "Wadi el Gemal", "Sataya", "Abu Dabbab"]
            },
            "Sinai": {
                "focus_categories": [
                    "tourism=attraction", "historic=monument",
                    "historic=monastery", "historic=mountain",
                    "tourism=wildlife_hide", "leisure=beach_resort"
                ],
                "important_tags": ["Mount Sinai", "Saint Catherine", "Sharm", "Dahab"]
            }
        }

    def _build_overpass_query(self, categories: List[str], bounds: Dict[str, float]) -> str:
        """Build Overpass API query for specific categories"""
        min_lat, max_lat = bounds.get("min_lat", 0), bounds.get("max_lat", 0)
        min_lon, max_lon = bounds.get("min_lon", 0), bounds.get("max_lon", 0)

        # Build query for multiple categories
        category_queries = []
        for category in categories:
            # Split "tourism=museum" into key="tourism" and value="museum"
            if "=" in category:
                key, value = category.split("=", 1)
                category_queries.append(f'node["{key}"="{value}"]({min_lat},{min_lon},{max_lat},{max_lon});')
                category_queries.append(f'way["{key}"="{value}"]({min_lat},{min_lon},{max_lat},{max_lon});')
                category_queries.append(f'relation["{key}"="{value}"]({min_lat},{min_lon},{max_lat},{max_lon});')
            else:
                # Fallback for categories without "="
                category_queries.append(f'node["{category}"]({min_lat},{min_lon},{max_lat},{max_lon});')
                category_queries.append(f'way["{category}"]({min_lat},{min_lon},{max_lat},{max_lon});')
                category_queries.append(f'relation["{category}"]({min_lat},{min_lon},{max_lat},{max_lon});')

        query = f"""
        [out:json][timeout:60];
        (
            {' '.join(category_queries)}
        );
        out geom;
        """

        return query

    def _get_regional_categories(self) -> List[str]:
        """Get categories relevant to the current region"""
        config = self.regions_config.get(self.region_name, {})
        return config.get("focus_categories", [
            "tourism=museum", "tourism=attraction", "historic=archaeological_site",
            "historic=monument", "amenity=restaurant", "amenity=cafe",
            "shop=mall", "leisure=park", "historic=temple", "historic=castle"
        ])

    def _extract_node_data(self, element: Dict) -> POIData:
        """Extract POI data from OSM node/way/relation element"""
        tags = element.get("tags", {})
        name = tags.get("name", "")
        name_arabic = tags.get("name:ar", "")

        if not name:
            return None

        # Get coordinates
        lat = None
        lon = None
        if "lat" in element and "lon" in element:
            lat = float(element["lat"])
            lon = float(element["lon"])
        elif "center" in element:
            lat = float(element["center"]["lat"])
            lon = float(element["center"]["lon"])

        if not lat or not lon:
            return None

        # Extract basic information
        poi_data = POIData(
            name=name,
            name_arabic=name_arabic,
            description=tags.get("description", ""),
            address=self._extract_address(tags),
            latitude=lat,
            longitude=lon,
            city=tags.get("addr:city", self.region_name),
            postal_code=tags.get("addr:postcode", ""),
            phone_number=tags.get("phone", ""),
            website_url=tags.get("website", ""),
            opening_hours=self.extract_hours_from_tags(list(tags.keys())),
            ticket_price=self._extract_price(tags),
            image_urls=[],  # OSM doesn't typically have images
            tags=list(tags.values()),
            source="OpenStreetMap",
            source_id=str(element.get("id", ""))
        )

        # Extract tourism/historic information
        if tags.get("historic") or tags.get("tourism"):
            poi_data.historical_significance = self._extract_historical_info(tags)

        # Extract ratings if available (rare in OSM but might exist)
        if tags.get("rating"):
            try:
                poi_data.average_rating = float(tags["rating"])
            except ValueError:
                pass

        # Categorize the POI
        poi_data.category = self.categorize_poi(list(tags.values()), name)

        return poi_data if self.validate_poi_data(poi_data) else None

    def _extract_address(self, tags: Dict) -> Optional[str]:
        """Extract formatted address from OSM tags"""
        address_parts = []

        if tags.get("addr:housenumber"):
            address_parts.append(tags["addr:housenumber"])

        if tags.get("addr:street"):
            address_parts.append(tags["addr:street"])

        if tags.get("addr:city"):
            address_parts.append(tags["addr:city"])

        if tags.get("addr:postcode"):
            address_parts.append(tags["addr:postcode"])

        return ", ".join(address_parts) if address_parts else None

    def _extract_price(self, tags: Dict) -> Optional[float]:
        """Extract price information from OSM tags"""
        # Look for admission fee, entrance fee, etc.
        for price_key in ["admission", "entrance_fee", "fee", "charge"]:
            if price_key in tags:
                try:
                    price_str = tags[price_key]
                    # Remove currency symbols and parse as float
                    import re
                    price_clean = re.sub(r'[^\d.]', '', price_str)
                    return float(price_clean)
                except (ValueError, AttributeError):
                    continue

        return None

    def _extract_historical_info(self, tags: Dict) -> Optional[str]:
        """Extract historical significance from tags"""
        info_parts = []

        if tags.get("historic"):
            info_parts.append(f"Historic type: {tags['historic']}")

        if tags.get("archaeological_site"):
            info_parts.append(f"Archaeological site: {tags['archaeological_site']}")

        if tags.get("building"):
            info_parts.append(f"Building type: {tags['building']}")

        if tags.get("religion"):
            info_parts.append(f"Religion: {tags['religion']}")

        if tags.get("denomination"):
            info_parts.append(f"Denomination: {tags['denomination']}")

        if tags.get("artist_name"):
            info_parts.append(f"Artist: {tags['artist_name']}")

        if tags.get("start_date"):
            info_parts.append(f"Period: {tags['start_date']}")

        return "; ".join(info_parts) if info_parts else None

    def scrape_pois(self, limit: Optional[int] = None) -> List[POIData]:
        """Scrape POIs from OpenStreetMap for the region"""
        logger.info(f"Starting OSM scraping for {self.region_name}")

        bounds = self.get_region_bounds()
        if not bounds:
            logger.error(f"No bounds found for region {self.region_name}")
            return []

        # Get regional categories
        categories = self._get_regional_categories()

        # Build and execute query
        query = self._build_overpass_query(categories, bounds)

        logger.info(f"Executing OSM query for {self.region_name}")
        response = self.make_request(
            self.overpass_url,
            method='POST',
            data=query.encode('utf-8'),
            headers={'Content-Type': 'text/plain'}
        )

        if not response:
            logger.error(f"No response from Overpass API for {self.region_name}")
            return []

        try:
            data = response.json()
            elements = data.get("elements", [])
            logger.info(f"Retrieved {len(elements)} elements from OSM for {self.region_name}")

            # Process elements and extract POI data
            pois = []
            processed_count = 0

            for element in elements:
                if limit and processed_count >= limit:
                    break

                poi = self._extract_node_data(element)
                if poi:
                    pois.append(poi)
                    processed_count += 1

                    if processed_count % 10 == 0:
                        logger.info(f"Processed {processed_count} POIs...")

            logger.info(f"Successfully extracted {len(pois)} valid POIs from {self.region_name}")
            return pois

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for {self.region_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error processing OSM response for {self.region_name}: {str(e)}")
            return []

    def get_poi_statistics(self) -> Dict[str, Any]:
        """Get statistics about POIs in the region"""
        bounds = self.get_region_bounds()
        categories = self._get_regional_categories()

        query = f"""
        [out:json][timeout:30];
        (
            node["tourism"]({bounds.get("min_lat", 0)},{bounds.get("min_lon", 0)},{bounds.get("max_lat", 0)},{bounds.get("max_lon", 0)});
            way["tourism"]({bounds.get("min_lat", 0)},{bounds.get("min_lon", 0)},{bounds.get("max_lat", 0)},{bounds.get("max_lon", 0)});
            relation["tourism"]({bounds.get("min_lat", 0)},{bounds.get("min_lon", 0)},{bounds.get("max_lat", 0)},{bounds.get("max_lon", 0)});
        );
        out count;
        """

        try:
            response = self.make_request(
                self.overpass_url,
                method='POST',
                data=query.encode('utf-8'),
                headers={'Content-Type': 'text/plain'}
            )

            if response:
                data = response.json()
                total_elements = data.get("elements", [{}])[0].get("count", 0)

                return {
                    "region": self.region_name,
                    "total_tourism_elements": total_elements,
                    "bounds": bounds,
                    "categories": len(categories)
                }

        except Exception as e:
            logger.error(f"Error getting statistics for {self.region_name}: {str(e)}")

        return {"region": self.region_name, "total_tourism_elements": 0}