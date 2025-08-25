import re
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Dict, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.metadata_objects import TableMetadata
from app.core.database import get_db

@dataclass
class TableValidationResult:
    valid: bool
    missing_objects: List[str]
    suggestions: Dict[str, List[str]]

class SchemaValidatorService:
    """
    Schema validation service with database integration.
    Validates SQL against registered table metadata stored in the database.
    """
    
    # Regex pattern to extract table names from SQL
    table_pattern = re.compile(r"FROM\s+([A-Z0-9_]+)|JOIN\s+([A-Z0-9_]+)", re.IGNORECASE)
    
    def __init__(self):
        # In-memory cache for performance (invalidated when tables are registered)
        self._cache: Dict[str, Set[str]] = {}
    
    def extract_table_names(self, sql: str) -> List[str]:
        """Extract table names from SQL query using regex pattern."""
        matches = self.table_pattern.findall(sql)
        tables = []
        for match in matches:
            tables.extend([t for t in match if t])
        return list({t.upper() for t in tables})
    
    async def get_schema_tables(self, schema_name: str) -> Set[str]:
        """
        Get all table names for a schema from the database.
        Uses async database session and caches results.
        """
        schema_upper = schema_name.upper()
        
        # Check cache first
        if schema_upper in self._cache:
            return self._cache[schema_upper]
        
        # Query database with direct session
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(TableMetadata.table_name)
                .where(TableMetadata.schema_name == schema_upper)
            )
            tables = {row[0] for row in result.fetchall()}
            
            # Cache the result
            self._cache[schema_upper] = tables
            return tables
    
    @lru_cache(maxsize=128)
    def fuzzy_suggestions(self, schema_name: str, table_name: str, available_tables: tuple) -> List[str]:
        """
        Generate fuzzy suggestions for a missing table name.
        Uses simple heuristics: character overlap and prefix matching.
        """
        name_upper = table_name.upper()
        scored = []
        
        for candidate in available_tables:
            # Simple scoring: character overlap + prefix bonus
            common_chars = len(set(name_upper) & set(candidate))
            prefix_bonus = 2 if candidate.startswith(name_upper[:3]) else 0
            score = common_chars + prefix_bonus
            scored.append((score, candidate))
        
        # Return top 5 suggestions
        scored.sort(reverse=True)
        return [candidate for _, candidate in scored[:5]]
    
    async def validate_sql(self, schema_name: str, sql: str) -> TableValidationResult:
        """
        Validate SQL against database-stored table metadata.
        Returns validation result with missing tables and suggestions.
        """
        # Extract table names from SQL
        extracted_tables = self.extract_table_names(sql)
        
        # Get available tables from database
        available_tables = await self.get_schema_tables(schema_name)
        
        # Find missing tables
        missing_tables = [t for t in extracted_tables if t not in available_tables]
        
        # Generate suggestions for missing tables
        suggestions = {}
        if missing_tables and available_tables:
            available_tuple = tuple(available_tables)  # For LRU cache compatibility
            for missing_table in missing_tables:
                suggestions[missing_table] = self.fuzzy_suggestions(
                    schema_name, missing_table, available_tuple
                )
        
        return TableValidationResult(
            valid=len(missing_tables) == 0,
            missing_objects=missing_tables,
            suggestions=suggestions
        )
    
    async def register_tables(self, schema_name: str, table_names: List[str]) -> int:
        """
        Register new tables for a schema in the database.
        Returns the number of tables actually added (excludes duplicates).
        """
        schema_upper = schema_name.upper()
        tables_upper = [t.upper() for t in table_names]
        
        # Clear cache for this schema
        self._cache.pop(schema_upper, None)
        
        # Create a direct database session
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Check which tables already exist
                existing_result = await db.execute(
                    select(TableMetadata.table_name)
                    .where(
                        TableMetadata.schema_name == schema_upper,
                        TableMetadata.table_name.in_(tables_upper)
                    )
                )
                existing_tables = {row[0] for row in existing_result.fetchall()}
                
                # Add only new tables
                new_tables = [t for t in tables_upper if t not in existing_tables]
                
                if new_tables:
                    # Bulk insert new table metadata
                    new_metadata = [
                        TableMetadata(schema_name=schema_upper, table_name=table_name)
                        for table_name in new_tables
                    ]
                    db.add_all(new_metadata)
                    await db.commit()
                
                return len(new_tables)
            except Exception:
                await db.rollback()
                raise
    
    async def list_tables(self, schema_name: str) -> List[str]:
        """Get list of all tables for a schema (for API responses)."""
        tables = await self.get_schema_tables(schema_name)
        return sorted(list(tables))
    
    def clear_cache(self):
        """Clear the in-memory cache (useful for testing)."""
        self._cache.clear()


# Global instance for dependency injection
validator_service = SchemaValidatorService()
