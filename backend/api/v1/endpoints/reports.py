"""
Report management endpoints with enterprise features and AI-powered template intelligence
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from backend.api.v1.endpoints.auth import oauth2_scheme
from backend.core.security import AuditEventType
from backend.core.template_intelligence import (
    TemplateIntelligenceEngine, 
    TableSchema, 
    SchemaField, 
    DataType, 
    TemplateType,
    PerformanceMetrics
)
from backend.core.oracle_bi_publisher import (
    OracleBIPublisherManager,
    OracleConnection,
    DeploymentStatus
)

router = APIRouter()


class ReportTemplate(BaseModel):
    id: str
    name: str
    description: str
    oracle_template_path: str
    parameters: dict
    created_at: datetime
    updated_at: datetime


class ReportExecution(BaseModel):
    id: str
    template_id: str
    parameters: dict
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    download_url: Optional[str]


class CreateReportRequest(BaseModel):
    template_id: str
    parameters: dict
    format: str = "PDF"
    notify_on_completion: bool = True


# New AI-powered template intelligence models
class SchemaAnalysisRequest(BaseModel):
    table_name: str
    connection_string: Optional[str] = None
    schema_fields: List[Dict[str, Any]]
    relationships: Optional[List[str]] = None


class TemplateGenerationRequest(BaseModel):
    schema_analysis: SchemaAnalysisRequest
    template_type: TemplateType
    user_preferences: Optional[Dict[str, Any]] = None
    auto_deploy: bool = False


class PerformanceOptimizationRequest(BaseModel):
    template_id: str
    current_metrics: Optional[Dict[str, Any]] = None
    optimization_level: str = "standard"  # basic, standard, aggressive


class TemplateVersionRequest(BaseModel):
    template_id: str
    changes: List[str]
    version_notes: Optional[str] = None


class ABTestRequest(BaseModel):
    template_a_id: str
    template_b_id: str
    test_name: str
    traffic_split: int = 50
    duration_days: int = 14
    success_metrics: List[str] = ["execution_time", "user_satisfaction"]


class DeploymentRequest(BaseModel):
    template_id: str
    target_folder: str = "/AI_Generated"
    deployment_options: Optional[Dict[str, Any]] = None
    schedule_deployment: bool = False


# Enhanced response models
class TemplateGenerationResponse(BaseModel):
    template_id: str
    generation_status: str
    ai_confidence: float
    estimated_performance: Dict[str, Any]
    preview_data: List[Dict[str, Any]]
    optimization_suggestions: List[Dict[str, str]]


class PerformanceAnalysisResponse(BaseModel):
    template_id: str
    analysis_results: Dict[str, Any]
    optimization_recommendations: List[Dict[str, Any]]
    estimated_improvements: Dict[str, Any]


class DeploymentResponse(BaseModel):
    deployment_id: str
    template_id: str
    oracle_path: str
    status: DeploymentStatus
    estimated_completion: Optional[str] = None


@router.get("/templates", response_model=List[ReportTemplate])
async def get_report_templates(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: str = Depends(oauth2_scheme)
):
    """Get available report templates with Oracle Redwood design"""
    # Mock data for demonstration
    templates = [
        {
            "id": "sales_summary",
            "name": "Sales Summary Report",
            "description": "Comprehensive sales performance analysis with AI insights",
            "oracle_template_path": "/oracle/bi/reports/sales_summary.rtf",
            "parameters": {
                "date_range": {"type": "date_range", "required": True},
                "region": {"type": "select", "options": ["North", "South", "East", "West"]},
                "include_forecast": {"type": "boolean", "default": True}
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": "financial_dashboard",
            "name": "Financial Performance Dashboard",
            "description": "Executive financial dashboard with KPIs and trends",
            "oracle_template_path": "/oracle/bi/reports/financial_dashboard.rtf",
            "parameters": {
                "quarter": {"type": "select", "options": ["Q1", "Q2", "Q3", "Q4"]},
                "year": {"type": "number", "default": 2024},
                "department": {"type": "multi_select", "options": ["Finance", "Sales", "Operations"]}
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    # Apply pagination
    paginated_templates = templates[offset:offset + limit]
    
    # Log access
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_ACCESS,
        resource="report_templates",
        details={"count": len(paginated_templates)}
    )
    
    return paginated_templates


@router.post("/execute", response_model=ReportExecution)
async def execute_report(
    request: Request,
    report_request: CreateReportRequest,
    token: str = Depends(oauth2_scheme)
):
    """Execute report with AI-enhanced Oracle BI Publisher integration"""
    
    # Validate template exists
    template_id = report_request.template_id
    if template_id not in ["sales_summary", "financial_dashboard"]:
        raise HTTPException(status_code=404, detail="Report template not found")
    
    # Create execution record
    execution = {
        "id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "template_id": template_id,
        "parameters": report_request.parameters,
        "status": "PROCESSING",
        "created_at": datetime.now(),
        "completed_at": None,
        "download_url": None
    }
    
    # Log report generation
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.REPORT_GENERATED,
        resource=f"report_template_{template_id}",
        details={
            "execution_id": execution["id"],
            "format": report_request.format,
            "parameters": report_request.parameters
        }
    )
    
    # In production, this would trigger async report generation
    # For demo, simulate immediate completion
    execution["status"] = "COMPLETED"
    execution["completed_at"] = datetime.now()
    execution["download_url"] = f"/api/v1/reports/{execution['id']}/download"
    
    return execution


@router.get("/{execution_id}/status")
async def get_report_status(
    execution_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get report execution status"""
    # Mock status check
    return {
        "execution_id": execution_id,
        "status": "COMPLETED",
        "progress": 100,
        "estimated_completion": None
    }


