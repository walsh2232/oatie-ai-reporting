from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.schema_validator import validator_service
from app.services.sql_agent import agent
from prometheus_client import Counter

router = APIRouter()

# Request/Response Models
class SQLRequest(BaseModel):
    schema_name: str
    sql: str

class SQLValidationResponse(BaseModel):
    valid: bool
    missing_objects: List[str]
    suggestions: dict[str, List[str]]

class NLRequest(BaseModel):
    schema_name: str
    request: str

class SQLGenerationResponse(BaseModel):
    sql: str
    valid: bool
    missing_objects: List[str]
    suggestions: dict[str, List[str]]
    generation_method: str  # New field to show LLM vs deterministic

class RegisterTablesRequest(BaseModel):
    schema_name: str
    tables: List[str]

class RegisterTablesResponse(BaseModel):
    schema_name: str
    count: int
    total: int

class AIStatusResponse(BaseModel):
    llm_enabled: bool
    generation_method: str
    model_info: dict

# Prometheus Metrics
validate_counter = Counter('oatie_sql_validate_total', 'SQL validation requests total')
generate_counter = Counter('oatie_sql_generate_total', 'SQL generation requests total')
register_counter = Counter('oatie_sql_register_tables_total', 'Register tables requests total')
ai_generate_counter = Counter('oatie_ai_generate_total', 'AI-powered SQL generation requests total')

@router.get("/ai-status", response_model=AIStatusResponse)
async def get_ai_status():
    """Get current AI/LLM status and capabilities"""
    return AIStatusResponse(
        llm_enabled=agent.llm_enabled,
        generation_method=agent.get_generation_method(),
        model_info={
            "available": agent.llm_enabled,
            "fallback": "deterministic heuristics",
            "model": "gpt-3.5-turbo" if agent.llm_enabled else None
        }
    )

@router.post("/validate", response_model=SQLValidationResponse)
async def validate_sql(req: SQLRequest):
    """Validate SQL against schema metadata stored in database."""
    try:
        validate_counter.inc()
        result = await validator_service.validate_sql(req.schema_name, req.sql)
        return SQLValidationResponse(
            valid=result.valid,
            missing_objects=result.missing_objects,
            suggestions=result.suggestions,
        )
    except Exception as e:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", response_model=RegisterTablesResponse)
async def register_schema_tables(req: RegisterTablesRequest):
    """Register new tables for a schema in the database."""
    try:
        register_counter.inc()
        # Register tables in database
        added_count = await validator_service.register_tables(req.schema_name, req.tables)
        # Get total count after registration
        total_tables = await validator_service.list_tables(req.schema_name)
        return RegisterTablesResponse(
            schema_name=req.schema_name, 
            count=added_count, 
            total=len(total_tables)
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=SQLGenerationResponse)
async def generate_sql(req: NLRequest):
    """Generate SQL from natural language request and validate it."""
    try:
        generate_counter.inc()
        if agent.llm_enabled:
            ai_generate_counter.inc()
        
        sql, validation = await agent.generate_and_validate(req.schema_name, req.request)
        return SQLGenerationResponse(
            sql=sql,
            valid=validation.valid,
            missing_objects=validation.missing_objects,
            suggestions=validation.suggestions,
            generation_method=agent.get_generation_method()
        )
    except Exception as e:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(e))
