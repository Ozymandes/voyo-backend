#!/usr/bin/env python3
"""
VOYO Database Setup Script
Sets up the complete Supabase database with schema and initial data
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# Add current directory to Python path
sys.path.insert(0, str(script_dir.parent))

try:
    from database.supabase_client import initialize_database
    from database.schema_manager import schema_manager
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
        logging.FileHandler('database_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_SERVICE_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please copy .env.example to .env and fill in your credentials")
        return False

    return True

def setup_database():
    """Complete database setup process"""
    logger.info("Starting VOYO database setup...")

    # Step 1: Check environment
    logger.info("Checking environment configuration...")
    if not check_environment():
        return False

    # Step 2: Test database connection
    logger.info("Testing database connection...")
    if not initialize_database():
        logger.error("Failed to connect to database")
        return False

    # Step 3: Initialize schema and data
    logger.info("Initializing database schema and initial data...")
    if not schema_manager.initialize_database():
        logger.error("Failed to initialize database schema")
        return False

    # Step 4: Show status
    logger.info("Getting database status...")
    status = schema_manager.get_database_status()

    logger.info("Database setup completed successfully!")
    logger.info("Database Status:")
    logger.info(f"  - Connected: {status.get('is_connected', False)}")
    logger.info(f"  - Regions: {status.get('regions_count', 0)}")
    logger.info(f"  - Total POIs: {status.get('total_pois', 0)}")

    if 'poi_counts_by_region' in status:
        logger.info("  - POIs by region:")
        for region, count in status['poi_counts_by_region'].items():
            target = status.get('targets_by_region', {}).get(region, 0)
            completion = status.get('completion_percentage', {}).get(region, 0)
            logger.info(f"    * {region}: {count}/{target} ({completion:.1f}%)")

    return True

def reset_database():
    """Reset the entire database (use with caution!)"""
    logger.warning("WARNING: This will delete all data from the database!")
    logger.warning("This action cannot be undone.")

    confirm = input("Are you sure you want to reset the database? (type 'RESET' to confirm): ")
    if confirm != "RESET":
        logger.info("Database reset cancelled")
        return False

    logger.info("Resetting database...")
    if schema_manager.reset_database():
        logger.info("Database reset successfully")
        return True
    else:
        logger.error("Failed to reset database")
        return False

def show_status():
    """Show current database status"""
    logger.info("Getting current database status...")
    status = schema_manager.get_database_status()

    if not status.get('is_connected'):
        logger.error("Database connection failed")
        return False

    print("\n" + "="*50)
    print("VOYO DATABASE STATUS")
    print("="*50)
    print(f"Connected: {'✅' if status.get('is_connected') else '❌'}")
    print(f"Regions: {status.get('regions_count', 0)}")
    print(f"Total POIs: {status.get('total_pois', 0)}")

    if 'poi_counts_by_region' in status:
        print("\nPOIs by Region:")
        print("-" * 30)
        for region, count in status['poi_counts_by_region'].items():
            target = status.get('targets_by_region', {}).get(region, 0)
            completion = status.get('completion_percentage', {}).get(region, 0)
            progress_bar = '█' * int(completion // 10) + '░' * (10 - int(completion // 10))
            print(f"{region:12} | {count:2}/{target:2} | {progress_bar} {completion:5.1f}%")

    print("="*50)
    return True

def main():
    """Main script entry point"""
    if len(sys.argv) < 2:
        print("Usage: python setup_database.py [setup|reset|status]")
        print("  setup  - Set up the database (default)")
        print("  reset  - Reset the entire database")
        print("  status - Show database status")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "setup":
        success = setup_database()
    elif command == "reset":
        success = reset_database()
    elif command == "status":
        success = show_status()
    else:
        logger.error(f"Unknown command: {command}")
        sys.exit(1)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()