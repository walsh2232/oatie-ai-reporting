"""
Enterprise API v1 module with comprehensive endpoint organization
"""

from fastapi import APIRouter
from .endpoints import reports, queries, auth, users, admin, analytics, sql

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User management endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Report management endpoints  
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# Query execution endpoints
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])

# Advanced NLP to SQL endpoints
api_router.include_router(sql.router, prefix="/sql", tags=["sql-generation"])

# Analytics and monitoring endpoints
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Administrative endpoints
api_router.include_router(admin.router, prefix="/admin", tags=["administration"])