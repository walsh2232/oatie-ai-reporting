from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog

from app.db.database import get_db
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database connectivity"""
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Database connectivity check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["checks"]["database"] = {"status": "unhealthy", "message": f"Database error: {str(e)}"}
        health_status["status"] = "unhealthy"
    
    # Additional checks can be added here
    health_status["checks"]["application"] = {"status": "healthy", "message": "Application running normally"}
    
    return health_status