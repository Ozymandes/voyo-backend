#!/usr/bin/env python3
"""
Quick runner for Optimized VoyO Pipeline
Run with Redis caching, parallel processing, and error recovery
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("="*70)
print("OPTIMIZED VOYO ENRICHMENT PIPELINE")
print("="*70)
print("\nFeatures:")
print("  - Redis caching (10x faster re-runs)")
print("  - Parallel processing (5 workers)")
print("  - Dead letter queue (no lost POIs)")
print("  - Progress tracking")
print("\nPress Ctrl+C to cancel\n")

input("Press Enter to continue...")

# Import and run
from src.pipeline.optimized_enrichment_pipeline import OptimizedVoyOPipeline, ConfigPresets

try:
    # Use production config
    config = ConfigPresets.production()
    pipeline = OptimizedVoyOPipeline(config)

    print("\nStarting pipeline...\n")
    pipeline.run()

    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70)
    print("\nCheck your Supabase database for new POIs!")
    print("\nTo run again:")
    print("  python run_optimized_pipeline.py")
    print("\nTo run specific region:")
    print("  python src/pipeline/optimized_enrichment_pipeline.py --region Cairo")
    print("\nTo run in fast mode:")
    print("  python src/pipeline/optimized_enrichment_pipeline.py --fast")

except KeyboardInterrupt:
    print("\n\nPipeline cancelled by user")
except Exception as e:
    print(f"\n\nError: {str(e)}")
    import traceback
    traceback.print_exc()
