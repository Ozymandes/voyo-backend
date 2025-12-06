#!/usr/bin/env python3
"""
VOYO Data Pipeline Runner
Main script to run the POI scraping and population pipeline
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add src directory to Python path
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from pipeline.orchestrator import VOYOOrchestrator
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voyo_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Run VOYO POI scraping and population pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline for all regions
  python run_pipeline.py

  # Run specific regions
  python run_pipeline.py --regions Cairo Giza Alexandria

  # Run with limits
  python run_pipeline.py --regions Cairo --limit 10

  # Dry run (no database insertion)
  python run_pipeline.py --dry-run --regions Cairo

  # Skip Google Places API (OSM only)
  python run_pipeline.py --no-google --regions Cairo

  # Generate report file
  python run_pipeline.py --output pipeline_report.txt
        """
    )

    parser.add_argument(
        "--regions",
        nargs="+",
        choices=["Cairo", "Giza", "Alexandria", "Luxor", "Aswan", "Hurghada", "Marsa Alam", "Sinai"],
        help="Specific regions to process (default: all regions)"
    )

    parser.add_argument(
        "--no-google",
        action="store_true",
        help="Skip Google Places API enhancement (OSM only)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum POIs to process per region (default: target amounts)"
    )

    parser.add_argument(
        "--output",
        default="voyo_pipeline_report.txt",
        help="Output report file (default: voyo_pipeline_report.txt)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline without database insertion (for testing)"
    )

    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with very small limits"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("VOYO - Egyptian POI Data Pipeline")
    print("=" * 80)
    print()

    # Display configuration
    print("Configuration:")
    print(f"  Regions: {args.regions or 'All 8 regions'}")
    print(f"  Google Places: {'Disabled' if args.no_google else 'Enabled'}")
    print(f"  POI limit per region: {args.limit or 'Target amounts'}")
    print(f"  Dry run: {'Yes' if args.dry_run else 'No'}")
    print(f"  Test mode: {'Yes' if args.test_mode else 'No'}")
    print(f"  Output report: {args.output}")
    print()

    # Adjust for test mode
    if args.test_mode:
        if not args.limit:
            args.limit = 3  # Very small limit for testing
        print("TEST MODE ENABLED - Using small limits for testing")
        print()

    # Confirm before running unless dry run
    if not args.dry_run:
        try:
            response = input("Continue with full pipeline execution? (y/N): ").lower().strip()
            if response not in ['y', 'yes']:
                print("Pipeline cancelled by user")
                return
        except KeyboardInterrupt:
            print("\nPipeline cancelled by user")
            return

    print("Starting VOYO data pipeline...")
    print("-" * 40)

    try:
        # Initialize orchestrator
        orchestrator = VOYOOrchestrator()

        # Validate database connection
        if not orchestrator.initialize_scrapers():
            print("ERROR: Failed to initialize scrapers. Check your API keys and network connection.")
            return

        # Set POI limits
        pois_per_region = None
        if args.limit:
            regions_to_process = args.regions or orchestrator.regions
            pois_per_region = {region: args.limit for region in regions_to_process}
            print(f"Processing limit: {args.limit} POIs per region")

        # Run the pipeline
        if not args.dry_run:
            print("Executing pipeline with database insertion...")
            report = orchestrator.run_full_pipeline(
                regions=args.regions,
                use_google_places=not args.no_google,
                pois_per_region=pois_per_region
            )

            # Generate and display report
            print("\n" + "=" * 80)
            print("PIPELINE EXECUTION COMPLETE")
            print("=" * 80)

            report_text = orchestrator.generate_report(report, args.output)

            # Display summary
            pipeline_summary = report.get("pipeline_summary", {})
            completion_stats = report.get("completion_stats", {})

            print(f"Total POIs scraped: {pipeline_summary.get('total_pois_scraped', 0):,}")
            print(f"Total POIs inserted: {pipeline_summary.get('total_pois_inserted', 0):,}")
            print(f"Processing efficiency: {pipeline_summary.get('processing_efficiency', 0):.1f}%")
            print(f"Duration: {report.get('duration_minutes', 0):.2f} minutes")
            print(f"Completion rate: {report.get('completion_rate', 0):.1f}%")
            print()

            print("Region Completion:")
            print("-" * 30)
            for region, stats in completion_stats.items():
                print(f"{region:12} | {stats['actual']:3}/{stats['target']:3} | {stats['completion_percentage']:5.1f}%")

            if report.get("stats", {}).get("errors"):
                print(f"\nWarnings/Errors: {len(report['stats']['errors'])}")
                for error in report["stats"]["errors"][:3]:
                    print(f"  - {error}")

            print(f"\nDetailed report saved to: {args.output}")

        else:
            print("DRY RUN MODE - No database insertion performed")
            print("Pipeline would process the following:")

            # Show what would be processed
            regions_to_show = args.regions or orchestrator.regions
            for region in regions_to_show:
                target = orchestrator.target_pois_per_region[region]
                limit = args.limit or target
                print(f"  {region}: {limit} POIs (target: {target})")

            print(f"  Google Places: {'Disabled' if args.no_google else 'Enabled'}")

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Pipeline execution failed: {str(e)}")
        logger.exception("Pipeline execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main()