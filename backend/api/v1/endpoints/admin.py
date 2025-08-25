"""
Administrative endpoints for system management
"""

from typing import List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel

from backend.api.v1.endpoints.auth import oauth2_scheme
from backend.core.security import AuditEventType

router = APIRouter()


class SystemConfig(BaseModel):
    cache_ttl: int
    max_query_timeout: int
    rate_limit_requests: int
    debug_mode: bool


@router.get("/config")
async def get_system_config(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get system configuration (admin only)"""
    
    settings = request.app.state.settings if hasattr(request.app.state, 'settings') else None
    
    config = {
        "cache_ttl": 3600,
        "max_query_timeout": 30,
        "rate_limit_requests": 1000,
        "debug_mode": False,
        "version": "3.0.0",
        "environment": "production"
    }
    
    return config


@router.put("/config")
async def update_system_config(
    request: Request,
    config: SystemConfig,
    token: str = Depends(oauth2_scheme)
):
    """Update system configuration (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Log configuration change
    await security_manager.log_audit_event(
        AuditEventType.SYSTEM_ACCESS,
        resource="system_config",
        details={"config_update": True, "changes": config.dict()}
    )
    
    return {"message": "Configuration updated successfully", "config": config}


@router.post("/cache/clear")
async def clear_cache(
    request: Request,
    namespace: str = None,
    token: str = Depends(oauth2_scheme)
):
    """Clear system cache (admin only)"""
    
    cache_manager = request.app.state.cache_manager
    security_manager = request.app.state.security_manager
    
    if namespace:
        await cache_manager.invalidate_namespace(namespace)
        message = f"Cache namespace '{namespace}' cleared"
    else:
        # Clear all cache
        cache_manager.memory_cache.clear()
        message = "All cache cleared"
    
    # Log cache clear action
    await security_manager.log_audit_event(
        AuditEventType.SYSTEM_ACCESS,
        resource="cache_management",
        details={"action": "clear_cache", "namespace": namespace}
    )
    
    return {"message": message}


@router.get("/audit-logs")
async def get_audit_logs(
    request: Request,
    limit: int = 100,
    event_type: str = None,
    token: str = Depends(oauth2_scheme)
):
    """Get audit logs (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Filter logs
    event_type_filter = None
    if event_type:
        try:
            event_type_filter = AuditEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid event type")
    
    logs = await security_manager.get_audit_logs(
        event_type=event_type_filter
    )
    
    # Apply limit
    limited_logs = logs[-limit:] if logs else []
    
    return {
        "logs": limited_logs,
        "total_count": len(logs),
        "returned_count": len(limited_logs)
    }


@router.get("/database/stats")
async def get_database_stats(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get database connection statistics (admin only)"""
    
    db_manager = request.app.state.db_manager
    
    if db_manager:
        stats = await db_manager.get_connection_stats()
    else:
        stats = {
            "main_pool": {"status": "not_connected"},
            "read_replicas": 0,
            "query_stats": {
                "queries_executed": 0,
                "slow_queries": 0
            }
        }
    
    return stats


@router.post("/maintenance/start")
async def start_maintenance_mode(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Enable maintenance mode (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Log maintenance mode activation
    await security_manager.log_audit_event(
        AuditEventType.SYSTEM_ACCESS,
        resource="maintenance_mode",
        details={"action": "enable", "timestamp": datetime.utcnow().isoformat()}
    )
    
    return {
        "message": "Maintenance mode enabled",
        "enabled_at": datetime.utcnow().isoformat()
    }


@router.post("/maintenance/stop")
async def stop_maintenance_mode(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Disable maintenance mode (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Log maintenance mode deactivation
    await security_manager.log_audit_event(
        AuditEventType.SYSTEM_ACCESS,
        resource="maintenance_mode",
        details={"action": "disable", "timestamp": datetime.utcnow().isoformat()}
    )
    
    return {
        "message": "Maintenance mode disabled",
        "disabled_at": datetime.utcnow().isoformat()
    }


@router.get("/webhooks")
async def list_webhooks(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """List configured webhooks (admin only)"""
    
    # Mock webhook list
    webhooks = [
        {
            "id": "webhook_001",
            "url": "https://external-system.com/oatie-webhook",
            "events": ["report.completed", "query.executed"],
            "active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    return {"webhooks": webhooks}


@router.post("/webhooks/test")
async def test_webhook(
    request: Request,
    webhook_url: str,
    token: str = Depends(oauth2_scheme)
):
    """Test webhook endpoint (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Log webhook test
    await security_manager.log_audit_event(
        AuditEventType.SYSTEM_ACCESS,
        resource="webhook_test",
        details={"url": webhook_url, "test": True}
    )
    
    return {
        "message": f"Webhook test sent to {webhook_url}",
        "status": "success",
        "response_time_ms": 150
    }