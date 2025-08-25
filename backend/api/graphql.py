"""
Enterprise GraphQL API for advanced querying capabilities
Provides flexible data access with optimized resolvers
"""

import strawberry
from typing import List, Optional
from datetime import datetime

from starlette.applications import Starlette
from strawberry.starlette import GraphQLRouter


@strawberry.type
class User:
    id: str
    username: str
    email: str
    full_name: str
    roles: List[str]
    active: bool
    created_at: datetime


@strawberry.type
class Report:
    id: str
    name: str
    description: str
    template_path: str
    created_at: datetime
    execution_count: int


@strawberry.type
class QueryExecution:
    id: str
    sql: str
    status: str
    execution_time_ms: float
    row_count: int
    created_at: datetime


@strawberry.type
class PerformanceMetric:
    metric_name: str
    value: float
    unit: str
    timestamp: datetime


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, limit: int = 10) -> List[User]:
        """Get list of users with pagination"""
        # Mock data
        return [
            User(
                id="user_001",
                username="admin",
                email="admin@company.com",
                full_name="System Administrator",
                roles=["admin"],
                active=True,
                created_at=datetime.now()
            ),
            User(
                id="user_002", 
                username="analyst1",
                email="analyst1@company.com",
                full_name="Business Analyst",
                roles=["analyst"],
                active=True,
                created_at=datetime.now()
            )
        ][:limit]
    
    @strawberry.field
    async def reports(self, limit: int = 10) -> List[Report]:
        """Get list of available reports"""
        return [
            Report(
                id="sales_summary",
                name="Sales Summary Report",
                description="Comprehensive sales performance analysis",
                template_path="/oracle/bi/reports/sales_summary.rtf",
                created_at=datetime.now(),
                execution_count=524
            ),
            Report(
                id="financial_dashboard",
                name="Financial Performance Dashboard",
                description="Executive financial dashboard with KPIs",
                template_path="/oracle/bi/reports/financial_dashboard.rtf",
                created_at=datetime.now(),
                execution_count=398
            )
        ][:limit]
    
    @strawberry.field
    async def query_executions(self, limit: int = 20) -> List[QueryExecution]:
        """Get recent query executions"""
        return [
            QueryExecution(
                id="q_abc12345",
                sql="SELECT product, SUM(sales_amount) FROM sales GROUP BY product",
                status="COMPLETED",
                execution_time_ms=150.5,
                row_count=25,
                created_at=datetime.now()
            ),
            QueryExecution(
                id="q_def67890",
                sql="SELECT * FROM customers WHERE region = 'North'",
                status="COMPLETED",
                execution_time_ms=89.2,
                row_count=142,
                created_at=datetime.now()
            )
        ][:limit]
    
    @strawberry.field
    async def performance_metrics(self) -> List[PerformanceMetric]:
        """Get system performance metrics"""
        return [
            PerformanceMetric(
                metric_name="average_response_time",
                value=0.85,
                unit="seconds",
                timestamp=datetime.now()
            ),
            PerformanceMetric(
                metric_name="cache_hit_rate",
                value=85.5,
                unit="percent",
                timestamp=datetime.now()
            ),
            PerformanceMetric(
                metric_name="active_users",
                value=142,
                unit="count",
                timestamp=datetime.now()
            )
        ]


@strawberry.input
class CreateReportInput:
    name: str
    description: str
    template_path: str


@strawberry.input
class ExecuteQueryInput:
    sql: str
    parameters: Optional[str] = None
    use_cache: bool = True


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_report(self, input: CreateReportInput) -> Report:
        """Create a new report template"""
        return Report(
            id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=input.name,
            description=input.description,
            template_path=input.template_path,
            created_at=datetime.now(),
            execution_count=0
        )
    
    @strawberry.mutation
    async def execute_query(self, input: ExecuteQueryInput) -> QueryExecution:
        """Execute a SQL query"""
        return QueryExecution(
            id=f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            sql=input.sql,
            status="COMPLETED",
            execution_time_ms=125.3,
            row_count=15,
            created_at=datetime.now()
        )


# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router
graphql_app = GraphQLRouter(schema, debug=True)