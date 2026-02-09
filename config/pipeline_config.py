"""
Pipeline Configuration
Centralized configuration for the VoyO enrichment pipeline
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineConfig:
    """Configuration for VoyO enrichment pipeline"""

    # Processing
    max_workers: int = 5  # Number of parallel workers
    rate_limit_delay: float = 0.2  # Seconds between API requests

    # Caching
    enable_redis_cache: bool = True
    cache_ttl: int = 86400  # 24 hours in seconds
    cache_key_prefix: str = "voyo"

    # Retry logic
    max_retries: int = 3
    retry_delay: float = 1.0  # Seconds between retries
    retry_backoff: float = 2.0  # Exponential backoff multiplier

    # Data sources
    enable_wikipedia: bool = True
    enable_wikipedia_fallback: bool = True  # Use description if no article

    # Dead Letter Queue
    enable_dlq: bool = True
    dlq_path: str = "data/failed_pois.json"

    # Logging
    log_level: str = "INFO"
    log_file: str = "enrichment_pipeline.log"
    enable_progress_bar: bool = True

    # Database
    batch_insert_size: int = 10  # Insert in batches for performance
    enable_duplicate_check: bool = True

    # Processing limits
    processing_timeout: int = 300  # Seconds per POI (5 minutes)

    # Features
    calculate_egyptian_pricing: bool = True
    egyptian_price_multiplier: float = 0.2  # 20% of tourist price

    def __post_init__(self):
        """Validate configuration"""
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if self.max_workers > 20:
            raise ValueError("max_workers cannot exceed 20 (API limits)")
        if self.rate_limit_delay < 0.1:
            raise ValueError("rate_limit_delay must be at least 0.1 (100ms)")
        if self.cache_ttl < 60:
            raise ValueError("cache_ttl must be at least 60 seconds")


# Preset configurations
class ConfigPresets:
    """Predefined configurations for different scenarios"""

    @staticmethod
    def development() -> PipelineConfig:
        """Fast configuration for development/testing"""
        return PipelineConfig(
            max_workers=3,
            enable_redis_cache=True,
            enable_progress_bar=True,
            log_level="DEBUG"
        )

    @staticmethod
    def production() -> PipelineConfig:
        """Optimized configuration for production runs"""
        return PipelineConfig(
            max_workers=5,  # Respect API limits
            enable_redis_cache=True,
            enable_dlq=True,
            enable_progress_bar=True,
            log_level="INFO",
            batch_insert_size=20
        )

    @staticmethod
    def fast() -> PipelineConfig:
        """Maximum speed configuration (use with caution)"""
        return PipelineConfig(
            max_workers=10,
            rate_limit_delay=0.1,  # Faster but close to rate limit
            enable_redis_cache=True,
            enable_progress_bar=True,
            log_level="WARNING"
        )

    @staticmethod
    def safe() -> PipelineConfig:
        """Conservative configuration for reliability"""
        return PipelineConfig(
            max_workers=3,
            rate_limit_delay=0.5,  # Slower but safe
            enable_redis_cache=True,
            enable_dlq=True,
            max_retries=5,
            log_level="DEBUG"
        )


def load_config_from_env() -> PipelineConfig:
    """Load configuration from environment variables"""
    import os

    max_workers = int(os.getenv('PIPELINE_MAX_WORKERS', 5))

    return PipelineConfig(
        max_workers=min(max_workers, 20),  # Cap at 20
        rate_limit_delay=float(os.getenv('PIPELINE_RATE_LIMIT', 0.2)),
        enable_redis_cache=os.getenv('PIPELINE_ENABLE_CACHE', 'true').lower() == 'true',
        cache_ttl=int(os.getenv('PIPELINE_CACHE_TTL', 86400)),
        enable_wikipedia=os.getenv('PIPELINE_ENABLE_WIKIPEDIA', 'true').lower() == 'true',
        enable_dlq=os.getenv('PIPELINE_ENABLE_DLQ', 'true').lower() == 'true',
        log_level=os.getenv('PIPELINE_LOG_LEVEL', 'INFO')
    )
