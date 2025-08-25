"""
Oracle BI Publisher data models for enterprise integration
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field, validator


class OracleReportStatus(str, Enum):
    """Oracle BI Publisher report execution status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING" 
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class OracleReportFormat(str, Enum):
    """Supported Oracle BI Publisher report formats"""
    PDF = "PDF"
    EXCEL = "EXCEL"
    WORD = "WORD"
    CSV = "CSV"
    XML = "XML"
    RTF = "RTF"
    POWERPOINT = "POWERPOINT"


class OracleDataSourceType(str, Enum):
    """Oracle data source types"""
    ORACLE_DB = "ORACLE_DB"
    SQL_SERVER = "SQL_SERVER"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    WEB_SERVICE = "WEB_SERVICE"
    LDAP = "LDAP"


class OracleUser(BaseModel):
    """Oracle BI Publisher user model"""
    username: str
    display_name: str
    email: Optional[str] = None
    roles: List[str] = []
    active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OracleDataSource(BaseModel):
    """Oracle BI Publisher data source configuration"""
    name: str
    display_name: str
    type: OracleDataSourceType
    connection_string: str
    username: str
    password: str  # Will be encrypted in storage
    connection_pool_size: int = Field(default=10, ge=1, le=100)
    timeout: int = Field(default=30, ge=5, le=300)
    test_query: str = "SELECT 1 FROM DUAL"
    active: bool = True
    created_at: datetime
    updated_at: datetime
    
    @validator('connection_pool_size')
    def validate_pool_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Pool size must be between 1 and 100')
        return v


class OracleReport(BaseModel):
    """Oracle BI Publisher report model"""
    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    catalog_path: str  # e.g., "/Shared Folders/Reports/Sales/"
    template_path: str  # Path to .rtf or .xpt template
    data_source: str  # Data source name
    parameters: Dict[str, Any] = {}
    default_format: OracleReportFormat = OracleReportFormat.PDF
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"
    active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OracleReportExecution(BaseModel):
    """Oracle BI Publisher report execution model"""
    execution_id: str
    report_id: str
    status: OracleReportStatus
    format: OracleReportFormat
    parameters: Dict[str, Any] = {}
    created_by: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    output_size_bytes: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OracleFolder(BaseModel):
    """Oracle BI Publisher catalog folder model"""
    path: str
    name: str
    parent_path: Optional[str] = None
    description: Optional[str] = None
    created_by: str
    created_at: datetime
    permissions: Dict[str, List[str]] = {}  # role -> permissions mapping
    
    @validator('path')
    def validate_path(cls, v):
        if not v.startswith('/'):
            raise ValueError('Path must start with /')
        return v


class OracleSchedule(BaseModel):
    """Oracle BI Publisher report schedule model"""
    schedule_id: str
    report_id: str
    name: str
    description: Optional[str] = None
    cron_expression: str
    parameters: Dict[str, Any] = {}
    output_format: OracleReportFormat = OracleReportFormat.PDF
    delivery_method: str = "FILE_SYSTEM"  # FILE_SYSTEM, EMAIL, FTP, etc.
    delivery_config: Dict[str, Any] = {}
    active: bool = True
    created_by: str
    created_at: datetime
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    last_status: Optional[OracleReportStatus] = None


class OracleSessionInfo(BaseModel):
    """Oracle BI Publisher session information"""
    session_id: str
    user: OracleUser
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class OracleAPIResponse(BaseModel):
    """Standard Oracle BI Publisher API response wrapper"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OracleConnectionStatus(BaseModel):
    """Oracle BI Publisher connection status model"""
    connected: bool
    server_url: str
    server_version: Optional[str] = None
    last_check: datetime
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None