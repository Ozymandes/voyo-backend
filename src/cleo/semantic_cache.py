"""
Semantic Cache for CLEO
Redis-based caching for common questions and answers
"""

import hashlib
import json
import re
import logging
from typing import Optional, Dict, Any
from src.cleo.config import config

logger = logging.getLogger(__name__)

class SemanticCache:
    """Redis-based semantic cache for CLEO responses"""

    # Question patterns that should be cached (factual data)
    CACHEABLE_PATTERNS = [
        r"(when|open|hours)",
        r"(how much|price|ticket|cost|fee)",
        r"(where|location|address)",
        r"(phone|contact)",
        r"(website|url)",
        r"(best time|visit time)",
        r"(how long|duration)",
        r"(rating|reviews?|stars?)",
        r"(category|type|kind)"
    ]

    def __init__(self):
        """Initialize Redis connection"""
        try:
            from src.cache.redis_cache import RedisCache

            # Use existing Redis cache from pipeline
            self.redis_client = RedisCache()

            # Test connection - check if redis_client was initialized
            if self.redis_client.redis_client is not None:
                self.enabled = True
                logger.info("Semantic cache initialized (enabled=True)")
            else:
                self.enabled = False
                logger.info("Redis cache not available - running without cache")

        except Exception as e:
            logger.error(f"Failed to initialize semantic cache: {e}")
            self.redis_client = None
            self.enabled = False
            logger.info("Running without cache - performance will be slower")

    def is_cacheable(self, question: str) -> bool:
        """
        Check if a question should be cached (factual vs complex)

        Args:
            question: User's question

        Returns:
            True if cacheable, False otherwise
        """
        question_lower = question.lower()

        # Check if question matches cacheable patterns
        for pattern in self.CACHEABLE_PATTERNS:
            if re.search(pattern, question_lower):
                return True

        return False

    def get(self, question: str) -> Optional[str]:
        """
        Get cached answer if exists

        Args:
            question: User's question

        Returns:
            Cached answer or None
        """
        if not self.enabled:
            return None

        cache_key = self._generate_key(question)

        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info(f"CLEO cache HIT: {question[:50]}...")
                return cached
            else:
                logger.debug(f"CLEO cache MISS: {question[:50]}...")
                return None

        except Exception as e:
            logger.error(f"Error reading CLEO cache: {e}")
            return None

    def set(self, question: str, answer: str, ttl: int = None):
        """
        Cache answer with TTL

        Args:
            question: User's question
            answer: CLEO's response
            ttl: Time to live in seconds (default: from config)
        """
        if not self.enabled:
            return

        cache_key = self._generate_key(question)
        ttl = ttl or config.cache_ttl

        try:
            self.redis_client.set(cache_key, answer, ttl=ttl)
            logger.debug(f"Cached CLEO answer for: {question[:50]}...")

        except Exception as e:
            logger.error(f"Error writing to CLEO cache: {e}")

    def _generate_key(self, question: str) -> str:
        """
        Generate cache key from question

        Args:
            question: User's question

        Returns:
            Cache key string
        """
        # Normalize question
        normalized = question.lower().strip()
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        # Generate hash
        question_hash = hashlib.md5(normalized.encode('utf-8')).hexdigest()
        return f"cleo:question:{question_hash}"

    def clear_all(self):
        """Clear all CLEO cache entries"""
        if not self.enabled:
            return

        try:
            # This would need to be implemented in RedisCache
            # For now, just log
            logger.warning("Clear all CLEO cache - needs implementation in RedisCache")

        except Exception as e:
            logger.error(f"Error clearing CLEO cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {"enabled": False}

        try:
            # Get cache size (would need implementation in RedisCache)
            return {
                "enabled": True,
                "ttl": config.cache_ttl,
                "db": config.cache_db
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}
