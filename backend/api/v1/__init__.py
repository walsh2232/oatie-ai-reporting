"""
Enterprise API v1 module with comprehensive endpoint organization
"""

from fastapi import APIRouter
from .endpoints import reports, queries, auth, users, admin, analytics, mfa, roles, security

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Multi-Factor Authentication endpoints
api_router.include_router(mfa.router, prefix="/auth/mfa", tags=["multi-factor-authentication"])

# Role and Permission Management endpoints
api_router.include_router(roles.router, prefix="/roles", tags=["role-management"])

# Security Monitoring endpoints
api_router.include_router(security.router, prefix="/security", tags=["security-monitoring"])

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