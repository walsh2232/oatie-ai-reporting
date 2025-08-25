"""
Performance and Error Recovery API endpoints for Oatie AI Platform
Provides access to performance monitoring, scaling recommendations, and error recovery status
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

from backend.core.performance import (
    startup_optimizer,
    resource_monitor, 
    scaling_engine,
    PerformanceRecommendation,
    StartupProfile,
    ResourceUsage
)
from backend.core.error_recovery import (
    error_recovery_manager,
    degradation_manager,
    setup_error_recovery,
    ErrorEvent,
    ServiceState
)

router = APIRouter(prefix="/performance", tags=["performance"])


# Performance Monitoring Endpoints

@router.get("/startup/stats", summary="Get startup performance statistics")
async def get_startup_stats():
    """Get startup performance statistics and bottleneck analysis"""
    try:
        stats = startup_optimizer.get_startup_stats()
        recommendations = startup_optimizer.get_startup_recommendations()
        
        return {
            "startup_statistics": stats,
            "recommendations": [asdict(rec) for rec in recommendations],
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get startup stats: {str(e)}")


@router.post("/startup/profile", summary="Start startup profiling")
async def start_startup_profiling(service_name: str):
    """Start profiling a service startup"""
    try:
        profile_id = startup_optimizer.start_profiling(service_name)
        
        return {
            "profile_id": profile_id,
            "service_name": service_name,
            "started_at": time.time(),
            "message": f"Started profiling startup for {service_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start profiling: {str(e)}")


@router.post("/startup/profile/{profile_id}/checkpoint", summary="Add startup checkpoint")
async def add_startup_checkpoint(
    profile_id: str,
    checkpoint_name: str,
    dependency: Optional[str] = None
):
    """Add a checkpoint during startup profiling"""
    try:
        startup_optimizer.add_checkpoint(profile_id, checkpoint_name, dependency)
        
        return {
            "profile_id": profile_id,
            "checkpoint": checkpoint_name,
            "dependency": dependency,
            "timestamp": time.time(),
            "message": f"Checkpoint '{checkpoint_name}' added"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add checkpoint: {str(e)}")


@router.post("/startup/profile/{profile_id}/finish", summary="Finish startup profiling")
async def finish_startup_profiling(profile_id: str):
    """Finish startup profiling and get analysis"""
    try:
        profile = startup_optimizer.finish_profiling(profile_id)
        
        return {
            "profile": asdict(profile),
            "analysis": {
                "total_time": profile.ready_time,
                "bottlenecks_count": len(profile.bottlenecks),
                "dependencies_count": len(profile.dependencies_loaded)
            },
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to finish profiling: {str(e)}")


@router.get("/resources/current", summary="Get current resource usage")
async def get_current_resources():
    """Get current system resource usage"""
    try:
        usage = resource_monitor.get_current_usage()
        
        return {
            "resource_usage": asdict(usage),
            "monitoring_active": resource_monitor.is_monitoring,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resource usage: {str(e)}")


@router.get("/resources/trends", summary="Get resource usage trends")
async def get_resource_trends(hours: int = Query(1, ge=1, le=24)):
    """Get resource usage trends over specified hours"""
    try:
        trends = resource_monitor.get_usage_trends(hours=hours)
        
        return {
            "trends": trends,
            "analysis_period_hours": hours,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resource trends: {str(e)}")


@router.post("/resources/monitoring/start", summary="Start resource monitoring")
async def start_resource_monitoring():
    """Start continuous resource monitoring"""
    try:
        if not resource_monitor.is_monitoring:
            resource_monitor.start_monitoring()
            message = "Resource monitoring started"
        else:
            message = "Resource monitoring already active"
        
        return {
            "message": message,
            "monitoring_active": resource_monitor.is_monitoring,
            "collection_interval": resource_monitor.collection_interval,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/resources/monitoring/stop", summary="Stop resource monitoring")
async def stop_resource_monitoring():
    """Stop continuous resource monitoring"""
    try:
        if resource_monitor.is_monitoring:
            resource_monitor.stop_monitoring()
            message = "Resource monitoring stopped"
        else:
            message = "Resource monitoring not active"
        
        return {
            "message": message,
            "monitoring_active": resource_monitor.is_monitoring,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


# Scaling and Optimization Endpoints

@router.get("/scaling/recommendations", summary="Get scaling recommendations")
async def get_scaling_recommendations():
    """Get automatic scaling recommendations based on current performance"""
    try:
        recommendations = scaling_engine.get_scaling_recommendations()
        optimal_config = scaling_engine.get_optimal_configuration()
        
        return {
            "recommendations": [asdict(rec) for rec in recommendations],
            "optimal_configuration": optimal_config,
            "total_recommendations": len(recommendations),
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/scaling/configuration", summary="Get optimal configuration")
async def get_optimal_configuration():
    """Get optimal configuration recommendations"""
    try:
        config = scaling_engine.get_optimal_configuration()
        
        return {
            "optimal_configuration": config,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")


# Error Recovery Endpoints

@router.get("/errors/summary", summary="Get error summary")
async def get_error_summary(hours: int = Query(1, ge=1, le=24)):
    """Get error summary for specified time period"""
    try:
        summary = error_recovery_manager.get_error_summary(hours=hours)
        
        return {
            "error_summary": summary,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error summary: {str(e)}")


@router.get("/errors/services", summary="Get service health status")
async def get_service_health():
    """Get health status of all managed services"""
    try:
        health_data = error_recovery_manager.get_service_health()
        degradation_status = degradation_manager.get_degradation_status()
        
        return {
            "service_health": health_data,
            "degradation_status": degradation_status,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get service health: {str(e)}")


@router.post("/errors/recovery/setup", summary="Setup error recovery system")
async def setup_error_recovery_system():
    """Initialize the error recovery system with default configurations"""
    try:
        setup_error_recovery()
        
        return {
            "message": "Error recovery system initialized",
            "services_registered": len(error_recovery_manager.service_states),
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup error recovery: {str(e)}")


@router.post("/errors/services/{service_name}/recover", summary="Manually trigger service recovery")
async def trigger_service_recovery(service_name: str, background_tasks: BackgroundTasks):
    """Manually trigger recovery for a specific service"""
    try:
        if service_name not in error_recovery_manager.service_states:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        # Create a mock error event for manual recovery
        error_event = ErrorEvent(
            timestamp=time.time(),
            service_name=service_name,
            error_type="ManualRecovery",
            severity="MEDIUM",
            message="Manual recovery triggered",
            context={"manual": True}
        )
        
        # Attempt recovery in background
        async def recover():
            await error_recovery_manager._attempt_recovery(service_name, error_event)
        
        background_tasks.add_task(recover)
        
        return {
            "message": f"Recovery triggered for service: {service_name}",
            "service_name": service_name,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger recovery: {str(e)}")


@router.post("/errors/services/{service_name}/degrade", summary="Activate service degradation")
async def activate_service_degradation(service_name: str, reason: str):
    """Manually activate degraded mode for a service"""
    try:
        degradation_manager.activate_degradation(service_name, reason)
        
        return {
            "message": f"Degraded mode activated for service: {service_name}",
            "service_name": service_name,
            "reason": reason,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate degradation: {str(e)}")


@router.post("/errors/services/{service_name}/restore", summary="Restore service from degradation")
async def restore_service_from_degradation(service_name: str):
    """Restore a service from degraded mode"""
    try:
        degradation_manager.deactivate_degradation(service_name)
        
        return {
            "message": f"Service restored from degraded mode: {service_name}",
            "service_name": service_name,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore service: {str(e)}")


@router.get("/errors/degradation/status", summary="Get degradation status")
async def get_degradation_status():
    """Get current service degradation status"""
    try:
        status = degradation_manager.get_degradation_status()
        
        return {
            "degradation_status": status,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get degradation status: {str(e)}")


# Combined Status Endpoint

@router.get("/overview", summary="Get complete performance overview")
async def get_performance_overview():
    """Get comprehensive performance and error recovery overview"""
    try:
        # Collect all performance data
        current_resources = resource_monitor.get_current_usage()
        resource_trends = resource_monitor.get_usage_trends(hours=1)
        startup_stats = startup_optimizer.get_startup_stats()
        scaling_recommendations = scaling_engine.get_scaling_recommendations()
        error_summary = error_recovery_manager.get_error_summary(hours=1)
        service_health = error_recovery_manager.get_service_health()
        degradation_status = degradation_manager.get_degradation_status()
        
        # Calculate overall performance score
        performance_score = calculate_performance_score(
            current_resources, error_summary, service_health
        )
        
        return {
            "performance_overview": {
                "performance_score": performance_score,
                "current_resources": asdict(current_resources),
                "resource_trends": resource_trends,
                "startup_statistics": startup_stats,
                "error_summary": error_summary,
                "service_health": service_health,
                "degradation_status": degradation_status
            },
            "recommendations": {
                "scaling": [asdict(rec) for rec in scaling_recommendations],
                "startup": [asdict(rec) for rec in startup_optimizer.get_startup_recommendations()]
            },
            "monitoring_status": {
                "resource_monitoring_active": resource_monitor.is_monitoring,
                "services_managed": len(error_recovery_manager.service_states),
                "active_degradations": len(degradation_status.get("active_degradations", []))
            },
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance overview: {str(e)}")


def calculate_performance_score(
    resources: ResourceUsage,
    error_summary: Dict[str, Any], 
    service_health: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate an overall performance score"""
    
    # Resource score (0-100, higher is better)
    cpu_score = max(0, 100 - resources.cpu_percent)
    memory_score = max(0, 100 - resources.memory_percent)
    resource_score = (cpu_score + memory_score) / 2
    
    # Error score (0-100, higher is better)
    total_errors = error_summary.get("total_errors", 0)
    error_score = max(0, 100 - min(total_errors * 5, 100))  # Penalize errors
    
    # Service health score (0-100, higher is better)
    healthy_services = sum(
        1 for health in service_health.values() 
        if health.get("state") == "healthy"
    )
    total_services = len(service_health)
    service_score = (healthy_services / total_services * 100) if total_services > 0 else 100
    
    # Overall score (weighted average)
    overall_score = (resource_score * 0.4 + error_score * 0.3 + service_score * 0.3)
    
    # Determine performance level
    if overall_score >= 90:
        performance_level = "excellent"
    elif overall_score >= 70:
        performance_level = "good"
    elif overall_score >= 50:
        performance_level = "fair"
    else:
        performance_level = "poor"
    
    return {
        "overall_score": round(overall_score, 1),
        "performance_level": performance_level,
        "component_scores": {
            "resources": round(resource_score, 1),
            "errors": round(error_score, 1),
            "services": round(service_score, 1)
        },
        "details": {
            "cpu_usage": resources.cpu_percent,
            "memory_usage": resources.memory_percent,
            "total_errors": total_errors,
            "healthy_services": healthy_services,
            "total_services": total_services
        }
    }


# Helper function to convert dataclass to dict
def asdict(obj):
    """Convert dataclass to dictionary"""
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if hasattr(value, '__dict__'):
                result[key] = asdict(value)
            elif isinstance(value, list):
                result[key] = [asdict(item) if hasattr(item, '__dict__') else item for item in value]
            elif hasattr(value, 'value'):  # For Enum types
                result[key] = value.value
            else:
                result[key] = value
        return result
    else:
        return obj