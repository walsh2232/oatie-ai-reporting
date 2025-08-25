from pydantic import BaseModel
from typing import Optional


class AIQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class AIQueryResponse(BaseModel):
    response: str
    sql_query: Optional[str] = None
    suggested_report_name: Optional[str] = None
    confidence: Optional[float] = None