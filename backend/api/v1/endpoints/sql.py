"""
SQL Generation API endpoints with Advanced NLP capabilities
Enterprise-grade natural language to SQL conversion with Oracle optimization
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field

from backend.api.v1.endpoints.auth import oauth2_scheme
from backend.services.nlp_sql_service import (
    NLPSQLGenerator, 
    SQLOptimizer, 
    SQLDialect, 
    SQLGenerationContext,
    TableSchema,
    GeneratedSQL
)
from backend.core.cache import CacheManager
from backend.core.security import AuditEventType
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


class NLQueryRequest(BaseModel):
    """Natural language query request"""
    query: str = Field(..., description="Natural language description of the query", min_length=1)
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for query generation")
    dialect: str = Field(default="oracle", description="SQL dialect to generate")
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me the total sales by region for the last quarter",
                "context": {
                    "user_preferences": {"date_format": "YYYY-MM-DD"},
                    "available_tables": ["sales", "regions", "customers"]
                },
                "dialect": "oracle",
                "use_cache": True
            }
        }


class SQLGenerationResponse(BaseModel):
    """SQL generation response with metadata"""
    query_id: str
    natural_query: str
    generated_sql: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the generated SQL")
    complexity: str
    estimated_cost: int
    optimization_hints: List[str]
    tables_used: List[str]
    explanation: str
    cached: bool = False
    execution_time_ms: float


class SQLOptimizationRequest(BaseModel):
    """SQL optimization request"""
    sql: str = Field(..., description="SQL query to optimize", min_length=1)
    context: Optional[Dict[str, Any]] = Field(default=None, description="Database context for optimization")
    dialect: str = Field(default="oracle", description="SQL dialect")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sql": "SELECT * FROM sales s JOIN customers c ON s.customer_id = c.id WHERE s.date > '2024-01-01'",
                "context": {
                    "table_stats": {"sales": {"row_count": 1000000}, "customers": {"row_count": 50000}},
                    "available_indexes": ["sales.customer_id", "sales.date", "customers.id"]
                },
                "dialect": "oracle"
            }
        }


class SQLOptimizationResponse(BaseModel):
    """SQL optimization response"""
    query_id: str
    original_sql: str
    optimized_sql: str
    analysis: Dict[str, Any]
    optimizations_applied: List[str]
    performance_improvement_estimate: str
    recommendations: List[str]
    execution_time_ms: float


class SQLValidationRequest(BaseModel):
    """Enhanced SQL validation request"""
    sql: str = Field(..., description="SQL query to validate", min_length=1)
    dialect: str = Field(default="oracle", description="SQL dialect to validate against")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Database context for validation")
    check_performance: bool = Field(default=True, description="Whether to include performance analysis")


class SQLValidationResponse(BaseModel):
    """Enhanced SQL validation response"""
    query_id: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    estimated_cost: Optional[int]
    performance_analysis: Optional[Dict[str, Any]]
    oracle_compliance: bool
    execution_time_ms: float


class SQLExplainRequest(BaseModel):
    """SQL execution plan request"""
    sql: str = Field(..., description="SQL query to explain", min_length=1)
    dialect: str = Field(default="oracle", description="SQL dialect")
    format: str = Field(default="json", description="Output format: json, text, or xml")


class SQLExplainResponse(BaseModel):
    """SQL execution plan response"""
    query_id: str
    sql: str
    execution_plan: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    recommendations: List[str]
    estimated_rows: int
    estimated_cost: int
    execution_time_ms: float


# Initialize services
nlp_generator = NLPSQLGenerator(SQLDialect.ORACLE)
sql_optimizer = SQLOptimizer(SQLDialect.ORACLE)


@router.post("/generate", response_model=SQLGenerationResponse)
async def generate_sql_from_natural_language(
    request: Request,
    query_request: NLQueryRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Generate SQL from natural language query with Oracle optimization
    
    This endpoint converts natural language descriptions into optimized SQL queries
    with context awareness and performance optimization specifically for Oracle databases.
    """
    start_time = datetime.now()
    query_id = hashlib.md5(f"{query_request.query}{start_time}".encode()).hexdigest()[:16]
    
    try:
        # Check cache first
        cache_manager = getattr(request.app.state, 'cache_manager', None)
        cache_key = f"nlp_sql:{hashlib.md5(query_request.query.encode()).hexdigest()}"
        
        if query_request.use_cache and cache_manager:
            cached_result = await cache_manager.get("nlp_sql", cache_key)
            if cached_result:
                logger.info("SQL generation cache hit", query_id=query_id, cache_key=cache_key)
                cached_result['cached'] = True
                cached_result['query_id'] = query_id
                return SQLGenerationResponse(**cached_result)
        
        # Set up context for SQL generation
        context = await _build_sql_context(query_request.context, request)
        await nlp_generator.set_context(context)
        
        # Generate SQL from natural language
        logger.info("Generating SQL from natural language", 
                   query_id=query_id, 
                   query_length=len(query_request.query))
        
        generated_sql: GeneratedSQL = await nlp_generator.generate_sql(query_request.query)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Prepare response
        response_data = {
            'query_id': query_id,
            'natural_query': query_request.query,
            'generated_sql': generated_sql.sql,
            'confidence': generated_sql.confidence,
            'complexity': generated_sql.complexity.value,
            'estimated_cost': generated_sql.estimated_cost,
            'optimization_hints': generated_sql.optimization_hints,
            'tables_used': generated_sql.tables_used,
            'explanation': generated_sql.explanation,
            'cached': False,
            'execution_time_ms': execution_time
        }
        
        # Cache the result
        if cache_manager:
            await cache_manager.set("nlp_sql", cache_key, response_data, ttl=3600)  # 1 hour cache
        
        # Log audit event
        background_tasks.add_task(
            _log_audit_event,
            request,
            AuditEventType.SQL_GENERATION,
            {
                'query_id': query_id,
                'natural_query': query_request.query,
                'confidence': generated_sql.confidence,
                'complexity': generated_sql.complexity.value
            }
        )
        
        logger.info("SQL generation completed", 
                   query_id=query_id,
                   confidence=generated_sql.confidence,
                   execution_time_ms=execution_time)
        
        return SQLGenerationResponse(**response_data)
        
    except Exception as e:
        logger.error("SQL generation failed", 
                    query_id=query_id, 
                    error=str(e),
                    query=query_request.query)
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")


