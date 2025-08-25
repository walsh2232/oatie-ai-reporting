"""
Enterprise API v1 module with comprehensive endpoint organization
"""

from fastapi import APIRouter
from .endpoints import reports, queries, auth, users, admin, analytics, oracle

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User management endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Report management endpoints  
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# Query execution endpoints
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])

# Analytics and monitoring endpoints
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Administrative endpoints
api_router.include_router(admin.router, prefix="/admin", tags=["administration"])

# Oracle BI Publisher integration endpoints
api_router.include_router(oracle.router, prefix="/oracle", tags=["oracle-bi-publisher"])