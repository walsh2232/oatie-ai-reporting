"""
Oracle BI Publisher Integration Module
Comprehensive API integration for automated report generation
"""

import aiohttp
import asyncio
import logging
import json
import base64
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import io
import zipfile

logger = logging.getLogger(__name__)

class ExportFormat(Enum):
    PDF = "pdf"
    EXCEL = "xlsx"
    CSV = "csv"
    XML = "xml"
    HTML = "html"
    RTF = "rtf"
    PPT = "pptx"

class ScheduleFrequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

@dataclass
class DataSource:
    """Oracle data source configuration"""
    name: str
    type: str  # oracle, postgresql, mysql, etc.
    connection_string: str
    username: str
    password: str
    schema: Optional[str] = None
    pool_size: int = 10

@dataclass
class ReportTemplate:
    """Report template definition"""
    id: str
    name: str
    description: str
    category: str
    template_file: str  # RTF/XSL template content
    data_model: str  # SQL or XML data model
    parameters: List[Dict[str, Any]]
    created_by: str
    created_at: datetime
    version: str = "1.0"

@dataclass
class Schedule:
    """Report scheduling configuration"""
    frequency: ScheduleFrequency
    start_date: datetime
    end_date: Optional[datetime]
    time_of_day: str  # HH:MM format
    timezone: str = "UTC"
    recipients: List[str]
    format: ExportFormat = ExportFormat.PDF

@dataclass
class ReportJob:
    """Report generation job"""
    job_id: str
    template_id: str
    parameters: Dict[str, Any]
    format: ExportFormat
    status: str  # queued, running, completed, failed
    created_at: datetime
    completed_at: Optional[datetime]
    file_path: Optional[str]
    error_message: Optional[str]
    file_size: Optional[int]

