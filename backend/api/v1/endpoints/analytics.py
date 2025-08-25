"""
Analytics and monitoring endpoints for enterprise insights
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.api.v1.endpoints.auth import oauth2_scheme

router = APIRouter()


class PerformanceMetrics(BaseModel):
    average_response_time: float
    total_requests: int
    cache_hit_rate: float
    active_users: int
    error_rate: float


class UsageStatistics(BaseModel):
    period: str
    report_generations: int
    query_executions: int
    data_exports: int
    unique_users: int


class PredictiveAnalytics(BaseModel):
    model_type: str
    forecast_period: str
    predictions: List[Dict[str, Any]]
    confidence_interval: Dict[str, float]
    trend_analysis: Dict[str, Any]


class AnomalyDetection(BaseModel):
    timestamp: datetime
    metric_name: str
    actual_value: float
    expected_value: float
    anomaly_score: float
    is_anomaly: bool
    severity: str


class CustomKPI(BaseModel):
    id: str
    name: str
    description: str
    formula: str
    data_source: str
    visualization_type: str
    thresholds: Dict[str, float]
    created_at: datetime
    updated_at: datetime


class DashboardConfig(BaseModel):
    id: str
    name: str
    layout: List[Dict[str, Any]]
    widgets: List[Dict[str, Any]]
    filters: Dict[str, Any]
    refresh_interval: int
    created_by: str
    is_public: bool


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get real-time performance metrics"""
    
    # Get cache statistics
    cache_manager = request.app.state.cache_manager
    cache_stats = await cache_manager.get_stats()
    
    # Mock performance data
    metrics = {
        "average_response_time": 0.85,  # seconds
        "total_requests": 15420,
        "cache_hit_rate": cache_stats.get("hit_rate", 85.5),
        "active_users": 142,
        "error_rate": 0.02  # 2%
    }
    
    return PerformanceMetrics(**metrics)


@router.get("/usage")
async def get_usage_statistics(
    request: Request,
    period: str = "24h",
    token: str = Depends(oauth2_scheme)
):
    """Get usage statistics for different time periods"""
    
    # Mock usage data based on period
    if period == "24h":
        stats = {
            "period": "Last 24 hours",
            "report_generations": 324,
            "query_executions": 1842,
            "data_exports": 156,
            "unique_users": 89
        }
    elif period == "7d":
        stats = {
            "period": "Last 7 days", 
            "report_generations": 2100,
            "query_executions": 12500,
            "data_exports": 890,
            "unique_users": 245
        }
    else:
        stats = {
            "period": "Last 30 days",
            "report_generations": 8500,
            "query_executions": 45200,
            "data_exports": 3200,
            "unique_users": 412
        }
    
    return UsageStatistics(**stats)


@router.get("/top-reports")
async def get_top_reports(
    request: Request,
    limit: int = 10,
    token: str = Depends(oauth2_scheme)
):
    """Get most popular report templates"""
    
    top_reports = [
        {
            "template_id": "sales_summary",
            "name": "Sales Summary Report",
            "executions": 524,
            "avg_execution_time": 2.3,
            "success_rate": 98.5
        },
        {
            "template_id": "financial_dashboard",
            "name": "Financial Performance Dashboard",
            "executions": 398,
            "avg_execution_time": 3.1,
            "success_rate": 97.2
        },
        {
            "template_id": "inventory_analysis",
            "name": "Inventory Analysis",
            "executions": 276,
            "avg_execution_time": 1.8,
            "success_rate": 99.1
        }
    ]
    
    return {"reports": top_reports[:limit]}


