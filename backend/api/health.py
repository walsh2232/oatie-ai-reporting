"""
Enhanced health monitoring API endpoints for Oatie AI Platform
Provides comprehensive health checks, dashboards, and service management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from typing import Dict, Any, List, Optional
import time
import asyncio
from datetime import datetime, timedelta

from backend.core.monitoring import (
    health_checker, 
    service_recovery, 
    dashboard_manager,
    HealthChecker,
    ServiceRecoveryManager,
    DashboardManager
)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", summary="Basic health check")
async def basic_health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "message": "Oatie AI Platform is running"
    }


@router.get("/detailed", summary="Detailed health status")
async def detailed_health_check(
    include_system: bool = True,
    include_services: bool = True
):
    """Comprehensive health check with detailed service status"""
    try:
        # Get health status from monitoring system
        health_status = await health_checker.get_health_status()
        
        if not include_system:
            health_status.pop("system", None)
        
        if not include_services:
            health_status.pop("services", None)
        
        # Set appropriate HTTP status based on health
        status_code = 200
        if health_status.get("status") == "critical":
            status_code = 503  # Service Unavailable
        elif health_status.get("status") == "degraded":
            status_code = 200  # OK but with warnings
        
        return JSONResponse(
            content=health_status,
            status_code=status_code
        )
        
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "timestamp": time.time()
            },
            status_code=500
        )


@router.get("/dashboard", summary="Real-time dashboard data")
async def get_dashboard():
    """Get comprehensive dashboard data including metrics and history"""
    try:
        dashboard_data = await dashboard_manager.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.get("/dashboard/html", response_class=HTMLResponse, summary="HTML dashboard")
async def get_dashboard_html():
    """Get HTML dashboard for browser viewing"""
    try:
        dashboard_data = await dashboard_manager.get_dashboard_data()
        
        # Generate HTML dashboard
        html_content = generate_dashboard_html(dashboard_data)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        error_html = f"""
        <html>
            <head><title>Dashboard Error</title></head>
            <body>
                <h1>Dashboard Error</h1>
                <p>Failed to load dashboard: {str(e)}</p>
                <p>Timestamp: {datetime.now()}</p>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@router.get("/metrics", response_class=PlainTextResponse, summary="Prometheus metrics")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    try:
        metrics = await dashboard_manager.export_metrics_prometheus()
        return PlainTextResponse(content=metrics)
    except Exception as e:
        return PlainTextResponse(
            content=f"# Error getting metrics: {str(e)}",
            status_code=500
        )


@router.get("/services", summary="Individual service status")
async def get_services_status():
    """Get status of individual services"""
    try:
        services = await health_checker.check_service_health()
        return {
            "services": services,
            "timestamp": time.time(),
            "total_services": len(services),
            "healthy_services": sum(1 for status in services.values() if status),
            "unhealthy_services": sum(1 for status in services.values() if not status)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service status: {str(e)}"
        )


@router.post("/services/{service_name}/restart", summary="Restart a service")
async def restart_service(
    service_name: str,
    background_tasks: BackgroundTasks
):
    """Attempt to restart/recover a specific service"""
    valid_services = ["database", "cache", "external_apis", "system_resources"]
    
    if service_name not in valid_services:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service name. Valid services: {valid_services}"
        )
    
    try:
        # Start recovery attempt in background
        background_tasks.add_task(
            service_recovery.attempt_service_recovery,
            service_name
        )
        
        return {
            "message": f"Recovery attempt started for service: {service_name}",
            "service": service_name,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate service recovery: {str(e)}"
        )


@router.get("/history", summary="Health metrics history")
async def get_health_history(
    limit: int = 100,
    hours: Optional[int] = None
):
    """Get historical health metrics"""
    try:
        history = dashboard_manager.get_metrics_history(limit)
        
        # Filter by time if hours parameter is provided
        if hours:
            cutoff_time = time.time() - (hours * 3600)
            history = [
                metric for metric in history
                if metric.get("timestamp", 0) >= cutoff_time
            ]
        
        return {
            "history": history,
            "count": len(history),
            "limit_applied": limit,
            "hours_filter": hours,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health history: {str(e)}"
        )


@router.get("/recovery/status", summary="Service recovery status")
async def get_recovery_status():
    """Get current service recovery status and statistics"""
    try:
        return {
            "recovery_attempts": service_recovery.recovery_attempts,
            "last_recovery_times": service_recovery.last_recovery_time,
            "max_attempts": service_recovery.max_recovery_attempts,
            "recovery_interval": service_recovery.recovery_interval,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recovery status: {str(e)}"
        )


