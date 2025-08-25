"""
Advanced NLP to SQL Generation Service with Oracle Optimization
Enterprise-grade natural language processing for business intelligence queries
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

import structlog

logger = structlog.get_logger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels for optimization"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ADVANCED = "advanced"


class SQLDialect(Enum):
    """Supported SQL dialects"""
    ORACLE = "oracle"
    POSTGRES = "postgres"
    MYSQL = "mysql"


@dataclass
class TableSchema:
    """Database table schema information"""
    name: str
    columns: List[Dict[str, str]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[Dict[str, str]]
    description: Optional[str] = None


@dataclass
class SQLGenerationContext:
    """Context for SQL generation"""
    schemas: List[TableSchema]
    user_preferences: Dict[str, Any]
    query_history: List[str]
    performance_hints: Dict[str, str]


@dataclass
class GeneratedSQL:
    """Generated SQL query with metadata"""
    sql: str
    confidence: float
    complexity: QueryComplexity
    estimated_cost: int
    optimization_hints: List[str]
    tables_used: List[str]
    explanation: str


class NLPSQLGenerator:
    """
    Advanced Natural Language to SQL conversion engine with Oracle optimization
    """
    
    def __init__(self, dialect: SQLDialect = SQLDialect.ORACLE):
        self.dialect = dialect
        self.context: Optional[SQLGenerationContext] = None
        
        # Initialize pattern matching for common business queries
        self._init_query_patterns()
        
        # Oracle-specific function mappings
        self._init_oracle_functions()
        
        logger.info("NLP SQL Generator initialized", dialect=dialect.value)
    
    def _init_query_patterns(self):
        """Initialize natural language query patterns"""
        self.query_patterns = {
            # Aggregation patterns
            r'(?:show|get|find|list)\s+(?:total|sum|count|average|avg)\s+(.+?)(?:\s+by\s+(.+?))?(?:\s+where\s+(.+?))?$': {
                'type': 'aggregation',
                'function': self._build_aggregation_query
            },
            
            # Comparison patterns
            r'(?:show|get|find|list)\s+(.+?)\s+(?:where|with|having)\s+(.+?)\s+(?:>|<|>=|<=|=|!=)\s+(.+?)$': {
                'type': 'comparison',
                'function': self._build_comparison_query
            },
            
            # Time-based patterns
            r'(?:show|get|find|list)\s+(.+?)\s+(?:from|in|during)\s+(?:last|past)\s+(\d+)\s+(day|week|month|year)s?': {
                'type': 'temporal',
                'function': self._build_temporal_query
            },
            
            # Top/Bottom patterns
            r'(?:show|get|find|list)\s+(?:top|bottom)\s+(\d+)\s+(.+?)(?:\s+by\s+(.+?))?': {
                'type': 'ranking',
                'function': self._build_ranking_query
            },
            
            # Join patterns
            r'(?:show|get|find|list)\s+(.+?)\s+(?:and|with)\s+(?:their|its)\s+(.+?)': {
                'type': 'join',
                'function': self._build_join_query
            }
        }
    
    def _init_oracle_functions(self):
        """Initialize Oracle-specific function mappings"""
        self.oracle_functions = {
            'current_date': 'SYSDATE',
            'current_time': 'SYSTIMESTAMP',
            'concatenate': 'CONCAT',
            'substring': 'SUBSTR',
            'length': 'LENGTH',
            'upper': 'UPPER',
            'lower': 'LOWER',
            'round': 'ROUND',
            'truncate': 'TRUNC',
            'rank': 'RANK() OVER',
            'row_number': 'ROW_NUMBER() OVER'
        }
    
    async def set_context(self, context: SQLGenerationContext):
        """Set the database context for SQL generation"""
        self.context = context
        logger.debug("Context updated", 
                    schema_count=len(context.schemas),
                    has_history=len(context.query_history) > 0)
    
    async def generate_sql(self, natural_query: str) -> GeneratedSQL:
        """
        Generate SQL from natural language query
        
        Args:
            natural_query: Natural language description of the query
            
        Returns:
            GeneratedSQL object with query and metadata
        """
        if not self.context:
            raise ValueError("Context must be set before generating SQL")
        
        # Preprocess the natural language query
        processed_query = self._preprocess_query(natural_query)
        
        # Analyze query complexity
        complexity = self._analyze_complexity(processed_query)
        
        # Pattern matching to determine query type
        query_type, match_result = self._match_query_pattern(processed_query)
        
        if query_type:
            # Generate SQL using pattern-based approach
            sql = await self._generate_from_pattern(query_type, match_result, processed_query)
        else:
            # Fallback to keyword-based generation
            sql = await self._generate_from_keywords(processed_query)
        
        # Apply Oracle-specific optimizations
        optimized_sql = self._apply_oracle_optimizations(sql, complexity)
        
        # Generate optimization hints
        optimization_hints = self._generate_optimization_hints(optimized_sql, complexity)
        
        # Extract tables used
        tables_used = self._extract_table_references(optimized_sql)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(natural_query, optimized_sql, query_type)
        
        # Estimate query cost
        estimated_cost = self._estimate_query_cost(optimized_sql, complexity)
        
        # Generate explanation
        explanation = self._generate_explanation(natural_query, optimized_sql, query_type)
        
        result = GeneratedSQL(
            sql=optimized_sql,
            confidence=confidence,
            complexity=complexity,
            estimated_cost=estimated_cost,
            optimization_hints=optimization_hints,
            tables_used=tables_used,
            explanation=explanation
        )
        
        logger.info("SQL generated", 
                   query_length=len(natural_query),
                   sql_length=len(optimized_sql),
                   confidence=confidence,
                   complexity=complexity.value)
        
        return result
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess natural language query"""
        # Convert to lowercase and normalize whitespace
        query = re.sub(r'\s+', ' ', query.lower().strip())
        
        # Expand common abbreviations
        abbreviations = {
            'qty': 'quantity',
            'amt': 'amount',
            'avg': 'average',
            'max': 'maximum',
            'min': 'minimum',
            'dept': 'department',
            'mgr': 'manager',
            'emp': 'employee',
            'cust': 'customer',
            'prod': 'product'
        }
        
        for abbr, full in abbreviations.items():
            query = re.sub(rf'\b{abbr}\b', full, query)
        
        return query
    
    def _analyze_complexity(self, query: str) -> QueryComplexity:
        """Analyze query complexity based on keywords and patterns"""
        complexity_indicators = {
            QueryComplexity.SIMPLE: ['show', 'get', 'list', 'count', 'sum'],
            QueryComplexity.MODERATE: ['where', 'group by', 'order by', 'join', 'and', 'or'],
            QueryComplexity.COMPLEX: ['subquery', 'union', 'having', 'case when', 'window'],
            QueryComplexity.ADVANCED: ['recursive', 'pivot', 'unpivot', 'analytic', 'partition']
        }
        
        scores = {}
        for level, keywords in complexity_indicators.items():
            score = sum(1 for keyword in keywords if keyword in query)
            scores[level] = score
        
        # Determine complexity based on highest scoring level with minimum threshold
        if scores[QueryComplexity.ADVANCED] >= 1:
            return QueryComplexity.ADVANCED
        elif scores[QueryComplexity.COMPLEX] >= 2:
            return QueryComplexity.COMPLEX
        elif scores[QueryComplexity.MODERATE] >= 3:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
    
    def _match_query_pattern(self, query: str) -> Tuple[Optional[str], Optional[Any]]:
        """Match query against known patterns"""
        for pattern, config in self.query_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return config['type'], match
        return None, None
    
    async def _generate_from_pattern(self, query_type: str, match_result: Any, original_query: str) -> str:
        """Generate SQL from matched pattern"""
        pattern_config = None
        for pattern, config in self.query_patterns.items():
            if config['type'] == query_type:
                pattern_config = config
                break
        
        if pattern_config and 'function' in pattern_config:
            return await pattern_config['function'](match_result, original_query)
        
        return await self._generate_from_keywords(original_query)
    
    async def _build_aggregation_query(self, match_result: Any, original_query: str) -> str:
        """Build aggregation query from pattern match"""
        groups = match_result.groups()
        metric = groups[0] if groups[0] else "count(*)"
        group_by = groups[1] if len(groups) > 1 and groups[1] else None
        where_clause = groups[2] if len(groups) > 2 and groups[2] else None
        
        # Map common metrics to SQL functions
        metric_mapping = {
            'total': 'SUM',
            'sum': 'SUM',
            'count': 'COUNT',
            'average': 'AVG',
            'avg': 'AVG',
            'maximum': 'MAX',
            'max': 'MAX',
            'minimum': 'MIN',
            'min': 'MIN'
        }
        
        # Try to find appropriate table and column
        table_name, column_name = self._resolve_table_and_column(metric)
        
        sql_parts = ["SELECT"]
        
        if group_by:
            group_col = self._resolve_column_name(group_by, table_name)
            sql_parts.append(f"{group_col},")
        
        # Determine aggregation function
        agg_func = "COUNT"
        for key, func in metric_mapping.items():
            if key in metric.lower():
                agg_func = func
                break
        
        if column_name and agg_func != "COUNT":
            sql_parts.append(f"{agg_func}({column_name}) as {metric.replace(' ', '_')}")
        else:
            sql_parts.append(f"{agg_func}(*) as total_count")
        
        sql_parts.extend([f"FROM {table_name}"])
        
        if where_clause:
            where_sql = self._build_where_clause(where_clause, table_name)
            sql_parts.append(f"WHERE {where_sql}")
        
        if group_by:
            group_col = self._resolve_column_name(group_by, table_name)
            sql_parts.append(f"GROUP BY {group_col}")
        
        return " ".join(sql_parts)
    
    async def _build_comparison_query(self, match_result: Any, original_query: str) -> str:
        """Build comparison query from pattern match"""
        groups = match_result.groups()
        fields = groups[0] if groups[0] else "*"
        condition = groups[1] if len(groups) > 1 and groups[1] else ""
        value = groups[2] if len(groups) > 2 and groups[2] else ""
        
        table_name, _ = self._resolve_table_and_column(fields)
        
        sql_parts = ["SELECT"]
        
        if fields == "*" or "all" in fields:
            sql_parts.append("*")
        else:
            column_list = self._resolve_column_list(fields, table_name)
            sql_parts.append(column_list)
        
        sql_parts.extend([f"FROM {table_name}"])
        
        if condition and value:
            where_clause = self._build_comparison_where(condition, value, table_name)
            sql_parts.append(f"WHERE {where_clause}")
        
        return " ".join(sql_parts)
    
    async def _build_temporal_query(self, match_result: Any, original_query: str) -> str:
        """Build time-based query from pattern match"""
        groups = match_result.groups()
        fields = groups[0] if groups[0] else "*"
        number = groups[1] if len(groups) > 1 and groups[1] else "1"
        unit = groups[2] if len(groups) > 2 and groups[2] else "day"
        
        table_name, date_column = self._resolve_table_and_date_column(fields)
        
        sql_parts = ["SELECT"]
        
        if fields == "*" or "all" in fields:
            sql_parts.append("*")
        else:
            column_list = self._resolve_column_list(fields, table_name)
            sql_parts.append(column_list)
        
        sql_parts.extend([f"FROM {table_name}"])
        
        # Build temporal WHERE clause for Oracle
        if self.dialect == SQLDialect.ORACLE:
            time_expr = f"SYSDATE - INTERVAL '{number}' {unit.upper()}"
            sql_parts.append(f"WHERE {date_column} >= {time_expr}")
        
        return " ".join(sql_parts)
    
    async def _build_ranking_query(self, match_result: Any, original_query: str) -> str:
        """Build ranking query (TOP/BOTTOM N) from pattern match"""
        groups = match_result.groups()
        limit = groups[0] if groups[0] else "10"
        fields = groups[1] if len(groups) > 1 and groups[1] else "*"
        order_by = groups[2] if len(groups) > 2 and groups[2] else None
        
        table_name, _ = self._resolve_table_and_column(fields)
        
        # Determine if it's TOP or BOTTOM
        is_bottom = "bottom" in original_query.lower()
        
        sql_parts = ["SELECT"]
        
        if fields == "*" or "all" in fields:
            sql_parts.append("*")
        else:
            column_list = self._resolve_column_list(fields, table_name)
            sql_parts.append(column_list)
        
        sql_parts.extend([f"FROM {table_name}"])
        
        if order_by:
            order_column = self._resolve_column_name(order_by, table_name)
            order_direction = "ASC" if is_bottom else "DESC"
            sql_parts.append(f"ORDER BY {order_column} {order_direction}")
        
        # For Oracle, use ROWNUM or FETCH FIRST
        if self.dialect == SQLDialect.ORACLE:
            sql_parts.append(f"FETCH FIRST {limit} ROWS ONLY")
        
        return " ".join(sql_parts)
    
    async def _build_join_query(self, match_result: Any, original_query: str) -> str:
        """Build JOIN query from pattern match"""
        groups = match_result.groups()
        main_entity = groups[0] if groups[0] else ""
        related_entity = groups[1] if len(groups) > 1 and groups[1] else ""
        
        # Resolve table names and relationship
        main_table = self._resolve_table_name(main_entity)
        related_table = self._resolve_table_name(related_entity)
        join_condition = self._find_join_condition(main_table, related_table)
        
        sql_parts = [
            "SELECT",
            f"{main_table}.*, {related_table}.*",
            f"FROM {main_table}",
            f"JOIN {related_table} ON {join_condition}"
        ]
        
        return " ".join(sql_parts)
    
    async def _generate_from_keywords(self, query: str) -> str:
        """Fallback keyword-based SQL generation"""
        # Basic keyword extraction and mapping
        keywords = query.split()
        
        # Default simple SELECT query
        sql_parts = ["SELECT *"]
        
        # Try to identify table from keywords
        table_name = self._guess_table_from_keywords(keywords)
        sql_parts.append(f"FROM {table_name}")
        
        # Add basic WHERE if conditions detected
        condition_keywords = ['where', 'with', 'having', 'equals', 'greater', 'less']
        if any(kw in keywords for kw in condition_keywords):
            sql_parts.append("WHERE 1=1 -- Add specific conditions")
        
        return " ".join(sql_parts)
    
    def _resolve_table_and_column(self, field_description: str) -> Tuple[str, Optional[str]]:
        """Resolve table and column names from field description"""
        if not self.context or not self.context.schemas:
            return "default_table", None
        
        # Simple heuristic - use first table if only one, otherwise try to match
        if len(self.context.schemas) == 1:
            table = self.context.schemas[0]
            # Try to find matching column
            for col in table.columns:
                if field_description.lower() in col.get('name', '').lower():
                    return table.name, col['name']
            return table.name, None
        
        # Multiple tables - try to find best match
        best_table = self.context.schemas[0].name
        best_column = None
        
        for schema in self.context.schemas:
            for col in schema.columns:
                if field_description.lower() in col.get('name', '').lower():
                    return schema.name, col['name']
        
        return best_table, best_column
    
    def _resolve_table_and_date_column(self, field_description: str) -> Tuple[str, str]:
        """Resolve table and date column for temporal queries"""
        table_name, _ = self._resolve_table_and_column(field_description)
        
        # Common date column names
        date_columns = ['created_at', 'updated_at', 'date', 'timestamp', 'created_date']
        
        if self.context and self.context.schemas:
            for schema in self.context.schemas:
                if schema.name == table_name:
                    for col in schema.columns:
                        col_name = col.get('name', '').lower()
                        if any(date_col in col_name for date_col in date_columns):
                            return table_name, col['name']
        
        return table_name, "created_at"  # Default fallback
    
    def _resolve_column_name(self, column_description: str, table_name: str) -> str:
        """Resolve column name from description"""
        if self.context and self.context.schemas:
            for schema in self.context.schemas:
                if schema.name == table_name:
                    for col in schema.columns:
                        if column_description.lower() in col.get('name', '').lower():
                            return col['name']
        
        # Fallback to description
        return column_description.replace(' ', '_')
    
    def _resolve_column_list(self, fields_description: str, table_name: str) -> str:
        """Resolve multiple columns from description"""
        if fields_description == "*" or "all" in fields_description:
            return "*"
        
        # Split on common delimiters
        field_parts = re.split(r'[,\s]+and\s+|\s*,\s*', fields_description)
        resolved_columns = []
        
        for part in field_parts:
            if part.strip():
                col_name = self._resolve_column_name(part.strip(), table_name)
                resolved_columns.append(col_name)
        
        return ", ".join(resolved_columns) if resolved_columns else "*"
    
    def _resolve_table_name(self, entity_description: str) -> str:
        """Resolve table name from entity description"""
        if self.context and self.context.schemas:
            for schema in self.context.schemas:
                if entity_description.lower() in schema.name.lower():
                    return schema.name
        
        return entity_description.replace(' ', '_')
    
    def _find_join_condition(self, table1: str, table2: str) -> str:
        """Find JOIN condition between two tables"""
        if self.context and self.context.schemas:
            # Look for foreign key relationships
            for schema in self.context.schemas:
                if schema.name == table1:
                    for fk in schema.foreign_keys:
                        if fk.get('referenced_table') == table2:
                            return f"{table1}.{fk['column']} = {table2}.{fk['referenced_column']}"
        
        # Default fallback
        return f"{table1}.id = {table2}.{table1}_id"
    
    def _build_where_clause(self, condition: str, table_name: str) -> str:
        """Build WHERE clause from condition description"""
        # Simple condition parsing
        column = self._resolve_column_name(condition, table_name)
        return f"{column} IS NOT NULL -- Specify actual condition"
    
    def _build_comparison_where(self, condition: str, value: str, table_name: str) -> str:
        """Build comparison WHERE clause"""
        column = self._resolve_column_name(condition, table_name)
        
        # Determine operator from original query context
        operators = {
            'greater': '>',
            'less': '<',
            'equal': '=',
            'more': '>',
            'above': '>',
            'below': '<',
            'under': '<'
        }
        
        op = '='
        for keyword, operator in operators.items():
            if keyword in condition.lower():
                op = operator
                break
        
        # Handle numeric vs string values
        if value.isdigit():
            return f"{column} {op} {value}"
        else:
            return f"{column} {op} '{value}'"
    
    def _guess_table_from_keywords(self, keywords: List[str]) -> str:
        """Guess table name from query keywords"""
        if self.context and self.context.schemas:
            for schema in self.context.schemas:
                for keyword in keywords:
                    if keyword.lower() in schema.name.lower():
                        return schema.name
            
            # Return first table as fallback
            return self.context.schemas[0].name
        
        return "main_table"
    
    def _apply_oracle_optimizations(self, sql: str, complexity: QueryComplexity) -> str:
        """Apply Oracle-specific optimizations"""
        optimized_sql = sql
        
        # Add Oracle hints based on complexity
        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.ADVANCED]:
            # Add leading hint for complex queries
            if "JOIN" in sql.upper():
                optimized_sql = re.sub(
                    r'SELECT',
                    'SELECT /*+ USE_HASH */ ',
                    optimized_sql,
                    count=1
                )
        
        # Replace generic functions with Oracle equivalents
        for generic, oracle_func in self.oracle_functions.items():
            pattern = rf'\b{generic}\b'
            optimized_sql = re.sub(pattern, oracle_func, optimized_sql, flags=re.IGNORECASE)
        
        return optimized_sql
    
    def _generate_optimization_hints(self, sql: str, complexity: QueryComplexity) -> List[str]:
        """Generate optimization hints for the query"""
        hints = []
        
        # Performance hints based on complexity
        if complexity == QueryComplexity.SIMPLE:
            hints.append("Query is already optimized for simple operations")
        
        elif complexity == QueryComplexity.MODERATE:
            if "ORDER BY" in sql.upper():
                hints.append("Consider adding an index on ORDER BY columns")
            if "WHERE" in sql.upper():
                hints.append("Ensure WHERE clause columns are indexed")
        
        elif complexity == QueryComplexity.COMPLEX:
            hints.append("Consider using Oracle hints for join optimization")
            hints.append("Review subquery performance and consider WITH clauses")
            if "GROUP BY" in sql.upper():
                hints.append("Consider partitioning for large GROUP BY operations")
        
        elif complexity == QueryComplexity.ADVANCED:
            hints.append("Review execution plan and consider parallel processing")
            hints.append("Consider materialized views for frequently accessed data")
            hints.append("Evaluate partitioning strategy for large tables")
        
        # Oracle-specific hints
        if "JOIN" in sql.upper():
            hints.append("Oracle: Consider USE_HASH or USE_NL hints for join optimization")
        
        if "COUNT(" in sql.upper():
            hints.append("Oracle: For large tables, consider using parallel COUNT")
        
        return hints
    
    def _extract_table_references(self, sql: str) -> List[str]:
        """Extract table names referenced in the SQL"""
        tables = []
        
        # Simple regex to find table references
        from_pattern = r'FROM\s+(\w+)'
        join_pattern = r'JOIN\s+(\w+)'
        
        from_matches = re.findall(from_pattern, sql, re.IGNORECASE)
        join_matches = re.findall(join_pattern, sql, re.IGNORECASE)
        
        tables.extend(from_matches)
        tables.extend(join_matches)
        
        return list(set(tables))  # Remove duplicates
    
    def _calculate_confidence(self, natural_query: str, sql: str, query_type: Optional[str]) -> float:
        """Calculate confidence score for the generated SQL"""
        base_confidence = 0.7
        
        # Boost confidence if pattern was matched
        if query_type:
            base_confidence += 0.15
        
        # Boost confidence based on context availability
        if self.context and self.context.schemas:
            base_confidence += 0.1
        
        # Reduce confidence for very short queries
        if len(natural_query.split()) < 3:
            base_confidence -= 0.1
        
        # Reduce confidence for complex unmatched queries
        if not query_type and len(natural_query.split()) > 10:
            base_confidence -= 0.15
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _estimate_query_cost(self, sql: str, complexity: QueryComplexity) -> int:
        """Estimate query execution cost"""
        base_cost = {
            QueryComplexity.SIMPLE: 10,
            QueryComplexity.MODERATE: 50,
            QueryComplexity.COMPLEX: 200,
            QueryComplexity.ADVANCED: 500
        }
        
        cost = base_cost[complexity]
        
        # Adjust based on SQL features
        if "JOIN" in sql.upper():
            cost *= 2
        if "GROUP BY" in sql.upper():
            cost *= 1.5
        if "ORDER BY" in sql.upper():
            cost *= 1.3
        if "DISTINCT" in sql.upper():
            cost *= 1.2
        
        return int(cost)
    
    def _generate_explanation(self, natural_query: str, sql: str, query_type: Optional[str]) -> str:
        """Generate human-readable explanation of the generated SQL"""
        explanations = []
        
        # Base explanation
        if query_type:
            explanations.append(f"Generated {query_type} query based on natural language pattern matching.")
        else:
            explanations.append("Generated query using keyword-based analysis.")
        
        # SQL structure explanation
        if "SELECT" in sql.upper():
            if "COUNT" in sql.upper():
                explanations.append("Counts the number of records meeting the criteria.")
            elif "SUM" in sql.upper():
                explanations.append("Calculates the total sum of specified columns.")
            elif "AVG" in sql.upper():
                explanations.append("Calculates the average value of specified columns.")
            else:
                explanations.append("Retrieves data from the specified tables.")
        
        if "JOIN" in sql.upper():
            explanations.append("Combines data from multiple related tables.")
        
        if "WHERE" in sql.upper():
            explanations.append("Filters results based on specified conditions.")
        
        if "GROUP BY" in sql.upper():
            explanations.append("Groups results by specified columns for aggregation.")
        
        if "ORDER BY" in sql.upper():
            explanations.append("Sorts results in the specified order.")
        
        return " ".join(explanations)


