"""
VoyO Enrichment Pipeline
Enriches master attractions with Google Places data and automatically inserts into Supabase

This is the MAIN pipeline that connects everything together.
"""

import os
import sys
import logging
import time
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Import Wikipedia enricher
sys.path.insert(0, str(Path(__file__).parent))
from enrichers.wikipedia_enricher import WikipediaEnricher

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enrichment_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GooglePlacesEnricher:
    """Enriches attractions using Google Places API"""

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"

        if not self.api_key:
            logger.error("GOOGLE_PLACES_API_KEY not found in environment variables")
            raise ValueError("Google Places API key is required")

    def enrich_attraction(self, attraction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enrich a single attraction with data from Google Places API

        Returns:
            Enriched attraction data or None if not found
        """
        logger.info(f"Enriching: {attraction['name']}")

        # Debug: Log what we're searching for
        logger.info(f"Region: {attraction.get('region', 'NOT SET')}")
        logger.info(f"Search queries: {attraction.get('search_queries', [attraction['name']])}")

        # Try each search query until we find a match
        for search_query in attraction.get('search_queries', [attraction['name']]):
            # Add region to search for better results
            region = attraction.get('region', 'Egypt')
            query = f"{search_query} {region}"

            logger.info(f"Searching Google Places for: {query}")

            try:
                # Search for the place
                place_data = self._search_place(query)

                if place_data:
                    logger.info(f"Found place: {place_data.get('name')}")

                    # Get detailed information
                    details = self._get_place_details(place_data['place_id'])

                    if details:
                        logger.info(f"Retrieved details successfully")

                        # Merge with original attraction data
                        enriched = self._merge_data(attraction, place_data, details)
                        logger.info(f"Successfully enriched: {attraction['name']}")
                        return enriched
                    else:
                        logger.warning(f"Could not get details for {place_data.get('name')}")
                else:
                    logger.warning(f"No results for query: {query}")

            except Exception as e:
                logger.error(f"Error searching for '{query}': {str(e)}")
                continue

        logger.warning(f"Could not find data for: {attraction['name']}")
        return None

    def _search_place(self, query: str) -> Optional[Dict]:
        """Search for a place using Google Places Text Search"""
        url = f"{self.base_url}/textsearch/json"

        params = {
            'query': query,
            'key': self.api_key,
            'fields': 'place_id,name,formatted_address,geometry,photos,rating,types'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'OK' and data.get('results'):
                return data['results'][0]  # Return first (most relevant) result

            return None

        except Exception as e:
            logger.error(f"Google Places search error: {str(e)}")
            return None

    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a place"""
        url = f"{self.base_url}/details/json"

        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'name,formatted_address,geometry,photos,rating,reviews,opening_hours,website,formatted_phone_number,international_phone_number,price_level'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'OK':
                return data.get('result')

            return None

        except Exception as e:
            logger.error(f"Google Places details error: {str(e)}")
            return None

    def _merge_data(self, original: Dict, search_result: Dict, details: Dict) -> Dict[str, Any]:
        """Merge original attraction data with Google Places data"""

        # Extract coordinates
        geometry = details.get('geometry', search_result.get('geometry', {}))
        location = geometry.get('location', {})

        # Extract photos
        photos = details.get('photos', search_result.get('photos', []))
        photo_urls = []
        for photo in photos[:5]:  # Limit to 5 photos
            photo_reference = photo.get('photo_reference')
            if photo_reference:
                photo_urls.append(self._get_photo_url(photo_reference))

        # Extract opening hours
        opening_hours_data = details.get('opening_hours')
        opening_hours = None
        if opening_hours_data:
            opening_hours = {
                'periods': opening_hours_data.get('periods', []),
                'weekday_text': opening_hours_data.get('weekday_text', [])
            }

        # Build enriched data structure
        enriched = {
            # Original data
            'name': original['name'],
            'name_arabic': original.get('name_arabic', ''),
            'region': original.get('region', ''),
            'category': original.get('category', 'Historical'),
            'importance': original.get('importance', 'Major'),
            'description': original.get('description', ''),
            'unesco_site': original.get('UNESCO_site', False),

            # Google Places data
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'address': details.get('formatted_address', ''),
            'google_place_id': details.get('place_id', ''),
            'average_rating': details.get('rating', original.get('expected_rating', 0.0)),
            'total_reviews': len(details.get('reviews', [])),
            'image_urls': photo_urls,  # Changed from 'photo_urls' to 'image_urls' to match insert_poi()
            'opening_hours': opening_hours,
            'website_url': details.get('website', ''),
            # 'phone_number': removed from schema
            'price_level': details.get('price_level'),  # 0-4 scale

            # Metadata
            'data_sources': ['master_list', 'google_places'],
            'last_verified': datetime.now().isoformat(),
            'ticket_price_tourist': original.get('ticket_price'),  # From master list or default
            'ticket_price_egyptian': None,  # Will be calculated below

            # Search optimization
            'search_vector': f"{original['name']} {original.get('name_arabic', '')} {original.get('description', '')}"
        }

        return enriched

    def _calculate_egyptian_pricing(self, enriched: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Egyptian pricing (20% of tourist price)"""
        if enriched.get('ticket_price_tourist'):
            enriched['ticket_price_egyptian'] = round(enriched['ticket_price_tourist'] * 0.2, 2)
        else:
            # Default pricing if not specified
            enriched['ticket_price_tourist'] = 200  # Default adult tourist price
            enriched['ticket_price_egyptian'] = 40  # 20% for Egyptians
        return enriched

    def _get_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        """Generate URL for a photo"""
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"


class SupabaseInserter:
    """Inserts enriched attraction data into Supabase"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase credentials not found")
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required")

    def insert_poi(self, poi_data: Dict[str, Any]) -> bool:
        """Insert a single POI into Supabase"""
        url = f"{self.supabase_url}/rest/v1/pois"

        headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        # Map category names to match the enum (lowercase)
        category_mapping = {
            'Historical': 'historical',
            'Cultural': 'cultural',
            'Religious': 'religious',
            'Natural': 'natural',
            'Entertainment': 'entertainment',
            'Shopping': 'shopping',
            'Dining': 'dining',
            'Accommodation': 'accommodation',
            'Transportation': 'transportation',
            'Services': 'services'
        }

        original_category = poi_data.get('category', 'tourist_attraction')
        mapped_category = category_mapping.get(original_category, original_category.lower())

        # Map region names to region_id
        region_id_mapping = {
            'Cairo': 1,
            'Giza': 2,
            'Alexandria': 3,
            'Luxor': 4,
            'Aswan': 5,
            'Hurghada': 6,
            'Marsa Alam': 7,
            'Sinai': 8
        }

        region_name = poi_data.get('region', 'Egypt')
        region_id = region_id_mapping.get(region_name)

        # Build POI data with all available fields
        minimal_poi = {
            'name': poi_data.get('name'),
            'category': mapped_category,
            'description': poi_data.get('description', ''),
        }

        # Add region_id if we have a mapping
        if region_id is not None:
            minimal_poi['region_id'] = region_id

        # Add Arabic text if available
        if poi_data.get('name_arabic'):
            minimal_poi['name_arabic'] = poi_data['name_arabic']

        # Add coordinates
        if poi_data.get('latitude') is not None:
            minimal_poi['latitude'] = poi_data['latitude']
        if poi_data.get('longitude') is not None:
            minimal_poi['longitude'] = poi_data['longitude']

        # Add address
        if poi_data.get('address'):
            minimal_poi['address'] = poi_data['address']

        # Add contact info (phone_number column removed from schema)
        # if poi_data.get('phone_number'):
        #     minimal_poi['phone_number'] = poi_data['phone_number']
        if poi_data.get('website_url'):
            minimal_poi['website_url'] = poi_data['website_url']

        # Add ticket price (map from ticket_price_tourist)
        if poi_data.get('ticket_price_tourist') is not None:
            minimal_poi['ticket_price'] = poi_data['ticket_price_tourist']
            minimal_poi['currency'] = 'EGP'  # Set currency for all Egyptian attractions

        # Add ratings and popularity
        if poi_data.get('average_rating') is not None:
            minimal_poi['average_rating'] = poi_data['average_rating']
        if poi_data.get('total_reviews') is not None:
            minimal_poi['total_reviews'] = poi_data['total_reviews']

        # Add opening hours
        if poi_data.get('opening_hours'):
            minimal_poi['opening_hours'] = poi_data['opening_hours']

        # Add images (IMPORTANT: This is what you're missing!)
        image_urls = poi_data.get('image_urls', [])
        if image_urls:
            minimal_poi['image_urls'] = {'images': image_urls}  # JSONB array

        # Add video URLs if any
        video_urls = poi_data.get('video_urls', [])
        if video_urls:
            minimal_poi['video_urls'] = {'videos': video_urls}  # JSONB array

        # Add tags if any
        tags = poi_data.get('tags', [])
        if tags:
            minimal_poi['tags'] = {'tags': tags}  # JSONB array

        # Set verified flag for enriched POIs
        minimal_poi['is_verified'] = True

        # Add Wikipedia enrichment fields
        if poi_data.get('historical_significance'):
            minimal_poi['historical_significance'] = poi_data['historical_significance']
        if poi_data.get('historical_significance_arabic'):
            minimal_poi['historical_significance_arabic'] = poi_data['historical_significance_arabic']
        if poi_data.get('average_visit_duration'):
            minimal_poi['average_visit_duration'] = poi_data['average_visit_duration']
        if poi_data.get('best_visit_times'):
            minimal_poi['best_visit_times'] = poi_data['best_visit_times']

        try:
            response = requests.post(url, json=minimal_poi, headers=headers, timeout=10)
            response.raise_for_status()

            logger.info(f"Inserted into Supabase: {poi_data['name']}")
            return True

        except requests.exceptions.HTTPError as e:
            if response.status_code == 409:  # Conflict (duplicate)
                logger.warning(f"POI already exists: {poi_data['name']}")
                return False
            else:
                # Log the actual error from Supabase
                try:
                    error_data = response.json()
                    logger.error(f"Supabase error: {error_data.get('message', str(e))}")
                except:
                    logger.error(f"Failed to insert {poi_data['name']}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error inserting {poi_data['name']}: {str(e)}")
            return False

    def batch_insert(self, pois: List[Dict[str, Any]]) -> Dict[str, int]:
        """Insert multiple POIs in batch"""
        results = {
            'success': 0,
            'failed': 0,
            'duplicates': 0
        }

        for poi in pois:
            if self.insert_poi(poi):
                results['success'] += 1
            else:
                results['failed'] += 1

        return results


class VoyOEnrichmentPipeline:
    """Main pipeline: Load → Enrich → Insert"""

    def __init__(self, enable_wikipedia: bool = True):
        self.enricher = GooglePlacesEnricher()
        self.wikipedia_enricher = WikipediaEnricher() if enable_wikipedia else None
        self.inserter = SupabaseInserter()
        self.stats = {
            'total': 0,
            'enriched': 0,
            'wikipedia_enriched': 0,
            'inserted': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }

    def run(self, region: Optional[str] = None, limit: Optional[int] = None):
        """
        Run the complete enrichment pipeline

        Args:
            region: Specific region to process (None = all regions)
            limit: Maximum number of attractions to process (None = all)
        """
        self.stats['start_time'] = datetime.now()

        logger.info("="*70)
        logger.info("VOYO ENRICHMENT PIPELINE STARTED")
        logger.info("="*70)

        # Load master attractions
        try:
            import sys
            from pathlib import Path
            # Add data directory to path
            data_dir = Path(__file__).parent.parent.parent / "data"
            sys.path.insert(0, str(data_dir))
            from master_attractions_clean import MASTER_ATTRACTIONS
        except ImportError as e:
            logger.error(f"Could not import master_attractions_clean: {str(e)}")
            return

        # Get attractions to process
        attractions_to_process = []

        if region:
            attractions = MASTER_ATTRACTIONS.get(region, [])
            logger.info(f"Processing region: {region} ({len(attractions)} attractions)")
        else:
            # Process all regions
            for r, attrs in MASTER_ATTRACTIONS.items():
                for attr in attrs:
                    attr['region'] = r
                    attractions_to_process.append(attr)

            attractions = attractions_to_process
            logger.info(f"Processing ALL regions ({len(attractions)} attractions)")

        # Apply limit if specified
        if limit:
            attractions = attractions[:limit]
            logger.info(f"Limited to first {limit} attractions")

        self.stats['total'] = len(attractions)

        # Process each attraction
        for i, attraction in enumerate(attractions, 1):
            logger.info(f"\n[{i}/{len(attractions)}] Processing: {attraction['name']}")

            try:
                # Enrich with Google Places
                enriched = self.enricher.enrich_attraction(attraction)

                if enriched:
                    self.stats['enriched'] += 1

                    # Enrich with Wikipedia (if enabled)
                    if self.wikipedia_enricher:
                        logger.info(f"  -> Enriching with Wikipedia...")
                        enriched = self.wikipedia_enricher.enrich_poi(enriched)
                        if enriched.get('wikipedia_enriched'):
                            self.stats['wikipedia_enriched'] += 1

                    # Calculate Egyptian pricing
                    enriched = self.enricher._calculate_egyptian_pricing(enriched)

                    # Insert into Supabase
                    if self.inserter.insert_poi(enriched):
                        self.stats['inserted'] += 1
                    else:
                        self.stats['failed'] += 1
                else:
                    self.stats['failed'] += 1

                # Rate limiting (Google Places free tier: 10 requests/second)
                time.sleep(0.2)  # 200ms between requests = 5 requests/second

            except Exception as e:
                logger.error(f"Error processing {attraction['name']}: {str(e)}")
                self.stats['failed'] += 1

        self.stats['end_time'] = datetime.now()

        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print pipeline execution summary"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        logger.info("\n" + "="*70)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Processed:         {self.stats['total']}")
        logger.info(f"Google Enriched:         {self.stats['enriched']} ({self.stats['enriched']/self.stats['total']*100:.1f}%)")
        if self.wikipedia_enricher:
            logger.info(f"Wikipedia Enriched:      {self.stats['wikipedia_enriched']} ({self.stats['wikipedia_enriched']/self.stats['total']*100:.1f}%)")
        logger.info(f"Inserted:                {self.stats['inserted']} ({self.stats['inserted']/self.stats['total']*100:.1f}%)")
        logger.info(f"Failed:                  {self.stats['failed']} ({self.stats['failed']/self.stats['total']*100:.1f}%)")
        logger.info(f"Duration:                {duration:.1f} seconds ({duration/60:.1f} minutes)")
        logger.info("="*70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='VoyO Enrichment Pipeline')
    parser.add_argument('--region', type=str, help='Specific region to process')
    parser.add_argument('--limit', type=int, help='Limit number of attractions')
    parser.add_argument('--test', action='store_true', help='Test mode (process only 3 attractions)')

    args = parser.parse_args()

    # Create and run pipeline
    pipeline = VoyOEnrichmentPipeline()

    if args.test:
        logger.info("TEST MODE: Processing 3 attractions")
        pipeline.run(limit=3)
    elif args.region:
        pipeline.run(region=args.region)
    else:
        pipeline.run()


if __name__ == "__main__":
    main()
