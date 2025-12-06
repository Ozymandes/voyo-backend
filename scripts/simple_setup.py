#!/usr/bin/env python3
"""
VOYO Simple Database Setup Script
Works with current dependencies and successfully created database
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from database.simple_client import simple_db, db_client
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current Python path: {sys.path}")
    print(f"Script directory: {script_dir}")
    print(f"Src directory: {src_dir}")
    print(f"Src directory exists: {src_dir.exists()}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_database_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def show_status():
    """Show current database status"""
    logger.info("Getting current database status...")
    status = simple_db.get_database_status()

    print("\n" + "="*50)
    print("VOYO DATABASE STATUS")
    print("="*50)
    print(f"Connected: {'OK' if status.get('is_connected') else 'ERROR'}")
    print(f"Regions: {status.get('regions_count', 0)}")
    print(f"Total POIs: {status.get('total_pois', 0)}")

    if 'poi_counts_by_region' in status:
        print("\nPOIs by Region:")
        print("-" * 30)
        targets = status.get('targets_by_region', {})
        for region, count in status['poi_counts_by_region'].items():
            target = targets.get(region, 0)
            completion = (count / target * 100) if target > 0 else 0
            progress = '#' * int(completion // 10) + '-' * (10 - int(completion // 10))
            print(f"{region:12} | {count:2}/{target:2} | {progress} {completion:5.1f}%")

    print("="*50)
    return status

def add_sample_pois():
    """Add some sample POIs to test the system"""
    logger.info("Adding sample POIs...")

    # Get regions
    regions = simple_db.get_regions()
    region_map = {region['name']: region['id'] for region in regions}

    # Sample POI data for testing
    sample_pois = [
        # Cairo POIs
        {
            "region_id": region_map.get("Cairo"),
            "name": "Egyptian Museum",
            "description": "Home to an extensive collection of ancient Egyptian antiquities.",
            "category": "historical",
            "address": "Tahrir Square, Cairo",
            "latitude": 30.0478,
            "longitude": 31.2357,
            "average_rating": 4.5,
            "total_reviews": 15234,
            "ticket_price": 75.0,
            "currency": "EGP",
            "average_visit_duration": 120,
            "image_urls": ["https://example.com/egyptian_museum.jpg"],
            "is_active": True,
            "is_verified": True
        },
        {
            "region_id": region_map.get("Cairo"),
            "name": "Khan el-Khalili",
            "description": "Famous bazaar and souk in the historic center of Cairo.",
            "category": "shopping",
            "address": "Al-Azhar Street, Cairo",
            "latitude": 30.0468,
            "longitude": 31.2635,
            "average_rating": 4.3,
            "total_reviews": 8921,
            "ticket_price": 0.0,
            "currency": "EGP",
            "average_visit_duration": 90,
            "image_urls": ["https://example.com/khan_el_khalili.jpg"],
            "is_active": True,
            "is_verified": True
        },

        # Giza POIs
        {
            "region_id": region_map.get("Giza"),
            "name": "Great Pyramid of Giza",
            "description": "The largest and oldest of the three pyramids in the Giza pyramid complex.",
            "category": "historical",
            "address": "Giza Plateau, Giza",
            "latitude": 29.9792,
            "longitude": 31.1342,
            "average_rating": 4.7,
            "total_reviews": 45678,
            "ticket_price": 200.0,
            "currency": "EGP",
            "average_visit_duration": 180,
            "image_urls": ["https://example.com/great_pyramid.jpg"],
            "is_active": True,
            "is_verified": True
        },
        {
            "region_id": region_map.get("Giza"),
            "name": "Great Sphinx",
            "description": "Limestone statue of a reclining sphinx, a mythical creature.",
            "category": "historical",
            "address": "Giza Plateau, Giza",
            "latitude": 29.9753,
            "longitude": 31.1376,
            "average_rating": 4.6,
            "total_reviews": 34210,
            "ticket_price": 180.0,
            "currency": "EGP",
            "average_visit_duration": 60,
            "image_urls": ["https://example.com/sphinx.jpg"],
            "is_active": True,
            "is_verified": True
        },

        # Alexandria POIs
        {
            "region_id": region_map.get("Alexandria"),
            "name": "Bibliotheca Alexandrina",
            "description": "Modern library and cultural center commemorating the ancient Library of Alexandria.",
            "category": "cultural",
            "address": "El-Shatby, Alexandria",
            "latitude": 31.2089,
            "longitude": 29.9088,
            "average_rating": 4.4,
            "total_reviews": 12543,
            "ticket_price": 25.0,
            "currency": "EGP",
            "average_visit_duration": 90,
            "image_urls": ["https://example.com/bibliotheca.jpg"],
            "is_active": True,
            "is_verified": True
        }
    ]

    # Filter out POIs without valid region_id
    valid_pois = [poi for poi in sample_pois if poi["region_id"]]

    if not valid_pois:
        logger.error("No valid regions found for sample POIs")
        return False

    try:
        created_pois = simple_db.batch_create_pois(valid_pois)
        logger.info(f"Successfully created {len(created_pois)} sample POIs")
        return True

    except Exception as e:
        logger.error(f"Error creating sample POIs: {str(e)}")
        return False

def test_database_operations():
    """Test various database operations"""
    logger.info("Testing database operations...")

    try:
        # Test getting regions
        regions = simple_db.get_regions()
        logger.info(f"Retrieved {len(regions)} regions")

        # Test getting POIs by region
        if regions:
            first_region = regions[0]
            pois = simple_db.get_pois_by_region(first_region["id"])
            logger.info(f"Retrieved {len(pois)} POIs for region {first_region['name']}")

        # Test getting POIs by category
        historical_pois = simple_db.get_pois_by_category("historical")
        logger.info(f"Retrieved {len(historical_pois)} historical POIs")

        logger.info("All database operations test passed")
        return True

    except Exception as e:
        logger.error(f"Database operations test failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("VOYO - Simple Database Setup")
    print("=" * 60)

    # Test connection
    logger.info("Testing database connection...")
    if not db_client.test_connection():
        logger.error("Failed to connect to database")
        return False

    logger.info("Database connection successful!")

    # Show current status
    status = show_status()

    # Ask user what to do
    print("\nOptions:")
    print("1. Add sample POIs (for testing)")
    print("2. Test database operations")
    print("3. Show status only")
    print("4. Exit")

    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            logger.info("Adding sample POIs...")
            if add_sample_pois():
                print("✓ Sample POIs added successfully!")
                show_status()
            else:
                print("✗ Failed to add sample POIs")

        elif choice == "2":
            logger.info("Testing database operations...")
            if test_database_operations():
                print("✓ All database operations test passed!")
            else:
                print("✗ Database operations test failed")

        elif choice == "3":
            show_status()

        elif choice == "4":
            print("Exiting...")

        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

    logger.info("Simple database setup completed")
    return True

if __name__ == "__main__":
    main()