@router.post("/optimize", response_model=SQLOptimizationResponse)
async def optimize_sql_query(
    request: Request,
    optimization_request: SQLOptimizationRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Optimize SQL query for better performance with Oracle-specific enhancements
    
    Analyzes the provided SQL query and returns an optimized version with
    performance recommendations and Oracle-specific hints.
    """
    start_time = datetime.now()
    query_id = hashlib.md5(f"{optimization_request.sql}{start_time}".encode()).hexdigest()[:16]
    
    try:
        logger.info("Optimizing SQL query", 
                   query_id=query_id, 
                   sql_length=len(optimization_request.sql))
        
        # Set up context for optimization
        context = await _build_sql_context(optimization_request.context, request)
        
        # Optimize the SQL query
        optimization_result = await sql_optimizer.optimize_query(
            optimization_request.sql, 
            context
        )
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Prepare response
        response_data = {
            'query_id': query_id,
            'original_sql': optimization_result['original_sql'],
            'optimized_sql': optimization_result['optimized_sql'],
            'analysis': optimization_result['analysis'],
            'optimizations_applied': optimization_result['optimizations_applied'],
            'performance_improvement_estimate': optimization_result['performance_improvement_estimate'],
            'recommendations': optimization_result['recommendations'],
            'execution_time_ms': execution_time
        }
        
        # Log audit event
        background_tasks.add_task(
            _log_audit_event,
            request,
            AuditEventType.SQL_OPTIMIZATION,
            {
                'query_id': query_id,
                'optimizations_applied': optimization_result['optimizations_applied'],
                'improvement_estimate': optimization_result['performance_improvement_estimate']
            }
        )
        
        logger.info("SQL optimization completed", 
                   query_id=query_id,
                   optimizations_count=len(optimization_result['optimizations_applied']),
                   execution_time_ms=execution_time)
        
        return SQLOptimizationResponse(**response_data)
        
    except Exception as e:
        logger.error("SQL optimization failed", 
                    query_id=query_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"SQL optimization failed: {str(e)}")


@router.post("/validate", response_model=SQLValidationResponse)
async def validate_sql_query_enhanced(
    request: Request,
    validation_request: SQLValidationRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Enhanced SQL validation with Oracle compliance and performance analysis
    
    Validates SQL syntax, Oracle compliance, and provides performance analysis
    with detailed suggestions for improvement.
    """
    start_time = datetime.now()
    query_id = hashlib.md5(f"{validation_request.sql}{start_time}".encode()).hexdigest()[:16]
    
    try:
        logger.info("Validating SQL query", 
                   query_id=query_id, 
                   sql_length=len(validation_request.sql))
        
        sql = validation_request.sql.strip()
        errors = []
        warnings = []
        suggestions = []
        
        # Basic SQL validation
        if not sql:
            errors.append("Query cannot be empty")
        
        if not sql.upper().startswith(('SELECT', 'WITH')):
            errors.append("Only SELECT queries are allowed")
        
        # Check for potentially dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        for keyword in dangerous_keywords:
            if keyword in sql.upper():
                errors.append(f"'{keyword}' operations are not allowed")
        
        # Oracle-specific validation
        oracle_compliance = True
        
        # Check for Oracle-specific syntax issues
        if validation_request.dialect.lower() == 'oracle':
            # Check for proper Oracle functions
            if 'LIMIT' in sql.upper():
                warnings.append("Use ROWNUM or FETCH FIRST instead of LIMIT for Oracle compatibility")
                suggestions.append("Replace LIMIT with FETCH FIRST n ROWS ONLY")
                oracle_compliance = False
            
            if 'AUTO_INCREMENT' in sql.upper():
                warnings.append("Use SEQUENCE and TRIGGER instead of AUTO_INCREMENT for Oracle")
                oracle_compliance = False
            
            # Check for proper date functions
            if 'NOW()' in sql.upper():
                suggestions.append("Use SYSDATE instead of NOW() for Oracle")
                oracle_compliance = False
        
        # Performance analysis
        performance_analysis = None
        estimated_cost = None
        
        if validation_request.check_performance:
            performance_analysis = await _analyze_query_performance(sql)
            estimated_cost = performance_analysis.get('estimated_cost', 0)
            
            # Add performance warnings
            if 'SELECT *' in sql.upper():
                warnings.append("Consider specifying column names instead of SELECT *")
                suggestions.append("List specific columns to reduce data transfer and improve performance")
            
            if 'WHERE' not in sql.upper() and 'LIMIT' not in sql.upper() and 'FETCH' not in sql.upper():
                warnings.append("Query may return large result set - consider adding WHERE clause or LIMIT")
                suggestions.append("Add WHERE clause to filter results or use FETCH FIRST to limit rows")
            
            if performance_analysis.get('complexity_score', 0) > 100:
                warnings.append("Query complexity is high - consider optimization")
                suggestions.append("Break down complex query into smaller parts or use materialized views")
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Prepare response
        response_data = {
            'query_id': query_id,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'estimated_cost': estimated_cost,
            'performance_analysis': performance_analysis,
            'oracle_compliance': oracle_compliance,
            'execution_time_ms': execution_time
        }
        
        # Log audit event
        background_tasks.add_task(
            _log_audit_event,
            request,
            AuditEventType.SQL_VALIDATION,
            {
                'query_id': query_id,
                'valid': len(errors) == 0,
                'errors_count': len(errors),
                'warnings_count': len(warnings),
                'oracle_compliance': oracle_compliance
            }
        )
        
        logger.info("SQL validation completed", 
                   query_id=query_id,
                   valid=len(errors) == 0,
                   warnings_count=len(warnings),
                   execution_time_ms=execution_time)
        
        return SQLValidationResponse(**response_data)
        
    except Exception as e:
        logger.error("SQL validation failed", 
                    query_id=query_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"SQL validation failed: {str(e)}")


@router.post("/explain", response_model=SQLExplainResponse)
async def explain_sql_query(
    request: Request,
    explain_request: SQLExplainRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Generate execution plan analysis for SQL query
    
    Provides detailed execution plan with cost analysis and optimization
    recommendations specifically tailored for Oracle databases.
    """
    start_time = datetime.now()
    query_id = hashlib.md5(f"{explain_request.sql}{start_time}".encode()).hexdigest()[:16]
    
    try:
        logger.info("Explaining SQL query", 
                   query_id=query_id, 
                   sql_length=len(explain_request.sql))
        
        # Generate execution plan analysis
        execution_plan = await _generate_execution_plan(explain_request.sql, explain_request.dialect)
        cost_analysis = await _analyze_query_cost(explain_request.sql)
        recommendations = await _generate_execution_recommendations(explain_request.sql, execution_plan)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Prepare response
        response_data = {
            'query_id': query_id,
            'sql': explain_request.sql,
            'execution_plan': execution_plan,
            'cost_analysis': cost_analysis,
            'recommendations': recommendations,
            'estimated_rows': cost_analysis.get('estimated_rows', 0),
            'estimated_cost': cost_analysis.get('total_cost', 0),
            'execution_time_ms': execution_time
        }
        
        # Log audit event
        background_tasks.add_task(
            _log_audit_event,
            request,
            AuditEventType.SQL_EXPLAIN,
            {
                'query_id': query_id,
                'estimated_cost': cost_analysis.get('total_cost', 0),
                'estimated_rows': cost_analysis.get('estimated_rows', 0)
            }
        )
        
        logger.info("SQL explain completed", 
                   query_id=query_id,
                   estimated_cost=cost_analysis.get('total_cost', 0),
                   execution_time_ms=execution_time)
        
        return SQLExplainResponse(**response_data)
        
    except Exception as e:
        logger.error("SQL explain failed", 
                    query_id=query_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"SQL explain failed: {str(e)}")


# Helper functions

async def _build_sql_context(context_data: Optional[Dict[str, Any]], request: Request) -> SQLGenerationContext:
    """Build SQL generation context from request data"""
    
    # Mock schemas for demonstration - in production, this would query the actual database
    default_schemas = [
        TableSchema(
            name="sales",
            columns=[
                {"name": "id", "type": "NUMBER", "nullable": False},
                {"name": "customer_id", "type": "NUMBER", "nullable": False},
                {"name": "product_id", "type": "NUMBER", "nullable": False},
                {"name": "amount", "type": "NUMBER(10,2)", "nullable": False},
                {"name": "sale_date", "type": "DATE", "nullable": False},
                {"name": "region", "type": "VARCHAR2(50)", "nullable": True},
                {"name": "created_at", "type": "TIMESTAMP", "nullable": False}
            ],
            primary_keys=["id"],
            foreign_keys=[
                {"column": "customer_id", "referenced_table": "customers", "referenced_column": "id"},
                {"column": "product_id", "referenced_table": "products", "referenced_column": "id"}
            ],
            indexes=[
                {"name": "idx_sales_customer", "columns": ["customer_id"]},
                {"name": "idx_sales_date", "columns": ["sale_date"]},
                {"name": "idx_sales_region", "columns": ["region"]}
            ],
            description="Sales transaction records"
        ),
        TableSchema(
            name="customers",
            columns=[
                {"name": "id", "type": "NUMBER", "nullable": False},
                {"name": "name", "type": "VARCHAR2(100)", "nullable": False},
                {"name": "email", "type": "VARCHAR2(100)", "nullable": True},
                {"name": "region", "type": "VARCHAR2(50)", "nullable": True},
                {"name": "created_at", "type": "TIMESTAMP", "nullable": False}
            ],
            primary_keys=["id"],
            foreign_keys=[],
            indexes=[
                {"name": "idx_customers_email", "columns": ["email"]},
                {"name": "idx_customers_region", "columns": ["region"]}
            ],
            description="Customer information"
        ),
        TableSchema(
            name="products",
            columns=[
                {"name": "id", "type": "NUMBER", "nullable": False},
                {"name": "name", "type": "VARCHAR2(100)", "nullable": False},
                {"name": "category", "type": "VARCHAR2(50)", "nullable": True},
                {"name": "price", "type": "NUMBER(10,2)", "nullable": False},
                {"name": "created_at", "type": "TIMESTAMP", "nullable": False}
            ],
            primary_keys=["id"],
            foreign_keys=[],
            indexes=[
                {"name": "idx_products_category", "columns": ["category"]},
                {"name": "idx_products_price", "columns": ["price"]}
            ],
            description="Product catalog"
        )
    ]
    
    user_preferences = {}
    query_history = []
    performance_hints = {}
    
    if context_data:
        user_preferences = context_data.get('user_preferences', {})
        query_history = context_data.get('query_history', [])
        performance_hints = context_data.get('performance_hints', {})
    
    return SQLGenerationContext(
        schemas=default_schemas,
        user_preferences=user_preferences,
        query_history=query_history,
        performance_hints=performance_hints
    )


async def _analyze_query_performance(sql: str) -> Dict[str, Any]:
    """Analyze query performance characteristics"""
    analysis = {
        'complexity_score': 0,
        'estimated_cost': 10,
        'bottlenecks': [],
        'optimization_opportunities': []
    }
    
    # Simple complexity scoring
    sql_upper = sql.upper()
    
    # Base complexity from length
    analysis['complexity_score'] = len(sql) // 10
    
    # Add complexity for various features
    if 'JOIN' in sql_upper:
        analysis['complexity_score'] += 20
        analysis['optimization_opportunities'].append("Consider join order optimization")
    
    if 'GROUP BY' in sql_upper:
        analysis['complexity_score'] += 15
        analysis['optimization_opportunities'].append("Ensure GROUP BY columns are indexed")
    
    if 'ORDER BY' in sql_upper:
        analysis['complexity_score'] += 10
        analysis['optimization_opportunities'].append("Create composite index for ORDER BY columns")
    
    if 'SELECT *' in sql_upper:
        analysis['bottlenecks'].append("Selecting all columns increases I/O")
        analysis['optimization_opportunities'].append("Specify only required columns")
    
    # Estimate cost based on complexity
    analysis['estimated_cost'] = analysis['complexity_score'] * 5
    
    return analysis


async def _generate_execution_plan(sql: str, dialect: str) -> Dict[str, Any]:
    """Generate mock execution plan for SQL query"""
    # In production, this would interface with the actual database EXPLAIN PLAN
    plan = {
        'operation': 'SELECT STATEMENT',
        'cost': 100,
        'cardinality': 1000,
        'steps': [
            {
                'id': 1,
                'operation': 'TABLE ACCESS',
                'object_name': 'SALES',
                'cost': 50,
                'cardinality': 1000,
                'access_method': 'FULL SCAN'
            }
        ],
        'total_cost': 100,
        'optimizer_mode': 'ALL_ROWS'
    }
    
    # Adjust plan based on SQL content
    sql_upper = sql.upper()
    
    if 'JOIN' in sql_upper:
        plan['steps'].append({
            'id': 2,
            'operation': 'HASH JOIN',
            'cost': 75,
            'cardinality': 500,
            'access_method': 'HASH'
        })
        plan['total_cost'] += 75
    
    if 'ORDER BY' in sql_upper:
        plan['steps'].append({
            'id': 3,
            'operation': 'SORT',
            'cost': 25,
            'cardinality': plan['cardinality'],
            'access_method': 'SORT'
        })
        plan['total_cost'] += 25
    
    return plan


async def _analyze_query_cost(sql: str) -> Dict[str, Any]:
    """Analyze query cost components"""
    cost_analysis = {
        'cpu_cost': 50,
        'io_cost': 30,
        'network_cost': 10,
        'total_cost': 90,
        'estimated_rows': 1000,
        'estimated_bytes': 50000
    }
    
    # Adjust costs based on SQL complexity
    sql_upper = sql.upper()
    
    if 'JOIN' in sql_upper:
        cost_analysis['cpu_cost'] += 30
        cost_analysis['io_cost'] += 20
        cost_analysis['estimated_rows'] *= 2
    
    if 'GROUP BY' in sql_upper:
        cost_analysis['cpu_cost'] += 25
        cost_analysis['estimated_rows'] //= 2
    
    if 'ORDER BY' in sql_upper:
        cost_analysis['cpu_cost'] += 15
    
    # Recalculate total
    cost_analysis['total_cost'] = (
        cost_analysis['cpu_cost'] + 
        cost_analysis['io_cost'] + 
        cost_analysis['network_cost']
    )
    
    cost_analysis['estimated_bytes'] = cost_analysis['estimated_rows'] * 50
    
    return cost_analysis


async def _generate_execution_recommendations(sql: str, execution_plan: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on execution plan"""
    recommendations = []
    
    # Analyze execution plan for optimization opportunities
    total_cost = execution_plan.get('total_cost', 0)
    
    if total_cost > 100:
        recommendations.append("Query cost is high - consider adding WHERE clause to reduce rows")
    
    # Check for full table scans
    for step in execution_plan.get('steps', []):
        if step.get('access_method') == 'FULL SCAN':
            recommendations.append(f"Consider adding index on {step.get('object_name')} for better performance")
    
    # SQL-specific recommendations
    sql_upper = sql.upper()
    
    if 'SELECT *' in sql_upper:
        recommendations.append("Replace SELECT * with specific columns to reduce I/O")
    
    if 'ORDER BY' in sql_upper and 'LIMIT' not in sql_upper and 'FETCH' not in sql_upper:
        recommendations.append("Consider adding FETCH FIRST to limit result set")
    
    if not recommendations:
        recommendations.append("Query appears to be well-optimized")
    
    return recommendations


async def _log_audit_event(request: Request, event_type: AuditEventType, details: Dict[str, Any]):
    """Log audit event for SQL operations"""
    # In production, this would log to audit system
    logger.info("Audit event", 
               event_type=event_type.value,
               details=details,
               user_agent=request.headers.get("user-agent"),
               ip_address=request.client.host if request.client else "unknown")