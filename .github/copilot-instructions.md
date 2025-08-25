# Oatie AI Reporting - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview
Oatie is an AI-powered Oracle BI Publisher assistant built with FastAPI (Python) backend and React+TypeScript frontend using Material-UI and Oracle Redwood Design System. The application converts natural language queries into SQL using OpenAI GPT integration.

## Working Effectively

### Initial Repository Setup
- Fork and clone the repository
- **CRITICAL**: Use the `copilot/vscode1756093483621` or `copilot/vscode1756093722248` branches for full project structure, NOT the minimal `main` branch
- Switch to a complete branch: `git fetch origin copilot/vscode1756093483621:full-project && git checkout full-project`

### Backend Setup and Build Process
**Prerequisites**: Python 3.12+ (NOT 3.13 as specified in original config)

1. **Setup Python Environment**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   **Timing**: ~3 seconds - NEVER CANCEL

2. **CRITICAL Configuration Fix**: Update `backend/pyproject.toml` before installation:
   - Change `requires-python = ">=3.13"` to `requires-python = ">=3.12"`
   - Change `target-version = ['py313']` to `target-version = ['py312']`  
   - Change `python_version = "3.13"` to `python_version = "3.12"`
   - Change `license = {text = "MIT"}` to `license = "MIT"`
   - Add `packages = ["app"]` under the `[project]` section

3. **Install Dependencies** (use direct installation to avoid editable install issues):
   ```bash
   pip install fastapi uvicorn[standard] pydantic sqlalchemy[asyncio] alembic aiosqlite python-multipart openai httpx prometheus-client python-dotenv pydantic-settings requests
   ```
   **Timing**: ~15-20 seconds - NEVER CANCEL - Set timeout to 60+ seconds

4. **Database Setup**:
   ```bash
   alembic upgrade head
   ```
   **Timing**: ~0.5 seconds - Set timeout to 30+ seconds

5. **Start Backend Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   **Timing**: ~5-10 seconds to full startup - NEVER CANCEL - Set timeout to 30+ seconds

### Frontend Setup and Build Process
**Prerequisites**: Node.js 18+ (confirmed working with Node.js 20)

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```
   **Timing**: ~2-3 seconds - NEVER CANCEL - Set timeout to 30+ seconds

2. **CRITICAL BUILD ISSUE**: Frontend build currently FAILS due to TypeScript syntax errors:
   - `src/components/LoginForm.tsx`: JSX structure issues (missing parent elements, unclosed tags)
   - `src/themes/oracleRedwoodTheme.ts`: Object syntax errors in color definitions
   - **DO NOT** attempt `npm run build` until these files are fixed
   - Use `npm run dev` for development server instead

3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   **Timing**: ~3-5 seconds - Set timeout to 30+ seconds

### Database and Testing

1. **Database**: Uses SQLite for development (file: `backend/oatie.db`)
   - Migrations work correctly with `alembic upgrade head`
   - Database file is already included in repository

2. **Backend Testing**: Tests exist but have import configuration issues
   - **DO NOT** run `pytest` directly - module import issues exist
   - Tests are located in `backend/tests/` but require app module configuration fixes
   - Phase completion tests exist: `phase1_completion_test.py`, `phase2_completion_test.py`

### Pre-commit Hooks and Code Quality

1. **Pre-commit Configuration**: `.pre-commit-config.yaml` exists but needs Python version adjustments
   - Change `language_version: python3.13` to `language_version: python3.12`
   - Install: `pip install pre-commit && pre-commit install`

2. **Code Formatting**:
   ```bash
   # Backend (from backend/ directory with venv activated)
   pip install black isort mypy pylint
   black .
   isort .
   # Note: mypy and pylint may have configuration issues
   
   # Frontend (from frontend/ directory)
   npm run lint  # ESLint configuration exists
   ```

## Validation Scenarios

### Backend Health Checks
**ALWAYS test these endpoints after backend setup**:
```bash
curl http://localhost:8000/health/live     # Should return: {"status":"live"}
curl http://localhost:8000/health/ready    # Should return: {"status":"ready"}
curl http://localhost:8000/docs            # FastAPI auto-generated documentation
```

### Complete Development Workflow
1. Start backend server (port 8000)
2. Start frontend dev server (port 5173/5174) 
3. Test health endpoints
4. Access frontend at http://localhost:5173 or http://localhost:5174
5. Backend API docs available at http://localhost:8000/docs

## Common Issues and Solutions

### Backend Issues
- **Module not found errors**: Ensure all dependencies are installed, especially `pydantic-settings`
- **Python version errors**: Use Python 3.12, not 3.13
- **Database errors**: Run `alembic upgrade head` in backend directory
- **Import errors in tests**: Tests require additional app module configuration

### Frontend Issues  
- **Build failures**: Known TypeScript syntax errors in LoginForm.tsx and oracleRedwoodTheme.ts
- **Dependency warnings**: npm audit shows 5 moderate vulnerabilities - expected
- **CORS errors**: Backend configured for ports 5173 and 5174

### Configuration Issues
- **pyproject.toml**: Original has setuptools compatibility issues - use fixes above
- **Docker Compose**: `docker-compose.yml` file exists but is empty
- **Environment variables**: Use `.env.template` as reference

## Key Project Structure

### Backend (`backend/`)
```
app/
├── api/routes/          # API endpoints (health.py, sql.py, metrics.py)
├── core/               # Configuration and utilities  
├── models/             # SQLAlchemy models
├── services/           # Business logic (SQL agent, schema validator)
└── main.py            # FastAPI application entry point
```

### Frontend (`frontend/`)
```
src/
├── components/         # React components (has syntax errors)
├── themes/            # Oracle Redwood theme (has syntax errors)
└── [other standard React structure]
```

## Timeout Values and Timing Expectations

**CRITICAL: NEVER CANCEL these operations - Set appropriate timeouts**:

- **Python venv creation**: 10+ seconds timeout
- **Backend dependency installation**: 60+ seconds timeout
- **Frontend dependency installation**: 30+ seconds timeout  
- **Database migrations**: 30+ seconds timeout
- **Server startup (backend)**: 30+ seconds timeout
- **Frontend development server**: 30+ seconds timeout
- **Build processes**: 120+ seconds timeout (when frontend is fixed)

## Additional Notes

- **GitHub Workflows**: Comprehensive CI/CD exists (`.github/workflows/`) but may need Python version updates
- **Security**: Pre-commit hooks include security scanning with multiple tools
- **Documentation**: Extensive README and CONTRIBUTING.md files exist
- **API Integration**: OpenAI GPT-3.5-turbo integration for SQL generation
- **Database**: Supports both SQLite (dev) and PostgreSQL (production)

## Development Priorities

1. **IMMEDIATE**: Fix TypeScript syntax errors in frontend files
2. **HIGH**: Resolve backend test import configuration
3. **MEDIUM**: Complete Docker Compose configuration
4. **LOW**: Update all Python version references from 3.13 to 3.12

Always validate your changes by running the health checks and confirming both backend and frontend servers start successfully.