@router.post("/recovery/reset", summary="Reset recovery counters")
async def reset_recovery_counters(service_name: Optional[str] = None):
    """Reset recovery attempt counters for all services or a specific service"""
    try:
        if service_name:
            if service_name in service_recovery.recovery_attempts:
                service_recovery.recovery_attempts[service_name] = 0
                service_recovery.last_recovery_time.pop(service_name, None)
                message = f"Recovery counters reset for service: {service_name}"
            else:
                message = f"No recovery history found for service: {service_name}"
        else:
            service_recovery.recovery_attempts.clear()
            service_recovery.last_recovery_time.clear()
            message = "All recovery counters reset"
        
        return {
            "message": message,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset recovery counters: {str(e)}"
        )


def generate_dashboard_html(dashboard_data: Dict[str, Any]) -> str:
    """Generate HTML dashboard from dashboard data"""
    health = dashboard_data.get("health", {})
    performance = dashboard_data.get("performance", {})
    system = dashboard_data.get("system", {})
    
    status = health.get("status", "unknown")
    services = health.get("services", {})
    
    # Status color
    status_color = {
        "healthy": "#28a745",
        "degraded": "#ffc107", 
        "critical": "#dc3545",
        "unknown": "#6c757d"
    }.get(status, "#6c757d")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Oatie AI Platform - Health Dashboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .status-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                text-transform: uppercase;
                background-color: {status_color};
                color: white;
                margin-top: 10px;
            }}
            .content {{
                padding: 30px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                background: #ffffff;
            }}
            .metric-title {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 15px;
                color: #495057;
            }}
            .service-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #f8f9fa;
            }}
            .service-status {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            .status-healthy {{ background: #d4edda; color: #155724; }}
            .status-unhealthy {{ background: #f8d7da; color: #721c24; }}
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin-top: 15px;
            }}
            .info-item {{
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
                font-size: 14px;
            }}
            .info-label {{
                font-weight: 600;
                color: #6c757d;
            }}
            .info-value {{
                color: #495057;
                margin-top: 5px;
            }}
            .refresh-info {{
                text-align: center;
                margin-top: 20px;
                padding: 15px;
                background: #e9ecef;
                border-radius: 4px;
                font-size: 14px;
                color: #6c757d;
            }}
        </style>
        <script>
            setTimeout(function() {{
                location.reload();
            }}, 30000);  // Auto-refresh every 30 seconds
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Oatie AI Platform</h1>
                <h2>Health Dashboard</h2>
                <div class="status-badge">{status}</div>
            </div>
            
            <div class="content">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">🔧 Services Status</div>
    """
    
    # Add services status
    for service_name, is_healthy in services.items():
        status_class = "status-healthy" if is_healthy else "status-unhealthy"
        status_text = "Healthy" if is_healthy else "Unhealthy"
        service_display = service_name.replace("_", " ").title()
        
        html += f"""
                        <div class="service-item">
                            <span>{service_display}</span>
                            <span class="service-status {status_class}">{status_text}</span>
                        </div>
        """
    
    # Add system information
    html += f"""
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">💻 System Information</div>
                        <div class="info-grid">
    """
    
    system_info = health.get("system", {})
    if system_info:
        for key, value in system_info.items():
            if key != "uptime":
                display_key = key.replace("_", " ").title()
                html += f"""
                            <div class="info-item">
                                <div class="info-label">{display_key}</div>
                                <div class="info-value">{value}</div>
                            </div>
                """
    
    # Add performance metrics if available
    if performance and "error" not in performance:
        html += """
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">📊 Performance Metrics</div>
                        <div class="info-grid">
        """
        
        for key, value in performance.items():
            if isinstance(value, (int, float)):
                display_key = key.replace("_", " ").title()
                if "percent" in key:
                    display_value = f"{value:.1f}%"
                elif "memory" in key and isinstance(value, int):
                    display_value = f"{value / 1024 / 1024:.1f} MB"
                else:
                    display_value = str(value)
                
                html += f"""
                            <div class="info-item">
                                <div class="info-label">{display_key}</div>
                                <div class="info-value">{display_value}</div>
                            </div>
                """
    
    # Close the HTML
    html += f"""
                        </div>
                    </div>
                </div>
                
                <div class="refresh-info">
                    ⏰ Last updated: {datetime.fromtimestamp(dashboard_data.get('timestamp', time.time())).strftime('%Y-%m-%d %H:%M:%S')}<br>
                    🔄 Auto-refresh in 30 seconds | 
                    ⚡ Uptime: {dashboard_data.get('uptime', 0):.0f} seconds
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html