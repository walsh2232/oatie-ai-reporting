import pytest
import pytest_asyncio
from app.services.sql_agent import SQLAgent
from app.services.schema_validator import SchemaValidatorService

@pytest_asyncio.fixture
async def agent():
    validator = SchemaValidatorService() 
    validator.clear_cache()
    # Pre-register some test tables
    await validator.register_tables("HCM", ["PER_ALL_PEOPLE_F", "PER_ALL_ASSIGNMENTS_F"])
    return SQLAgent(validator)

@pytest.mark.asyncio
async def test_generate_people_count(agent):
    """Test generating people count SQL"""
    sql, validation = await agent.generate_and_validate("HCM", "people count")
    assert "COUNT" in sql.upper()
    assert "PER_ALL_PEOPLE_F" in sql
    assert validation.valid is True

@pytest.mark.asyncio 
async def test_generate_assignments(agent):
    """Test generating assignment-related SQL"""
    sql, validation = await agent.generate_and_validate("HCM", "show assignments")
    assert "PER_ALL_ASSIGNMENTS_F" in sql
    assert validation.valid is True
