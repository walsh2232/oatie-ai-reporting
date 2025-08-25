"""
Simplified Oatie AI Reporting - FastAPI Backend (Demo Version)
Oracle BI Publisher AI Assistant with enhanced SQL intelligence
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Oatie AI Reporting API",
    description="Oracle BI Publisher AI Assistant with enhanced SQL intelligence",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class SQLRequest(BaseModel):
    natural_language: str = Field(..., description="Natural language query")
    schema_context: Optional[Dict[str, Any]] = Field(None, description="Database schema context")
    optimization_level: Optional[str] = Field("standard", description="Query optimization level")

class SQLResponse(BaseModel):
    sql_query: str
    confidence_score: float
    optimization_suggestions: List[str]
    execution_plan: Optional[Dict[str, Any]]
    estimated_performance: Optional[str]

class ReportRequest(BaseModel):
    template_id: str
    data_source: str
    parameters: Dict[str, Any]
    format: str = Field("PDF", description="Export format: PDF, Excel, CSV, XML")

class ReportResponse(BaseModel):
    report_id: str
    status: str
    download_url: Optional[str]
    created_at: datetime

class AnalyticsResponse(BaseModel):
    query_performance: Dict[str, Any]
    user_activity: Dict[str, Any]
    system_health: Dict[str, Any]
    popular_queries: List[Dict[str, Any]]

# Mock data store
mock_reports = []
mock_queries = []

# Dependency for authentication (simplified for demo)
async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Simplified auth for demo - always returns demo user"""
    return {"user_id": "demo_user", "tenant_id": "demo_tenant"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "services": {
            "sql_agent": "active",
            "oracle_integration": "active",
            "analytics": "active",
            "cache": "active"
        }
    }