class SQLOptimizer:
    """
    SQL Query Optimization Service with Oracle-specific enhancements
    """
    
    def __init__(self, dialect: SQLDialect = SQLDialect.ORACLE):
        self.dialect = dialect
        logger.info("SQL Optimizer initialized", dialect=dialect.value)
    
    async def optimize_query(self, sql: str, context: Optional[SQLGenerationContext] = None) -> Dict[str, Any]:
        """
        Optimize SQL query for performance
        
        Args:
            sql: Original SQL query
            context: Database context for optimization
            
        Returns:
            Dictionary with optimized query and recommendations
        """
        analysis = self._analyze_query(sql)
        optimizations = self._generate_optimizations(sql, analysis, context)
        optimized_sql = self._apply_optimizations(sql, optimizations)
        
        return {
            'original_sql': sql,
            'optimized_sql': optimized_sql,
            'analysis': analysis,
            'optimizations_applied': optimizations,
            'performance_improvement_estimate': self._estimate_improvement(analysis),
            'recommendations': self._generate_recommendations(analysis, context)
        }
    
    def _analyze_query(self, sql: str) -> Dict[str, Any]:
        """Analyze SQL query for optimization opportunities"""
        analysis = {
            'has_joins': 'JOIN' in sql.upper(),
            'has_subqueries': '(' in sql and 'SELECT' in sql.upper(),
            'has_aggregations': any(func in sql.upper() for func in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']),
            'has_order_by': 'ORDER BY' in sql.upper(),
            'has_group_by': 'GROUP BY' in sql.upper(),
            'has_where': 'WHERE' in sql.upper(),
            'select_star': 'SELECT *' in sql.upper(),
            'estimated_complexity': self._estimate_complexity(sql)
        }
        
        return analysis
    
    def _generate_optimizations(self, sql: str, analysis: Dict[str, Any], context: Optional[SQLGenerationContext]) -> List[str]:
        """Generate list of optimizations to apply"""
        optimizations = []
        
        if analysis['select_star']:
            optimizations.append('replace_select_star')
        
        if analysis['has_joins'] and self.dialect == SQLDialect.ORACLE:
            optimizations.append('add_oracle_join_hints')
        
        if analysis['has_aggregations']:
            optimizations.append('optimize_aggregations')
        
        if analysis['estimated_complexity'] > 50:
            optimizations.append('add_performance_hints')
        
        return optimizations
    
    def _apply_optimizations(self, sql: str, optimizations: List[str]) -> str:
        """Apply optimizations to SQL query"""
        optimized_sql = sql
        
        for optimization in optimizations:
            if optimization == 'replace_select_star':
                # Replace SELECT * with specific columns (simplified)
                optimized_sql = re.sub(r'SELECT \*', 'SELECT col1, col2, col3', optimized_sql, flags=re.IGNORECASE)
            
            elif optimization == 'add_oracle_join_hints':
                optimized_sql = re.sub(r'SELECT', 'SELECT /*+ USE_HASH */', optimized_sql, count=1, flags=re.IGNORECASE)
            
            elif optimization == 'add_performance_hints':
                if self.dialect == SQLDialect.ORACLE:
                    optimized_sql = re.sub(r'SELECT', 'SELECT /*+ PARALLEL(4) */', optimized_sql, count=1, flags=re.IGNORECASE)
        
        return optimized_sql
    
    def _estimate_complexity(self, sql: str) -> int:
        """Estimate query complexity score"""
        score = len(sql) // 10  # Base score from length
        
        # Add complexity for various features
        if 'JOIN' in sql.upper():
            score += 20
        if 'GROUP BY' in sql.upper():
            score += 15
        if 'ORDER BY' in sql.upper():
            score += 10
        if 'DISTINCT' in sql.upper():
            score += 10
        
        # Count subqueries
        subquery_count = sql.upper().count('SELECT') - 1
        score += subquery_count * 25
        
        return score
    
    def _estimate_improvement(self, analysis: Dict[str, Any]) -> str:
        """Estimate performance improvement percentage"""
        improvement = 0
        
        if analysis['select_star']:
            improvement += 10
        if analysis['has_joins']:
            improvement += 15
        if analysis['estimated_complexity'] > 50:
            improvement += 20
        
        if improvement == 0:
            return "0-5%"
        elif improvement < 20:
            return "5-15%"
        elif improvement < 40:
            return "15-30%"
        else:
            return "30-50%"
    
    def _generate_recommendations(self, analysis: Dict[str, Any], context: Optional[SQLGenerationContext]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if analysis['select_star']:
            recommendations.append("Replace SELECT * with specific column names to reduce data transfer")
        
        if analysis['has_joins'] and not analysis['has_where']:
            recommendations.append("Add WHERE clauses to reduce join result set size")
        
        if analysis['has_order_by']:
            recommendations.append("Ensure ORDER BY columns are indexed for better performance")
        
        if analysis['estimated_complexity'] > 100:
            recommendations.append("Consider breaking complex query into smaller parts or using materialized views")
        
        if self.dialect == SQLDialect.ORACLE:
            if analysis['has_aggregations']:
                recommendations.append("Consider using Oracle parallel processing for large aggregations")
            if analysis['has_joins']:
                recommendations.append("Use Oracle optimizer hints (USE_HASH, USE_NL) for join optimization")
        
        return recommendations