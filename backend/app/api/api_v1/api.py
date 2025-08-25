from fastapi import APIRouter

from app.api.api_v1.endpoints import reports, ai, health

api_router = APIRouter()

api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(health.router, prefix="/health", tags=["health"])