"""
Base Scraper Class
Common functionality for all POI scrapers
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import requests
from ratelimit import limits, sleep_and_retry

logger = logging.getLogger(__name__)

class POICategory(Enum):
    HISTORICAL = "historical"
    CULTURAL = "cultural"
    NATURAL = "natural"
    ENTERTAINMENT = "entertainment"
    RELIGIOUS = "religious"
    SHOPPING = "shopping"
    DINING = "dining"
    ACCOMMODATION = "accommodation"
    TRANSPORTATION = "transportation"
    SERVICES = "services"

@dataclass
class POIData:
    """Standardized POI data structure"""
    name: str
    name_arabic: Optional[str] = None
    description: Optional[str] = None
    description_arabic: Optional[str] = None
    category: Optional[POICategory] = None
    address: Optional[str] = None
    address_arabic: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    website_url: Optional[str] = None
    email_address: Optional[str] = None
    opening_hours: Optional[Dict] = None
    ticket_price: Optional[float] = None
    currency: str = "EGP"
    average_visit_duration: Optional[int] = None
    average_rating: Optional[float] = None
    total_reviews: Optional[int] = None
    image_urls: Optional[List[str]] = None
    historical_significance: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    source_id: Optional[str] = None

class BaseScraper(ABC):
    """Base class for all POI scrapers"""

    def __init__(self, region_name: str, region_bounds: Optional[Dict] = None):
        self.region_name = region_name
        self.region_bounds = region_bounds or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VOYO-TravelApp/1.0 (Educational Research)',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8'
        })

        # Rate limiting configuration
        self.requests_per_second = 1
        self.requests_per_minute = 30

    @sleep_and_retry(limits(calls=1, period=1))
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with rate limiting and error handling"""
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return None

    def get_region_bounds(self) -> Dict[str, float]:
        """Get geographic bounds for the region"""
        # Default bounds for major Egyptian regions
        region_bounds = {
            "Cairo": {"min_lat": 29.8, "max_lat": 30.2, "min_lon": 31.1, "max_lon": 31.5},
            "Giza": {"min_lat": 29.9, "max_lat": 30.1, "min_lon": 31.0, "max_lon": 31.3},
            "Alexandria": {"min_lat": 31.0, "max_lat": 31.3, "min_lon": 29.8, "max_lon": 30.0},
            "Luxor": {"min_lat": 25.6, "max_lat": 25.8, "min_lon": 32.5, "max_lon": 32.8},
            "Aswan": {"min_lat": 24.0, "max_lat": 24.2, "min_lon": 32.8, "max_lon": 33.0},
            "Hurghada": {"min_lat": 27.1, "max_lat": 27.3, "min_lon": 33.7, "max_lon": 33.9},
            "Marsa Alam": {"min_lat": 25.0, "max_lat": 25.2, "min_lon": 34.8, "max_lon": 35.0},
            "Sinai": {"min_lat": 27.8, "max_lat": 30.5, "min_lon": 32.8, "max_lon": 34.8}
        }

        return region_bounds.get(self.region_name, self.region_bounds)

    def categorize_poi(self, tags: List[str], name: str) -> Optional[POICategory]:
        """Categorize POI based on tags and name"""
        name_lower = name.lower()
        tags_lower = [tag.lower() for tag in tags]

        # Historical and archaeological sites
        historical_keywords = ['museum', 'temple', 'pyramid', 'tomb', 'ancient', 'monument',
                             'archaeological', 'ruins', 'historical', 'castle', 'fortress']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in historical_keywords):
            return POICategory.HISTORICAL

        # Religious sites
        religious_keywords = ['mosque', 'church', 'monastery', 'cathedral', 'synagogue',
                            'temple', 'shrine', 'religious']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in religious_keywords):
            return POICategory.RELIGIOUS

        # Cultural sites
        cultural_keywords = ['gallery', 'theater', 'cinema', 'cultural center', 'library',
                           'opera', 'arts', 'culture']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in cultural_keywords):
            return POICategory.CULTURAL

        # Shopping
        shopping_keywords = ['mall', 'market', 'souk', 'shop', 'store', 'bazaar',
                           'shopping', 'retail']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in shopping_keywords):
            return POICategory.SHOPPING

        # Dining
        dining_keywords = ['restaurant', 'cafe', 'café', 'food', 'dining', 'bar',
                        'bakery', 'coffee', 'tea']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in dining_keywords):
            return POICategory.DINING

        # Accommodation
        accommodation_keywords = ['hotel', 'hostel', 'guesthouse', 'resort', 'motel',
                               'lodging', 'accommodation']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in accommodation_keywords):
            return POICategory.ACCOMMODATION

        # Transportation
        transport_keywords = ['airport', 'station', 'bus', 'metro', 'taxi', 'transport',
                            'terminal', 'railway']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in transport_keywords):
            return POICategory.TRANSPORTATION

        # Natural attractions
        natural_keywords = ['beach', 'park', 'garden', 'nature', 'mountain', 'desert',
                         'sea', 'river', 'lake', 'oasis', 'island']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in natural_keywords):
            return POICategory.NATURAL

        # Entertainment
        entertainment_keywords = ['cinema', 'theater', 'club', 'entertainment', 'amusement',
                               'zoo', 'aquarium', 'park']
        if any(keyword in name_lower or keyword in ' '.join(tags_lower) for keyword in entertainment_keywords):
            return POICategory.ENTERTAINMENT

        return POICategory.SERVICES  # Default category

    def extract_hours_from_tags(self, tags: List[str]) -> Optional[Dict]:
        """Extract opening hours information from tags"""
        hours_info = {}

        # Look for opening hours tags
        for tag in tags:
            tag_lower = tag.lower()
            if 'opening_hours' in tag_lower:
                # Parse OSM opening hours format
                # Example: "Mo-Su 09:00-17:00"
                try:
                    parts = tag.split(':')
                    if len(parts) > 1:
                        hours_part = ':'.join(parts[1:]).strip()
                        hours_info['raw'] = hours_part

                        # Parse simple time ranges
                        if ' ' in hours_part and '-' in hours_part:
                            days_part, time_part = hours_part.split(' ', 1)
                            hours_info['days'] = days_part
                            if '-' in time_part:
                                start_time, end_time = time_part.split('-')
                                hours_info['open'] = start_time.strip()
                                hours_info['close'] = end_time.strip()
                except Exception as e:
                    logger.warning(f"Failed to parse opening hours tag {tag}: {str(e)}")

        return hours_info if hours_info else None

    def validate_poi_data(self, poi: POIData) -> bool:
        """Validate POI data completeness"""
        # Must have at least name and coordinates
        if not poi.name:
            return False

        if not poi.latitude or not poi.longitude:
            return False

        # Basic coordinate validation
        if not (-90 <= poi.latitude <= 90) or not (-180 <= poi.longitude <= 180):
            return False

        return True

    @abstractmethod
    def scrape_pois(self, limit: Optional[int] = None) -> List[POIData]:
        """Abstract method for scraping POIs"""
        pass

    def run_with_backoff(self, max_retries: int = 3, base_delay: float = 1.0) -> List[POIData]:
        """Run scraper with exponential backoff"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping {self.region_name} - Attempt {attempt + 1}/{max_retries}")
                pois = self.scrape_pois()

                if pois:
                    logger.info(f"Successfully scraped {len(pois)} POIs from {self.region_name}")
                    return pois

            except Exception as e:
                logger.error(f"Scraping attempt {attempt + 1} failed: {str(e)}")

                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries exceeded for {self.region_name}")
                    raise

        return []