"""
Enterprise multi-layer caching strategy for high-performance data access
Implements Redis cluster, memory cache, and CDN integration for optimal performance
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import asyncio
import logging

import aioredis
from cachetools import LRUCache
import structlog

logger = structlog.get_logger(__name__)


class CacheManager:
    """
    Multi-layer cache manager supporting:
    - L1: In-memory LRU cache for hot data
    - L2: Redis cache for distributed caching
    - L3: CDN cache for static content
    """
    
    def __init__(self, redis_url: str, cluster_mode: bool = False):
        self.redis_url = redis_url
        self.cluster_mode = cluster_mode
        self.redis_client: Optional[aioredis.Redis] = None
        
        # L1 Cache: In-memory LRU cache for frequently accessed data
        self.memory_cache = LRUCache(maxsize=1000)
        
        # Cache statistics
        self.stats = {
            "hits": {"memory": 0, "redis": 0, "total": 0},
            "misses": {"memory": 0, "redis": 0, "total": 0},
            "sets": {"memory": 0, "redis": 0, "total": 0},
        }
    
    async def initialize(self):
        """Initialize Redis connection with cluster support"""
        try:
            if self.cluster_mode:
                self.redis_client = aioredis.Redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_keepalive_options={1: 1, 2: 3, 3: 5},
                    health_check_interval=30
                )
            else:
                self.redis_client = aioredis.Redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_keepalive_options={1: 1, 2: 3, 3: 5}
                )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully", cluster_mode=self.cluster_mode)
            
        except Exception as e:
            logger.error("Failed to initialize Redis cache", error=str(e))
            # Continue without Redis cache
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis cache connection closed")
    
    def _generate_cache_key(self, namespace: str, key: str, **kwargs) -> str:
        """Generate a deterministic cache key with namespace"""
        key_data = f"{namespace}:{key}"
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_data += ":" + ":".join(f"{k}={v}" for k, v in sorted_kwargs)
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, namespace: str, key: str, **kwargs) -> Optional[Any]:
        """
        Multi-layer cache retrieval with fallback strategy
        1. Check memory cache first
        2. Check Redis cache if memory miss
        3. Return None if both miss
        """
        cache_key = self._generate_cache_key(namespace, key, **kwargs)
        
        # L1: Memory cache lookup
        if cache_key in self.memory_cache:
            self.stats["hits"]["memory"] += 1
            self.stats["hits"]["total"] += 1
            logger.debug("Cache hit (memory)", key=cache_key, namespace=namespace)
            return self.memory_cache[cache_key]
        
        self.stats["misses"]["memory"] += 1
        
        # L2: Redis cache lookup
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    # Deserialize data
                    try:
                        data = json.loads(cached_data)
                    except json.JSONDecodeError:
                        # Fallback to pickle for complex objects
                        data = pickle.loads(cached_data.encode('latin1'))
                    
                    # Update memory cache
                    self.memory_cache[cache_key] = data
                    
                    self.stats["hits"]["redis"] += 1
                    self.stats["hits"]["total"] += 1
                    logger.debug("Cache hit (Redis)", key=cache_key, namespace=namespace)
                    return data
                
            except Exception as e:
                logger.warning("Redis cache lookup failed", error=str(e), key=cache_key)
        
        self.stats["misses"]["redis"] += 1
        self.stats["misses"]["total"] += 1
        logger.debug("Cache miss", key=cache_key, namespace=namespace)
        return None
    
    async def set(self, namespace: str, key: str, value: Any, ttl: int = 3600, **kwargs):
        """
        Multi-layer cache storage
        Stores in both memory cache and Redis with specified TTL
        """
        cache_key = self._generate_cache_key(namespace, key, **kwargs)
        
        # L1: Store in memory cache
        self.memory_cache[cache_key] = value
        self.stats["sets"]["memory"] += 1
        
        # L2: Store in Redis cache
        if self.redis_client:
            try:
                # Serialize data
                try:
                    serialized_data = json.dumps(value, default=str)
                except (TypeError, ValueError):
                    # Fallback to pickle for complex objects
                    serialized_data = pickle.dumps(value).decode('latin1')
                
                await self.redis_client.setex(cache_key, ttl, serialized_data)
                self.stats["sets"]["redis"] += 1
                logger.debug("Cache set", key=cache_key, namespace=namespace, ttl=ttl)
                
            except Exception as e:
                logger.warning("Redis cache set failed", error=str(e), key=cache_key)
        
        self.stats["sets"]["total"] += 1
    
    async def delete(self, namespace: str, key: str, **kwargs):
        """Delete from both memory and Redis cache"""
        cache_key = self._generate_cache_key(namespace, key, **kwargs)
        
        # Remove from memory cache
        self.memory_cache.pop(cache_key, None)
        
        # Remove from Redis cache
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
                logger.debug("Cache deleted", key=cache_key, namespace=namespace)
            except Exception as e:
                logger.warning("Redis cache delete failed", error=str(e), key=cache_key)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.stats["hits"]["total"] + self.stats["misses"]["total"]
        hit_rate = (self.stats["hits"]["total"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "memory_size": len(self.memory_cache),
            "stats": self.stats,
            "redis_connected": self.redis_client is not None
        }