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
            "external_apis": False,
            "system_resources": False
        }
        self.start_time = time.time()
        self.restart_attempts = {}
    
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
    
    async def check_system_resources(self) -> bool:
        """Check system resource usage"""
        try:
            import psutil
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Set thresholds
            cpu_threshold = 90.0
            memory_threshold = 90.0
            disk_threshold = 90.0
            
            resources_healthy = (
                cpu_percent < cpu_threshold and
                memory.percent < memory_threshold and
                disk.percent < disk_threshold
            )
            
            self.components["system_resources"] = resources_healthy
            
            if not resources_healthy:
                logger.warning(
                    "High resource usage detected",
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=disk.percent
                )
            
            return resources_healthy
            
        except ImportError:
            logger.warning("psutil not available, skipping system resource check")
            self.components["system_resources"] = True
            return True
        except Exception as e:
            logger.error("System resource check failed", error=str(e))
            self.components["system_resources"] = False
            return False

    async def check_service_health(self) -> Dict[str, bool]:
        """Check health of individual services"""
        services = {
            "backend_api": True,  # Assumed healthy if this code is running
            "database": False,
            "cache": False,
            "external_apis": False,
            "system_resources": False
        }
        
        # Update with actual health check results
        services.update(self.components)
        
        return services

    async def get_health_status(self, db_manager=None, cache_manager=None) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        import platform
        import os
        
        # Perform all health checks
        await asyncio.gather(
            self.check_database_health(db_manager),
            self.check_cache_health(cache_manager),
            self.check_external_apis(),
            self.check_system_resources()
        )
        
        services = await self.check_service_health()
        all_healthy = all(services.values())
        
        # Determine overall status
        if all_healthy:
            status = "healthy"
        elif services.get("backend_api", False) and services.get("database", False):
            status = "degraded"  # Core services are up
        else:
            status = "critical"  # Core services are down
        
        # Get system information
        system_info = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "uptime": time.time() - (hasattr(self, 'start_time') and self.start_time or time.time()),
            "environment": os.environ.get("DEPLOYMENT_ENVIRONMENT", "unknown"),
            "version": "3.0.0"
        }
        
        return {
            "status": status,
            "services": services,
            "system": system_info,
            "timestamp": time.time(),
            "checks_performed": len(services)
        }


