# 🤖 Oatie - Transform Your Fusion Reporting with AI

[![CI/CD Pipeline](https://github.com/username/oatie/actions/workflows/ci.yml/badge.svg)](https://github.com/username/oatie/actions/workflows/ci.yml)
[![Security Scan](https://github.com/username/oatie/actions/workflows/security.yml/badge.svg)](https://github.com/username/oatie/actions/workflows/security.yml)
[![CodeQL](https://github.com/username/oatie/actions/workflows/codeql.yml/badge.svg)](https://github.com/username/oatie/actions/workflows/codeql.yml)
[![Coverage](https://codecov.io/gh/username/oatie/branch/main/graph/badge.svg)](https://codecov.io/gh/username/oatie)
[![Docker](https://img.shields.io/docker/pulls/username/oatie)](https://hub.docker.com/r/username/oatie)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Pro](https://img.shields.io/badge/GitHub-Pro-purple)](https://github.com/pricing)

> **AI-Powered Oracle BI Publisher Assistant** - Transform natural language queries into powerful Oracle Fusion reports with enterprise-grade security and performance.

## 🌟 Features

### 🎯 **Core Capabilities**
- **Natural Language Processing**: Convert plain English to complex SQL queries using GPT-3.5-turbo
- **Oracle BI Publisher Integration**: Seamless connection to Oracle Fusion reporting
- **Real-time Query Validation**: Advanced schema validation with intelligent error correction
- **Interactive Dashboard**: Modern React-based UI with Material-UI components
- **Enterprise Authentication**: Secure login with Oracle connection management

### 🛡️ **Security & Compliance**
- **Automated Security Scanning**: Trivy vulnerability assessment
- **Dependency Monitoring**: Dependabot automated updates
- **Code Quality Gates**: ESLint, Pylint, Black, MyPy integration
- **Branch Protection**: Required reviews and status checks
- **Container Security**: Multi-layer security scanning

### 🚀 **Performance & Scalability**
- **Async Operations**: FastAPI with async SQLAlchemy
- **Caching Strategy**: Intelligent query result caching
- **Database Optimization**: Composite indexes and query optimization
- **Containerized Deployment**: Docker Compose ready
- **Monitoring**: Prometheus metrics integration

## 📋 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.13+ (for development)

### 🐳 Production Deployment
```bash
# Clone the repository
git clone https://github.com/username/oatie.git
cd oatie

# Start all services
docker-compose up -d

# Access the application
open http://localhost:5174
```

### 🔧 Development Setup
```bash
# Backend setup
cd backend
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev
```

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React + TypeScript + Material-UI]
        AUTH[Authentication Context]
        ROUTER[React Router]
    end
    
    subgraph "API Layer"
        API[FastAPI + Pydantic v2]
        MIDDLEWARE[CORS + Security]
        ROUTES[Health | SQL | Metrics]
    end
    
    subgraph "Service Layer"
        SQL_AGENT[SQL Agent + OpenAI]
        VALIDATOR[Schema Validator]
        CACHE[Query Cache]
    end
    
    subgraph "Data Layer"
        DB[(SQLite/PostgreSQL)]
        MIGRATIONS[Alembic Migrations]
        METADATA[Table Metadata]
    end
    
    subgraph "External Services"
        ORACLE[Oracle BI Publisher]
        OPENAI[OpenAI GPT-3.5-turbo]
    end
    
    UI --> API
    AUTH --> API
    API --> SQL_AGENT
    API --> VALIDATOR
    SQL_AGENT --> OPENAI
    VALIDATOR --> DB
    SQL_AGENT --> ORACLE
    API --> DB
```

## 🧪 Testing

Our comprehensive test suite ensures reliability:

```bash
# Backend tests (17/17 passing)
cd backend
pytest --cov=app --cov-report=html -v

# Frontend tests
cd frontend
npm test -- --coverage

# Integration tests
python backend/test_integration.py
python backend/phase1_completion_test.py
python backend/phase2_completion_test.py
```

### Test Coverage
- **Backend**: 95%+ line coverage
- **API Endpoints**: 100% endpoint coverage
- **SQL Agent**: Complete LLM integration testing
- **Schema Validation**: Comprehensive edge case testing

## 🔄 CI/CD Pipeline

Leveraging **GitHub Pro's 3,000 Actions minutes** for comprehensive automation:

### Continuous Integration
- ✅ **Code Quality**: Black, Pylint, ESLint, Prettier
- ✅ **Type Safety**: MyPy, TypeScript strict mode
- ✅ **Security**: Trivy, Safety, npm audit
- ✅ **Testing**: pytest, Jest, integration tests
- ✅ **Docker**: Multi-stage builds with caching

### Continuous Deployment
- 🚀 **Automated Releases**: Semantic versioning
- 📦 **Container Registry**: GitHub Container Registry
- 🌐 **Multi-Environment**: Staging → Production
- 📊 **Performance Testing**: Load testing with Artillery
- 📈 **Monitoring**: Health checks and metrics

## 🛠️ Development Workflow

### Branch Protection Rules
- ✅ **Required Reviews**: Minimum 1 reviewer
- ✅ **Status Checks**: All tests must pass
- ✅ **Up-to-date**: Branches must be current
- ✅ **Admin Enforcement**: No bypass for admins

### Code Review Process
1. **Feature Branch**: Create from `develop`
2. **Development**: Use GitHub Copilot for acceleration
3. **Testing**: Local + CI pipeline validation
4. **Pull Request**: Automated review assignment
5. **Review**: Code quality and functionality review
6. **Merge**: Squash and merge to `develop`
7. **Release**: Tag-based production deployment

## 🔧 Configuration

### Environment Variables
```bash
# Backend Configuration
DATABASE_URL=sqlite:///./oatie.db
OPENAI_API_KEY=your_openai_key
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5174

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

### Oracle Connection Setup
1. Navigate to the Dashboard
2. Click "Add Oracle Connection"
3. Complete the connection wizard:
   - **Server Details**: Host, port, service name
   - **Credentials**: Username, password
   - **Test Connection**: Validate connectivity
   - **Save**: Store encrypted connection details

## 📊 Monitoring & Analytics

### Application Metrics
- **API Performance**: Response times, error rates
- **Database Queries**: Execution time, query patterns
- **AI Integration**: Token usage, model performance
- **User Activity**: Query frequency, success rates

### Health Checks
- **Backend**: `/health` endpoint with dependency checks
- **Database**: Connection and migration status
- **External APIs**: Oracle and OpenAI connectivity

## 🔒 Security

### Authentication & Authorization
- **JWT-based**: Secure token authentication
- **Role-based Access**: User permissions and roles
- **Session Management**: Secure session handling
- **Oracle Integration**: Encrypted credential storage

### Data Protection
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content Security Policy
- **HTTPS Enforcement**: TLS encryption

## 📚 Documentation

### API Documentation
- **OpenAPI/Swagger**: Interactive API documentation
- **Postman Collection**: Ready-to-use API collection
- **Schema Validation**: Pydantic model documentation

### User Guides
- **Getting Started**: Quick setup and first query
- **Oracle Integration**: Detailed connection guide
- **Query Examples**: Common reporting patterns
- **Troubleshooting**: Common issues and solutions

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Process
1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Develop** with GitHub Copilot assistance
5. **Test** thoroughly (maintain 95%+ coverage)
6. **Submit** a pull request

### Code Standards
- **Python**: Black formatting, Pylint linting, type hints
- **TypeScript**: ESLint, Prettier, strict mode
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: Unit, integration, and end-to-end tests

## 📈 Roadmap

### Phase 4: Advanced Analytics
- **Dashboard Analytics**: Query performance insights
- **Usage Patterns**: User behavior analysis
- **AI Optimization**: Model fine-tuning
- **Report Templates**: Pre-built Oracle reports

### Phase 5: Enterprise Features
- **Multi-tenant**: Organization support
- **Advanced Security**: SSO integration
- **Audit Logging**: Comprehensive activity tracking
- **API Rate Limiting**: Enterprise-grade controls

### Phase 6: Platform Expansion
- **Other BI Tools**: Power BI, Tableau integration
- **Cloud Deployment**: AWS, Azure, GCP support
- **Mobile App**: React Native companion
- **Marketplace**: Template and plugin ecosystem

## 📞 Support

### Community Support
- **GitHub Discussions**: Community Q&A
- **Issues**: Bug reports and feature requests
- **Wiki**: Comprehensive documentation

### Enterprise Support
- **Email**: support@oatie.ai
- **Slack**: Join our community workspace
- **Documentation**: Detailed technical guides

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: GPT-3.5-turbo integration
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework
- **Material-UI**: Component library
- **GitHub Pro**: Advanced development features

---

**Built with ❤️ using GitHub Pro features including 3,000 Actions minutes, advanced security scanning, and GitHub Copilot integration.**