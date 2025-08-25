from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ReportBase(BaseModel):
    name: str
    description: Optional[str] = None
    oracle_report_path: Optional[str] = None
    ai_generated_query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class ReportCreate(ReportBase):
    pass


class ReportResponse(ReportBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True