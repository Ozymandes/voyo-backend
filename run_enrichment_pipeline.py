#!/usr/bin/env python3
"""
Quick test script for VoyO Enrichment Pipeline
Tests with 3 attractions to verify everything works
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "data"))

print("="*70)
print("VOYO ENRICHMENT PIPELINE - TEST MODE")
print("="*70)
print("\nThis will:")
print("1. Load 3 sample attractions from master list")
print("2. Enrich them with Google Places API")
print("3. Insert them into Supabase")
print("\nPress Ctrl+C to cancel\n")

input("Press Enter to continue...")

# Import and run pipeline
from src.pipeline.enrichment_pipeline import VoyOEnrichmentPipeline

try:
    pipeline = VoyOEnrichmentPipeline()

    print("\nStarting pipeline in TEST mode (3 attractions)...\n")
    pipeline.run(limit=3)

    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nCheck your Supabase database - you should have 3 new POIs!")
    print("\nTo run full pipeline:")
    print("  python src/pipeline/enrichment_pipeline.py")
    print("\nTo run specific region:")
    print("  python src/pipeline/enrichment_pipeline.py --region Cairo")

except KeyboardInterrupt:
    print("\n\nPipeline cancelled by user")
except Exception as e:
    print(f"\n\nError: {str(e)}")
    import traceback
    traceback.print_exc()
