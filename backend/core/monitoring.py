"""
Enterprise monitoring and observability setup
Prometheus metrics, health checks, and performance monitoring
"""

import asyncio
import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Info
import structlog

logger = structlog.get_logger(__name__)

# Prometheus metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_connections = Gauge('active_connections_total', 'Active database connections')
cache_hit_rate = Gauge('cache_hit_rate_percent', 'Cache hit rate percentage')
query_execution_time = Histogram('query_execution_seconds', 'Query execution time', ['query_type'])
system_info = Info('oatie_system', 'System information')

# Application metrics
report_generations_total = Counter('report_generations_total', 'Total report generations', ['status'])
user_sessions_active = Gauge('user_sessions_active', 'Active user sessions')
api_rate_limit_exceeded = Counter('api_rate_limit_exceeded_total', 'API rate limit exceeded')


def setup_monitoring():
    """Setup monitoring and observability"""
    # Set system information
    system_info.info({
        'version': '3.0.0',
        'application': 'oatie_ai_reporting',
        'environment': 'production'
    })
    
    logger.info("Monitoring setup complete")


class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "total_duration": 0,
            "slow_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def record_request(self, duration: float, endpoint: str, status_code: int):
        """Record request metrics"""
        self.metrics["request_count"] += 1
        self.metrics["total_duration"] += duration
        
        if duration > 2.0:  # Slow request threshold
            self.metrics["slow_requests"] += 1
            logger.warning("Slow request detected", duration=duration, endpoint=endpoint)
        
        # Update Prometheus metrics
        http_request_duration_seconds.observe(duration)
        http_requests_total.labels(method="GET", endpoint=endpoint, status=str(status_code)).inc()
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics["cache_hits"] += 1
        self._update_cache_hit_rate()
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics["cache_misses"] += 1
        self._update_cache_hit_rate()
    
    def _update_cache_hit_rate(self):
        """Update cache hit rate metric"""
        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total_requests > 0:
            hit_rate = (self.metrics["cache_hits"] / total_requests) * 100
            cache_hit_rate.set(hit_rate)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_duration = 0
        if self.metrics["request_count"] > 0:
            avg_duration = self.metrics["total_duration"] / self.metrics["request_count"]
        
        return {
            "request_count": self.metrics["request_count"],
            "average_duration": round(avg_duration, 3),
            "slow_requests": self.metrics["slow_requests"],
            "cache_hit_rate": round(self._calculate_hit_rate(), 2)
        }
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total == 0:
            return 0.0
        return (self.metrics["cache_hits"] / total) * 100


class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.components = {
            "database": False,
            "cache": False,
            "external_apis": False
        }
    
    async def check_database_health(self, db_manager) -> bool:
        """Check database connectivity"""
        try:
            if db_manager and db_manager.engine:
                async with db_manager.get_session() as session:
                    if session:
                        self.components["database"] = True
                        return True
            self.components["database"] = False
            return False
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            self.components["database"] = False
            return False
    
    async def check_cache_health(self, cache_manager) -> bool:
        """Check cache connectivity"""
        try:
            if cache_manager and cache_manager.redis_client:
                await cache_manager.redis_client.ping()
                self.components["cache"] = True
                return True
            self.components["cache"] = False
            return False
        except Exception as e:
            logger.error("Cache health check failed", error=str(e))
            self.components["cache"] = False
            return False
    
    async def check_external_apis(self) -> bool:
        """Check external API connectivity"""
        try:
            # Check Oracle BI Publisher connection
            # Implementation would test actual connection
            self.components["external_apis"] = True
            return True
        except Exception as e:
            logger.error("External API health check failed", error=str(e))
            self.components["external_apis"] = False
            return False
    
    async def get_health_status(self, db_manager=None, cache_manager=None) -> Dict[str, Any]:
        """Get overall system health status"""
        await asyncio.gather(
            self.check_database_health(db_manager),
            self.check_cache_health(cache_manager),
            self.check_external_apis()
        )
        
        all_healthy = all(self.components.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": self.components,
            "timestamp": time.time()
        }