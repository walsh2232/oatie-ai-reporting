#!/usr/bin/env python3
"""
Business Metrics and KPI Tracking System
Monitors business-critical performance indicators for Oatie AI Reporting Platform
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
import time
import asyncio
from enum import Enum

class MetricType(Enum):
    """Types of business metrics"""
    COUNTER = "counter"
    GAUGE = "gauge" 
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BusinessMetric:
    """Business metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = None
    unit: str = ""
    description: str = ""
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass 
class KPIThreshold:
    """KPI threshold configuration"""
    metric_name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    target_value: Optional[float] = None
    severity: AlertSeverity = AlertSeverity.MEDIUM
    enabled: bool = True

class BusinessMetricsCollector:
    """Collects and tracks business metrics for Oatie AI platform"""
    
    def __init__(self):
        self.metrics: List[BusinessMetric] = []
        self.kpi_thresholds: Dict[str, KPIThreshold] = {}
        self.aggregated_metrics: Dict[str, Any] = {}
        self._setup_default_kpis()
    
    def _setup_default_kpis(self):
        """Setup default KPI thresholds for Oatie AI platform"""
        
        default_kpis = [
            # User Engagement KPIs
            KPIThreshold("active_users_daily", min_value=100, target_value=500, severity=AlertSeverity.HIGH),
            KPIThreshold("user_session_duration_avg", min_value=300, target_value=900, severity=AlertSeverity.MEDIUM),  # 5-15 min
            KPIThreshold("user_bounce_rate", max_value=0.3, target_value=0.1, severity=AlertSeverity.MEDIUM),
            
            # Report Generation KPIs
            KPIThreshold("reports_generated_hourly", min_value=10, target_value=50, severity=AlertSeverity.HIGH),
            KPIThreshold("report_generation_success_rate", min_value=0.95, target_value=0.99, severity=AlertSeverity.CRITICAL),
            KPIThreshold("report_avg_generation_time", max_value=30.0, target_value=10.0, severity=AlertSeverity.HIGH),
            
            # Query Performance KPIs
            KPIThreshold("queries_executed_hourly", min_value=50, target_value=200, severity=AlertSeverity.MEDIUM),
            KPIThreshold("query_success_rate", min_value=0.98, target_value=0.995, severity=AlertSeverity.HIGH),
            KPIThreshold("query_avg_execution_time", max_value=5.0, target_value=2.0, severity=AlertSeverity.HIGH),
            
            # System Performance KPIs
            KPIThreshold("api_response_time_p95", max_value=2000, target_value=500, severity=AlertSeverity.HIGH),
            KPIThreshold("system_availability", min_value=0.999, target_value=0.9999, severity=AlertSeverity.CRITICAL),
            KPIThreshold("error_rate", max_value=0.01, target_value=0.001, severity=AlertSeverity.HIGH),
            
            # Oracle Integration KPIs
            KPIThreshold("oracle_connection_pool_usage", max_value=0.8, target_value=0.5, severity=AlertSeverity.MEDIUM),
            KPIThreshold("oracle_query_cache_hit_rate", min_value=0.7, target_value=0.9, severity=AlertSeverity.MEDIUM),
            
            # Business Value KPIs
            KPIThreshold("revenue_per_user_monthly", min_value=50, target_value=200, severity=AlertSeverity.LOW),
            KPIThreshold("customer_satisfaction_score", min_value=4.0, target_value=4.5, severity=AlertSeverity.MEDIUM),
            KPIThreshold("feature_adoption_rate", min_value=0.6, target_value=0.8, severity=AlertSeverity.LOW),
        ]
        
        for kpi in default_kpis:
            self.kpi_thresholds[kpi.metric_name] = kpi
    
    def record_metric(self, 
                     name: str, 
                     value: float, 
                     metric_type: MetricType = MetricType.GAUGE,
                     labels: Dict[str, str] = None,
                     unit: str = "",
                     description: str = "") -> None:
        """Record a business metric"""
        
        metric = BusinessMetric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            unit=unit,
            description=description
        )
        
        self.metrics.append(metric)
        
        # Update aggregated metrics
        self._update_aggregated_metrics(metric)
        
        # Check for KPI violations
        self._check_kpi_thresholds(metric)
    
    def _update_aggregated_metrics(self, metric: BusinessMetric) -> None:
        """Update aggregated metrics for dashboard display"""
        
        key = f"{metric.name}_{metric.metric_type.value}"
        
        if key not in self.aggregated_metrics:
            self.aggregated_metrics[key] = {
                "name": metric.name,
                "type": metric.metric_type.value,
                "current_value": metric.value,
                "unit": metric.unit,
                "description": metric.description,
                "last_updated": metric.timestamp.isoformat(),
                "history": [],
                "trend": "stable"
            }
        else:
            agg = self.aggregated_metrics[key]
            previous_value = agg["current_value"]
            agg["current_value"] = metric.value
            agg["last_updated"] = metric.timestamp.isoformat()
            
            # Calculate trend
            if metric.value > previous_value * 1.05:  # 5% increase
                agg["trend"] = "increasing"
            elif metric.value < previous_value * 0.95:  # 5% decrease
                agg["trend"] = "decreasing"
            else:
                agg["trend"] = "stable"
        
        # Keep limited history
        self.aggregated_metrics[key]["history"].append({
            "value": metric.value,
            "timestamp": metric.timestamp.isoformat()
        })
        
        # Keep only last 100 data points
        if len(self.aggregated_metrics[key]["history"]) > 100:
            self.aggregated_metrics[key]["history"] = self.aggregated_metrics[key]["history"][-100:]
    
    def _check_kpi_thresholds(self, metric: BusinessMetric) -> None:
        """Check if metric violates KPI thresholds"""
        
        if metric.name not in self.kpi_thresholds:
            return
        
        threshold = self.kpi_thresholds[metric.name]
        if not threshold.enabled:
            return
        
        violations = []
        
        # Check minimum threshold
        if threshold.min_value is not None and metric.value < threshold.min_value:
            violations.append(f"Below minimum threshold: {metric.value} < {threshold.min_value}")
        
        # Check maximum threshold
        if threshold.max_value is not None and metric.value > threshold.max_value:
            violations.append(f"Above maximum threshold: {metric.value} > {threshold.max_value}")
        
        # Check target deviation (warn if >20% away from target)
        if threshold.target_value is not None:
            deviation = abs(metric.value - threshold.target_value) / threshold.target_value
            if deviation > 0.2:  # 20% deviation
                violations.append(f"Significant deviation from target: {metric.value} (target: {threshold.target_value})")
        
        # Log violations
        if violations:
            self._handle_kpi_violation(metric, threshold, violations)
    
    def _handle_kpi_violation(self, 
                            metric: BusinessMetric, 
                            threshold: KPIThreshold, 
                            violations: List[str]) -> None:
        """Handle KPI threshold violations"""
        
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "metric_name": metric.name,
            "current_value": metric.value,
            "severity": threshold.severity.value,
            "violations": violations,
            "labels": metric.labels,
            "unit": metric.unit
        }
        
        # Log alert (in real implementation, send to alerting system)
        print(f"🚨 KPI ALERT [{threshold.severity.value.upper()}]: {metric.name}")
        print(f"   Current Value: {metric.value} {metric.unit}")
        print(f"   Violations: {', '.join(violations)}")
        
        # Store alert for dashboard
        if "alerts" not in self.aggregated_metrics:
            self.aggregated_metrics["alerts"] = []
        
        self.aggregated_metrics["alerts"].append(alert)
        
        # Keep only last 50 alerts
        if len(self.aggregated_metrics["alerts"]) > 50:
            self.aggregated_metrics["alerts"] = self.aggregated_metrics["alerts"][-50:]
    
    # Business Metric Recording Methods
    
    def record_user_login(self, user_id: str, session_duration: Optional[float] = None) -> None:
        """Record user login event"""
        self.record_metric("user_logins_total", 1, MetricType.COUNTER, 
                          labels={"user_id": user_id}, description="Total user logins")
        
        if session_duration:
            self.record_metric("user_session_duration", session_duration, MetricType.TIMER,
                              labels={"user_id": user_id}, unit="seconds", description="User session duration")
    
    def record_report_generation(self, 
                               report_id: str, 
                               generation_time: float, 
                               success: bool,
                               user_id: str = None) -> None:
        """Record report generation event"""
        
        labels = {"report_id": report_id, "status": "success" if success else "failure"}
        if user_id:
            labels["user_id"] = user_id
        
        self.record_metric("reports_generated_total", 1, MetricType.COUNTER, 
                          labels=labels, description="Total reports generated")
        
        if success:
            self.record_metric("report_generation_time", generation_time, MetricType.TIMER,
                              labels=labels, unit="seconds", description="Report generation time")
        
        # Update success rate
        self._update_success_rate("report_generation_success_rate", success)
    
    def record_query_execution(self, 
                             query_hash: str, 
                             execution_time: float, 
                             success: bool,
                             row_count: int = 0,
                             cache_hit: bool = False) -> None:
        """Record query execution event"""
        
        labels = {
            "query_hash": query_hash, 
            "status": "success" if success else "failure",
            "cache_hit": str(cache_hit)
        }
        
        self.record_metric("queries_executed_total", 1, MetricType.COUNTER,
                          labels=labels, description="Total queries executed")
        
        if success:
            self.record_metric("query_execution_time", execution_time, MetricType.TIMER,
                              labels=labels, unit="seconds", description="Query execution time")
            
            self.record_metric("query_result_rows", row_count, MetricType.GAUGE,
                              labels=labels, unit="rows", description="Query result row count")
        
        # Update success rate
        self._update_success_rate("query_success_rate", success)
        
        # Update cache hit rate
        if cache_hit:
            self.record_metric("cache_hits_total", 1, MetricType.COUNTER, description="Cache hits")
        else:
            self.record_metric("cache_misses_total", 1, MetricType.COUNTER, description="Cache misses")
    
    def record_api_request(self, 
                          endpoint: str, 
                          method: str, 
                          response_time: float, 
                          status_code: int) -> None:
        """Record API request metrics"""
        
        labels = {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code),
            "status_class": f"{status_code // 100}xx"
        }
        
        self.record_metric("api_requests_total", 1, MetricType.COUNTER,
                          labels=labels, description="Total API requests")
        
        self.record_metric("api_response_time", response_time, MetricType.TIMER,
                          labels=labels, unit="milliseconds", description="API response time")
        
        # Track error rate
        success = 200 <= status_code < 400
        if not success:
            self.record_metric("api_errors_total", 1, MetricType.COUNTER,
                              labels=labels, description="API errors")
    
    def record_business_value(self, metric_name: str, value: float, user_id: str = None) -> None:
        """Record business value metrics"""
        
        labels = {}
        if user_id:
            labels["user_id"] = user_id
        
        self.record_metric(metric_name, value, MetricType.GAUGE,
                          labels=labels, description=f"Business metric: {metric_name}")
    
    def _update_success_rate(self, metric_name: str, success: bool) -> None:
        """Update success rate metric using sliding window"""
        
        # Simple implementation - in production, use time-series database
        if metric_name not in self.aggregated_metrics:
            self.aggregated_metrics[metric_name] = {
                "successes": 0,
                "total": 0,
                "rate": 1.0
            }
        
        metrics = self.aggregated_metrics[metric_name]
        metrics["total"] += 1
        if success:
            metrics["successes"] += 1
        
        metrics["rate"] = metrics["successes"] / metrics["total"] if metrics["total"] > 0 else 0
        
        # Record the calculated rate
        self.record_metric(metric_name, metrics["rate"], MetricType.GAUGE,
                          unit="ratio", description=f"Success rate for {metric_name}")
    
    def get_kpi_dashboard(self) -> Dict[str, Any]:
        """Generate KPI dashboard data"""
        
        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "kpis": {},
            "alerts": self.aggregated_metrics.get("alerts", []),
            "summary": {
                "total_metrics": len(self.metrics),
                "active_alerts": len([a for a in self.aggregated_metrics.get("alerts", []) 
                                    if a.get("severity") in ["high", "critical"]]),
                "kpis_in_target": 0,
                "kpis_total": len(self.kpi_thresholds)
            }
        }
        
        # Calculate KPI status
        for name, threshold in self.kpi_thresholds.items():
            if not threshold.enabled:
                continue
            
            # Get current metric value
            current_value = None
            for key, agg in self.aggregated_metrics.items():
                if agg.get("name") == name:
                    current_value = agg.get("current_value")
                    break
            
            if current_value is None:
                status = "no_data"
                health_score = 0
            else:
                # Calculate KPI health
                within_min = threshold.min_value is None or current_value >= threshold.min_value
                within_max = threshold.max_value is None or current_value <= threshold.max_value
                
                if within_min and within_max:
                    status = "healthy"
                    health_score = 100
                    dashboard["summary"]["kpis_in_target"] += 1
                else:
                    status = "violation"
                    # Calculate severity-based health score
                    if threshold.severity == AlertSeverity.CRITICAL:
                        health_score = 0
                    elif threshold.severity == AlertSeverity.HIGH:
                        health_score = 25
                    elif threshold.severity == AlertSeverity.MEDIUM:
                        health_score = 50
                    else:
                        health_score = 75
            
            dashboard["kpis"][name] = {
                "current_value": current_value,
                "target_value": threshold.target_value,
                "min_value": threshold.min_value,
                "max_value": threshold.max_value,
                "status": status,
                "health_score": health_score,
                "severity": threshold.severity.value
            }
        
        return dashboard
    
    def export_metrics(self, format: str = "prometheus") -> str:
        """Export metrics in specified format"""
        
        if format == "prometheus":
            return self._export_prometheus()
        elif format == "json":
            return json.dumps([asdict(m) for m in self.metrics[-100:]], default=str, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        
        lines = []
        
        # Group metrics by name
        metric_groups = {}
        for metric in self.metrics[-1000:]:  # Last 1000 metrics
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric)
        
        for name, metrics in metric_groups.items():
            # Get latest metric for help and type
            latest = metrics[-1]
            
            # Add help and type
            lines.append(f"# HELP {name} {latest.description or 'Business metric'}")
            lines.append(f"# TYPE {name} {latest.metric_type.value}")
            
            # Add metric samples
            for metric in metrics[-10:]:  # Last 10 samples
                labels_str = ""
                if metric.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                timestamp_ms = int(metric.timestamp.timestamp() * 1000)
                lines.append(f"{name}{labels_str} {metric.value} {timestamp_ms}")
        
        return "\n".join(lines)

