"""
Oracle BI Publisher API endpoints for enterprise integration
Provides complete Oracle BI Publisher REST API coverage with enterprise features
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from pydantic import BaseModel, Field

from backend.api.v1.endpoints.auth import oauth2_scheme
from backend.core.security import AuditEventType
from backend.integrations.oracle import OracleBIPublisherSDK
from backend.integrations.oracle.models import (
    OracleReportFormat, OracleDataSourceType, OracleReportStatus
)

logger = structlog.get_logger(__name__)
router = APIRouter()


# Request/Response Models

class OracleAuthRequest(BaseModel):
    """Oracle BI Publisher authentication request"""
    username: str
    password: str
    server_url: Optional[str] = None


class OracleAuthResponse(BaseModel):
    """Oracle BI Publisher authentication response"""
    session_id: str
    user: Dict[str, Any]
    expires_at: str
    server_url: str


class OracleReportExecuteRequest(BaseModel):
    """Oracle BI Publisher report execution request"""
    report_id: str
    format: OracleReportFormat = OracleReportFormat.PDF
    parameters: Dict[str, Any] = Field(default_factory=dict)
    async_execution: bool = True
    notify_on_completion: bool = False


class OracleDataSourceCreateRequest(BaseModel):
    """Oracle BI Publisher data source creation request"""
    name: str
    display_name: str
    type: OracleDataSourceType
    connection_string: str
    username: str
    password: str
    connection_pool_size: int = Field(default=10, ge=1, le=100)
    timeout: int = Field(default=30, ge=5, le=300)
    test_query: str = "SELECT 1 FROM DUAL"


class OracleFolderCreateRequest(BaseModel):
    """Oracle BI Publisher folder creation request"""
    path: str
    name: str
    description: Optional[str] = None
    permissions: Dict[str, List[str]] = Field(default_factory=dict)


class OracleScheduleCreateRequest(BaseModel):
    """Oracle BI Publisher report schedule creation request"""
    report_id: str
    name: str
    description: Optional[str] = None
    cron_expression: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    output_format: OracleReportFormat = OracleReportFormat.PDF
    delivery_method: str = "FILE_SYSTEM"
    delivery_config: Dict[str, Any] = Field(default_factory=dict)


class OracleBatchExecuteRequest(BaseModel):
    """Oracle BI Publisher batch execution request"""
    reports: List[OracleReportExecuteRequest]
    max_concurrent: int = Field(default=10, ge=1, le=50)


# Authentication Endpoints

@router.post("/auth/login", response_model=OracleAuthResponse)
async def oracle_auth_login(
    request: Request,
    auth_request: OracleAuthRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Authenticate with Oracle BI Publisher
    
    Establishes a session with Oracle BI Publisher using provided credentials.
    Supports both direct authentication and SSO integration.
    """
    try:
        # Get Oracle SDK instance from app state
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Authenticate with Oracle BI Publisher
        auth_result = await oracle_sdk.auth_manager.authenticate_user(
            username=auth_request.username,
            password=auth_request.password,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        if not auth_result.success:
            # Log audit event for failed login
            security_manager = request.app.state.security_manager
            await security_manager.log_audit_event(
                AuditEventType.LOGIN_FAILED,
                resource="oracle_bi_publisher",
                details={
                    "username": auth_request.username,
                    "server_url": auth_request.server_url,
                    "error": auth_result.error
                }
            )
            
            raise HTTPException(
                status_code=401,
                detail=f"Oracle authentication failed: {auth_result.error}"
            )
        
        # Log successful authentication
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.LOGIN_SUCCESS,
            resource="oracle_bi_publisher",
            details={
                "username": auth_request.username,
                "session_id": auth_result.data["session_id"]
            }
        )
        
        return OracleAuthResponse(**auth_result.data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Oracle authentication error: {str(e)}"
        )


@router.post("/auth/logout")
async def oracle_auth_logout(
    request: Request,
    session_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Logout from Oracle BI Publisher
    
    Invalidates the Oracle BI Publisher session and cleans up resources.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Logout from Oracle BI Publisher
        logout_result = await oracle_sdk.auth_manager.logout(session_id)
        
        # Log audit event
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.LOGOUT,
            resource="oracle_bi_publisher",
            details={"session_id": session_id}
        )
        
        return {"message": "Oracle logout successful"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Oracle logout error: {str(e)}"
        )


# Report Management Endpoints