@router.get("/{execution_id}/download")
async def download_report(
    request: Request,
    execution_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Download completed report"""
    
    # Log data export
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_EXPORT,
        resource=f"report_{execution_id}",
        details={"format": "PDF", "download": True}
    )
    
    # In production, return actual file
    return {
        "message": f"Report {execution_id} download would start here",
        "download_url": f"/files/reports/{execution_id}.pdf"
    }


@router.delete("/{execution_id}")
async def delete_report_execution(
    request: Request,
    execution_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Delete report execution"""
    
    # Log deletion
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_ACCESS,
        resource=f"report_{execution_id}",
        details={"action": "delete"}
    )
    
    return {"message": f"Report execution {execution_id} deleted"}


# Initialize AI-powered template intelligence engine
template_engine = TemplateIntelligenceEngine()


@router.post("/templates/generate", response_model=TemplateGenerationResponse)
async def generate_template_from_schema(
    request: Request,
    generation_request: TemplateGenerationRequest,
    token: str = Depends(oauth2_scheme)
):
    """Auto-generate Oracle BI Publisher template from database schema"""
    
    # Convert request to internal schema format
    schema_fields = []
    for field_data in generation_request.schema_analysis.schema_fields:
        field = SchemaField(
            name=field_data["name"],
            data_type=DataType(field_data["data_type"]),
            nullable=field_data.get("nullable", True),
            primary_key=field_data.get("primary_key", False),
            foreign_key=field_data.get("foreign_key"),
            display_name=field_data.get("display_name"),
            description=field_data.get("description")
        )
        schema_fields.append(field)
    
    table_schema = TableSchema(
        table_name=generation_request.schema_analysis.table_name,
        fields=schema_fields,
        relationships=generation_request.schema_analysis.relationships or []
    )
    
    # Generate template using AI engine
    template_data = await template_engine.generate_template(
        table_schema,
        generation_request.template_type,
        generation_request.user_preferences
    )
    
    # Log template generation
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.REPORT_GENERATED,
        resource=f"ai_template_{template_data['metadata']['template_id']}",
        details={
            "schema_source": table_schema.table_name,
            "template_type": generation_request.template_type,
            "ai_confidence": template_data['metadata']['ai_confidence']
        }
    )
    
    # Auto-deploy if requested
    deployment_info = None
    if generation_request.auto_deploy:
        # This would trigger deployment to Oracle BI Publisher
        deployment_info = {"auto_deployment": "scheduled"}
    
    return TemplateGenerationResponse(
        template_id=template_data['metadata']['template_id'],
        generation_status="completed",
        ai_confidence=template_data['metadata']['ai_confidence'],
        estimated_performance=template_data['structure'],
        preview_data=template_data['preview_data'],
        optimization_suggestions=template_data['optimizations']
    )


