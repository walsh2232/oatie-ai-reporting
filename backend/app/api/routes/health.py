from fastapi import APIRouter

router = APIRouter()

@router.get("/live")
async def health_live():
    """Basic liveness check"""
    return {"status": "live"}

@router.get("/ready")
async def health_ready():
    """Readiness check (could include database connectivity check)"""
    return {"status": "ready"}
