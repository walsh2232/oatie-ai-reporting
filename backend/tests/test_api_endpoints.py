import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_live():
    """Test health endpoint"""
    r = client.get('/health/live')
    assert r.status_code == 200
    assert r.json()['status'] == 'live'

@pytest.mark.asyncio
async def test_sql_validate_endpoint():
    """Test validate endpoint with database integration"""
    # First register a table
    reg_payload = {"schema_name": "HCM", "tables": ["PER_ALL_PEOPLE_F"]}
    reg_response = client.post('/sql/register', json=reg_payload)
    assert reg_response.status_code == 200
    
    # Now validate SQL against the registered table
    payload = {"schema_name": "HCM", "sql": "SELECT * FROM PER_ALL_PEOPLE_F"}
    r = client.post('/sql/validate', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['valid'] is True

@pytest.mark.asyncio
async def test_sql_generate_endpoint():
    """Test generate endpoint with database integration"""
    # First register tables
    reg_payload = {"schema_name": "HCM", "tables": ["PER_ALL_PEOPLE_F", "PER_ALL_ASSIGNMENTS_F"]}
    reg_response = client.post('/sql/register', json=reg_payload)
    assert reg_response.status_code == 200
    
    # Now generate SQL
    payload = {"schema_name": "HCM", "request": "people count"}
    r = client.post('/sql/generate', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert 'COUNT' in data['sql']
    assert data['valid'] is True

@pytest.mark.asyncio
async def test_register_tables_endpoint_and_validate():
    """Test register endpoint and subsequent validation"""
    import uuid
    # Use unique table names to avoid conflicts
    test_id = str(uuid.uuid4()).replace('-', '')[:8]
    unique_tables = [f"TEST_TABLE_{test_id}_1", f"TEST_TABLE_{test_id}_2"]
    
    # Register new tables under a test schema
    reg_payload = {"schema_name": "TEST_SCHEMA", "tables": unique_tables}
    r = client.post('/sql/register', json=reg_payload)
    assert r.status_code == 200
    data = r.json()
    assert data['schema_name'] == 'TEST_SCHEMA'
    assert data['count'] == 2
    assert data['total'] >= 2  # May have other tables from previous tests

    # Now validate SQL referencing a newly registered table
    val_payload = {"schema_name": "TEST_SCHEMA", "sql": f"SELECT * FROM {unique_tables[0]}"}
    r2 = client.post('/sql/validate', json=val_payload)
    assert r2.status_code == 200
    vdata = r2.json()
    assert vdata['valid'] is True
    assert vdata['missing_objects'] == []