@router.post("/templates/optimize", response_model=PerformanceAnalysisResponse)
async def optimize_template_performance(
    request: Request,
    optimization_request: PerformanceOptimizationRequest,
    token: str = Depends(oauth2_scheme)
):
    """Analyze and optimize template performance with AI recommendations"""
    
    # Convert current metrics if provided
    current_metrics = None
    if optimization_request.current_metrics:
        metrics_data = optimization_request.current_metrics
        current_metrics = PerformanceMetrics(
            execution_time_ms=metrics_data.get("execution_time_ms", 0),
            memory_usage_mb=metrics_data.get("memory_usage_mb", 0),
            query_complexity=metrics_data.get("query_complexity", 1),
            cache_hit_ratio=metrics_data.get("cache_hit_ratio", 0.0),
            optimization_score=metrics_data.get("optimization_score", 50),
            bottlenecks=metrics_data.get("bottlenecks", [])
        )
    
    # Perform optimization analysis
    analysis_results = await template_engine.optimize_template_performance(
        optimization_request.template_id,
        current_metrics
    )
    
    # Log optimization analysis
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_ACCESS,
        resource=f"template_optimization_{optimization_request.template_id}",
        details={
            "optimization_level": optimization_request.optimization_level,
            "recommendations_count": len(analysis_results["optimization_recommendations"])
        }
    )
    
    return PerformanceAnalysisResponse(
        template_id=optimization_request.template_id,
        analysis_results=analysis_results,
        optimization_recommendations=analysis_results["optimization_recommendations"],
        estimated_improvements=analysis_results["estimated_improvements"]
    )


@router.post("/templates/deploy", response_model=DeploymentResponse)
async def deploy_template_to_oracle(
    request: Request,
    deployment_request: DeploymentRequest,
    token: str = Depends(oauth2_scheme)
):
    """Deploy template to Oracle BI Publisher with automated pipeline"""
    
    # Initialize Oracle BI Publisher connection (mock for demonstration)
    oracle_connection = OracleConnection(
        server_url="https://bi.company.com",
        username="ai_service",
        password="secure_password"  # This would come from secure config
    )
    
    oracle_manager = OracleBIPublisherManager(oracle_connection)
    
    try:
        await oracle_manager.initialize()
        
        # Get template data from cache/storage
        template_data = template_engine.template_cache.get(deployment_request.template_id)
        if not template_data:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Deploy to Oracle BI Publisher
        deployment_result = await oracle_manager.deploy_ai_generated_template(
            template_data,
            deployment_request.target_folder
        )
        
        # Log deployment
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.REPORT_GENERATED,
            resource=f"oracle_deployment_{deployment_result['template_id']}",
            details={
                "oracle_path": deployment_result["oracle_path"],
                "deployment_id": deployment_result["deploy_result"]["deployment_id"]
            }
        )
        
        return DeploymentResponse(
            deployment_id=deployment_result["deploy_result"]["deployment_id"],
            template_id=deployment_request.template_id,
            oracle_path=deployment_result["oracle_path"],
            status=DeploymentStatus.DEPLOYING,
            estimated_completion="2-3 minutes"
        )
        
    finally:
        await oracle_manager.close()


@router.get("/templates/{template_id}/versions")
async def get_template_versions(
    template_id: str,
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    token: str = Depends(oauth2_scheme)
):
    """Get version history for template"""
    
    versions = template_engine.version_store.get(template_id, [])
    
    # Log access
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_ACCESS,
        resource=f"template_versions_{template_id}",
        details={"version_count": len(versions)}
    )
    
    return {
        "template_id": template_id,
        "versions": [
            {
                "version_id": v.version_id,
                "version_number": v.version_number,
                "created_at": v.created_at,
                "created_by": v.created_by,
                "changes": v.changes,
                "is_active": v.is_active
            }
            for v in versions[-limit:]  # Return latest versions
        ],
        "total_versions": len(versions)
    }


