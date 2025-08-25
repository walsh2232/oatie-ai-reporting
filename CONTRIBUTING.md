# Contributing to Oatie

Thank you for your interest in contributing to Oatie! This document provides guidelines and instructions for contributing to our AI-powered Oracle BI Publisher assistant.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** for backend development
- **Node.js 18+** for frontend development  
- **Docker & Docker Compose** for local development
- **Git** for version control
- **GitHub Pro account** (optional, for advanced features)

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/oatie.git
   cd oatie
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   alembic upgrade head
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Copy example environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit with your configuration
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## 📝 Development Workflow

### Branch Strategy

We use a **GitHub Flow** approach with GitHub Pro features:

- `main` - Production-ready code, protected branch
- `develop` - Integration branch for features
- `feature/*` - New features or enhancements
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### GitHub Pro Features in Use

- ✅ **Protected Branches**: Main branch requires reviews
- ✅ **3,000 Actions Minutes**: Comprehensive CI/CD pipeline
- ✅ **Code Owners**: Automatic reviewer assignment
- ✅ **Advanced Security**: Dependabot, CodeQL, secret scanning
- ✅ **Draft PRs**: Work-in-progress collaboration

### Making Changes

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow our coding standards (see below)
   - Write tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest --cov=app --cov-report=html

   # Frontend tests
   cd frontend
   npm test

   # Integration tests
   python backend/test_integration.py
   ```

4. **Code Quality Checks**
   ```bash
   # Backend formatting and linting
   cd backend
   black .
   isort .
   mypy app/
   pylint app/

   # Frontend formatting and linting
   cd frontend
   npm run lint
   npm run format
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation updates
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub using our PR template.

## 🎯 Coding Standards

### Python (Backend)

- **Formatting**: Black (line length: 88)
- **Import Sorting**: isort with Black profile
- **Type Checking**: MyPy with strict settings
- **Linting**: Pylint with custom configuration
- **Testing**: pytest with 95%+ coverage target

**Example:**
```python
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.database import get_db
from app.models.metadata_objects import TableMetadata


class QueryRequest(BaseModel):
    """Request model for natural language queries."""
    
    query: str
    table_name: Optional[str] = None


async def process_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Process natural language query and return SQL."""
    # Implementation here
    pass
```

### TypeScript/React (Frontend)

- **Formatting**: Prettier with single quotes
- **Linting**: ESLint with TypeScript rules
- **Type Safety**: Strict TypeScript configuration
- **Components**: Functional components with hooks
- **State Management**: React Context API

**Example:**
```typescript
import React, { useContext, useState } from 'react';

import { Button, TextField } from '@mui/material';

import { AuthContext } from '../contexts/AuthContext';
import { QueryRequest } from '../types/auth';

interface QueryFormProps {
  onSubmit: (query: QueryRequest) => void;
}

export const QueryForm: React.FC<QueryFormProps> = ({ onSubmit }) => {
  const [query, setQuery] = useState('');
  const { user } = useContext(AuthContext);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSubmit({ query, userId: user?.id });
  };

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your query..."
        fullWidth
      />
      <Button type="submit" variant="contained">
        Submit
      </Button>
    </form>
  );
};
```

## 🧪 Testing Guidelines

### Backend Testing

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test API endpoints and database interactions
- **Coverage**: Maintain 95%+ line coverage
- **Fixtures**: Use pytest fixtures for common test data

```python
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Frontend Testing

- **Component Tests**: Test React components with React Testing Library
- **Hook Tests**: Test custom hooks
- **Integration Tests**: Test user workflows
- **Accessibility**: Include a11y testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import { QueryForm } from '../QueryForm';

describe('QueryForm', () => {
  it('submits query on form submission', () => {
    const mockSubmit = jest.fn();
    render(<QueryForm onSubmit={mockSubmit} />);
    
    const input = screen.getByPlaceholderText('Enter your query...');
    const button = screen.getByRole('button', { name: 'Submit' });
    
    fireEvent.change(input, { target: { value: 'test query' } });
    fireEvent.click(button);
    
    expect(mockSubmit).toHaveBeenCalledWith({ query: 'test query' });
  });
});
```

## 📚 Documentation

