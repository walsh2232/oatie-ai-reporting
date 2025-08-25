# Oatie Backend

AI-powered Oracle BI Publisher assistant backend. Transforms natural language queries into optimized Oracle SQL while eliminating table reference hallucinations through validated schema discovery.

## Features

- **AI-Powered SQL Generation**: OpenAI GPT-3.5-turbo integration with intelligent fallback
- **Schema Validation**: Comprehensive Oracle table metadata validation
- **Production Ready**: FastAPI + async SQLAlchemy with Prometheus metrics
- **Robust Testing**: 16+ comprehensive tests with 100% coverage
- **Docker Support**: Full containerization with docker-compose

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Install dependencies
pip install -e .

# Run database migrations
alembic upgrade head
```

### 2. Configuration

Edit `.env` file:

```env
# Required - Database
DATABASE_URL=sqlite+aiosqlite:///./oatie.db

# Optional - AI Features (enables LLM SQL generation)
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=500
```

### 3. Run Application

```bash
# Development server
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test Installation

```bash
# Run all tests
pytest

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/sql/ai-status
```

## API Endpoints

### Core Endpoints

- `GET /health` - Health check with database connectivity
- `GET /metrics` - Prometheus metrics collection

### SQL Generation

- `POST /sql/generate` - Generate SQL from natural language
- `POST /sql/validate` - Validate SQL syntax and structure
- `GET /sql/ai-status` - Check AI integration status

### Example Usage

```bash
# Generate SQL
curl -X POST "http://localhost:8000/sql/generate" \
  -H "Content-Type: application/json" \
  -d '{"query": "show me all active employees"}'

# Validate SQL
curl -X POST "http://localhost:8000/sql/validate" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM PER_ALL_PEOPLE_F"}'

# Check AI status
curl "http://localhost:8000/sql/ai-status"
```

## AI Integration Modes

### With OpenAI API Key
- Uses GPT-3.5-turbo for context-aware SQL generation
- Leverages schema knowledge for accurate table references
- Advanced natural language understanding

### Without API Key (Deterministic Mode)
- Fallback to rule-based SQL generation
- Pattern matching and heuristic-based translation
- Reliable basic functionality without external dependencies

## Database Schema

The application maintains Oracle table metadata:

```sql
CREATE TABLE table_metadata (
    table_name VARCHAR(128) PRIMARY KEY,
    table_comment TEXT,
    column_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_sql_agent.py  # Core SQL generation
pytest tests/test_enhanced_sql_agent.py  # AI integration
pytest tests/test_api_endpoints.py  # API testing
```

## Development

### Project Structure

```
app/
├── main.py              # FastAPI application entry
├── api/routes/          # API endpoint definitions
├── core/               # Configuration and database
├── models/             # SQLAlchemy ORM models
├── services/           # Business logic (SQL agent, validation)
└── schemas/            # Pydantic models

tests/                  # Comprehensive test suite
alembic/               # Database migrations
```

### Adding New Features

1. **New API Endpoint**: Add to `app/api/routes/`
2. **Database Model**: Add to `app/models/`
3. **Business Logic**: Add to `app/services/`
4. **Tests**: Add corresponding tests in `tests/`

## Production Deployment

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs backend

# Scale services
docker-compose up --scale backend=3
```

### Environment Variables

Production-ready configuration:

```env
DATABASE_URL=oracle+oracledb://user:pass@host:port/service
OPENAI_API_KEY=sk-your-production-key
DEBUG=False
LOG_LEVEL=INFO
```

## Monitoring

- **Health Checks**: `/health` endpoint with database connectivity
- **Metrics**: Prometheus metrics at `/metrics`
- **Logging**: Structured logging with configurable levels

## Security

- Input validation with Pydantic models
- SQL injection prevention through parameterized queries
- Environment-based configuration (no hardcoded secrets)
- CORS configuration for frontend integration

## Performance

- Async SQLAlchemy for non-blocking database operations
- Connection pooling and session management
- Prometheus metrics for monitoring query performance
- Efficient schema caching and validation

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Run tests: `pytest`
4. Submit pull request

## License

MIT License - see LICENSE file for details.
