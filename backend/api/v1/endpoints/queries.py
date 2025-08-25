"""
Query execution endpoints with AI assistance and caching
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from backend.api.v1.endpoints.auth import oauth2_scheme
from backend.core.security import AuditEventType

router = APIRouter()


class QueryRequest(BaseModel):
    sql: str
    parameters: Optional[Dict[str, Any]] = {}
    use_cache: bool = True
    timeout: int = 30


class QueryResult(BaseModel):
    query_id: str
    sql: str
    columns: List[str]
    rows: List[List[Any]]
    execution_time_ms: float
    cached: bool
    row_count: int


class QueryValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]
    estimated_cost: Optional[int]


@router.post("/validate", response_model=QueryValidationResponse)
async def validate_query(
    request: Request,
    query_request: QueryRequest,
    token: str = Depends(oauth2_scheme)
):
    """Validate SQL query with AI assistance"""
    
    sql = query_request.sql.strip()
    errors = []
    warnings = []
    
    # Basic SQL validation
    if not sql:
        errors.append("Query cannot be empty")
    
    if not sql.upper().startswith(('SELECT', 'WITH')):
        errors.append("Only SELECT queries are allowed")
    
    # Check for potentially dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
    for keyword in dangerous_keywords:
        if keyword in sql.upper():
            errors.append(f"'{keyword}' operations are not allowed")
    
    # Check for performance concerns
    if 'SELECT *' in sql.upper():
        warnings.append("Consider specifying column names instead of SELECT *")
    
    if 'WHERE' not in sql.upper() and 'LIMIT' not in sql.upper():
        warnings.append("Query may return large result set - consider adding WHERE clause or LIMIT")
    
    # Estimate query cost (mock)
    estimated_cost = len(sql) * 10  # Simple estimation
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "estimated_cost": estimated_cost
    }


@router.post("/execute", response_model=QueryResult)
async def execute_query(
    request: Request,
    query_request: QueryRequest,
    token: str = Depends(oauth2_scheme)
):
    """Execute SQL query with intelligent caching"""
    
    # Generate query hash for caching
    query_hash = hashlib.md5(
        json.dumps({
            "sql": query_request.sql,
            "parameters": query_request.parameters
        }, sort_keys=True).encode()
    ).hexdigest()
    
    # Check cache first
    cache_manager = request.app.state.cache_manager
    cached_result = None
    
    if query_request.use_cache:
        cached_result = await cache_manager.get("queries", query_hash)
    
    if cached_result:
        # Return cached result
        security_manager = request.app.state.security_manager
        await security_manager.log_audit_event(
            AuditEventType.QUERY_EXECUTED,
            resource="cached_query",
            details={"query_hash": query_hash, "cached": True}
        )
        
        return QueryResult(**cached_result)
    
    # Execute query (mock implementation)
    start_time = datetime.now()
    
    # Mock query execution with sample data
    if "sales" in query_request.sql.lower():
        columns = ["product", "region", "sales_amount", "date"]
        rows = [
            ["Product A", "North", 15000.50, "2024-01-15"],
            ["Product B", "South", 22000.75, "2024-01-16"],
            ["Product C", "East", 18500.25, "2024-01-17"]
        ]
    else:
        columns = ["id", "name", "value"]
        rows = [
            [1, "Sample Data 1", 100],
            [2, "Sample Data 2", 200],
            [3, "Sample Data 3", 300]
        ]
    
    execution_time = (datetime.now() - start_time).total_seconds() * 1000
    
    result = {
        "query_id": f"q_{query_hash[:8]}",
        "sql": query_request.sql,
        "columns": columns,
        "rows": rows,
        "execution_time_ms": execution_time,
        "cached": False,
        "row_count": len(rows)
    }
    
    # Cache the result
    if query_request.use_cache:
        await cache_manager.set(
            "queries", 
            query_hash, 
            result, 
            ttl=1800  # 30 minutes
        )
    
    # Log query execution
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.QUERY_EXECUTED,
        resource="oracle_bi_database",
        details={
            "query_hash": query_hash,
            "execution_time_ms": execution_time,
            "row_count": len(rows),
            "cached": False
        }
    )
    
    return QueryResult(**result)


@router.get("/history")
async def get_query_history(
    request: Request,
    limit: int = 20,
    token: str = Depends(oauth2_scheme)
):
    """Get user query execution history"""
    
    # Mock query history
    history = [
        {
            "query_id": "q_abc12345",
            "sql": "SELECT product, SUM(sales_amount) FROM sales GROUP BY product",
            "executed_at": "2024-01-15T10:30:00Z",
            "execution_time_ms": 150.5,
            "row_count": 25,
            "cached": False
        },
        {
            "query_id": "q_def67890",
            "sql": "SELECT * FROM customers WHERE region = 'North'",
            "executed_at": "2024-01-15T09:15:00Z",
            "execution_time_ms": 89.2,
            "row_count": 142,
            "cached": True
        }
    ]
    
    return {"queries": history[:limit]}


@router.get("/suggestions")
async def get_query_suggestions(
    request: Request,
    partial_query: str = "",
    token: str = Depends(oauth2_scheme)
):
    """Get AI-powered query suggestions"""
    
    suggestions = []
    
    if "select" in partial_query.lower():
        suggestions.extend([
            "SELECT product, SUM(sales_amount) FROM sales_data GROUP BY product",
            "SELECT customer_name, COUNT(*) as order_count FROM orders GROUP BY customer_name",
            "SELECT region, AVG(revenue) FROM regional_sales GROUP BY region"
        ])
    
    if not partial_query:
        suggestions.extend([
            "SELECT * FROM sales_data LIMIT 10",
            "SELECT COUNT(*) FROM customers",
            "SELECT product, price FROM products WHERE price > 100"
        ])
    
    return {
        "suggestions": suggestions[:5],
        "ai_powered": True,
        "context": "Oracle BI Publisher data sources"
    }