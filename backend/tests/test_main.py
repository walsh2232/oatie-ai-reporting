import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db, Base
from app.models.models import Report, AIInteraction, UserSession  # Import models to register them

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_check():
    """Test health check endpoints"""
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"
    
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to Oatie AI Reporting" in response.json()["message"]


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_reports_endpoint():
    """Test reports API endpoints"""
    # Test GET reports
    response = client.get("/api/v1/reports/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test POST report
    report_data = {
        "name": "Test Report",
        "description": "A test report",
        "oracle_report_path": "/test/path"
    }
    response = client.post("/api/v1/reports/", json=report_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Report"


def test_ai_query_endpoint():
    """Test AI query endpoint"""
    query_data = {
        "query": "Create a sales report",
        "session_id": "test_session"
    }
    response = client.post("/api/v1/ai/query", json=query_data)
    assert response.status_code == 200
    assert "response" in response.json()
    assert "sql_query" in response.json()


def test_detailed_health_endpoint():
    """Test detailed health check"""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["status"] == "healthy"
    assert "checks" in health_data