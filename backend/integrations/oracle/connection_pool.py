"""
Oracle BI Publisher connection pool manager for enterprise performance optimization
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from contextlib import asynccontextmanager

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a single Oracle BI Publisher connection"""
    connection_id: str
    server_url: str
    created_at: float
    last_used: float
    in_use: bool = False
    username: Optional[str] = None
    session_id: Optional[str] = None
    request_count: int = 0


class OracleConnectionPool:
    """
    Enterprise-grade Oracle BI Publisher connection pool manager
    
    Features:
    - Configurable pool size and timeout settings
    - Connection health monitoring and auto-recovery
    - Round-robin load balancing across Oracle BI Publisher instances
    - Connection reuse and lifecycle management
    - Performance metrics and monitoring
    """
    
    def __init__(
        self,
        server_urls: List[str],
        pool_size: int = 50,
        max_connections: int = 100,
        connection_timeout: int = 30,
        idle_timeout: int = 300,  # 5 minutes
        health_check_interval: int = 60  # 1 minute
    ):
        self.server_urls = server_urls
        self.pool_size = pool_size
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval
        
        # Connection pools per server
        self.pools: Dict[str, List[ConnectionInfo]] = {}
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.server_health: Dict[str, bool] = {}
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "pool_utilization": 0.0,
            "connection_timeouts": 0,
            "health_check_failures": 0
        }
        
        # Initialize pools
        for server_url in server_urls:
            self.pools[server_url] = []
            self.server_health[server_url] = True
        
        # Start background tasks
        self._health_check_task = None
        self._cleanup_task = None
        self._running = False
    
    async def initialize(self):
        """Initialize the connection pool and start background tasks"""
        self._running = True
        
        # Pre-populate connection pools
        for server_url in self.server_urls:
            await self._populate_pool(server_url)
        
        # Start background tasks
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info(
            "Oracle connection pool initialized",
            servers=len(self.server_urls),
            pool_size=self.pool_size,
            max_connections=self.max_connections
        )
    
    async def shutdown(self):
        """Shutdown the connection pool and cleanup resources"""
        self._running = False
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Close all connections
        for server_url in self.pools:
            for connection in self.pools[server_url]:
                await self._close_connection(connection)
            self.pools[server_url].clear()
        
        self.active_connections.clear()
        
        logger.info("Oracle connection pool shutdown complete")
    
    @asynccontextmanager
    async def get_connection(self, preferred_server: Optional[str] = None):
        """
        Get a connection from the pool using context manager
        
        Args:
            preferred_server: Preferred Oracle BI Publisher server URL
            
        Yields:
            ConnectionInfo: Available connection from the pool
        """
        connection = None
        start_time = time.time()
        
        try:
            # Get connection from pool
            connection = await self._acquire_connection(preferred_server)
            
            if connection:
                connection.in_use = True
                connection.last_used = time.time()
                self.active_connections[connection.connection_id] = connection
                
                logger.debug(
                    "Connection acquired",
                    connection_id=connection.connection_id,
                    server_url=connection.server_url
                )
                
                yield connection
                
        finally:
            # Return connection to pool
            if connection:
                await self._release_connection(connection)
                
                # Update metrics
                request_time = time.time() - start_time
                self.metrics["total_requests"] += 1
                self.metrics["successful_requests"] += 1
                
                # Update average response time
                current_avg = self.metrics["average_response_time"]
                total_requests = self.metrics["total_requests"]
                self.metrics["average_response_time"] = (
                    (current_avg * (total_requests - 1) + request_time) / total_requests
                )
    
    async def _acquire_connection(self, preferred_server: Optional[str] = None) -> Optional[ConnectionInfo]:
        """Acquire a connection from the pool"""
        # Try preferred server first
        if preferred_server and preferred_server in self.pools:
            if self.server_health.get(preferred_server, False):
                connection = await self._get_connection_from_pool(preferred_server)
                if connection:
                    return connection
        
        # Round-robin through healthy servers
        for server_url in self.server_urls:
            if self.server_health.get(server_url, False):
                connection = await self._get_connection_from_pool(server_url)
                if connection:
                    return connection
        
        # No healthy servers available
        logger.error("No healthy Oracle BI Publisher servers available")
        self.metrics["failed_requests"] += 1
        return None
    
    async def _get_connection_from_pool(self, server_url: str) -> Optional[ConnectionInfo]:
        """Get an available connection from a specific server pool"""
        pool = self.pools[server_url]
        
        # Find available connection
        for connection in pool:
            if not connection.in_use:
                # Check if connection is still valid
                if await self._validate_connection(connection):
                    return connection
                else:
                    # Remove invalid connection
                    pool.remove(connection)
        
        # Create new connection if pool not at capacity
        if len(pool) < self.pool_size:
            connection = await self._create_connection(server_url)
            if connection:
                pool.append(connection)
                return connection
        
        return None
    
    async def _create_connection(self, server_url: str) -> Optional[ConnectionInfo]:
        """Create a new Oracle BI Publisher connection"""
        try:
            connection_id = f"oracle_conn_{int(time.time() * 1000)}"
            
            # In a real implementation, this would establish an actual Oracle BI Publisher connection
            # For now, we'll simulate the connection creation
            await asyncio.sleep(0.1)  # Simulate connection establishment time
            
            connection = ConnectionInfo(
                connection_id=connection_id,
                server_url=server_url,
                created_at=time.time(),
                last_used=time.time()
            )
            
            logger.debug(
                "New Oracle connection created",
                connection_id=connection_id,
                server_url=server_url
            )
            
            return connection
            
        except Exception as e:
            logger.error(
                "Failed to create Oracle connection",
                server_url=server_url,
                error=str(e)
            )
            return None
    
    async def _validate_connection(self, connection: ConnectionInfo) -> bool:
        """Validate that a connection is still healthy"""
        try:
            # Check if connection has been idle too long
            if time.time() - connection.last_used > self.idle_timeout:
                return False
            
            # In a real implementation, this would ping the Oracle BI Publisher server
            # For now, we'll simulate a health check
            await asyncio.sleep(0.01)
            
            return True
            
        except Exception as e:
            logger.warning(
                "Connection validation failed",
                connection_id=connection.connection_id,
                error=str(e)
            )
            return False
    
    async def _release_connection(self, connection: ConnectionInfo):
        """Release a connection back to the pool"""
        connection.in_use = False
        connection.last_used = time.time()
        connection.request_count += 1
        
        # Remove from active connections
        if connection.connection_id in self.active_connections:
            del self.active_connections[connection.connection_id]
        
        logger.debug(
            "Connection released",
            connection_id=connection.connection_id,
            server_url=connection.server_url,
            request_count=connection.request_count
        )
    
    async def _close_connection(self, connection: ConnectionInfo):
        """Close and cleanup a connection"""
        try:
            # In a real implementation, this would properly close the Oracle BI Publisher connection
            logger.debug(
                "Connection closed",
                connection_id=connection.connection_id,
                server_url=connection.server_url
            )
        except Exception as e:
            logger.error(
                "Error closing connection",
                connection_id=connection.connection_id,
                error=str(e)
            )
    
    async def _populate_pool(self, server_url: str):
        """Pre-populate a server's connection pool"""
        pool = self.pools[server_url]
        target_size = min(self.pool_size // len(self.server_urls), 10)  # Distribute evenly
        
        for _ in range(target_size):
            connection = await self._create_connection(server_url)
            if connection:
                pool.append(connection)
    
    async def _health_check_loop(self):
        """Background task to monitor server health"""
        while self._running:
            try:
                for server_url in self.server_urls:
                    is_healthy = await self._check_server_health(server_url)
                    self.server_health[server_url] = is_healthy
                    
                    if not is_healthy:
                        self.metrics["health_check_failures"] += 1
                
                # Update pool utilization metric
                total_connections = sum(len(pool) for pool in self.pools.values())
                active_connections = len(self.active_connections)
                self.metrics["pool_utilization"] = (
                    active_connections / max(total_connections, 1) * 100
                )
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(5)
    
    async def _check_server_health(self, server_url: str) -> bool:
        """Check if a specific Oracle BI Publisher server is healthy"""
        try:
            # In a real implementation, this would make a health check request to Oracle BI Publisher
            # For now, we'll simulate a health check
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.warning(
                "Server health check failed",
                server_url=server_url,
                error=str(e)
            )
            return False
    
    async def _cleanup_loop(self):
        """Background task to cleanup idle connections"""
        while self._running:
            try:
                current_time = time.time()
                
                for server_url, pool in self.pools.items():
                    # Remove idle connections
                    connections_to_remove = []
                    for connection in pool:
                        if (not connection.in_use and 
                            current_time - connection.last_used > self.idle_timeout):
                            connections_to_remove.append(connection)
                    
                    for connection in connections_to_remove:
                        pool.remove(connection)
                        await self._close_connection(connection)
                
                await asyncio.sleep(60)  # Cleanup every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Cleanup loop error", error=str(e))
                await asyncio.sleep(5)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current connection pool metrics"""
        total_connections = sum(len(pool) for pool in self.pools.values())
        active_connections = len(self.active_connections)
        
        return {
            **self.metrics,
            "total_connections": total_connections,
            "active_connections": active_connections,
            "servers": len(self.server_urls),
            "healthy_servers": sum(1 for healthy in self.server_health.values() if healthy),
            "pool_distribution": {
                url: len(pool) for url, pool in self.pools.items()
            }
        }