@router.get("/reports")
async def list_oracle_reports(
    request: Request,
    catalog_path: str = Query("/", description="Catalog path to list reports from"),
    include_subfolders: bool = Query(True, description="Include reports from subfolders"),
    filter_active: bool = Query(True, description="Only return active reports"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    token: str = Depends(oauth2_scheme)
):
    """
    List Oracle BI Publisher reports
    
    Retrieves a list of reports from the Oracle BI Publisher catalog with
    support for filtering, pagination, and performance optimization.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # List reports from Oracle BI Publisher
        result = await oracle_sdk.list_reports(
            catalog_path=catalog_path,
            include_subfolders=include_subfolders,
            filter_active=filter_active
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list Oracle reports: {result.error}"
            )
        
        # Apply pagination
        reports = result.data
        total_count = len(reports)
        paginated_reports = reports[offset:offset + limit]
        
        # Log audit event
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.DATA_ACCESS,
            resource="oracle_reports",
            details={
                "catalog_path": catalog_path,
                "count": len(paginated_reports),
                "total": total_count
            }
        )
        
        return {
            "reports": paginated_reports,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total_count,
                "has_more": offset + limit < total_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing Oracle reports: {str(e)}"
        )


@router.get("/reports/{report_id}")
async def get_oracle_report(
    request: Request,
    report_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Get detailed information about a specific Oracle BI Publisher report
    
    Retrieves comprehensive metadata and configuration for a report,
    including parameters, data sources, and execution history.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Get report from Oracle BI Publisher
        result = await oracle_sdk.get_report(report_id)
        
        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Oracle report not found: {report_id}"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get Oracle report: {result.error}"
                )
        
        # Log audit event
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.DATA_ACCESS,
            resource=f"oracle_report_{report_id}",
            details={"action": "view"}
        )
        
        return result.data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Oracle report: {str(e)}"
        )


@router.post("/reports/execute")
async def execute_oracle_report(
    request: Request,
    execute_request: OracleReportExecuteRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Execute an Oracle BI Publisher report
    
    Initiates report execution with specified parameters and format.
    Supports both synchronous and asynchronous execution modes.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Execute report in Oracle BI Publisher
        result = await oracle_sdk.execute_report(
            report_id=execute_request.report_id,
            format=execute_request.format,
            parameters=execute_request.parameters,
            async_execution=execute_request.async_execution
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute Oracle report: {result.error}"
            )
        
        # Log audit event
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.REPORT_GENERATED,
            resource=f"oracle_report_{execute_request.report_id}",
            details={
                "execution_id": result.data["execution_id"],
                "format": execute_request.format.value,
                "parameters": execute_request.parameters,
                "async": execute_request.async_execution
            }
        )
        
        # Schedule notification if requested
        if execute_request.notify_on_completion:
            background_tasks.add_task(
                _monitor_execution,
                oracle_sdk,
                result.data["execution_id"]
            )
        
        return result.data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing Oracle report: {str(e)}"
        )


@router.get("/reports/execution/{execution_id}/status")
async def get_oracle_execution_status(
    request: Request,
    execution_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Get the status of an Oracle BI Publisher report execution
    
    Retrieves current execution status, progress information, and
    download URLs for completed reports.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Get execution status from Oracle BI Publisher
        result = await oracle_sdk.get_execution_status(execution_id)
        
        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Oracle execution not found: {execution_id}"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get execution status: {result.error}"
                )
        
        return result.data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting execution status: {str(e)}"
        )


@router.post("/reports/batch-execute")
async def batch_execute_oracle_reports(
    request: Request,
    batch_request: OracleBatchExecuteRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Execute multiple Oracle BI Publisher reports in batch
    
    Efficiently executes multiple reports with concurrency control
    and performance optimization for large-scale operations.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Convert requests to the format expected by the SDK
        report_requests = []
        for report_req in batch_request.reports:
            report_requests.append({
                "report_id": report_req.report_id,
                "format": report_req.format.value,
                "parameters": report_req.parameters,
                "async_execution": report_req.async_execution
            })
        
        # Execute reports in batch
        executions = []
        async for result in oracle_sdk.batch_execute_reports(
            report_requests=report_requests,
            max_concurrent=batch_request.max_concurrent
        ):
            if result.success:
                executions.append(result.data)
            else:
                executions.append({
                    "error": result.error,
                    "error_code": result.error_code
                })
        
        # Log batch execution
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.REPORT_GENERATED,
            resource="oracle_batch_execution",
            details={
                "report_count": len(batch_request.reports),
                "max_concurrent": batch_request.max_concurrent,
                "successful_executions": len([e for e in executions if "error" not in e])
            }
        )
        
        return {
            "executions": executions,
            "summary": {
                "total_reports": len(batch_request.reports),
                "successful": len([e for e in executions if "error" not in e]),
                "failed": len([e for e in executions if "error" in e])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch execution: {str(e)}"
        )


# Data Source Management Endpoints

@router.get("/datasources")
async def list_oracle_datasources(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """
    List Oracle BI Publisher data sources
    
    Retrieves all configured data sources with connection information
    and performance metrics.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # List data sources from Oracle BI Publisher
        result = await oracle_sdk.list_data_sources()
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list Oracle data sources: {result.error}"
            )
        
        # Log audit event
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.DATA_ACCESS,
            resource="oracle_datasources",
            details={"count": len(result.data)}
        )
        
        return {"datasources": result.data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing Oracle data sources: {str(e)}"
        )


