import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.sql_agent import SQLAgent, QueryContext
from app.services.schema_validator import SchemaValidatorService

@pytest_asyncio.fixture
async def agent():
    validator = SchemaValidatorService() 
    validator.clear_cache()
    # Pre-register some test tables
    await validator.register_tables("HCM", ["PER_ALL_PEOPLE_F", "PER_ALL_ASSIGNMENTS_F"])
    return SQLAgent(validator)

@pytest.mark.asyncio
async def test_generate_people_count_deterministic(agent):
    """Test generating people count SQL with deterministic generation"""
    sql, validation = await agent.generate_and_validate("HCM", "people count")
    assert "COUNT" in sql.upper()
    assert "PER_ALL_PEOPLE_F" in sql
    assert validation.valid is True
    assert agent.get_generation_method() == "Deterministic"

@pytest.mark.asyncio 
async def test_generate_assignments_deterministic(agent):
    """Test generating assignment-related SQL with deterministic generation"""
    sql, validation = await agent.generate_and_validate("HCM", "show assignments")
    assert "PER_ALL_ASSIGNMENTS_F" in sql
    assert validation.valid is True

@pytest.mark.asyncio
async def test_query_context_building(agent):
    """Test query context building functionality"""
    context = await agent._get_query_context("HCM")
    assert context.schema_name == "HCM"
    assert "PER_ALL_PEOPLE_F" in context.available_tables
    assert "PER_ALL_ASSIGNMENTS_F" in context.available_tables

@pytest.mark.asyncio
async def test_llm_prompt_building(agent):
    """Test LLM prompt construction"""
    context = QueryContext(
        schema_name="HCM",
        available_tables=["PER_ALL_PEOPLE_F", "PER_ALL_ASSIGNMENTS_F"]
    )
    prompt = agent._build_llm_prompt(context, "show me all employees")
    
    assert "HCM" in prompt
    assert "PER_ALL_PEOPLE_F" in prompt
    assert "PER_ALL_ASSIGNMENTS_F" in prompt
    assert "show me all employees" in prompt
    assert "Oracle SQL" in prompt

@pytest.mark.asyncio
async def test_llm_generation_fallback():
    """Test LLM generation with fallback to deterministic"""
    validator = SchemaValidatorService()
    validator.clear_cache()
    await validator.register_tables("TEST", ["TEST_TABLE"])
    
    # Create agent and mock LLM client to simulate failure
    agent = SQLAgent(validator)
    agent.llm_enabled = True
    agent.openai_client = MagicMock()
    
    # Mock OpenAI client to raise an exception
    agent.openai_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
    
    sql, validation = await agent.generate_and_validate("TEST", "count records")
    
    # Should fallback to deterministic generation
    assert "COUNT" in sql.upper()
    assert sql is not None

@pytest.mark.asyncio
@patch('app.services.sql_agent.AsyncOpenAI')
@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
async def test_llm_integration_mock(mock_openai):
    """Test LLM integration with mocked OpenAI client"""
    # Setup mock client
    mock_client = AsyncMock()
    mock_openai.return_value = mock_client
    
    # Mock the response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "SELECT COUNT(*) FROM PER_ALL_PEOPLE_F"
    mock_client.chat.completions.create.return_value = mock_response
    
    # Create agent (will initialize with mocked OpenAI)
    validator = SchemaValidatorService()
    validator.clear_cache()
    await validator.register_tables("HCM", ["PER_ALL_PEOPLE_F"])
    
    # Import agent class and create instance after mocking
    from app.services.sql_agent import SQLAgent
    agent = SQLAgent(validator)
    
    # Force LLM setup with mock
    agent.openai_client = mock_client
    agent.llm_enabled = True
    
    sql, validation = await agent.generate_and_validate("HCM", "count people")
    
    assert sql == "SELECT COUNT(*) FROM PER_ALL_PEOPLE_F"
    assert validation.valid is True
    mock_client.chat.completions.create.assert_called_once()

def test_agent_initialization_without_api_key():
    """Test agent initialization when no OpenAI API key is provided"""
    validator = SchemaValidatorService()
    agent = SQLAgent(validator)
    
    assert agent.llm_enabled is False
    assert agent.openai_client is None
    assert agent.get_generation_method() == "Deterministic"

@pytest.mark.asyncio
async def test_advanced_query_types(agent):
    """Test various query types with deterministic generation"""
    
    # Test list/show queries
    sql, _ = await agent.generate_and_validate("HCM", "list all people")
    assert "SELECT" in sql.upper()
    assert "PER_ALL_PEOPLE_F" in sql
    assert "ROWNUM" in sql.upper()  # Oracle pagination
    
    # Test count queries
    sql, _ = await agent.generate_and_validate("HCM", "how many assignments")
    assert "COUNT" in sql.upper()
    assert "PER_ALL_ASSIGNMENTS_F" in sql
    
    # Test default fallback
    sql, _ = await agent.generate_and_validate("HCM", "random query")
    assert "SELECT" in sql.upper()
    assert "ROWNUM" in sql.upper()
