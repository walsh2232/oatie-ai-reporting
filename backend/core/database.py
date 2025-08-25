"""
Enterprise database management with optimization for high-performance queries
Supports read replicas, connection pooling, and query optimization
"""

import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
import structlog

logger = structlog.get_logger(__name__)

Base = declarative_base()


class DatabaseManager:
    """Database manager with enterprise features for high-performance operations"""
    
    def __init__(self, database_url: str, read_replica_urls: Optional[List[str]] = None):
        self.database_url = database_url
        self.read_replica_urls = read_replica_urls or []
        
        # Main database engine (read/write)
        self.engine = None
        self.async_session_factory = None
        
        # Read replica engines (read-only)
        self.read_engines = []
        self.read_session_factories = []
        
        # Connection statistics
        self.stats = {
            "connections_created": 0,
            "connections_closed": 0,
            "queries_executed": 0,
            "slow_queries": 0,
            "read_replica_queries": 0
        }
    
    async def initialize(self):
        """Initialize database connections with optimized configuration"""
        try:
            # Main database engine with connection pooling
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                poolclass=QueuePool,
                pool_size=20,
                max_overflow=30,
                pool_timeout=30,
                pool_recycle=3600,  # Recycle connections every hour
                pool_pre_ping=True,  # Validate connections before use
            )
            
            # Create async session factory
            self.async_session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize read replica engines
            for i, replica_url in enumerate(self.read_replica_urls):
                read_engine = create_async_engine(
                    replica_url,
                    echo=False,
                    poolclass=QueuePool,
                    pool_size=15,
                    max_overflow=20,
                    pool_timeout=30,
                    pool_recycle=3600,
                    pool_pre_ping=True,
                )
                
                read_session_factory = async_sessionmaker(
                    bind=read_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                
                self.read_engines.append(read_engine)
                self.read_session_factories.append(read_session_factory)
            
            # Test connections
            await self._test_connections()
            
            logger.info(
                "Database initialized successfully",
                read_replicas=len(self.read_replica_urls),
                pool_size=20
            )
            
        except Exception as e:
            logger.error("Database initialization failed", error=str(e))
            # For demo purposes, continue without database
            logger.warning("Continuing without database connection")
    
    async def close(self):
        """Close all database connections"""
        if self.engine:
            await self.engine.dispose()
        
        for engine in self.read_engines:
            await engine.dispose()
        
        logger.info("Database connections closed")
    
    async def _test_connections(self):
        """Test database connections"""
        # Test main connection
        if self.async_session_factory:
            async with self.async_session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
        
        # Test read replica connections
        for i, session_factory in enumerate(self.read_session_factories):
            async with session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
                logger.debug(f"Read replica {i} connection test passed")
    
    @asynccontextmanager
    async def get_session(self, read_only: bool = False):
        """Get database session with read replica support"""
        if read_only and self.read_session_factories:
            # Use read replica for read-only queries
            import random
            session_factory = random.choice(self.read_session_factories)
            self.stats["read_replica_queries"] += 1
        else:
            # Use main database
            session_factory = self.async_session_factory
        
        if session_factory:
            async with session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
        else:
            # No session factory available; raise an error instead of yielding None
            raise RuntimeError("No session factory available. Cannot provide a database session.")