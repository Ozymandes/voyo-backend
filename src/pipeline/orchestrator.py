"""
VOYO Data Pipeline Orchestrator
Coordinates all scraping and database operations
"""

import os
import sys
import logging
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.simple_client import simple_db
from scrapers.osm_scraper import OSMScraper
from scrapers.google_places_scraper import GooglePlacesScraper
from processors.data_processor import DataProcessor
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class VOYOOrchestrator:
    """Main orchestrator for VOYO data pipeline"""

    def __init__(self):
        load_dotenv()

        # Configuration
        self.regions = [
            "Cairo", "Giza", "Alexandria", "Luxor", "Aswan",
            "Hurghada", "Marsa Alam", "Sinai"
        ]

        self.target_pois_per_region = {
            "Cairo": 20, "Giza": 15, "Alexandria": 15,
            "Luxor": 20, "Aswan": 10, "Hurghada": 10,
            "Marsa Alam": 10, "Sinai": 15
        }

        # Initialize components
        self.data_processor = DataProcessor()
        self.scrapers = {}
        self.stats = {
            "start_time": None,
            "end_time": None,
            "regions_processed": 0,
            "total_pois_scraped": 0,
            "total_pois_processed": 0,
            "total_pois_inserted": 0,
            "processing_stats": {},
            "errors": []
        }

    def initialize_scrapers(self) -> bool:
        """Initialize all scrapers"""
        try:
            logger.info("Initializing scrapers...")

            # Initialize OSM scraper for each region
            for region in self.regions:
                self.scrapers[f"{region}_osm"] = OSMScraper(region)
                logger.info(f"Initialized OSM scraper for {region}")

            # Initialize Google Places scraper (shared across regions)
            self.scrapers["google_places"] = GooglePlacesScraper("Egypt")
            logger.info("Initialized Google Places scraper")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize scrapers: {str(e)}")
            self.stats["errors"].append(f"Scraper initialization: {str(e)}")
            return False

    def scrape_region(self, region: str, use_google_places: bool = True, limit: Optional[int] = None) -> Tuple[List, Dict]:
        """Scrape POIs for a specific region"""
        logger.info(f"Starting scraping for region: {region}")
        region_stats = {
            "region": region,
            "osm_pois": 0,
            "google_enhanced": 0,
            "processed": 0,
            "inserted": 0,
            "processing_time": 0,
            "errors": []
        }

        start_time = time.time()
        all_pois = []

        try:
            # Step 1: Scrape from OpenStreetMap
            osm_scraper = self.scrapers[f"{region}_osm"]
            logger.info(f"Scraping OSM data for {region}...")

            osm_pois = osm_scraper.run_with_backoff(max_retries=3)
            region_stats["osm_pois"] = len(osm_pois)
            all_pois.extend(osm_pois)

            logger.info(f"OSM scraping complete for {region}: {len(osm_pois)} POIs")

            # Step 2: Enhance with Google Places
            if use_google_places and osm_pois:
                logger.info(f"Enhancing {region} POIs with Google Places data...")

                google_scraper = self.scrapers["google_places"]
                enhanced_pois = google_scraper.enhance_poi_data(osm_pois[:limit])
                region_stats["google_enhanced"] = len(enhanced_pois)

                # Replace with enhanced data
                all_pois = enhanced_pois + osm_pois[len(enhanced_pois):]

                logger.info(f"Google Places enhancement complete for {region}")

            # Step 3: Process and clean data
            logger.info(f"Processing {len(all_pois)} POIs for {region}...")
            processor = DataProcessor()
            processed_pois, processing_stats = processor.process_pois(all_pois, region)

            region_stats["processed"] = len(processed_pois)
            region_stats["processing_stats"] = processing_stats.__dict__
            region_stats["processing_time"] = time.time() - start_time

            logger.info(f"Data processing complete for {region}: {len(processed_pois)} valid POIs")

            # Step 4: Insert into database
            logger.info(f"Inserting POIs into database for {region}...")
            inserted_count = self._insert_pois(processed_pois, region)
            region_stats["inserted"] = inserted_count

            self.stats["total_pois_scraped"] += region_stats["osm_pois"]
            self.stats["total_pois_processed"] += region_stats["processed"]
            self.stats["total_pois_inserted"] += region_stats["inserted"]

            logger.info(f"Region {region} complete: {region_stats}")

        except Exception as e:
            error_msg = f"Error scraping {region}: {str(e)}"
            logger.error(error_msg)
            region_stats["errors"].append(error_msg)
            self.stats["errors"].append(error_msg)

        return processed_pois, region_stats

    def _insert_pois(self, pois: List, region: str) -> int:
        """Insert processed POIs into database"""
        if not pois:
            return 0

        # Get region ID
        regions = simple_db.get_regions()
        region_id = None
        for r in regions:
            if r["name"] == region:
                region_id = r["id"]
                break

        if not region_id:
            logger.error(f"Region {region} not found in database")
            return 0

        # Convert POIData to database format
        poi_data_list = []
        for poi in pois:
            poi_dict = {
                "region_id": region_id,
                "name": poi.name,
                "name_arabic": poi.name_arabic,
                "description": poi.description,
                "description_arabic": poi.description_arabic,
                "category": poi.category.value if poi.category else "services",
                "address": poi.address,
                "address_arabic": poi.address_arabic,
                "latitude": poi.latitude,
                "longitude": poi.longitude,
                "city": poi.city or region,
                "postal_code": poi.postal_code,
                "phone_number": poi.phone_number,
                "website_url": poi.website_url,
                "email_address": poi.email_address,
                "opening_hours": poi.opening_hours,
                "ticket_price": poi.ticket_price,
                "currency": poi.currency,
                "average_visit_duration": poi.average_visit_duration,
                "average_rating": poi.average_rating,
                "total_reviews": poi.total_reviews,
                "image_urls": poi.image_urls,
                "historical_significance": poi.historical_significance,
                "tags": poi.tags,
                "source": poi.source,
                "source_id": poi.source_id,
                "is_active": True,
                "is_verified": poi.source != "OpenStreetMap"  # Verify Google Places data
            }
            poi_data_list.append(poi_dict)

        # Batch insert
        inserted_pois = simple_db.batch_create_pois(poi_data_list)
        return len(inserted_pois)

    def run_full_pipeline(self, regions: Optional[List[str]] = None,
                          use_google_places: bool = True,
                          pois_per_region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Run the complete data pipeline"""
        self.stats["start_time"] = datetime.now(timezone.utc)
        logger.info("Starting VOYO full data pipeline")

        if not self.initialize_scrapers():
            return {"success": False, "error": "Failed to initialize scrapers", "stats": self.stats}

        # Use provided regions or default
        target_regions = regions or self.regions

        # Override POI targets if provided
        if pois_per_region:
            self.target_pois_per_region.update(pois_per_region)

        # Process each region
        all_region_stats = {}

        for region in target_regions:
            logger.info(f"Processing region {self.stats['regions_processed'] + 1}/{len(target_regions)}: {region}")

            # Set limit based on target
            limit = self.target_pois_per_region.get(region, 15)

            processed_pois, region_stats = self.scrape_region(
                region,
                use_google_places=use_google_places,
                limit=limit
            )

            all_region_stats[region] = region_stats
            self.stats["regions_processed"] += 1

            # Add delay between regions to be respectful to APIs
            if region != target_regions[-1]:  # Don't delay after last region
                logger.info("Waiting 2 seconds before processing next region...")
                time.sleep(2)

        self.stats["end_time"] = datetime.now(timezone.utc)

        # Generate final report
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        final_report = {
            "success": True,
            "stats": self.stats,
            "region_stats": all_region_stats,
            "duration_seconds": duration,
            "duration_minutes": duration / 60,
            "regions_completed": self.stats["regions_processed"],
            "total_regions": len(target_regions),
            "completion_rate": (self.stats["regions_processed"] / len(target_regions)) * 100,
            "pipeline_summary": {
                "total_pois_scraped": self.stats["total_pois_scraped"],
                "total_pois_processed": self.stats["total_pois_processed"],
                "total_pois_inserted": self.stats["total_pois_inserted"],
                "processing_efficiency": (self.stats["total_pois_inserted"] / max(1, self.stats["total_pois_scraped"])) * 100
            },
            "timestamp": self.stats["end_time"].isoformat()
        }

        # Add completion percentages
        completion_stats = {}
        for region, stats in all_region_stats.items():
            target = self.target_pois_per_region.get(region, 15)
            completion = (stats.get("inserted", 0) / target) * 100
            completion_stats[region] = {
                "target": target,
                "actual": stats.get("inserted", 0),
                "completion_percentage": completion
            }

        final_report["completion_stats"] = completion_stats

        logger.info(f"VOYO data pipeline completed successfully!")
        logger.info(f"Total POIs scraped: {self.stats['total_pois_scraped']}")
        logger.info(f"Total POIs inserted: {self.stats['total_pois_inserted']}")
        logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")

        return final_report

    def generate_report(self, report_data: Dict[str, Any], output_file: str = None) -> str:
        """Generate a detailed report of the scraping process"""
        report_lines = [
            "=" * 80,
            "VOYO DATA PIPELINE REPORT",
            "=" * 80,
            "",
            f"Pipeline completed at: {report_data.get('timestamp', 'Unknown')}",
            f"Duration: {report_data.get('duration_minutes', 0):.2f} minutes",
            f"Regions processed: {report_data.get('regions_completed', 0)}/{report_data.get('total_regions', 0)}",
            f"Completion rate: {report_data.get('completion_rate', 0):.1f}%",
            "",
            "SUMMARY STATISTICS:",
            "-" * 40,
        ]

        # Add pipeline summary
        pipeline_summary = report_data.get("pipeline_summary", {})
        report_lines.extend([
            f"Total POIs scraped: {pipeline_summary.get('total_pois_scraped', 0):,}",
            f"Total POIs processed: {pipeline_summary.get('total_pois_processed', 0):,}",
            f"Total POIs inserted: {pipeline_summary.get('total_pois_inserted', 0):,}",
            f"Processing efficiency: {pipeline_summary.get('processing_efficiency', 0):.1f}%",
            ""
        ])

        # Add completion statistics
        report_lines.extend([
            "REGION COMPLETION:",
            "-" * 40,
        ])

        completion_stats = report_data.get("completion_stats", {})
        for region, stats in completion_stats.items():
            report_lines.append(
                f"{region:15} | {stats['actual']:3}/{stats['target']:3} | {stats['completion_percentage']:5.1f}%"
            )

        report_lines.extend([
            "",
            "DETAILED REGION STATISTICS:",
            "-" * 40,
        ])

        region_stats = report_data.get("region_stats", {})
        for region, stats in region_stats.items():
            report_lines.extend([
                f"\n{region}:",
                f"  OSM POIs scraped: {stats.get('osm_pois', 0):,}",
                f"  Google enhanced: {stats.get('google_enhanced', 0):,}",
                f"  Processed: {stats.get('processed', 0):,}",
                f"  Inserted: {stats.get('inserted', 0):,}",
                f"  Processing time: {stats.get('processing_time', 0):.2f}s",
            ])

            if stats.get("errors"):
                report_lines.append(f"  Errors: {len(stats['errors']):,}")
                for error in stats["errors"][:3]:  # Show first 3 errors
                    report_lines.append(f"    - {error}")

        # Add errors if any
        if self.stats.get("errors"):
            report_lines.extend([
                "",
                "ERRORS:",
                "-" * 40,
            ])
            for error in self.stats["errors"]:
                report_lines.append(f"- {error}")

        report_lines.extend([
            "",
            "=" * 80
        ])

        report_text = "\n".join(report_lines)

        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                logger.info(f"Report saved to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save report to {output_file}: {str(e)}")

        return report_text

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="VOYO Data Pipeline Orchestrator")
    parser.add_argument("--regions", nargs="+", help="Specific regions to process")
    parser.add_argument("--no-google", action="store_true", help="Skip Google Places enhancement")
    parser.add_argument("--limit", type=int, help="POI limit per region")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--dry-run", action="store_true", help="Run without database insertion")

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('voyo_pipeline.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    try:
        orchestrator = VOYOOrchestrator()

        # Configure based on arguments
        pois_per_region = None
        if args.limit:
            pois_per_region = {region: args.limit for region in (args.regions or orchestrator.regions)}

        # Run pipeline
        if args.dry_run:
            logger.info("DRY RUN: Would process regions: {args.regions or orchestrator.regions}")
            logger.info(f"Google Places: {'disabled' if args.no_google else 'enabled'}")
            logger.info(f"POI limit per region: {args.limit or 'default'}")
        else:
            report = orchestrator.run_full_pipeline(
                regions=args.regions,
                use_google_places=not args.no_google,
                pois_per_region=pois_per_region
            )

            # Generate and display report
            report_text = orchestrator.generate_report(report, args.output)
            print(report_text)

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()