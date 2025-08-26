"""
Simplified cache manager for development environment
Provides in-memory caching without Redis dependency
"""

import asyncio
import hashlib
import json
import logging
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import structlog
from cachetools import LRUCache

logger = structlog.get_logger(__name__)


class SimpleCacheManager:
    """
    Simple in-memory cache manager for development
    """

    def __init__(self, redis_url: str = None, cluster_mode: bool = False):
        self.redis_url = redis_url
        self.cluster_mode = cluster_mode
        self.redis_pool = None

        # In-memory cache
        self.memory_cache = LRUCache(maxsize=1000)
        self.cache_ttl: Dict[str, datetime] = {}

        logger.info("SimpleCacheManager initialized for development")

    async def initialize(self):
        """Initialize cache connections - simplified for development"""
        logger.info("Cache manager initialized (development mode)")
        return True

    async def close(self):
        """Close cache connections"""
        self.memory_cache.clear()
        self.cache_ttl.clear()
        logger.info("Cache manager closed")

    def _generate_key(self, prefix: str, identifier: Union[str, Dict, List]) -> str:
        """Generate cache key with prefix and identifier hash"""
        if isinstance(identifier, (dict, list)):
            identifier_str = json.dumps(identifier, sort_keys=True)
        else:
            identifier_str = str(identifier)

        key_hash = hashlib.md5(identifier_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.cache_ttl:
            return True
        return datetime.utcnow() > self.cache_ttl[key]

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            self.memory_cache[key] = value
            self.cache_ttl[key] = datetime.utcnow() + timedelta(seconds=ttl)
            return True
        except Exception as e:
            logger.error("Error setting cache value", key=key, error=str(e))
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key in self.memory_cache and not self._is_expired(key):
                return self.memory_cache[key]
            elif key in self.memory_cache:
                # Remove expired entry
                del self.memory_cache[key]
                del self.cache_ttl[key]
            return None
        except Exception as e:
            logger.error("Error getting cache value", key=key, error=str(e))
            return None

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self.memory_cache:
                del self.memory_cache[key]
            if key in self.cache_ttl:
                del self.cache_ttl[key]
            return True
        except Exception as e:
            logger.error("Error deleting cache value", key=key, error=str(e))
            return False

    async def clear_prefix(self, prefix: str) -> bool:
        """Clear all cache entries with given prefix"""
        try:
            keys_to_delete = [
                k for k in self.memory_cache.keys() if k.startswith(prefix)
            ]
            for key in keys_to_delete:
                await self.delete(key)
            return True
        except Exception as e:
            logger.error("Error clearing cache prefix", prefix=prefix, error=str(e))
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
            "active_ttl_entries": len(self.cache_ttl),
            "redis_connected": False,  # Not using Redis in dev mode
            "cache_mode": "development_memory_only",
        }


# Create alias for compatibility
CacheManager = SimpleCacheManager