### Code Documentation

- **Python**: Use Google-style docstrings
- **TypeScript**: Use JSDoc comments for public APIs
- **README**: Update relevant README files
- **API Docs**: FastAPI automatically generates OpenAPI docs

### Documentation Updates

When adding features:

1. Update relevant README files
2. Add/update API documentation
3. Update user guides if needed
4. Add inline code comments for complex logic

## 🔒 Security Considerations

### Security Best Practices

- **Input Validation**: Validate all user inputs
- **SQL Injection**: Use parameterized queries
- **Authentication**: Implement proper token handling
- **Secrets**: Never commit secrets or credentials
- **Dependencies**: Keep dependencies up to date

### Security Review Process

1. **Automated Scanning**: CI/CD includes security scans
2. **Manual Review**: Security-sensitive PRs get manual review
3. **Dependency Updates**: Dependabot creates automated PRs
4. **Vulnerability Response**: Follow our security policy

## 🏗️ Architecture Guidelines

### Backend Architecture

- **FastAPI**: RESTful API with automatic docs
- **Async/Await**: Use async patterns for I/O operations
- **Dependency Injection**: Leverage FastAPI's DI system
- **Error Handling**: Consistent error responses
- **Logging**: Structured logging with context

### Frontend Architecture

- **Component Structure**: Organized by feature
- **State Management**: Context API for global state
- **TypeScript**: Full type safety
- **Material-UI**: Consistent design system
- **Performance**: Code splitting and lazy loading

### Database Guidelines

- **Migrations**: Use Alembic for schema changes
- **Indexing**: Add appropriate database indexes
- **Queries**: Optimize for performance
- **Transactions**: Use transactions for data consistency

## 🚀 CI/CD and GitHub Pro Integration

### Automated Workflows

Our CI/CD pipeline leverages GitHub Pro's 3,000 Actions minutes:

- **Code Quality**: Linting, formatting, type checking
- **Testing**: Unit, integration, and end-to-end tests
- **Security**: Vulnerability scanning and dependency checks
- **Performance**: Load testing and benchmarks
- **Deployment**: Automated deployment to staging/production

### Pull Request Process

1. **Draft PR**: Create draft PR for early feedback
2. **Automated Checks**: CI/CD pipeline runs automatically
3. **Code Review**: Required reviewers assigned via CODEOWNERS
4. **Security Review**: Security-sensitive changes get extra scrutiny
5. **Merge**: Squash and merge after approval

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues for duplicates
2. Ensure you're on the latest version
3. Try to reproduce the issue consistently

### Bug Report Template

Use our GitHub issue template and include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed reproduction steps
- **Expected Behavior**: What should happen
- **Environment**: OS, browser, versions
- **Logs**: Relevant error messages or logs

## ✨ Feature Requests

### Feature Request Process

1. **Check Roadmap**: Review our roadmap for planned features
2. **Discussion**: Start with GitHub Discussions for big features
3. **Issue**: Create feature request using our template
4. **Design**: For complex features, create design docs

### Feature Implementation

- **Small Features**: Can be implemented directly
- **Large Features**: Require design review and planning
- **Breaking Changes**: Need careful consideration and migration plan

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. **Feature Complete**: All features for release are merged
2. **Testing**: Comprehensive testing on staging
3. **Documentation**: Update docs and changelog
4. **Release**: Create release with automated deployment
5. **Monitoring**: Monitor release for issues

## 💬 Getting Help

### Community Support

- **GitHub Discussions**: General questions and ideas
- **Issues**: Bug reports and feature requests
- **Wiki**: Detailed documentation
- **README**: Quick start guides

### Maintainer Contact

- **Email**: team@oatie.ai
- **GitHub**: @username
- **Security Issues**: security@oatie.ai

## 🙏 Recognition

Contributors are recognized in:

- **Release Notes**: Feature contributions acknowledged
- **Contributors File**: All contributors listed
- **Special Thanks**: Significant contributions highlighted

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to Oatie! Your contributions help make Oracle BI Publisher more accessible through AI-powered assistance. 🚀

**Built with ❤️ using GitHub Pro features including 3,000 Actions minutes, advanced security scanning, and GitHub Copilot integration.**
