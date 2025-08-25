#!/usr/bin/env python3
"""
Simple analytics API server for demonstration
"""

import json
import asyncio
import random
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Analytics API Demo")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_data():
    """Mock dashboard data endpoint"""
    
    # Generate trend data for charts
    trend_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        trend_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "users": random.randint(50, 200),
            "reports": random.randint(100, 500),
            "queries": random.randint(500, 2000),
            "performance_score": round(random.uniform(75, 95), 2)
        })
    
    # Mock predictive insights
    predictions = []
    for i in range(7):
        base_value = 100
        trend_factor = 1 + (i * 0.02)
        noise = random.uniform(-0.1, 0.1)
        predicted_value = base_value * trend_factor * (1 + noise)
        
        predictions.append({
            "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
            "predicted_value": round(predicted_value, 2),
            "confidence_lower": round(predicted_value * 0.9, 2),
            "confidence_upper": round(predicted_value * 1.1, 2),
            "trend": "increasing" if predicted_value > base_value else "stable"
        })
    
    # Mock anomalies
    anomalies = []
    metrics = ["response_time", "cpu_usage", "memory_usage", "error_rate"]
    
    for metric in metrics:
        if random.random() < 0.4:  # 40% chance of anomaly
            anomaly_time = datetime.now() - timedelta(minutes=random.randint(0, 1440))
            
            if metric == "response_time":
                actual = random.uniform(2000, 5000)
                expected = 800
            elif metric == "cpu_usage":
                actual = random.uniform(85, 100)
                expected = 45
            elif metric == "memory_usage":
                actual = random.uniform(90, 100)
                expected = 70
            else:
                actual = random.uniform(5, 15)
                expected = 1
            
            anomaly_score = abs(actual - expected) / expected
            
            anomalies.append({
                "timestamp": anomaly_time.isoformat(),
                "metric_name": metric,
                "actual_value": round(actual, 2),
                "expected_value": round(expected, 2),
                "anomaly_score": round(anomaly_score, 2),
                "is_anomaly": anomaly_score > 1.5,
                "severity": "high" if anomaly_score > 3 else "medium" if anomaly_score > 1.5 else "low"
            })
    
    dashboard_data = {
        "performance_metrics": {
            "average_response_time": 0.85,
            "total_requests": 15420,
            "cache_hit_rate": 85.5,
            "active_users": 142,
            "error_rate": 0.02
        },
        "usage_statistics": {
            "period": "Last 24 hours",
            "report_generations": 324,
            "query_executions": 1842,
            "data_exports": 156,
            "unique_users": 89
        },
        "system_health": {
            "status": "healthy",
            "uptime_hours": 72.5,
            "memory_usage_percent": 68.2,
            "cpu_usage_percent": 34.1,
            "disk_usage_percent": 45.8
        },
        "trend_data": trend_data,
        "real_time_metrics": {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "active_users": random.randint(80, 150),
                "queries_per_second": round(random.uniform(15.5, 45.2), 2),
                "response_time_ms": round(random.uniform(200, 800), 2),
                "memory_usage": round(random.uniform(60, 85), 2),
                "cpu_usage": round(random.uniform(25, 75), 2),
            }
        },
        "predictive_insights": predictions,
        "anomaly_alerts": anomalies,
        "last_updated": datetime.now().isoformat()
    }
    
    return dashboard_data

if __name__ == "__main__":
    print("Starting Analytics API server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")