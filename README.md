# 🤖 Oatie AI Reporting

> Transform Your Fusion Reporting with AI - Oracle BI Publisher AI Assistant with Oracle Redwood Design System

[![CI/CD Pipeline](https://github.com/walsh2232/oatie-ai-reporting/actions/workflows/ci.yml/badge.svg)](https://github.com/walsh2232/oatie-ai-reporting/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-blue.svg)](https://www.typescriptlang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Oatie is an AI-powered assistant for Oracle BI Publisher that streamlines report development and enhances the reporting experience with intelligent automation and modern UI components based on Oracle Redwood Design System.

## ✨ Features

- 🧠 **AI-Powered Report Generation**: Intelligent assistance for creating Oracle BI Publisher reports
- 🎨 **Oracle Redwood Design System**: Modern, accessible UI components
- ⚡ **FastAPI Backend**: High-performance Python backend with async support
- ⚛️ **React Frontend**: Modern TypeScript React application
- 🔐 **Enterprise Security**: OAuth2 integration with Oracle Cloud
- 📊 **Real-time Analytics**: Live report monitoring and analytics
- 🔄 **CI/CD Ready**: Automated testing, linting, and deployment
- 📚 **Comprehensive Documentation**: API docs with interactive examples

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Oracle BI Publisher access
- OpenAI API key (optional, for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/walsh2232/oatie-ai-reporting.git
   cd oatie-ai-reporting
   ```

2. **Set up the backend**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev]"
   
   # Copy environment configuration
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up the frontend**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Build the frontend
   npm run build
   ```

4. **Run the application**
   ```bash
   # Terminal 1: Start backend
   uvicorn backend.oatie.main:app --reload
   
   # Terminal 2: Start frontend (development)
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

```
oatie-ai-reporting/
├── backend/                 # Python FastAPI backend
│   └── oatie/
│       ├── api/            # API routes and endpoints
│       ├── core/           # Core functionality and config
│       ├── models/         # Database models
│       ├── services/       # Business logic
│       └── utils/          # Utility functions
├── frontend/               # TypeScript React frontend
│   └── src/
│       ├── components/     # React components
│       ├── hooks/          # Custom React hooks
│       ├── pages/          # Page components
│       ├── services/       # API services
│       ├── types/          # TypeScript types
│       └── utils/          # Utility functions
├── docs/                   # Documentation
├── tests/                  # Test files
└── .github/workflows/      # CI/CD pipelines
```

## 🛠️ Development

### Code Quality

This project enforces strict code quality standards:

- **Python**: Black formatting, Pylint linting, MyPy type checking
- **TypeScript**: ESLint, Prettier, strict TypeScript configuration
- **Testing**: >95% backend coverage, >90% frontend coverage
- **Security**: Automated vulnerability scanning with Safety and Bandit

### Development Commands

```bash
# Python Backend
black backend/                    # Format code
pylint backend/oatie/            # Lint code
mypy backend/oatie/              # Type checking
pytest --cov=oatie              # Run tests with coverage

# TypeScript Frontend
npm run format                   # Format code
npm run lint                     # Lint code
npm run type-check              # Type checking
npm run test                    # Run tests
npm run test:coverage           # Run tests with coverage

# Security Checks
safety check                    # Check Python dependencies
bandit -r backend/              # Security linting
npm audit                       # Check Node.js dependencies
```

### Docker Development

```bash
# Build and run with Docker
docker build -t oatie-ai-reporting .
docker run -p 8000:8000 oatie-ai-reporting

# Or use Docker Compose (when available)
docker-compose up --build
```

## 📊 Testing

### Running Tests

```bash
# Backend tests
pytest                          # All tests
pytest tests/unit/             # Unit tests only
pytest tests/integration/      # Integration tests only
pytest --cov=oatie --cov-report=html  # With coverage report

# Frontend tests
npm test                        # All tests
npm run test:coverage          # With coverage
npm run test:ui                # Interactive test UI
```

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: API and service integration
- **End-to-End Tests**: Full application workflow testing
- **Security Tests**: Vulnerability and penetration testing

## 🔐 Security

### Security Features

- **Authentication**: OAuth2 with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: Encryption at rest and in transit
- **Input Validation**: Comprehensive input sanitization
- **Security Headers**: CORS, CSP, and security headers
- **Dependency Scanning**: Automated vulnerability detection

### Security Best Practices

- Never commit secrets to version control
- Use environment variables for sensitive configuration
- Regularly update dependencies
- Follow OWASP security guidelines
- Implement proper error handling without information disclosure

## 📚 Documentation

- **API Documentation**: Available at `/docs` endpoint
- **Architecture Guide**: See `docs/architecture.md`
- **Deployment Guide**: See `docs/deployment.md`
- **Contributing Guide**: See `CONTRIBUTING.md`
- **Security Policy**: See `SECURITY.md`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

1. **Code**: Follow our coding standards and conventions
2. **Test**: Write tests for new functionality
3. **Document**: Update documentation as needed
4. **Review**: Submit PR for code review
5. **CI/CD**: Ensure all checks pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Oracle Corporation for BI Publisher and Redwood Design System
- OpenAI for AI capabilities
- The open-source community for amazing tools and libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/walsh2232/oatie-ai-reporting/issues)
- **Discussions**: [GitHub Discussions](https://github.com/walsh2232/oatie-ai-reporting/discussions)
- **Email**: walsh2232@users.noreply.github.com

---

**Made with ❤️ by the Oatie Team**