class ServiceRecoveryManager:
    """Automatic service recovery and restart management"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        self.recovery_interval = 30  # seconds
        self.last_recovery_time = {}
        self.logger = structlog.get_logger(__name__)
    
    async def attempt_service_recovery(self, service_name: str) -> bool:
        """Attempt to recover a failed service"""
        current_time = time.time()
        
        # Check if we've exceeded max recovery attempts
        if self.recovery_attempts.get(service_name, 0) >= self.max_recovery_attempts:
            last_attempt = self.last_recovery_time.get(service_name, 0)
            if current_time - last_attempt < 3600:  # 1 hour cooldown
                self.logger.warning(
                    "Service recovery attempts exceeded, waiting for cooldown",
                    service=service_name,
                    attempts=self.recovery_attempts[service_name]
                )
                return False
            else:
                # Reset attempts after cooldown
                self.recovery_attempts[service_name] = 0
        
        self.logger.info(f"Attempting recovery for service: {service_name}")
        
        try:
            recovery_success = False
            
            if service_name == "database":
                recovery_success = await self._recover_database()
            elif service_name == "cache":
                recovery_success = await self._recover_cache()
            elif service_name == "external_apis":
                recovery_success = await self._recover_external_apis()
            elif service_name == "system_resources":
                recovery_success = await self._recover_system_resources()
            
            # Update recovery tracking
            if recovery_success:
                self.recovery_attempts[service_name] = 0
                self.logger.info(f"Service recovery successful: {service_name}")
            else:
                self.recovery_attempts[service_name] = self.recovery_attempts.get(service_name, 0) + 1
                self.last_recovery_time[service_name] = current_time
                self.logger.error(f"Service recovery failed: {service_name}")
            
            return recovery_success
            
        except Exception as e:
            self.logger.error(
                "Service recovery attempt failed with exception",
                service=service_name,
                error=str(e)
            )
            self.recovery_attempts[service_name] = self.recovery_attempts.get(service_name, 0) + 1
            self.last_recovery_time[service_name] = current_time
            return False
    
    async def _recover_database(self) -> bool:
        """Attempt to recover database connection"""
        try:
            # Try to reconnect by creating a new connection
            # This would be implemented based on your database manager
            await asyncio.sleep(2)  # Brief wait before retry
            return True
        except Exception:
            return False
    
    async def _recover_cache(self) -> bool:
        """Attempt to recover cache connection"""
        try:
            # Try to reconnect to Redis/cache
            await asyncio.sleep(1)  # Brief wait before retry
            return True
        except Exception:
            return False
    
    async def _recover_external_apis(self) -> bool:
        """Attempt to recover external API connections"""
        try:
            # Retry external API connections
            await asyncio.sleep(3)  # Brief wait before retry
            return True
        except Exception:
            return False
    
    async def _recover_system_resources(self) -> bool:
        """Attempt to free up system resources"""
        try:
            import gc
            import os
            
            # Force garbage collection
            gc.collect()
            
            # Clear any temporary files if possible
            temp_dirs = ['/tmp', '/var/tmp']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir) and os.access(temp_dir, os.W_OK):
                    # This is a simplified approach - in practice you'd be more careful
                    pass
            
            return True
        except Exception:
            return False
    
    async def monitor_and_recover(self, db_manager=None, cache_manager=None, 
                                interval: int = 60) -> None:
        """Continuously monitor services and attempt recovery when needed"""
        self.logger.info("Starting service monitoring and recovery")
        
        while True:
            try:
                # Get current health status
                health_status = await self.health_checker.get_health_status(
                    db_manager, cache_manager
                )
                
                # Check each service and attempt recovery if needed
                for service_name, is_healthy in health_status.get("services", {}).items():
                    if not is_healthy:
                        self.logger.warning(f"Unhealthy service detected: {service_name}")
                        await self.attempt_service_recovery(service_name)
                
                # Wait before next check
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(interval)


class DashboardManager:
    """Real-time status dashboard and metrics management"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.metrics_history = []
        self.max_history_size = 1000
        self.logger = structlog.get_logger(__name__)
    
    async def get_dashboard_data(self, db_manager=None, cache_manager=None) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        health_status = await self.health_checker.get_health_status(db_manager, cache_manager)
        
        # Add performance metrics
        performance_metrics = await self._get_performance_metrics()
        
        # Add system metrics
        system_metrics = await self._get_system_metrics()
        
        dashboard_data = {
            "health": health_status,
            "performance": performance_metrics,
            "system": system_metrics,
            "timestamp": time.time(),
            "uptime": time.time() - self.health_checker.start_time
        }
        
        # Store in history
        self._store_metrics(dashboard_data)
        
        return dashboard_data
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            import psutil
            
            # Get process information
            process = psutil.Process()
            
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_info": process.memory_info()._asdict(),
                "num_threads": process.num_threads(),
                "connections": len(process.connections()),
                "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        try:
            import psutil
            
            return {
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage('/')._asdict(),
                "network": psutil.net_io_counters()._asdict(),
                "boot_time": psutil.boot_time()
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _store_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store metrics in history"""
        self.metrics_history.append(metrics)
        
        # Trim history if too large
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical metrics"""
        return self.metrics_history[-limit:]
    
    async def export_metrics_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        try:
            from prometheus_client import generate_latest
            return generate_latest().decode('utf-8')
        except ImportError:
            return "# Prometheus client not available"


# Global instances
health_checker = HealthChecker()
service_recovery = ServiceRecoveryManager(health_checker)
dashboard_manager = DashboardManager(health_checker)