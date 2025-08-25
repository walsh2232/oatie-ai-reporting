import os
import asyncio
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from app.services.schema_validator import SchemaValidatorService, TableValidationResult

# LLM Integration imports
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class QueryContext:
    """Context information for SQL generation"""
    schema_name: str
    available_tables: List[str]
    table_relationships: Dict[str, List[str]] = None  # Future: table joins
    column_metadata: Dict[str, List[str]] = None      # Future: column info

class SQLAgent:
    """
    Enhanced SQL Generation Agent with LLM integration.
    Falls back to deterministic heuristics if LLM is unavailable.
    """
    
    def __init__(self, validator_service: SchemaValidatorService):
        self.validator = validator_service
        self.openai_client = None
        self._setup_llm()
    
    def _setup_llm(self):
        """Initialize OpenAI client if API key is available"""
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.llm_enabled = True
        else:
            self.llm_enabled = False
    
    async def _get_query_context(self, schema_name: str) -> QueryContext:
        """Build context for SQL generation"""
        available_tables = await self.validator.get_schema_tables(schema_name)
        return QueryContext(
            schema_name=schema_name,
            available_tables=list(available_tables)
        )
    
    def _build_llm_prompt(self, context: QueryContext, request: str) -> str:
        """Build optimized prompt for LLM SQL generation"""
        tables_list = ", ".join(context.available_tables) if context.available_tables else "No tables registered"
        
        return f"""You are an expert Oracle SQL generator for BI Publisher reports. Generate a valid Oracle SQL query based on the user request.

IMPORTANT CONSTRAINTS:
- ONLY use tables from this exact list: {tables_list}
- Use Oracle SQL syntax (ROWNUM for limits, proper date functions)
- For Oracle BI Publisher, prefer simple, efficient queries
- Always include ROWNUM <= N for large result sets to prevent timeouts
- Use proper Oracle date formats and functions

SCHEMA: {context.schema_name}
AVAILABLE TABLES: {tables_list}

USER REQUEST: {request}

Generate ONLY the SQL query without explanations. If tables are missing, use the available ones that best match the intent."""

    async def _generate_sql_with_llm(self, context: QueryContext, request: str) -> str:
        """Generate SQL using OpenAI LLM"""
        try:
            prompt = self._build_llm_prompt(context, request)
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using 3.5-turbo for speed and cost efficiency
                messages=[
                    {"role": "system", "content": "You are an expert Oracle SQL generator. Return only valid SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1,  # Low temperature for consistent SQL generation
                timeout=10.0
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Clean up the response (remove markdown formatting if present)
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]
            
            return sql.strip()
            
        except Exception as e:
            # Fall back to deterministic generation on LLM failure
            print(f"LLM generation failed: {e}, falling back to deterministic generation")
            return self._generate_sql_deterministic(request)
    
    def _generate_sql_deterministic(self, request: str) -> str:
        """
        Fallback deterministic SQL generation (original logic)
        """
        request_lower = request.lower()
        
        # Basic keyword-based SQL generation
        if any(keyword in request_lower for keyword in ['count', 'how many', 'number of']):
            if 'people' in request_lower:
                return "SELECT COUNT(*) AS PEOPLE_COUNT FROM PER_ALL_PEOPLE_F"
            elif 'assignment' in request_lower:
                return "SELECT COUNT(*) AS ASSIGNMENT_COUNT FROM PER_ALL_ASSIGNMENTS_F"
            else:
                return "SELECT COUNT(*) FROM PER_ALL_PEOPLE_F"
        
        elif any(keyword in request_lower for keyword in ['show', 'list', 'get', 'find']):
            if 'people' in request_lower:
                return "SELECT PERSON_ID, FIRST_NAME, LAST_NAME FROM PER_ALL_PEOPLE_F WHERE ROWNUM <= 10"
            elif 'assignment' in request_lower:
                return "SELECT ASSIGNMENT_ID, PERSON_ID, JOB_ID FROM PER_ALL_ASSIGNMENTS_F WHERE ROWNUM <= 10"
            else:
                return "SELECT * FROM PER_ALL_PEOPLE_F WHERE ROWNUM <= 10"
        
        else:
            # Default fallback
            return "SELECT * FROM PER_ALL_PEOPLE_F WHERE ROWNUM <= 5"
    
    async def generate_sql(self, schema_name: str, natural_language_request: str) -> str:
        """
        Generate SQL from natural language request.
        Uses LLM if available, falls back to deterministic generation.
        """
        if self.llm_enabled and self.openai_client:
            # Get context for LLM generation
            context = await self._get_query_context(schema_name)
            
            # Use LLM for intelligent generation
            return await self._generate_sql_with_llm(context, natural_language_request)
        else:
            # Use deterministic generation
            return self._generate_sql_deterministic(natural_language_request)
    
    async def generate_and_validate(self, schema_name: str, natural_language_request: str) -> Tuple[str, TableValidationResult]:
        """
        Generate SQL and validate it against the schema.
        Returns both the generated SQL and validation result.
        """
        # Generate SQL (with LLM or deterministic)
        sql = await self.generate_sql(schema_name, natural_language_request)
        
        # Validate the generated SQL
        validation = await self.validator.validate_sql(schema_name, sql)
        
        return sql, validation
    
    async def suggest_table_joins(self, schema_name: str, tables: List[str]) -> Dict[str, Any]:
        """
        Future enhancement: Suggest appropriate table joins based on schema analysis
        """
        # Placeholder for future implementation
        return {
            "suggestions": [],
            "message": "Table join suggestions not yet implemented"
        }
    
    def get_generation_method(self) -> str:
        """Return current generation method for debugging"""
        return "LLM-powered" if self.llm_enabled else "Deterministic"


# Global instance for dependency injection
from app.services.schema_validator import validator_service
agent = SQLAgent(validator_service)
