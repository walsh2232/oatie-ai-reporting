"""
Enterprise-grade FastAPI application for Oatie AI Reporting Platform
Optimized for 1000+ concurrent users with <2s response times
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import PlainTextResponse

from backend.api.graphql import graphql_app
from backend.api.v1 import api_router
from backend.core.cache_simple import CacheManager
from backend.core.config import get_settings
from backend.core.database import DatabaseManager
from backend.core.monitoring import setup_monitoring
from backend.core.security import SecurityManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle - startup and shutdown events"""
    settings = get_settings()

    # Initialize core services
    logger.info("Initializing Oatie AI Reporting Platform...")

    # Initialize database connections
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.initialize()
    app.state.db_manager = db_manager

    # Initialize cache manager
    cache_manager = CacheManager(settings.redis_url)
    await cache_manager.initialize()
    app.state.cache_manager = cache_manager

    # Initialize security manager
    security_manager = SecurityManager(settings)
    app.state.security_manager = security_manager

    # Initialize Oracle BI Publisher SDK if enabled
    oracle_sdk = None
    if settings.oracle_bi_enabled and settings.oracle_bi_urls:
        try:
            from backend.integrations.oracle import OracleBIPublisherSDK

            oracle_sdk = OracleBIPublisherSDK(
                server_urls=settings.oracle_bi_urls,
                username=settings.oracle_bi_username or "",
                password=settings.oracle_bi_password or "",
                encryption_key=settings.encryption_key,
                pool_size=settings.oracle_bi_pool_size,
                timeout=settings.oracle_bi_timeout,
                enable_caching=True,
                cache_ttl=settings.oracle_bi_cache_ttl,
                enable_audit=settings.oracle_bi_enable_audit,
            )

            await oracle_sdk.initialize()
            app.state.oracle_sdk = oracle_sdk

            logger.info(
                "Oracle BI Publisher SDK initialized",
                servers=len(settings.oracle_bi_urls),
                pool_size=settings.oracle_bi_pool_size,
            )

        except Exception as e:
            logger.error("Failed to initialize Oracle BI Publisher SDK", error=str(e))
            app.state.oracle_sdk = None
    else:
        app.state.oracle_sdk = None
        logger.info("Oracle BI Publisher integration disabled")

    # Setup monitoring
    setup_monitoring()

    logger.info("Platform initialization complete")

    yield

    # Cleanup
    logger.info("Shutting down platform...")

    # Shutdown Oracle SDK
    if oracle_sdk:
        await oracle_sdk.shutdown()

    await cache_manager.close()
    await db_manager.close()
    logger.info("Platform shutdown complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()

    app = FastAPI(
        title="Oatie AI Reporting Platform",
        description="Enterprise-grade Oracle BI Publisher AI Assistant",
        version="3.0.0",
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Security middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    # CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request middleware for monitoring and caching
    @app.middleware("http")
    async def monitoring_middleware(request: Request, call_next):
        start_time = asyncio.get_event_loop().time()

        # Process request through cache layer
        response = await call_next(request)

        # Record metrics
        duration = asyncio.get_event_loop().time() - start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        # Add performance headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Cache-Status"] = getattr(response, "cache_status", "MISS")

        return response

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    # Mount GraphQL endpoint
    app.mount("/graphql", graphql_app)

    # Health check endpoints
    @app.get("/health")
    async def health_check():
        """Health check endpoint for load balancers"""
        return {"status": "healthy", "version": "3.0.0"}

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return PlainTextResponse(generate_latest())

    return app


# Create application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        access_log=settings.debug,
    )
