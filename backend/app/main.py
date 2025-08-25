from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, sql, metrics
from app.core.logging_config import init_logging

# Initialize logging
init_logging()

app = FastAPI(
    title="Oatie Backend",
    description="Oracle BI Publisher AI Assistant - Eliminates SQL table reference hallucinations",
    version="0.1.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(sql.router, prefix="/sql", tags=["sql"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
