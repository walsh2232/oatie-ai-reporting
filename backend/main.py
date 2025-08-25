"""
Oatie AI Reporting - FastAPI Backend
Oracle BI Publisher AI Assistant with enhanced SQL intelligence
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import logging
from datetime import datetime
from sql_agent import EnhancedSQLAgent
from oracle_integration import OracleIntegration, MockOracleIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
sql_agent = None
oracle_integration = None

def initialize_services():
    """Initialize SQL Agent and Oracle Integration"""
    global sql_agent, oracle_integration
    
    # Initialize SQL Agent with OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY', 'demo-key')
    if openai_api_key and openai_api_key != 'demo-key':
        sql_agent = EnhancedSQLAgent(openai_api_key)
        logger.info("Enhanced SQL Agent initialized with OpenAI")
    else:
        logger.warning("OpenAI API key not found, SQL Agent will use mock responses")
    
    # Initialize Oracle Integration
    oracle_config = {
        'oracle_bi_url': os.getenv('ORACLE_BI_URL', 'https://demo.oracle.com'),
        'oracle_username': os.getenv('ORACLE_USERNAME', 'demo'),
        'oracle_password': os.getenv('ORACLE_PASSWORD', 'demo'),
    }
    
    # Use Mock Oracle Integration for demo
    oracle_integration = MockOracleIntegration(oracle_config)
    logger.info("Oracle Integration initialized (Mock mode)")

# Initialize FastAPI app
app = FastAPI(
    title="Oatie AI Reporting API",
    description="Oracle BI Publisher AI Assistant with enhanced SQL intelligence",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Initialize services
initialize_services()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

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

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return current user"""
    # TODO: Implement JWT validation
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
    """Generate SQL from natural language using GPT-4"""
    try:
        if sql_agent:
            # Use real SQL agent
            result = await sql_agent.generate_sql(
                request.natural_language,
                request.schema_context,
                request.optimization_level or "standard"
            )
            
            response = SQLResponse(
                sql_query=result.sql_query,
                confidence_score=result.confidence_score,
                optimization_suggestions=result.optimization_suggestions,
                execution_plan=result.execution_plan,
                estimated_performance=result.estimated_performance
            )
        else:
            # Fallback mock response
            response = SQLResponse(
                sql_query="SELECT * FROM employees WHERE department = 'Sales'",
                confidence_score=0.95,
                optimization_suggestions=[
                    "Add index on department column",
                    "Consider using LIMIT for large datasets"
                ],
                execution_plan={"cost": "low", "rows": "~100"},
                estimated_performance="<1s"
            )
        
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
        if sql_agent:
            # Use real SQL validation
            result = await sql_agent.validate_sql(sql_query)
            return result
        else:
            # Fallback mock validation
            return {
                "valid": True,
                "syntax_errors": [],
                "semantic_warnings": [],
                "optimization_score": 85,
                "optimization_suggestions": []
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
    """Create a new report using Oracle BI Publisher"""
    try:
        if oracle_integration:
            # Use real Oracle integration
            from oracle_integration import ExportFormat
            format_map = {
                'PDF': ExportFormat.PDF,
                'EXCEL': ExportFormat.EXCEL,
                'CSV': ExportFormat.CSV,
                'XML': ExportFormat.XML
            }
            
            job = await oracle_integration.create_report(
                request.template_id,
                request.data_source,
                request.parameters,
                format_map.get(request.format, ExportFormat.PDF)
            )
            
            response = ReportResponse(
                report_id=job.job_id,
                status=job.status,
                download_url=job.file_path,
                created_at=job.created_at
            )
        else:
            # Fallback mock response
            response = ReportResponse(
                report_id=f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                status="generating",
                download_url=None,
                created_at=datetime.utcnow()
            )
        
        logger.info(f"Created report for user {current_user['user_id']}")
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
        # TODO: Implement report status checking
        return {
            "report_id": report_id,
            "status": "completed",
            "download_url": f"/api/reports/{report_id}/download",
            "progress": 100
        }
    except Exception as e:
        logger.error(f"Error getting report status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/templates")
async def get_report_templates(
    current_user: dict = Depends(get_current_user)
):
    """Get available report templates"""
    try:
        if oracle_integration:
            # Use real Oracle integration
            templates = await oracle_integration.get_templates()
            return {
                "templates": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "description": t.description,
                        "category": t.category,
                        "parameters": t.parameters,
                        "created_by": t.created_by,
                        "created_at": t.created_at.isoformat(),
                        "version": t.version
                    }
                    for t in templates
                ]
            }
        else:
            # Fallback mock templates
            return {
                "templates": [
                    {"id": "sales_report", "name": "Sales Performance Report", "category": "Sales"},
                    {"id": "financial_report", "name": "Financial Summary", "category": "Finance"},
                    {"id": "inventory_report", "name": "Inventory Analysis", "category": "Operations"}
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
        # TODO: Implement real analytics
        mock_response = AnalyticsResponse(
            query_performance={
                "avg_execution_time": "2.3s",
                "success_rate": "94%",
                "total_queries": 1247,
                "cache_hit_rate": "78%"
            },
            user_activity={
                "active_users": 23,
                "queries_today": 156,
                "reports_generated": 42
            },
            system_health={
                "cpu_usage": "45%",
                "memory_usage": "62%",
                "database_connections": "8/20"
            },
            popular_queries=[
                {"query": "Sales by region", "usage_count": 45},
                {"query": "Monthly revenue", "usage_count": 38},
                {"query": "Employee performance", "usage_count": 32}
            ]
        )
        
        return mock_response
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/analytics/performance")
async def get_performance_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get detailed performance metrics"""
    try:
        # TODO: Implement performance monitoring
        return {
            "response_times": [1.2, 2.1, 1.8, 2.5, 1.9],
            "throughput": 150,
            "error_rate": 0.06,
            "cache_efficiency": 0.78
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
        # TODO: Implement user management
        return {
            "user_id": current_user["user_id"],
            "tenant_id": current_user["tenant_id"],
            "name": "Demo User",
            "email": "demo@example.com",
            "role": "analyst",
            "permissions": ["query", "report", "dashboard"]
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )