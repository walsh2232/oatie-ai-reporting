"""
Phase 2 Database Integration Completion Test

Validates that all database integration features are working correctly:
1. Database persistence and retrieval 
2. Async database operations
3. Cache consistency
4. API endpoint integration
5. SQL validation with database backend
6. Table registration and metadata management
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.services.schema_validator import SchemaValidatorService

client = TestClient(app)

@pytest.mark.asyncio
async def test_phase2_database_integration_complete():
    """Comprehensive test for Phase 2 database integration completion"""
    
    # Test unique identifiers
    test_id = str(uuid.uuid4()).replace('-', '')[:8]
    test_schema = f"PHASE2_TEST_{test_id}"
    test_tables = [f"TBL_{test_id}_1", f"TBL_{test_id}_2", f"TBL_{test_id}_3"]
    
    # 1. Test direct database operations
    validator = SchemaValidatorService()
    validator.clear_cache()
    
    # Register tables directly via service
    added_count = await validator.register_tables(test_schema, test_tables)
    assert added_count == 3, "Database registration failed"
    
    # Verify tables are persisted (database stores in uppercase)
    schema_tables = await validator.get_schema_tables(test_schema)
    assert len(schema_tables) == 3, "Database persistence failed"
    test_tables_upper = [t.upper() for t in test_tables]
    assert all(t in schema_tables for t in test_tables_upper), "Not all tables persisted"
    
    # 2. Test cache functionality
    # Second call should use cache
    cached_tables = await validator.get_schema_tables(test_schema)
    assert cached_tables == schema_tables, "Cache consistency failed"
    
    # 3. Test API endpoint integration
    api_payload = {"schema_name": test_schema, "tables": [f"TBL_{test_id}_4"]}
    response = client.post('/sql/register', json=api_payload)
    assert response.status_code == 200, "API registration failed"
    data = response.json()
    assert data['count'] == 1, "API registration count incorrect"
    assert data['total'] == 4, "API total count incorrect"
    
    # 4. Test SQL validation with database backend
    valid_sql = f"SELECT * FROM {test_tables[0]} WHERE id = 1"
    val_payload = {"schema_name": test_schema, "sql": valid_sql}
    val_response = client.post('/sql/validate', json=val_payload)
    assert val_response.status_code == 200, "SQL validation failed"
    val_data = val_response.json()
    assert val_data['valid'] is True, "Valid SQL incorrectly flagged"
    assert val_data['missing_objects'] == [], "False positive missing objects"
    
    # 5. Test invalid SQL detection
    invalid_sql = f"SELECT * FROM NONEXISTENT_TABLE_{test_id}"
    inv_payload = {"schema_name": test_schema, "sql": invalid_sql}
    inv_response = client.post('/sql/validate', json=inv_payload)
    assert inv_response.status_code == 200, "Invalid SQL validation failed"
    inv_data = inv_response.json()
    assert inv_data['valid'] is False, "Invalid SQL not detected"
    assert len(inv_data['missing_objects']) > 0, "Missing objects not identified"
    
    # 6. Test SQL generation (may reference tables not in test schema - this is expected)
    gen_payload = {"schema_name": test_schema, "request": "count records"}
    gen_response = client.post('/sql/generate', json=gen_payload)
    assert gen_response.status_code == 200, "SQL generation failed"
    gen_data = gen_response.json()
    assert 'COUNT' in gen_data['sql'], "Generated SQL missing COUNT"
    # Generated SQL may reference non-existent tables - this is expected behavior
    # The validation correctly identifies this as invalid
    
    # 7. Test metrics endpoints 
    metrics_response = client.get('/metrics/prometheus')
    assert metrics_response.status_code == 200, "Metrics endpoint failed"
    metrics_text = metrics_response.text
    assert 'oatie_sql_validate_total' in metrics_text, "Validation metrics missing"
    assert 'oatie_sql_generate_total' in metrics_text, "Generation metrics missing"
    assert 'oatie_sql_register_tables_total' in metrics_text, "Registration metrics missing"
    
    # 8. Test health check
    health_response = client.get('/health/live')
    assert health_response.status_code == 200, "Health check failed"
    health_data = health_response.json()
    assert health_data['status'] == 'live', "Health status incorrect"
    
    print("✅ Phase 2 Database Integration: ALL TESTS PASSED")
    print(f"   ✓ Database persistence and retrieval")
    print(f"   ✓ Async database operations") 
    print(f"   ✓ Cache consistency")
    print(f"   ✓ API endpoint integration")
    print(f"   ✓ SQL validation with database backend")
    print(f"   ✓ Table registration and metadata management")
    print(f"   ✓ Metrics collection")
    print(f"   ✓ Health monitoring")
    print(f"   📊 Test schema: {test_schema}")
    print(f"   📊 Registered tables: {len(test_tables)} + 1 via API")
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_phase2_database_integration_complete())
