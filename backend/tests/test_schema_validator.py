import pytest
from app.services.schema_validator import SchemaValidatorService

@pytest.fixture
def validator():
    service = SchemaValidatorService()
    service.clear_cache()
    return service

@pytest.mark.asyncio
async def test_valid_tables(validator):
    """Test validation with existing tables"""
    # First register some test tables
    await validator.register_tables("HCM", ["PER_ALL_PEOPLE_F", "PER_ALL_ASSIGNMENTS_F"])
    
    sql = "SELECT * FROM PER_ALL_PEOPLE_F"
    result = await validator.validate_sql("HCM", sql)
    
    assert result.valid is True
    assert len(result.missing_objects) == 0

@pytest.mark.asyncio
async def test_missing_table(validator):
    """Test validation with missing table"""
    # Register only one table
    await validator.register_tables("HCM", ["PER_ALL_PEOPLE_F"])
    
    sql = "SELECT * FROM MISSING_TABLE"
    result = await validator.validate_sql("HCM", sql)
    
    assert result.valid is False
    assert "MISSING_TABLE" in result.missing_objects
    assert "MISSING_TABLE" in result.suggestions