# SQL Intelligence endpoints
@app.post("/api/sql/generate", response_model=SQLResponse)
async def generate_sql(
    request: SQLRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate SQL from natural language using AI (Demo Mode)"""
    try:
        # Generate mock SQL based on input
        nl_query = request.natural_language.lower()
        
        # Simple keyword-based SQL generation for demo
        if "sales" in nl_query or "revenue" in nl_query:
            sql = "SELECT emp.name, SUM(s.amount) as total_revenue FROM employees emp JOIN sales s ON emp.id = s.employee_id WHERE s.date >= '2024-01-01' GROUP BY emp.name ORDER BY total_revenue DESC LIMIT 10;"
            confidence = 0.92
        elif "employee" in nl_query or "staff" in nl_query:
            sql = "SELECT id, name, department, salary, hire_date FROM employees WHERE hire_date >= '2024-01-01' ORDER BY hire_date DESC;"
            confidence = 0.88
        elif "inventory" in nl_query or "stock" in nl_query:
            sql = "SELECT name, category, stock, price FROM products WHERE stock < 10 ORDER BY stock ASC;"
            confidence = 0.85
        elif "customer" in nl_query:
            sql = "SELECT c.name, COUNT(o.id) as order_count, SUM(o.total) as total_spent FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id ORDER BY total_spent DESC;"
            confidence = 0.90
        else:
            sql = f"-- Generated from: {request.natural_language}\nSELECT * FROM data_table WHERE conditions_based_on_input;"
            confidence = 0.75
        
        # Mock optimization suggestions
        suggestions = []
        if "SELECT *" in sql:
            suggestions.append("Specify only required columns instead of SELECT *")
        if "LIMIT" not in sql and "employee" in nl_query:
            suggestions.append("Consider adding LIMIT for large datasets")
        if "INDEX" not in sql and confidence > 0.85:
            suggestions.append("Add appropriate indexes for better performance")
        
        response = SQLResponse(
            sql_query=sql,
            confidence_score=confidence,
            optimization_suggestions=suggestions,
            execution_plan={"estimated_cost": "medium", "estimated_rows": "~500"},
            estimated_performance="1.2s"
        )
        
        # Store query for analytics
        mock_queries.append({
            "query": request.natural_language,
            "sql": sql,
            "confidence": confidence,
            "timestamp": datetime.utcnow(),
            "user": current_user["user_id"]
        })
        
        logger.info(f"Generated SQL for user {current_user['user_id']}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/sql/validate")
async def validate_sql(
    sql_query: str,
    current_user: dict = Depends(get_current_user)
):
    """Validate SQL syntax and semantics"""
    try:
        # Simple validation logic for demo
        errors = []
        warnings = []
        score = 100
        
        # Basic syntax checks
        if not sql_query.strip():
            errors.append("SQL query cannot be empty")
            score = 0
        elif not any(keyword in sql_query.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
            errors.append("Query must contain a valid SQL statement")
            score = 0
        else:
            # Check for common issues
            if "SELECT *" in sql_query.upper():
                warnings.append("Using SELECT * may impact performance")
                score -= 15
            
            if "WHERE" not in sql_query.upper() and "SELECT" in sql_query.upper():
                warnings.append("Consider adding WHERE clause for better performance")
                score -= 10
            
            if sql_query.count("(") != sql_query.count(")"):
                errors.append("Unmatched parentheses")
                score -= 30
        
        return {
            "valid": len(errors) == 0,
            "syntax_errors": errors,
            "semantic_warnings": warnings,
            "optimization_score": max(0, score),
            "optimization_suggestions": warnings
        }
        
    except Exception as e:
        logger.error(f"Error validating SQL: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Oracle BI Publisher Integration endpoints
@app.post("/api/reports/create", response_model=ReportResponse)
async def create_report(
    request: ReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new report using Oracle BI Publisher (Demo Mode)"""
    try:
        report_id = f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Mock report creation
        report = {
            "report_id": report_id,
            "template_id": request.template_id,
            "status": "completed",
            "created_at": datetime.utcnow(),
            "user": current_user["user_id"],
            "parameters": request.parameters,
            "format": request.format
        }
        
        mock_reports.append(report)
        
        response = ReportResponse(
            report_id=report_id,
            status="completed",
            download_url=f"/api/reports/{report_id}/download",
            created_at=datetime.utcnow()
        )
        
        logger.info(f"Created report {report_id} for user {current_user['user_id']}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reports/{report_id}")
async def get_report_status(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get report generation status"""
    try:
        # Find report in mock data
        report = next((r for r in mock_reports if r["report_id"] == report_id), None)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "report_id": report_id,
            "status": report["status"],
            "download_url": f"/api/reports/{report_id}/download",
            "progress": 100,
            "created_at": report["created_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/templates")
async def get_report_templates(
    current_user: dict = Depends(get_current_user)
):
    """Get available report templates"""
    try:
        return {
            "templates": [
                {
                    "id": "sales_report",
                    "name": "Sales Performance Report",
                    "description": "Comprehensive sales performance analysis by region, product, and time period",
                    "category": "Sales",
                    "parameters": [
                        {"name": "start_date", "type": "date", "required": True},
                        {"name": "end_date", "type": "date", "required": True},
                        {"name": "region", "type": "string", "required": False}
                    ],
                    "created_by": "system",
                    "created_at": "2024-01-01T00:00:00Z",
                    "version": "1.0"
                },
                {
                    "id": "financial_report",
                    "name": "Financial Summary",
                    "description": "Quarterly financial summary with P&L, balance sheet, and cash flow",
                    "category": "Finance",
                    "parameters": [
                        {"name": "quarter", "type": "string", "required": True},
                        {"name": "year", "type": "integer", "required": True}
                    ],
                    "created_by": "system",
                    "created_at": "2024-01-01T00:00:00Z",
                    "version": "1.0"
                },
                {
                    "id": "inventory_report",
                    "name": "Inventory Analysis",
                    "description": "Current inventory levels, turnover analysis, and reorder recommendations",
                    "category": "Operations",
                    "parameters": [
                        {"name": "warehouse", "type": "string", "required": False},
                        {"name": "category", "type": "string", "required": False}
                    ],
                    "created_by": "system",
                    "created_at": "2024-01-01T00:00:00Z",
                    "version": "1.0"
                },
                {
                    "id": "hr_report",
                    "name": "HR Analytics Report",
                    "description": "Employee performance, attendance, and satisfaction metrics",
                    "category": "HR",
                    "parameters": [
                        {"name": "department", "type": "string", "required": False},
                        {"name": "period", "type": "string", "required": True}
                    ],
                    "created_by": "system",
                    "created_at": "2024-01-01T00:00:00Z",
                    "version": "1.0"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Analytics Dashboard endpoints
@app.get("/api/analytics/dashboard", response_model=AnalyticsResponse)
async def get_analytics_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get analytics dashboard data"""
    try:
        # Generate mock analytics based on stored data
        total_queries = len(mock_queries)
        total_reports = len(mock_reports)
        
        response = AnalyticsResponse(
            query_performance={
                "avg_execution_time": "1.8s",
                "success_rate": "96%",
                "total_queries": total_queries,
                "cache_hit_rate": "82%"
            },
            user_activity={
                "active_users": 15,
                "queries_today": total_queries,
                "reports_generated": total_reports
            },
            system_health={
                "cpu_usage": "42%",
                "memory_usage": "58%",
                "database_connections": "12/25"
            },
            popular_queries=[
                {"query": "Sales performance by region", "usage_count": 67},
                {"query": "Employee list with departments", "usage_count": 45},
                {"query": "Low inventory items", "usage_count": 38},
                {"query": "Customer order history", "usage_count": 29},
                {"query": "Monthly revenue trends", "usage_count": 23}
            ]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/analytics/performance")
async def get_performance_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get detailed performance metrics"""
    try:
        return {
            "response_times": [1.2, 1.8, 1.5, 2.1, 1.7, 1.9, 1.4, 1.6],
            "throughput": 125,
            "error_rate": 0.04,
            "cache_efficiency": 0.82,
            "query_success_rate": 0.96,
            "avg_query_time": 1.8
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User Management endpoints
@app.get("/api/users/profile")
async def get_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile"""
    try:
        return {
            "user_id": current_user["user_id"],
            "tenant_id": current_user["tenant_id"],
            "name": "Demo User",
            "email": "demo@oracle.com",
            "role": "analyst",
            "permissions": ["query", "report", "dashboard", "analytics"]
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Additional demo endpoints
@app.get("/api/reports/history")
async def get_report_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get report generation history"""
    try:
        # Return recent reports
        recent_reports = mock_reports[-limit:] if mock_reports else []
        
        return {
            "reports": [
                {
                    "report_id": r["report_id"],
                    "template_id": r["template_id"],
                    "status": r["status"],
                    "created_at": r["created_at"].isoformat(),
                    "format": r["format"]
                }
                for r in reversed(recent_reports)
            ]
        }
    except Exception as e:
        logger.error(f"Error getting report history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Oatie AI Reporting API server...")
    uvicorn.run(
        "main_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )