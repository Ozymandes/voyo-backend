"""
VOYO - Database Schema Manager
Handles database schema creation and initialization
"""

import logging
from typing import List, Dict, Any
from .supabase_client import db
from .schema import Base, Region, POICategory

logger = logging.getLogger(__name__)

class SchemaManager:
    """Manages database schema creation and initial data"""

    def __init__(self):
        self.db_client = db.db

    def create_initial_regions(self) -> bool:
        """Create the 8 initial regions for VOYO"""
        regions_data = [
            {
                "name": "Cairo",
                "country": "Egypt",
                "description": "Egypt's capital and largest city, home to the Egyptian Museum, Khan el-Khalili bazaar, and countless historic sites.",
                "capital_city": "Cairo",
                "timezone": "Africa/Cairo",
                "is_active": True
            },
            {
                "name": "Giza",
                "country": "Egypt",
                "description": "Home to the Great Pyramids of Giza, the Sphinx, and the Memphis Necropolis - ancient Egypt's most famous monuments.",
                "capital_city": "Giza",
                "timezone": "Africa/Cairo",
                "is_active": True
            },
            {
                "name": "Alexandria",
                "country": "Egypt",
                "description": "Egypt's second-largest city, known for the Library of Alexandria, Mediterranean coastline, and Greco-Roman heritage.",
                "capital_city": "Alexandria",
                "timezone": "Africa/Cairo",
                "is_active": True
            },
            {
                "name": "Luxor",
                "country": "Egypt",
                "description": "Ancient Thebes, home to the Valley of the Kings, Karnak Temple, and numerous Pharaonic monuments.",
                "capital_city": "Luxor",
                "timezone": "Africa/Cairo",
                "is_active": True
            },
            {
                "name": "Aswan",
                "country": "Egypt",
                "description": "Southern city known for the Aswan Dam, Philae Temple, Abu Simbel, and Nubian culture.",
                "capital_city": "Aswan",
                "timezone": "Africa/Cairo",
                "is_active": True
            },
            {
                "name": "Hurghada",
                "country": "Egypt",
                "description": "Red Sea resort town famous for diving, snorkeling, beaches, and marine life.",
                "capital_city": "Hurghada",
                "timezone": "Africa/Cairo",
                "is_active": True
            },
            {
                "name": "Marsa Alam",
                "country": "Egypt",
                "description": "Emerging Red Sea destination known for pristine beaches, coral reefs, and luxury resorts.",
                "capital_city": "Marsa Alam",
                "timezone": "Africa/Cairo",
                "is_active": True
            },
            {
                "name": "Sinai",
                "country": "Egypt",
                "description": "Peninsula featuring Mount Sinai, Sharm el-Sheikh, Dahab, and stunning desert landscapes.",
                "capital_city": "El-Tor",
                "timezone": "Africa/Cairo",
                "is_active": True
            }
        ]

        try:
            created_regions = self.db_client.batch_insert("regions", regions_data, use_admin=True)
            logger.info(f"Created {len(created_regions)} regions")
            return len(created_regions) > 0
        except Exception as e:
            logger.error(f"Error creating regions: {str(e)}")
            return False

    def get_region_poi_targets(self) -> Dict[str, int]:
        """Get target number of POIs per region"""
        return {
            "Cairo": 20,
            "Giza": 15,
            "Alexandria": 15,
            "Luxor": 20,
            "Aswan": 10,
            "Hurghada": 10,
            "Marsa Alam": 10,
            "Sinai": 15
        }

    def get_poi_categories_by_region(self) -> Dict[str, List[str]]:
        """Get recommended POI categories for each region"""
        return {
            "Cairo": [
                POICategory.HISTORICAL.value,
                POICategory.CULTURAL.value,
                POICategory.MUSEUMS.value,
                POICategory.SHOPPING.value,
                POICategory.DINING.value
            ],
            "Giza": [
                POICategory.HISTORICAL.value,
                POICategory.ARCHAEOLOGICAL.value,
                POICategory.CULTURAL.value,
                POICategory.ENTERTAINMENT.value
            ],
            "Alexandria": [
                POICategory.HISTORICAL.value,
                POICategory.CULTURAL.value,
                POICategory.COASTAL.value,
                POICategory.MUSEUMS.value
            ],
            "Luxor": [
                POICategory.HISTORICAL.value,
                POICategory.ARCHAEOLOGICAL.value,
                POICategory.TEMPLES.value,
                POICategory.NECROPOLIS.value
            ],
            "Aswan": [
                POICategory.HISTORICAL.value,
                POICategory.TEMPLES.value,
                POICategory.NATURAL.value,
                POICategory.CULTURAL.value
            ],
            "Hurghada": [
                POICategory.NATURAL.value,
                POICategory.BEACHES.value,
                POICategory.WATER_SPORTS.value,
                POICategory.RESORTS.value
            ],
            "Marsa Alam": [
                POICategory.NATURAL.value,
                POICategory.BEACHES.value,
                POICategory.DIVING.value,
                POICategory.RESORTS.value
            ],
            "Sinai": [
                POICategory.NATURAL.value,
                POICategory.RELIGIOUS.value,
                POICategory.DIVING.value,
                POICategory.MOUNTAIN.value
            ]
        }

    def check_regions_exist(self) -> bool:
        """Check if regions already exist in database"""
        existing_regions = db.get_regions()
        return len(existing_regions) > 0

    def initialize_database(self) -> bool:
        """Initialize the complete database schema and data"""
        try:
            logger.info("Starting database initialization...")

            # Check if already initialized
            if self.check_regions_exist():
                logger.info("Database already contains regions, skipping initialization")
                return True

            # Create regions
            if not self.create_initial_regions():
                logger.error("Failed to create initial regions")
                return False

            logger.info("Database initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return False

    def get_database_status(self) -> Dict[str, Any]:
        """Get current database status"""
        try:
            regions = db.get_regions()
            region_count = len(regions)

            # Count POIs per region
            poi_counts = {}
            total_pois = 0
            for region in regions:
                pois = db.get_pois_by_region(region["id"])
                poi_counts[region["name"]] = len(pois)
                total_pois += len(pois)

            targets = self.get_region_poi_targets()

            return {
                "is_connected": self.db_client.test_connection(),
                "regions_count": region_count,
                "total_pois": total_pois,
                "poi_counts_by_region": poi_counts,
                "targets_by_region": targets,
                "completion_percentage": {
                    region: min(100, (poi_counts.get(region, 0) / targets[region]) * 100)
                    for region in targets.keys()
                }
            }

        except Exception as e:
            logger.error(f"Error getting database status: {str(e)}")
            return {
                "is_connected": False,
                "error": str(e)
            }

    def reset_database(self) -> bool:
        """Reset all data (use with caution!)"""
        try:
            logger.warning("Resetting database - this will delete all data")

            # Delete in correct order to respect foreign key constraints
            tables_to_clear = [
                "special_deals",
                "accessibility_info",
                "translation_support",
                "user_ratings",
                "recommendations",
                "saved_items",
                "travel_plans",
                "pois",
                "user_preferences",
                "users",
                "regions"
            ]

            for table in tables_to_clear:
                try:
                    # Use admin client to bypass RLS if needed
                    response = self.db_client.admin_client.table(table).delete().neq("id", -1).execute()
                    logger.info(f"Cleared table {table}")
                except Exception as e:
                    logger.warning(f"Could not clear table {table}: {str(e)}")

            # Re-initialize regions
            return self.initialize_database()

        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")
            return False

# Global schema manager instance
schema_manager = SchemaManager()