@router.post("/templates/{template_id}/versions")
async def create_template_version(
    template_id: str,
    request: Request,
    version_request: TemplateVersionRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create new version of template"""
    
    # Extract user from token (simplified)
    created_by = "ai_service_user"  # This would come from token validation
    
    # Create new version
    new_version = await template_engine.create_template_version(
        template_id,
        version_request.changes,
        created_by
    )
    
    # Log version creation
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.REPORT_GENERATED,
        resource=f"template_version_{new_version.version_id}",
        details={
            "template_id": template_id,
            "version_number": new_version.version_number,
            "changes_count": len(version_request.changes)
        }
    )
    
    return {
        "version_id": new_version.version_id,
        "template_id": template_id,
        "version_number": new_version.version_number,
        "created_at": new_version.created_at,
        "changes": new_version.changes
    }


@router.post("/templates/test")
async def setup_ab_test(
    request: Request,
    ab_test_request: ABTestRequest,
    token: str = Depends(oauth2_scheme)
):
    """Setup A/B testing for template performance comparison"""
    
    # Setup A/B test using template engine
    test_config = await template_engine.setup_ab_test(
        ab_test_request.template_a_id,
        ab_test_request.template_b_id,
        {
            "test_name": ab_test_request.test_name,
            "traffic_split": ab_test_request.traffic_split,
            "duration_days": ab_test_request.duration_days,
            "metrics": ab_test_request.success_metrics
        }
    )
    
    # Log A/B test setup
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.REPORT_GENERATED,
        resource=f"ab_test_{test_config['test_id']}",
        details={
            "template_a": ab_test_request.template_a_id,
            "template_b": ab_test_request.template_b_id,
            "duration_days": ab_test_request.duration_days
        }
    )
    
    return {
        "test_id": test_config["test_id"],
        "status": "active",
        "configuration": test_config,
        "monitoring_url": f"/api/v1/reports/test/{test_config['test_id']}/results"
    }


@router.get("/templates/test/{test_id}/results")
async def get_ab_test_results(
    test_id: str,
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get A/B test results and performance comparison"""
    
    # Simulate A/B test results
    results = {
        "test_id": test_id,
        "status": "completed",
        "duration_days": 14,
        "results": {
            "template_a": {
                "avg_execution_time_ms": 1800,
                "user_satisfaction": 4.2,
                "error_rate": 0.02,
                "usage_count": 1250
            },
            "template_b": {
                "avg_execution_time_ms": 1200,
                "user_satisfaction": 4.6,
                "error_rate": 0.01,
                "usage_count": 1300
            }
        },
        "winner": "template_b",
        "confidence_level": 95.5,
        "recommendation": "Deploy template_b as primary template"
    }
    
    # Log results access
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_ACCESS,
        resource=f"ab_test_results_{test_id}",
        details={"winner": results["winner"]}
    )
    
    return results


@router.get("/templates/analytics/dashboard")
async def get_template_analytics_dashboard(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    token: str = Depends(oauth2_scheme)
):
    """Get comprehensive template analytics dashboard"""
    
    # Generate analytics dashboard data
    dashboard_data = {
        "period_days": days,
        "summary": {
            "total_templates": 24,
            "ai_generated_templates": 18,
            "avg_ai_confidence": 0.87,
            "total_deployments": 42,
            "successful_deployments": 40,
            "performance_score": 8.4
        },
        "template_performance": {
            "top_performers": [
                {"template_id": "sales_summary_ai_v3", "score": 9.2},
                {"template_id": "financial_dashboard_ai_v2", "score": 8.8}
            ],
            "needs_optimization": [
                {"template_id": "complex_report_v1", "score": 6.1}
            ]
        },
        "ai_insights": {
            "optimization_opportunities": 3,
            "recommended_improvements": 7,
            "predicted_performance_gains": "35% average improvement"
        },
        "usage_trends": {
            "daily_executions": [45, 52, 48, 61, 58, 67, 72],
            "oracle_integration_health": "excellent",
            "cache_efficiency": 0.78
        }
    }
    
    # Log dashboard access
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_ACCESS,
        resource="template_analytics_dashboard",
        details={"period_days": days}
    )
    
    return dashboard_data