class OracleSession:
    """Oracle BI Publisher session management"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session_id: Optional[str] = None
        self.session_expires: Optional[datetime] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        await self.login()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self.logout()
            await self._session.close()
    
    async def login(self) -> bool:
        """Authenticate with Oracle BI Publisher"""
        try:
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            async with self._session.post(
                f"{self.base_url}/xmlpserver/services/v2/session",
                json=auth_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    session_data = await response.json()
                    self.session_id = session_data.get('sessionId')
                    # Set expiration to 4 hours from now
                    self.session_expires = datetime.utcnow() + timedelta(hours=4)
                    logger.info("Successfully authenticated with Oracle BI Publisher")
                    return True
                else:
                    logger.error(f"Authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False
    
    async def logout(self):
        """End Oracle BI Publisher session"""
        if self.session_id:
            try:
                await self._session.delete(
                    f"{self.base_url}/xmlpserver/services/v2/session/{self.session_id}"
                )
                logger.info("Successfully logged out from Oracle BI Publisher")
            except Exception as e:
                logger.error(f"Error during logout: {str(e)}")
            finally:
                self.session_id = None
                self.session_expires = None
    
    async def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        return (
            self.session_id is not None and 
            self.session_expires is not None and 
            datetime.utcnow() < self.session_expires
        )
    
    async def ensure_authenticated(self):
        """Ensure we have a valid session"""
        if not await self.is_session_valid():
            await self.login()

class OracleIntegration:
    """Oracle BI Publisher API Integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config['oracle_bi_url']
        self.username = config['oracle_username']
        self.password = config['oracle_password']
        self.data_sources: Dict[str, DataSource] = {}
        self.templates: Dict[str, ReportTemplate] = {}
        self.active_jobs: Dict[str, ReportJob] = {}
        
    async def add_data_source(self, data_source: DataSource) -> bool:
        """Add a new data source to Oracle BI Publisher"""
        try:
            async with OracleSession(self.base_url, self.username, self.password) as session:
                ds_config = {
                    "name": data_source.name,
                    "type": data_source.type,
                    "connectionString": data_source.connection_string,
                    "username": data_source.username,
                    "password": data_source.password,
                    "schema": data_source.schema,
                    "maxConnections": data_source.pool_size
                }
                
                async with session._session.post(
                    f"{self.base_url}/xmlpserver/services/v2/catalog/shared/DataSources/{data_source.name}",
                    json=ds_config,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {session.session_id}'
                    }
                ) as response:
                    if response.status in [200, 201]:
                        self.data_sources[data_source.name] = data_source
                        logger.info(f"Data source '{data_source.name}' added successfully")
                        return True
                    else:
                        logger.error(f"Failed to add data source: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error adding data source: {str(e)}")
            return False
    
    async def create_report_template(self, template: ReportTemplate) -> bool:
        """Create a new report template"""
        try:
            async with OracleSession(self.base_url, self.username, self.password) as session:
                # Upload template file
                template_data = {
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "dataModel": template.data_model,
                    "parameters": template.parameters,
                    "version": template.version
                }
                
                # Create multipart form data for file upload
                form_data = aiohttp.FormData()
                form_data.add_field('metadata', json.dumps(template_data), content_type='application/json')
                form_data.add_field('template', template.template_file, content_type='application/octet-stream')
                
                async with session._session.post(
                    f"{self.base_url}/xmlpserver/services/v2/catalog/shared/Reports/{template.id}",
                    data=form_data,
                    headers={'Authorization': f'Bearer {session.session_id}'}
                ) as response:
                    if response.status in [200, 201]:
                        self.templates[template.id] = template
                        logger.info(f"Template '{template.name}' created successfully")
                        return True
                    else:
                        logger.error(f"Failed to create template: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return False
    
    async def create_report(
        self,
        template_id: str,
        data_source: str,
        parameters: Dict[str, Any],
        format: ExportFormat = ExportFormat.PDF
    ) -> ReportJob:
        """Create a new report using specified template"""
        
        job_id = f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            async with OracleSession(self.base_url, self.username, self.password) as session:
                
                job_request = {
                    "reportRequest": {
                        "reportAbsolutePath": f"/shared/Reports/{template_id}",
                        "sizeOfDataChunkDownload": -1,
                        "reportParameters": parameters,
                        "reportOutputFormat": format.value.upper(),
                        "reportLocale": "en_US"
                    }
                }
                
                async with session._session.post(
                    f"{self.base_url}/xmlpserver/services/v2/reports",
                    json=job_request,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {session.session_id}'
                    }
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        oracle_job_id = result.get('jobId')
                        
                        job = ReportJob(
                            job_id=job_id,
                            template_id=template_id,
                            parameters=parameters,
                            format=format,
                            status="running",
                            created_at=datetime.utcnow(),
                            completed_at=None,
                            file_path=None,
                            error_message=None,
                            file_size=None
                        )
                        
                        self.active_jobs[job_id] = job
                        
                        # Start monitoring job in background
                        asyncio.create_task(self._monitor_job(job_id, oracle_job_id, session))
                        
                        logger.info(f"Report job {job_id} created successfully")
                        return job
                        
                    else:
                        error_msg = f"Failed to create report: {response.status}"
                        logger.error(error_msg)
                        
                        return ReportJob(
                            job_id=job_id,
                            template_id=template_id,
                            parameters=parameters,
                            format=format,
                            status="failed",
                            created_at=datetime.utcnow(),
                            completed_at=datetime.utcnow(),
                            file_path=None,
                            error_message=error_msg,
                            file_size=None
                        )
                        
        except Exception as e:
            error_msg = f"Error creating report: {str(e)}"
            logger.error(error_msg)
            
            return ReportJob(
                job_id=job_id,
                template_id=template_id,
                parameters=parameters,
                format=format,
                status="failed",
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                file_path=None,
                error_message=error_msg,
                file_size=None
            )
    
    async def _monitor_job(self, job_id: str, oracle_job_id: str, session: OracleSession):
        """Monitor report generation job"""
        max_attempts = 60  # 5 minutes with 5-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            try:
                await asyncio.sleep(5)  # Wait 5 seconds between checks
                
                async with session._session.get(
                    f"{session.base_url}/xmlpserver/services/v2/reports/{oracle_job_id}",
                    headers={'Authorization': f'Bearer {session.session_id}'}
                ) as response:
                    
                    if response.status == 200:
                        status_data = await response.json()
                        status = status_data.get('status', 'unknown').lower()
                        
                        if status == 'success':
                            # Download the report
                            file_path = await self._download_report(oracle_job_id, session)
                            
                            job = self.active_jobs[job_id]
                            job.status = "completed"
                            job.completed_at = datetime.utcnow()
                            job.file_path = file_path
                            
                            logger.info(f"Report job {job_id} completed successfully")
                            return
                            
                        elif status == 'failed':
                            job = self.active_jobs[job_id]
                            job.status = "failed"
                            job.completed_at = datetime.utcnow()
                            job.error_message = status_data.get('errorMessage', 'Unknown error')
                            
                            logger.error(f"Report job {job_id} failed: {job.error_message}")
                            return
                        
                        # Job still running, continue monitoring
                        attempt += 1
                        
                    else:
                        logger.warning(f"Failed to check job status: {response.status}")
                        attempt += 1
                        
            except Exception as e:
                logger.error(f"Error monitoring job {job_id}: {str(e)}")
                attempt += 1
        
        # Timeout reached
        job = self.active_jobs[job_id]
        job.status = "failed"
        job.completed_at = datetime.utcnow()
        job.error_message = "Job monitoring timeout"
        logger.error(f"Report job {job_id} monitoring timeout")
    
    async def _download_report(self, oracle_job_id: str, session: OracleSession) -> Optional[str]:
        """Download completed report file"""
        try:
            async with session._session.get(
                f"{session.base_url}/xmlpserver/services/v2/reports/{oracle_job_id}/output",
                headers={'Authorization': f'Bearer {session.session_id}'}
            ) as response:
                
                if response.status == 200:
                    content = await response.read()
                    
                    # Generate file path
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    file_path = f"/tmp/reports/{oracle_job_id}_{timestamp}.pdf"
                    
                    # Ensure directory exists
                    import os
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Write file
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    logger.info(f"Report downloaded to {file_path}")
                    return file_path
                    
                else:
                    logger.error(f"Failed to download report: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading report: {str(e)}")
            return None
    
    async def get_report_status(self, job_id: str) -> Optional[ReportJob]:
        """Get report generation status"""
        return self.active_jobs.get(job_id)
    
    async def schedule_report(
        self,
        template_id: str,
        schedule: Schedule,
        data_source: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """Schedule a report for automatic generation"""
        try:
            async with OracleSession(self.base_url, self.username, self.password) as session:
                
                schedule_config = {
                    "name": f"Scheduled_{template_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    "reportPath": f"/shared/Reports/{template_id}",
                    "schedule": {
                        "frequency": schedule.frequency.value,
                        "startDate": schedule.start_date.isoformat(),
                        "endDate": schedule.end_date.isoformat() if schedule.end_date else None,
                        "timeOfDay": schedule.time_of_day,
                        "timezone": schedule.timezone
                    },
                    "delivery": {
                        "format": schedule.format.value,
                        "recipients": schedule.recipients
                    },
                    "parameters": parameters
                }
                
                async with session._session.post(
                    f"{self.base_url}/xmlpserver/services/v2/scheduler/jobs",
                    json=schedule_config,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {session.session_id}'
                    }
                ) as response:
                    
                    if response.status in [200, 201]:
                        logger.info(f"Report scheduled successfully for template {template_id}")
                        return True
                    else:
                        logger.error(f"Failed to schedule report: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error scheduling report: {str(e)}")
            return False
    
    async def get_templates(self, category: Optional[str] = None) -> List[ReportTemplate]:
        """Get available report templates"""
        try:
            async with OracleSession(self.base_url, self.username, self.password) as session:
                
                url = f"{self.base_url}/xmlpserver/services/v2/catalog/shared/Reports"
                if category:
                    url += f"?category={category}"
                
                async with session._session.get(
                    url,
                    headers={'Authorization': f'Bearer {session.session_id}'}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        templates = []
                        
                        for item in data.get('items', []):
                            template = ReportTemplate(
                                id=item['name'],
                                name=item['displayName'],
                                description=item.get('description', ''),
                                category=item.get('category', 'General'),
                                template_file='',  # Would need separate call to get content
                                data_model=item.get('dataModel', ''),
                                parameters=item.get('parameters', []),
                                created_by=item.get('createdBy', 'system'),
                                created_at=datetime.fromisoformat(item.get('createdDate', datetime.utcnow().isoformat())),
                                version=item.get('version', '1.0')
                            )
                            templates.append(template)
                        
                        return templates
                        
                    else:
                        logger.error(f"Failed to get templates: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            return []
    
    async def export_report(
        self,
        report_id: str,
        format: ExportFormat
    ) -> Optional[bytes]:
        """Export report in specified format"""
        job = self.active_jobs.get(report_id)
        
        if not job or job.status != "completed" or not job.file_path:
            logger.error(f"Report {report_id} not found or not completed")
            return None
        
        try:
            # If format matches job format, return file directly
            if job.format == format:
                with open(job.file_path, 'rb') as f:
                    return f.read()
            
            # Otherwise, need to convert format (simplified)
            # In a real implementation, you'd use Oracle's format conversion APIs
            logger.warning(f"Format conversion from {job.format} to {format} not implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            return None
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get Oracle BI Publisher system information"""
        try:
            async with OracleSession(self.base_url, self.username, self.password) as session:
                
                async with session._session.get(
                    f"{self.base_url}/xmlpserver/services/v2/system/info",
                    headers={'Authorization': f'Bearer {session.session_id}'}
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get system info: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}

# Mock Oracle integration for development/testing
class MockOracleIntegration(OracleIntegration):
    """Mock Oracle integration for testing and development"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._setup_mock_templates()
    
    def _setup_mock_templates(self):
        """Setup mock templates for testing"""
        templates = [
            ReportTemplate(
                id="sales_report",
                name="Sales Performance Report",
                description="Monthly sales performance by region and product",
                category="Sales",
                template_file="mock_template.rtf",
                data_model="SELECT * FROM sales_data",
                parameters=[
                    {"name": "start_date", "type": "date", "required": True},
                    {"name": "end_date", "type": "date", "required": True},
                    {"name": "region", "type": "string", "required": False}
                ],
                created_by="system",
                created_at=datetime.utcnow()
            ),
            ReportTemplate(
                id="financial_report",
                name="Financial Summary",
                description="Quarterly financial summary with P&L",
                category="Finance",
                template_file="mock_template.rtf",
                data_model="SELECT * FROM financial_data",
                parameters=[
                    {"name": "quarter", "type": "string", "required": True},
                    {"name": "year", "type": "integer", "required": True}
                ],
                created_by="system",
                created_at=datetime.utcnow()
            ),
            ReportTemplate(
                id="inventory_report",
                name="Inventory Analysis",
                description="Current inventory levels and turnover analysis",
                category="Operations",
                template_file="mock_template.rtf",
                data_model="SELECT * FROM inventory_data",
                parameters=[
                    {"name": "warehouse", "type": "string", "required": False},
                    {"name": "category", "type": "string", "required": False}
                ],
                created_by="system",
                created_at=datetime.utcnow()
            )
        ]
        
        for template in templates:
            self.templates[template.id] = template
    
    async def create_report(
        self,
        template_id: str,
        data_source: str,
        parameters: Dict[str, Any],
        format: ExportFormat = ExportFormat.PDF
    ) -> ReportJob:
        """Mock report creation"""
        
        job_id = f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        job = ReportJob(
            job_id=job_id,
            template_id=template_id,
            parameters=parameters,
            format=format,
            status="completed",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            file_path=f"/tmp/reports/{job_id}.{format.value}",
            error_message=None,
            file_size=1024000  # 1MB mock file
        )
        
        self.active_jobs[job_id] = job
        logger.info(f"Mock report job {job_id} created and completed")
        return job