# Global metrics collector instance
business_metrics = BusinessMetricsCollector()

# Helper functions for easy metric recording
def track_user_login(user_id: str, session_duration: float = None):
    business_metrics.record_user_login(user_id, session_duration)

def track_report_generation(report_id: str, generation_time: float, success: bool, user_id: str = None):
    business_metrics.record_report_generation(report_id, generation_time, success, user_id)

def track_query_execution(query_hash: str, execution_time: float, success: bool, row_count: int = 0, cache_hit: bool = False):
    business_metrics.record_query_execution(query_hash, execution_time, success, row_count, cache_hit)

def track_api_request(endpoint: str, method: str, response_time: float, status_code: int):
    business_metrics.record_api_request(endpoint, method, response_time, status_code)

def track_business_value(metric_name: str, value: float, user_id: str = None):
    business_metrics.record_business_value(metric_name, value, user_id)

def get_kpi_dashboard():
    return business_metrics.get_kpi_dashboard()

def export_metrics(format: str = "prometheus"):
    return business_metrics.export_metrics(format)

# Example usage and testing
if __name__ == "__main__":
    # Simulate some business metrics
    import random
    import time
    
    print("🚀 Oatie AI Business Metrics Simulation")
    
    # Simulate user activity
    for i in range(10):
        user_id = f"user_{random.randint(1, 100)}"
        session_duration = random.uniform(300, 1800)  # 5-30 minutes
        track_user_login(user_id, session_duration)
        
        # Simulate report generation
        report_id = f"report_{random.choice(['sales', 'finance', 'operations'])}"
        generation_time = random.uniform(5, 25)
        success = random.random() > 0.05  # 95% success rate
        track_report_generation(report_id, generation_time, success, user_id)
        
        # Simulate query execution
        query_hash = f"query_{random.randint(1, 50)}"
        execution_time = random.uniform(0.1, 10)
        query_success = random.random() > 0.02  # 98% success rate
        row_count = random.randint(10, 10000) if query_success else 0
        cache_hit = random.random() > 0.3  # 70% cache hit rate
        track_query_execution(query_hash, execution_time, query_success, row_count, cache_hit)
        
        # Simulate API requests
        endpoint = random.choice(["/api/v1/reports", "/api/v1/queries", "/api/v1/users"])
        method = random.choice(["GET", "POST"])
        response_time = random.uniform(50, 2000)
        status_code = random.choices([200, 201, 400, 404, 500], weights=[85, 5, 5, 3, 2])[0]
        track_api_request(endpoint, method, response_time, status_code)
        
        time.sleep(0.1)  # Small delay
    
    # Add some business value metrics
    track_business_value("revenue_per_user_monthly", random.uniform(45, 250))
    track_business_value("customer_satisfaction_score", random.uniform(3.5, 5.0))
    track_business_value("feature_adoption_rate", random.uniform(0.5, 0.9))
    
    # Get KPI dashboard
    dashboard = get_kpi_dashboard()
    print(f"\n📊 KPI Dashboard Summary:")
    print(f"Total Metrics: {dashboard['summary']['total_metrics']}")
    print(f"Active Alerts: {dashboard['summary']['active_alerts']}")
    print(f"KPIs in Target: {dashboard['summary']['kpis_in_target']}/{dashboard['summary']['kpis_total']}")
    
    # Show some KPI status
    print(f"\n🎯 Key Performance Indicators:")
    for name, kpi in list(dashboard['kpis'].items())[:5]:
        print(f"  {name}: {kpi['current_value']} (target: {kpi['target_value']}) - {kpi['status']}")
    
    # Export metrics
    print(f"\n📈 Exported {len(business_metrics.metrics)} metrics in Prometheus format")
    print("Ready for monitoring and alerting integration!")