"""
Performance Optimization Module for Oatie AI Platform
Monitors startup times, resource usage, scaling recommendations, and bottleneck detection
"""

import asyncio
import time
import psutil
import threading
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import json
import os
from statistics import mean, median


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    timestamp: float
    metric_name: str
    value: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class StartupProfile:
    """Service startup performance profile"""
    service_name: str
    start_time: float
    initialization_time: float
    first_request_time: float
    ready_time: float
    dependencies_loaded: List[str]
    bottlenecks: List[str]


@dataclass
class ResourceUsage:
    """System resource usage snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: float
    network_bytes_recv: float
    active_connections: int
    thread_count: int


@dataclass
class PerformanceRecommendation:
    """Performance optimization recommendation"""
    type: str  # 'scaling', 'configuration', 'resource', 'optimization'
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    action: str
    estimated_impact: str
    implementation_complexity: str


class StartupOptimizer:
    """Optimizes service startup times and tracks bottlenecks"""
    
    def __init__(self):
        self.startup_profiles = {}
        self.startup_history = deque(maxlen=100)
        self.logger = logging.getLogger(__name__)
        self.optimization_cache = {}
    
    def start_profiling(self, service_name: str) -> str:
        """Start profiling a service startup"""
        profile_id = f"{service_name}_{int(time.time())}"
        
        self.startup_profiles[profile_id] = {
            'service_name': service_name,
            'start_time': time.time(),
            'checkpoints': {},
            'dependencies': [],
            'bottlenecks': []
        }
        
        self.logger.info(f"Started profiling startup for {service_name}")
        return profile_id
    
    def add_checkpoint(self, profile_id: str, checkpoint_name: str, 
                      dependency: Optional[str] = None):
        """Add a checkpoint during startup profiling"""
        if profile_id not in self.startup_profiles:
            self.logger.warning(f"Profile {profile_id} not found")
            return
        
        profile = self.startup_profiles[profile_id]
        current_time = time.time()
        elapsed = current_time - profile['start_time']
        
        profile['checkpoints'][checkpoint_name] = {
            'timestamp': current_time,
            'elapsed': elapsed
        }
        
        if dependency:
            profile['dependencies'].append(dependency)
        
        self.logger.debug(f"Checkpoint '{checkpoint_name}' at {elapsed:.3f}s for {profile_id}")
    
    def finish_profiling(self, profile_id: str) -> StartupProfile:
        """Finish profiling and analyze performance"""
        if profile_id not in self.startup_profiles:
            raise ValueError(f"Profile {profile_id} not found")
        
        profile_data = self.startup_profiles[profile_id]
        checkpoints = profile_data['checkpoints']
        
        # Calculate key timing metrics
        start_time = profile_data['start_time']
        
        # Find key milestones
        initialization_time = checkpoints.get('initialized', {}).get('elapsed', 0)
        first_request_time = checkpoints.get('first_request', {}).get('elapsed', 0)
        ready_time = time.time() - start_time
        
        # Identify bottlenecks (checkpoints that took longer than expected)
        bottlenecks = self._identify_bottlenecks(checkpoints)
        
        startup_profile = StartupProfile(
            service_name=profile_data['service_name'],
            start_time=start_time,
            initialization_time=initialization_time,
            first_request_time=first_request_time,
            ready_time=ready_time,
            dependencies_loaded=profile_data['dependencies'],
            bottlenecks=bottlenecks
        )
        
        # Store in history
        self.startup_history.append(startup_profile)
        
        # Clean up
        del self.startup_profiles[profile_id]
        
        self.logger.info(f"Startup profiling completed for {startup_profile.service_name}: {ready_time:.3f}s")
        
        return startup_profile
    
    def _identify_bottlenecks(self, checkpoints: Dict) -> List[str]:
        """Identify startup bottlenecks based on timing"""
        bottlenecks = []
        
        # Define expected maximum times for common checkpoints
        expected_times = {
            'database_connect': 2.0,
            'cache_connect': 1.0,
            'config_load': 0.5,
            'dependencies_load': 3.0,
            'security_init': 1.0,
            'api_routes_setup': 1.0
        }
        
        for checkpoint, data in checkpoints.items():
            elapsed = data['elapsed']
            expected = expected_times.get(checkpoint, 5.0)  # Default 5s threshold
            
            if elapsed > expected:
                bottlenecks.append(f"{checkpoint}: {elapsed:.3f}s (expected <{expected}s)")
        
        return bottlenecks
    
    def get_startup_recommendations(self) -> List[PerformanceRecommendation]:
        """Get recommendations to improve startup performance"""
        recommendations = []
        
        if not self.startup_history:
            return recommendations
        
        recent_profiles = list(self.startup_history)[-10:]  # Last 10 startups
        avg_startup_time = mean([p.ready_time for p in recent_profiles])
        
        # Analyze common bottlenecks
        all_bottlenecks = []
        for profile in recent_profiles:
            all_bottlenecks.extend(profile.bottlenecks)
        
        # Count bottleneck frequency
        bottleneck_counts = defaultdict(int)
        for bottleneck in all_bottlenecks:
            bottleneck_counts[bottleneck] += 1
        
        # Generate recommendations based on analysis
        if avg_startup_time > 10.0:
            recommendations.append(PerformanceRecommendation(
                type="optimization",
                priority="high",
                title="Slow Startup Time",
                description=f"Average startup time is {avg_startup_time:.1f}s, which is above optimal threshold",
                action="Investigate dependency loading and implement lazy initialization",
                estimated_impact="50-70% startup time reduction",
                implementation_complexity="medium"
            ))
        
        # Database connection bottlenecks
        db_issues = [b for b in bottleneck_counts.keys() if 'database' in b.lower()]
        if db_issues:
            recommendations.append(PerformanceRecommendation(
                type="configuration",
                priority="medium",
                title="Database Connection Delays",
                description="Database connection is taking longer than expected",
                action="Optimize database connection pooling and check network latency",
                estimated_impact="20-30% startup time reduction",
                implementation_complexity="low"
            ))
        
        return recommendations
    
    def get_startup_stats(self) -> Dict[str, Any]:
        """Get startup performance statistics"""
        if not self.startup_history:
            return {}
        
        profiles = list(self.startup_history)
        startup_times = [p.ready_time for p in profiles]
        
        return {
            "total_startups": len(profiles),
            "average_startup_time": mean(startup_times),
            "median_startup_time": median(startup_times),
            "min_startup_time": min(startup_times),
            "max_startup_time": max(startup_times),
            "last_startup_time": profiles[-1].ready_time if profiles else 0,
            "common_bottlenecks": self._get_common_bottlenecks(profiles)
        }
    
    def _get_common_bottlenecks(self, profiles: List[StartupProfile]) -> List[Dict]:
        """Get most common bottlenecks across all startups"""
        bottleneck_counts = defaultdict(int)
        for profile in profiles:
            for bottleneck in profile.bottlenecks:
                bottleneck_counts[bottleneck] += 1
        
        # Sort by frequency and return top 5
        sorted_bottlenecks = sorted(bottleneck_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"bottleneck": bottleneck, "frequency": count, "percentage": count / len(profiles) * 100}
            for bottleneck, count in sorted_bottlenecks[:5]
        ]


class ResourceMonitor:
    """Monitors system resource usage and performance"""
    
    def __init__(self, collection_interval: int = 30):
        self.collection_interval = collection_interval
        self.resource_history = deque(maxlen=2880)  # 24 hours at 30s intervals
        self.is_monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_io_rate': 100.0,  # MB/s
            'connection_count': 1000
        }
    
    def start_monitoring(self):
        """Start continuous resource monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_disk_io = None
        last_network_io = None
        
        while self.is_monitoring:
            try:
                # Get current resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Get disk I/O
                disk_io = psutil.disk_io_counters()
                disk_read_mb = 0
                disk_write_mb = 0
                
                if last_disk_io and disk_io:
                    read_bytes = disk_io.read_bytes - last_disk_io.read_bytes
                    write_bytes = disk_io.write_bytes - last_disk_io.write_bytes
                    disk_read_mb = read_bytes / (1024 * 1024) / self.collection_interval
                    disk_write_mb = write_bytes / (1024 * 1024) / self.collection_interval
                
                last_disk_io = disk_io
                
                # Get network I/O
                network_io = psutil.net_io_counters()
                network_sent = 0
                network_recv = 0
                
                if last_network_io and network_io:
                    network_sent = (network_io.bytes_sent - last_network_io.bytes_sent) / self.collection_interval
                    network_recv = (network_io.bytes_recv - last_network_io.bytes_recv) / self.collection_interval
                
                last_network_io = network_io
                
                # Get process-specific metrics
                try:
                    process = psutil.Process()
                    active_connections = len(process.connections())
                    thread_count = process.num_threads()
                except:
                    active_connections = 0
                    thread_count = 0
                
                # Create resource usage record
                usage = ResourceUsage(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    disk_io_read_mb=disk_read_mb,
                    disk_io_write_mb=disk_write_mb,
                    network_bytes_sent=network_sent,
                    network_bytes_recv=network_recv,
                    active_connections=active_connections,
                    thread_count=thread_count
                )
                
                self.resource_history.append(usage)
                
                # Check for alerts
                self._check_resource_alerts(usage)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in resource monitoring: {e}")
                time.sleep(self.collection_interval)
    
    def _check_resource_alerts(self, usage: ResourceUsage):
        """Check if any resource usage exceeds alert thresholds"""
        alerts = []
        
        if usage.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {usage.cpu_percent:.1f}%")
        
        if usage.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {usage.memory_percent:.1f}%")
        
        total_disk_io = usage.disk_io_read_mb + usage.disk_io_write_mb
        if total_disk_io > self.alert_thresholds['disk_io_rate']:
            alerts.append(f"High disk I/O: {total_disk_io:.1f} MB/s")
        
        if usage.active_connections > self.alert_thresholds['connection_count']:
            alerts.append(f"High connection count: {usage.active_connections}")
        
        if alerts:
            for alert in alerts:
                self.logger.warning(f"Resource alert: {alert}")
    
    def get_current_usage(self) -> ResourceUsage:
        """Get current resource usage snapshot"""
        if self.resource_history:
            return self.resource_history[-1]
        
        # Return empty usage if no monitoring data
        return ResourceUsage(
            timestamp=time.time(),
            cpu_percent=0,
            memory_percent=0,
            memory_used_mb=0,
            disk_io_read_mb=0,
            disk_io_write_mb=0,
            network_bytes_sent=0,
            network_bytes_recv=0,
            active_connections=0,
            thread_count=0
        )
    
    def get_usage_trends(self, hours: int = 1) -> Dict[str, Any]:
        """Get resource usage trends over specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        recent_usage = [u for u in self.resource_history if u.timestamp >= cutoff_time]
        
        if not recent_usage:
            return {}
        
        return {
            "time_period_hours": hours,
            "data_points": len(recent_usage),
            "cpu": {
                "average": mean([u.cpu_percent for u in recent_usage]),
                "peak": max([u.cpu_percent for u in recent_usage]),
                "trend": self._calculate_trend([u.cpu_percent for u in recent_usage])
            },
            "memory": {
                "average": mean([u.memory_percent for u in recent_usage]),
                "peak": max([u.memory_percent for u in recent_usage]),
                "trend": self._calculate_trend([u.memory_percent for u in recent_usage])
            },
            "connections": {
                "average": mean([u.active_connections for u in recent_usage]),
                "peak": max([u.active_connections for u in recent_usage]),
                "trend": self._calculate_trend([u.active_connections for u in recent_usage])
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation using first and last quarters
        quarter_size = len(values) // 4
        if quarter_size == 0:
            quarter_size = 1
        
        first_quarter = mean(values[:quarter_size])
        last_quarter = mean(values[-quarter_size:])
        
        change_percent = ((last_quarter - first_quarter) / first_quarter) * 100 if first_quarter > 0 else 0
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"


class ScalingRecommendationEngine:
    """Generates automatic scaling recommendations based on performance data"""
    
    def __init__(self, resource_monitor: ResourceMonitor, startup_optimizer: StartupOptimizer):
        self.resource_monitor = resource_monitor
        self.startup_optimizer = startup_optimizer
        self.logger = logging.getLogger(__name__)
    
    def get_scaling_recommendations(self) -> List[PerformanceRecommendation]:
        """Generate scaling recommendations based on current performance data"""
        recommendations = []
        
        # Get current resource usage
        current_usage = self.resource_monitor.get_current_usage()
        trends = self.resource_monitor.get_usage_trends(hours=1)
        
        # CPU-based recommendations
        if current_usage.cpu_percent > 70 and trends.get('cpu', {}).get('trend') == 'increasing':
            recommendations.append(PerformanceRecommendation(
                type="scaling",
                priority="high",
                title="CPU Usage High - Scale Up Recommended",
                description=f"CPU usage is {current_usage.cpu_percent:.1f}% and trending upward",
                action="Increase worker processes or scale horizontally",
                estimated_impact="30-50% performance improvement",
                implementation_complexity="low"
            ))
        
        # Memory-based recommendations
        if current_usage.memory_percent > 75:
            recommendations.append(PerformanceRecommendation(
                type="scaling",
                priority="medium",
                title="Memory Usage High",
                description=f"Memory usage is {current_usage.memory_percent:.1f}%",
                action="Add more memory or optimize memory usage",
                estimated_impact="Prevent out-of-memory errors",
                implementation_complexity="medium"
            ))
        
        # Connection-based recommendations
        if current_usage.active_connections > 500:
            recommendations.append(PerformanceRecommendation(
                type="scaling",
                priority="medium",
                title="High Connection Count",
                description=f"Active connections: {current_usage.active_connections}",
                action="Implement connection pooling or add load balancer",
                estimated_impact="Improved response times",
                implementation_complexity="medium"
            ))
        
        # Startup time recommendations
        startup_stats = self.startup_optimizer.get_startup_stats()
        if startup_stats.get('average_startup_time', 0) > 15:
            recommendations.append(PerformanceRecommendation(
                type="optimization",
                priority="medium",
                title="Slow Startup Times",
                description=f"Average startup time: {startup_stats['average_startup_time']:.1f}s",
                action="Implement lazy loading and optimize initialization",
                estimated_impact="Faster deployment and recovery",
                implementation_complexity="medium"
            ))
        
        return recommendations
    
    def get_optimal_configuration(self) -> Dict[str, Any]:
        """Get optimal configuration recommendations based on current load"""
        current_usage = self.resource_monitor.get_current_usage()
        trends = self.resource_monitor.get_usage_trends(hours=2)
        
        # Calculate optimal worker count based on CPU usage
        optimal_workers = self._calculate_optimal_workers(current_usage, trends)
        
        # Calculate optimal connection pool size
        optimal_pool_size = self._calculate_optimal_pool_size(current_usage)
        
        return {
            "workers": optimal_workers,
            "database_pool_size": optimal_pool_size,
            "cache_size_mb": self._calculate_optimal_cache_size(current_usage),
            "connection_timeout": self._calculate_optimal_timeout(current_usage),
            "recommendations_basis": {
                "cpu_usage": current_usage.cpu_percent,
                "memory_usage": current_usage.memory_percent,
                "active_connections": current_usage.active_connections
            }
        }
    
    def _calculate_optimal_workers(self, usage: ResourceUsage, trends: Dict) -> int:
        """Calculate optimal number of worker processes"""
        # Base on CPU cores and current usage
        cpu_cores = psutil.cpu_count()
        
        if usage.cpu_percent < 30:
            return max(2, cpu_cores // 2)  # Low load
        elif usage.cpu_percent < 60:
            return cpu_cores  # Medium load
        else:
            return min(cpu_cores * 2, 8)  # High load, but cap at 8
    
    def _calculate_optimal_pool_size(self, usage: ResourceUsage) -> int:
        """Calculate optimal database connection pool size"""
        # Base on active connections and worker count
        base_size = max(10, usage.active_connections // 10)
        return min(base_size, 50)  # Cap at 50 connections
    
    def _calculate_optimal_cache_size(self, usage: ResourceUsage) -> int:
        """Calculate optimal cache size in MB"""
        # Use 10% of available memory for cache
        available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
        optimal_cache = int(available_memory_mb * 0.1)
        return max(64, min(optimal_cache, 512))  # Between 64MB and 512MB
    
    def _calculate_optimal_timeout(self, usage: ResourceUsage) -> int:
        """Calculate optimal connection timeout"""
        if usage.active_connections > 300:
            return 10  # Shorter timeout for high load
        else:
            return 30  # Standard timeout


# Global instances
startup_optimizer = StartupOptimizer()
resource_monitor = ResourceMonitor()
scaling_engine = ScalingRecommendationEngine(resource_monitor, startup_optimizer)