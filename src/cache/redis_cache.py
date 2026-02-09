"""
Redis Cache Manager for VoyO Pipeline
Caches API responses to avoid redundant calls
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import timedelta
import redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache for API responses"""

    def __init__(self):
        """Initialize Redis connection"""
        try:
            # Support both REDIS_URL and separate config vars
            if os.getenv('REDIS_URL'):
                self.redis_client = redis.from_url(
                    os.getenv('REDIS_URL'),
                    decode_responses=True
                )
            else:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    password=os.getenv('REDIS_PASSWORD'),
                    db=int(os.getenv('REDIS_DB', 0)),
                    decode_responses=True
                )

            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            logger.warning("Running without cache - performance will be slower")
            self.redis_client = None

    def get(self, key: str) -> Optional[Dict]:
        """Get cached response"""
        if not self.redis_client:
            return None

        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(cached)
            else:
                logger.debug(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
            return None

    def set(self, key: str, value: Dict, ttl: int = 86400):
        """Cache response with TTL (default: 24 hours)"""
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")

    def generate_key(self, prefix: str, query: str) -> str:
        """Generate cache key from query"""
        # Hash the query to create a short, unique key
        query_hash = hashlib.md5(query.encode('utf-8')).hexdigest()
        return f"{prefix}:{query_hash}"

    def delete(self, key: str):
        """Delete specific key from cache"""
        if not self.redis_client:
            return

        try:
            self.redis_client.delete(key)
            logger.debug(f"Deleted from cache: {key}")
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")

    def clear_all(self):
        """Clear all cached data (use with caution!)"""
        if not self.redis_client:
            return

        try:
            self.redis_client.flushdb()
            logger.info("Cache cleared completely")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"enabled": False}

        try:
            info = self.redis_client.info('memory')
            db_size = self.redis_client.dbsize()

            return {
                "enabled": True,
                "total_keys": db_size,
                "used_memory_mb": info['used_memory'] / (1024 * 1024),
                "used_memory_human": info['used_memory_human']
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}


# Singleton instance
_cache_instance = None


def get_cache() -> RedisCache:
    """Get singleton cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
