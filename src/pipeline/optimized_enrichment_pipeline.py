"""
Optimized VoyO Enrichment Pipeline
With Redis caching, parallel processing, and error recovery
"""

import os
import sys
import logging
import time
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dotenv import load_dotenv
from config.pipeline_config import PipelineConfig, ConfigPresets
from cache.redis_cache import get_cache
from utils.dead_letter_queue import DeadLetterQueue

# Import enrichers
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


class OptimizedGooglePlacesEnricher:
    """Google Places enricher with Redis caching"""

    def __init__(self, config: PipelineConfig):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.config = config
        self.cache = get_cache() if config.enable_redis_cache else None

        if not self.api_key:
            logger.error("GOOGLE_PLACES_API_KEY not found")
            raise ValueError("Google Places API key is required")

    def enrich_attraction(self, attraction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enrich attraction with caching"""
        name = attraction['name']
        logger.info(f"Enriching: {name}")

        # Try each search query
        for search_query in attraction.get('search_queries', [attraction['name']]):
            region = attraction.get('region', 'Egypt')
            query = f"{search_query} {region}"

            # Check cache first
            cache_key = self.cache.generate_key("google_places", query) if self.cache else None

            if cache_key:
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"Cache HIT: {query}")
                    # Merge cached data with original attraction
                    return self._merge_data(attraction, cached_result, cached_result)

            # Cache miss - call API
            logger.info(f"Searching Google Places for: {query}")

            try:
                place_data = self._search_place(query)

                if place_data:
                    details = self._get_place_details(place_data['place_id'])

                    if details:
                        # Cache the result
                        if cache_key:
                            result_to_cache = {**place_data, **details}
                            self.cache.set(cache_key, result_to_cache, self.config.cache_ttl)
                            logger.info(f"Cached: {query}")

                        # Merge and return
                        enriched = self._merge_data(attraction, place_data, details)
                        logger.info(f"Successfully enriched: {name}")
                        return enriched

            except Exception as e:
                logger.error(f"Error searching for '{query}': {str(e)}")
                continue

        logger.warning(f"Could not find data for: {name}")
        return None

    def _search_place(self, query: str) -> Optional[Dict]:
        """Search Google Places"""
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
                return data['results'][0]

            return None

        except Exception as e:
            logger.error(f"Google Places search error: {str(e)}")
            return None

    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get place details"""
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
        """Merge data from all sources"""
        geometry = details.get('geometry', search_result.get('geometry', {}))
        location = geometry.get('location', {})

        # Extract photos
        photos = details.get('photos', search_result.get('photos', []))
        photo_urls = []
        for photo in photos[:5]:
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

        enriched = {
            'name': original['name'],
            'name_arabic': original.get('name_arabic', ''),
            'region': original.get('region', ''),
            'category': original.get('category', 'Historical'),
            'importance': original.get('importance', 'Major'),
            'description': original.get('description', ''),
            'unesco_site': original.get('UNESCO_site', False),

            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'address': details.get('formatted_address', ''),
            'google_place_id': details.get('place_id', ''),
            'average_rating': details.get('rating', original.get('expected_rating', 0.0)),
            'total_reviews': len(details.get('reviews', [])),
            'image_urls': photo_urls,
            'opening_hours': opening_hours,
            'website_url': details.get('website', ''),
            'price_level': details.get('price_level'),

            'data_sources': ['master_list', 'google_places'],
            'last_verified': datetime.now().isoformat(),
            'ticket_price_tourist': original.get('ticket_price'),
            'ticket_price_egyptian': None,

            'search_vector': f"{original['name']} {original.get('name_arabic', '')} {original.get('description', '')}"
        }

        return enriched

    def _calculate_egyptian_pricing(self, enriched: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Egyptian pricing"""
        if self.config.calculate_egyptian_pricing:
            if enriched.get('ticket_price_tourist'):
                enriched['ticket_price_egyptian'] = round(
                    enriched['ticket_price_tourist'] * self.config.egyptian_price_multiplier,
                    2
                )
            else:
                enriched['ticket_price_tourist'] = 200
                enriched['ticket_price_egyptian'] = 40
        return enriched

    def _get_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        """Generate photo URL"""
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"


class OptimizedSupabaseInserter:
    """Supabase inserter with batch support"""

    def __init__(self, config: PipelineConfig):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.config = config

        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase credentials not found")
            raise ValueError("Supabase credentials are required")

    def insert_poi(self, poi_data: Dict[str, Any]) -> bool:
        """Insert single POI"""
        url = f"{self.supabase_url}/rest/v1/pois"

        headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        # Category mapping
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

        # Region ID mapping
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

        original_category = poi_data.get('category', 'tourist_attraction')
        mapped_category = category_mapping.get(original_category, original_category.lower())

        region_name = poi_data.get('region', 'Egypt')
        region_id = region_id_mapping.get(region_name)

        # Build POI data
        minimal_poi = {
            'name': poi_data.get('name'),
            'category': mapped_category,
            'description': poi_data.get('description', ''),
        }

        if region_id is not None:
            minimal_poi['region_id'] = region_id

        if poi_data.get('name_arabic'):
            minimal_poi['name_arabic'] = poi_data['name_arabic']

        if poi_data.get('latitude') is not None:
            minimal_poi['latitude'] = poi_data['latitude']
        if poi_data.get('longitude') is not None:
            minimal_poi['longitude'] = poi_data['longitude']

        if poi_data.get('address'):
            minimal_poi['address'] = poi_data['address']

        if poi_data.get('website_url'):
            minimal_poi['website_url'] = poi_data['website_url']

        if poi_data.get('ticket_price_tourist') is not None:
            minimal_poi['ticket_price'] = poi_data['ticket_price_tourist']
            minimal_poi['currency'] = 'EGP'

        if poi_data.get('average_rating') is not None:
            minimal_poi['average_rating'] = poi_data['average_rating']
        if poi_data.get('total_reviews') is not None:
            minimal_poi['total_reviews'] = poi_data['total_reviews']

        if poi_data.get('opening_hours'):
            minimal_poi['opening_hours'] = poi_data['opening_hours']

        image_urls = poi_data.get('image_urls', [])
        if image_urls:
            minimal_poi['image_urls'] = {'images': image_urls}

        video_urls = poi_data.get('video_urls', [])
        if video_urls:
            minimal_poi['video_urls'] = {'videos': video_urls}

        tags = poi_data.get('tags', [])
        if tags:
            minimal_poi['tags'] = {'tags': tags}

        minimal_poi['is_verified'] = True

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
            if response.status_code == 409:
                logger.warning(f"POI already exists: {poi_data['name']}")
                return False
            else:
                try:
                    error_data = response.json()
                    logger.error(f"Supabase error: {error_data.get('message', str(e))}")
                except:
                    logger.error(f"Failed to insert {poi_data['name']}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error inserting {poi_data['name']}: {str(e)}")
            return False


class OptimizedVoyOPipeline:
    """Optimized pipeline with parallel processing and error recovery"""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or ConfigPresets.production()
        self.enricher = OptimizedGooglePlacesEnricher(self.config)
        self.wikipedia_enricher = WikipediaEnricher() if self.config.enable_wikipedia else None
        self.inserter = OptimizedSupabaseInserter(self.config)
        self.dlq = DeadLetterQueue(self.config.dlq_path) if self.config.enable_dlq else None

        # Thread-safe stats
        self.stats = {
            'total': 0,
            'enriched': 0,
            'wikipedia_enriched': 0,
            'inserted': 0,
            'failed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'start_time': None,
            'end_time': None
        }
        self.stats_lock = threading.Lock()

    def _update_stats(self, key: str, value: int = 1):
        """Thread-safe stats update"""
        with self.stats_lock:
            self.stats[key] += value

    def process_single_attraction(self, attraction: Dict) -> Dict:
        """Process one attraction (thread-safe)"""
        result = {
            'attraction': attraction['name'],
            'success': False,
            'google_enriched': False,
            'wikipedia_enriched': False,
            'inserted': False,
            'error': None
        }

        try:
            # Enrich with Google Places
            enriched = self.enricher.enrich_attraction(attraction)

            if enriched:
                result['google_enriched'] = True
                self._update_stats('enriched')

                # Enrich with Wikipedia
                if self.wikipedia_enricher:
                    enriched = self.wikipedia_enricher.enrich_poi(enriched)
                    if enriched.get('wikipedia_enriched'):
                        result['wikipedia_enriched'] = True
                        self._update_stats('wikipedia_enriched')

                # Calculate pricing
                enriched = self.enricher._calculate_egyptian_pricing(enriched)

                # Insert to database
                if self.inserter.insert_poi(enriched):
                    result['inserted'] = True
                    result['success'] = True
                    self._update_stats('inserted')
                else:
                    result['error'] = "Database insert failed"
                    if self.dlq:
                        self.dlq.add(attraction, result['error'], 'database')
            else:
                result['error'] = "Google Places enrichment failed"
                if self.dlq:
                    self.dlq.add(attraction, result['error'], 'google_places')

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error processing {attraction['name']}: {e}")
            if self.dlq:
                self.dlq.add(attraction, str(e), 'unknown')

        if not result['success']:
            self._update_stats('failed')

        return result

    def run(self, region: Optional[str] = None, limit: Optional[int] = None):
        """Run optimized pipeline"""
        self.stats['start_time'] = datetime.now()

        logger.info("="*70)
        logger.info("OPTIMIZED VOYO ENRICHMENT PIPELINE")
        logger.info("="*70)

        # Load master attractions
        try:
            data_dir = Path(__file__).parent.parent.parent / "data"
            sys.path.insert(0, str(data_dir))
            from master_attractions_clean import MASTER_ATTRACTIONS
        except ImportError as e:
            logger.error(f"Could not import master_attractions_clean: {str(e)}")
            return

        # Get attractions to process
        if region:
            attractions = MASTER_ATTRACTIONS.get(region, [])
            logger.info(f"Processing region: {region} ({len(attractions)} attractions)")
        else:
            attractions_to_process = []
            for r, attrs in MASTER_ATTRACTIONS.items():
                for attr in attrs:
                    attr['region'] = r
                    attractions_to_process.append(attr)
            attractions = attractions_to_process
            logger.info(f"Processing ALL regions ({len(attractions)} attractions)")

        # Apply limit
        if limit:
            attractions = attractions[:limit]
            logger.info(f"Limited to first {limit} attractions")

        self.stats['total'] = len(attractions)

        # Process in parallel
        logger.info(f"Processing with {self.config.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_attraction = {
                executor.submit(self.process_single_attraction, attraction): attraction
                for attraction in attractions
            }

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_attraction):
                attraction = future_to_attraction[future]
                try:
                    result = future.result()
                    completed += 1

                    status = "[OK]" if result['success'] else "[FAIL]"
                    logger.info(f"({completed}/{len(attractions)}) {status} {result['attraction']}")

                except Exception as e:
                    logger.error(f"Failed to process {attraction['name']}: {e}")
                    self._update_stats('failed')

        self.stats['end_time'] = datetime.now()

        # Print summary
        self._print_summary()

        # Print cache stats if available
        if self.enricher.cache:
            cache_stats = self.enricher.cache.get_stats()
            if cache_stats.get('enabled'):
                logger.info(f"\nCache Statistics:")
                logger.info(f"  Total keys: {cache_stats.get('total_keys', 0)}")
                logger.info(f"  Memory used: {cache_stats.get('used_memory_mb', 0):.2f} MB")

        # Print DLQ summary if enabled
        if self.dlq:
            dlq_summary = self.dlq.get_summary()
            if dlq_summary['total_failed'] > 0:
                logger.info(f"\nDead Letter Queue:")
                logger.info(f"  Total failed: {dlq_summary['total_failed']}")
                logger.info(f"  By stage: {dlq_summary['by_stage']}")
                logger.info(f"  Report: data/failed_pois_report.txt")

    def _print_summary(self):
        """Print execution summary"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        logger.info("\n" + "="*70)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Processed:         {self.stats['total']}")
        logger.info(f"Google Enriched:         {self.stats['enriched']} ({self.stats['enriched']/max(self.stats['total'], 1)*100:.1f}%)")
        if self.wikipedia_enricher:
            logger.info(f"Wikipedia Enriched:      {self.stats['wikipedia_enriched']} ({self.stats['wikipedia_enriched']/max(self.stats['total'], 1)*100:.1f}%)")
        logger.info(f"Inserted:                {self.stats['inserted']} ({self.stats['inserted']/max(self.stats['total'], 1)*100:.1f}%)")
        logger.info(f"Failed:                  {self.stats['failed']} ({self.stats['failed']/max(self.stats['total'], 1)*100:.1f}%)")
        logger.info(f"Duration:                {duration:.1f} seconds ({duration/60:.1f} minutes)")
        logger.info(f"Avg per POI:             {duration/max(self.stats['total'], 1):.2f} seconds")
        logger.info("="*70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Optimized VoyO Enrichment Pipeline')
    parser.add_argument('--region', type=str, help='Specific region to process')
    parser.add_argument('--limit', type=int, help='Limit number of attractions')
    parser.add_argument('--test', action='store_true', help='Test mode (3 attractions)')
    parser.add_argument('--fast', action='store_true', help='Fast mode (10 workers)')
    parser.add_argument('--safe', action='store_true', help='Safe mode (3 workers)')

    args = parser.parse_args()

    # Select config preset
    if args.fast:
        config = ConfigPresets.fast()
        logger.info("Using FAST configuration")
    elif args.safe:
        config = ConfigPresets.safe()
        logger.info("Using SAFE configuration")
    else:
        config = ConfigPresets.production()
        logger.info("Using PRODUCTION configuration")

    # Create and run pipeline
    pipeline = OptimizedVoyOPipeline(config)

    if args.test:
        logger.info("TEST MODE: Processing 3 attractions")
        pipeline.run(limit=3)
    elif args.region:
        pipeline.run(region=args.region)
    else:
        pipeline.run()


if __name__ == "__main__":
    main()