@router.get("/system-health")
async def get_system_health(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get comprehensive system health status"""
    
    # Get health from monitoring
    from backend.core.monitoring import HealthChecker
    health_checker = HealthChecker()
    
    db_manager = request.app.state.db_manager
    cache_manager = request.app.state.cache_manager
    
    health_status = await health_checker.get_health_status(db_manager, cache_manager)
    
    # Add additional metrics
    health_status.update({
        "uptime_hours": 72.5,
        "memory_usage_percent": 68.2,
        "cpu_usage_percent": 34.1,
        "disk_usage_percent": 45.8,
        "version": "3.0.0"
    })
    
    return health_status


@router.get("/audit-summary")
async def get_audit_summary(
    request: Request,
    hours: int = 24,
    token: str = Depends(oauth2_scheme)
):
    """Get audit event summary"""
    
    security_manager = request.app.state.security_manager
    
    # Get recent audit logs
    start_date = datetime.utcnow() - timedelta(hours=hours)
    audit_logs = await security_manager.get_audit_logs(start_date=start_date)
    
    # Summarize events by type
    event_summary = {}
    for log in audit_logs:
        event_type = log["event_type"]
        event_summary[event_type] = event_summary.get(event_type, 0) + 1
    
    return {
        "period_hours": hours,
        "total_events": len(audit_logs),
        "event_breakdown": event_summary,
        "high_severity_events": len([log for log in audit_logs if log.get("severity") == "HIGH"])
    }


@router.get("/cache-analytics")
async def get_cache_analytics(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get detailed cache performance analytics"""
    
    cache_manager = request.app.state.cache_manager
    stats = await cache_manager.get_stats()
    
    # Enhanced cache analytics
    analytics = {
        "hit_rate": stats.get("hit_rate", 0),
        "total_requests": stats.get("total_requests", 0),
        "memory_cache_size": stats.get("memory_size", 0),
        "redis_connected": stats.get("redis_connected", False),
        "recommendations": []
    }
    
    # Generate recommendations
    if analytics["hit_rate"] < 80:
        analytics["recommendations"].append("Consider increasing cache TTL values")
    
    if analytics["hit_rate"] > 95:
        analytics["recommendations"].append("Excellent cache performance")
    
    return analytics


# WebSocket Connection Manager for Real-time Updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/streaming")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time analytics streaming"""
    await manager.connect(websocket)
    try:
        while True:
            # Send real-time analytics data every 5 seconds
            real_time_data = await generate_real_time_analytics()
            await manager.send_personal_message(json.dumps(real_time_data), websocket)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def generate_real_time_analytics():
    """Generate mock real-time analytics data"""
    import random
    
    current_time = datetime.now()
    return {
        "timestamp": current_time.isoformat(),
        "metrics": {
            "active_users": random.randint(80, 150),
            "queries_per_second": round(random.uniform(15.5, 45.2), 2),
            "response_time_ms": round(random.uniform(200, 800), 2),
            "memory_usage": round(random.uniform(60, 85), 2),
            "cpu_usage": round(random.uniform(25, 75), 2),
        },
        "alerts": [
            {
                "type": "performance",
                "message": "Response time spike detected",
                "severity": "warning",
                "timestamp": current_time.isoformat()
            }
        ] if random.random() < 0.3 else []
    }


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Main dashboard data endpoint with comprehensive analytics"""
    
    # Get various analytics data
    performance = await get_performance_metrics(request, token)
    usage = await get_usage_statistics(request, "24h", token)
    top_reports = await get_top_reports(request, 5, token)
    system_health = await get_system_health(request, token)
    
    # Generate trend data for charts
    trend_data = generate_trend_data()
    
    dashboard_data = {
        "performance_metrics": performance.model_dump(),
        "usage_statistics": usage.model_dump(),
        "top_reports": top_reports,
        "system_health": system_health,
        "trend_data": trend_data,
        "real_time_metrics": await generate_real_time_analytics(),
        "predictive_insights": await generate_predictive_insights(),
        "anomaly_alerts": await detect_anomalies(),
        "last_updated": datetime.now().isoformat()
    }
    
    return dashboard_data


def generate_trend_data():
    """Generate mock trend data for the last 30 days"""
    import random
    
    base_date = datetime.now() - timedelta(days=30)
    trend_data = []
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        trend_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "users": random.randint(50, 200),
            "reports": random.randint(100, 500),
            "queries": random.randint(500, 2000),
            "performance_score": round(random.uniform(75, 95), 2)
        })
    
    return trend_data


@router.post("/predict")
async def get_predictive_analytics(
    request: Request,
    model_type: str = "arima",
    forecast_days: int = 7,
    token: str = Depends(oauth2_scheme)
):
    """Predictive analytics service with multiple ML models"""
    
    predictions = await generate_predictive_insights(model_type, forecast_days)
    
    return {
        "model_type": model_type,
        "forecast_period": f"{forecast_days} days",
        "predictions": predictions,
        "generated_at": datetime.now().isoformat()
    }


async def generate_predictive_insights(model_type: str = "arima", forecast_days: int = 7):
    """Generate mock predictive analytics using statistical models"""
    import random
    
    base_value = 100
    predictions = []
    
    for i in range(forecast_days):
        # Mock trend with some randomness
        trend_factor = 1 + (i * 0.02)  # 2% daily growth
        noise = random.uniform(-0.1, 0.1)
        predicted_value = base_value * trend_factor * (1 + noise)
        
        predictions.append({
            "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
            "predicted_value": round(predicted_value, 2),
            "confidence_lower": round(predicted_value * 0.9, 2),
            "confidence_upper": round(predicted_value * 1.1, 2),
            "trend": "increasing" if predicted_value > base_value else "stable"
        })
        
        base_value = predicted_value
    
    return predictions


@router.get("/anomaly")
async def get_anomaly_detection(
    request: Request,
    hours: int = 24,
    threshold: float = 2.0,
    token: str = Depends(oauth2_scheme)
):
    """Anomaly detection service with configurable thresholds"""
    
    anomalies = await detect_anomalies(hours, threshold)
    
    return {
        "analysis_period": f"{hours} hours",
        "threshold": threshold,
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies,
        "recommendations": generate_anomaly_recommendations(anomalies)
    }


async def detect_anomalies(hours: int = 24, threshold: float = 2.0):
    """Mock anomaly detection using statistical methods"""
    import random
    
    anomalies = []
    metrics = ["response_time", "cpu_usage", "memory_usage", "error_rate", "query_count"]
    
    for metric in metrics:
        if random.random() < 0.3:  # 30% chance of anomaly per metric
            anomaly_time = datetime.now() - timedelta(minutes=random.randint(0, hours*60))
            
            if metric == "response_time":
                actual = random.uniform(2000, 5000)  # High response time
                expected = 800
            elif metric == "cpu_usage":
                actual = random.uniform(85, 100)  # High CPU
                expected = 45
            elif metric == "memory_usage":
                actual = random.uniform(90, 100)  # High memory
                expected = 70
            elif metric == "error_rate":
                actual = random.uniform(5, 15)  # High error rate
                expected = 1
            else:
                actual = random.uniform(1000, 5000)  # High query count
                expected = 200
            
            anomaly_score = abs(actual - expected) / expected
            
            anomalies.append({
                "timestamp": anomaly_time.isoformat(),
                "metric_name": metric,
                "actual_value": round(actual, 2),
                "expected_value": round(expected, 2),
                "anomaly_score": round(anomaly_score, 2),
                "is_anomaly": anomaly_score > threshold,
                "severity": "high" if anomaly_score > 3 else "medium" if anomaly_score > 1.5 else "low"
            })
    
    return anomalies


def generate_anomaly_recommendations(anomalies):
    """Generate actionable recommendations based on detected anomalies"""
    recommendations = []
    
    for anomaly in anomalies:
        if anomaly["metric_name"] == "response_time" and anomaly["severity"] == "high":
            recommendations.append("Consider optimizing database queries or adding caching")
        elif anomaly["metric_name"] == "cpu_usage" and anomaly["severity"] == "high":
            recommendations.append("Scale up compute resources or optimize resource-intensive operations")
        elif anomaly["metric_name"] == "memory_usage" and anomaly["severity"] == "high":
            recommendations.append("Investigate memory leaks or increase available memory")
        elif anomaly["metric_name"] == "error_rate" and anomaly["severity"] != "low":
            recommendations.append("Review error logs and fix underlying issues")
    
    return list(set(recommendations))  # Remove duplicates


@router.post("/kpi", response_model=CustomKPI)
async def create_custom_kpi(
    request: Request,
    kpi_data: Dict[str, Any],
    token: str = Depends(oauth2_scheme)
):
    """Create custom KPI with business logic"""
    
    kpi_id = f"kpi_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    custom_kpi = CustomKPI(
        id=kpi_id,
        name=kpi_data.get("name", "New KPI"),
        description=kpi_data.get("description", ""),
        formula=kpi_data.get("formula", "SUM(value)"),
        data_source=kpi_data.get("data_source", "default"),
        visualization_type=kpi_data.get("visualization_type", "line"),
        thresholds=kpi_data.get("thresholds", {"warning": 75, "critical": 90}),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    return custom_kpi


@router.get("/kpi")
async def list_custom_kpis(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """List all custom KPIs"""
    
    # Mock KPI data
    kpis = [
        {
            "id": "kpi_001",
            "name": "Report Generation Rate",
            "description": "Number of reports generated per hour",
            "formula": "COUNT(reports) / hours",
            "current_value": 45.2,
            "threshold_status": "normal",
            "trend": "increasing"
        },
        {
            "id": "kpi_002", 
            "name": "User Engagement Score",
            "description": "Average user session duration and interactions",
            "formula": "AVG(session_duration * interactions)",
            "current_value": 78.5,
            "threshold_status": "warning",
            "trend": "stable"
        }
    ]
    
    return {"kpis": kpis}


@router.get("/kpi/{kpi_id}")
async def get_kpi_details(
    kpi_id: str,
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get detailed KPI information and historical data"""
    
    # Mock KPI details with historical data
    historical_data = []
    for i in range(30):
        date = datetime.now() - timedelta(days=29-i)
        historical_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": round(45.2 + (i * 0.5) + (random.uniform(-5, 5)), 2)
        })
    
    return {
        "id": kpi_id,
        "name": "Sample KPI",
        "current_value": 45.2,
        "historical_data": historical_data,
        "performance_analysis": {
            "avg_30_days": 43.8,
            "trend": "increasing",
            "volatility": "low"
        }
    }