@router.post("/datasources/{datasource_name}/test")
async def test_oracle_datasource(
    request: Request,
    datasource_name: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Test Oracle BI Publisher data source connectivity
    
    Validates data source connection and returns performance metrics
    and connectivity status.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Test data source connectivity
        result = await oracle_sdk.test_data_source(datasource_name)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to test Oracle data source: {result.error}"
            )
        
        # Log audit event
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.DATA_ACCESS,
            resource=f"oracle_datasource_{datasource_name}",
            details={"action": "test_connectivity"}
        )
        
        return result.data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing Oracle data source: {str(e)}"
        )


# Catalog Management Endpoints

@router.get("/catalog/folders")
async def list_oracle_folders(
    request: Request,
    parent_path: str = Query("/", description="Parent path to list folders from"),
    token: str = Depends(oauth2_scheme)
):
    """
    List Oracle BI Publisher catalog folders
    
    Retrieves folder structure and permissions from the Oracle BI Publisher
    catalog with support for hierarchical navigation.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # List folders from Oracle BI Publisher
        result = await oracle_sdk.list_folders(parent_path)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list Oracle folders: {result.error}"
            )
        
        # Log audit event
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.DATA_ACCESS,
            resource="oracle_catalog",
            details={
                "parent_path": parent_path,
                "folder_count": len(result.data)
            }
        )
        
        return {"folders": result.data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing Oracle folders: {str(e)}"
        )


# Health and Monitoring Endpoints

@router.get("/health")
async def oracle_health_check(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """
    Oracle BI Publisher health check
    
    Comprehensive health check including server connectivity,
    connection pool status, and performance metrics.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            return {
                "healthy": False,
                "error": "Oracle BI Publisher integration not initialized"
            }
        
        # Perform health check
        result = await oracle_sdk.health_check()
        
        if result.success:
            return result.data
        else:
            return {
                "healthy": False,
                "error": result.error
            }
        
    except Exception as e:
        return {
            "healthy": False,
            "error": f"Health check failed: {str(e)}"
        }


@router.get("/metrics")
async def oracle_performance_metrics(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """
    Oracle BI Publisher performance metrics
    
    Detailed performance and usage metrics for monitoring
    and optimization purposes.
    """
    try:
        oracle_sdk = request.app.state.oracle_sdk
        
        if not oracle_sdk:
            raise HTTPException(
                status_code=500,
                detail="Oracle BI Publisher integration not initialized"
            )
        
        # Get performance metrics
        metrics = oracle_sdk.get_performance_metrics()
        
        return {"metrics": metrics}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Oracle metrics: {str(e)}"
        )


# Background task helpers

async def _monitor_execution(oracle_sdk: OracleBIPublisherSDK, execution_id: str):
    """Monitor execution and send notification when complete"""
    try:
        # Poll execution status
        max_polls = 120  # 10 minutes with 5-second intervals
        poll_count = 0
        
        while poll_count < max_polls:
            result = await oracle_sdk.get_execution_status(execution_id)
            
            if result.success:
                status = result.data.get("status")
                
                if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                    # Send notification (implement notification logic here)
                    logger.info(
                        "Oracle report execution completed",
                        execution_id=execution_id,
                        status=status
                    )
                    break
            
            await asyncio.sleep(5)  # Wait 5 seconds before next poll
            poll_count += 1
        
    except Exception as e:
        logger.error(
            "Error monitoring Oracle execution",
            execution_id=execution_id,
            error=str(e)
        )