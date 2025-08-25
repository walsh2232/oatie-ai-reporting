# 🥣 Oatie AI Reporting

Transform Your Fusion Reporting with AI - Oracle BI Publisher AI Assistant with Oracle Redwood Design System

[![CI/CD Pipeline](https://github.com/walsh2232/oatie-ai-reporting/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/walsh2232/oatie-ai-reporting/actions/workflows/ci-cd.yml)
[![Security Scan](https://github.com/walsh2232/oatie-ai-reporting/actions/workflows/security.yml/badge.svg)](https://github.com/walsh2232/oatie-ai-reporting/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

Oatie is an enterprise-ready AI-powered assistant for Oracle BI Publisher that revolutionizes report creation and data analysis. Built with production-grade infrastructure, automated CI/CD, and comprehensive monitoring.

## ✨ Features

- 🤖 **AI-Powered Report Generation** - Natural language to SQL and report creation
- 📊 **Oracle BI Publisher Integration** - Seamless connection to Oracle Fusion applications
- 🎨 **Oracle Redwood Design System** - Modern, accessible UI components
- 🐳 **Production Docker Setup** - Multi-stage builds with security hardening
- ⚡ **High Performance** - FastAPI backend with PostgreSQL and Redis
- 📈 **Comprehensive Monitoring** - Prometheus metrics and Grafana dashboards
- 🛡️ **Enterprise Security** - Container scanning, dependency auditing, HTTPS
- 🔄 **Zero-Downtime Deployments** - Automated CI/CD with GitHub Actions

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React +      │◄──►│   (FastAPI +    │◄──►│   (PostgreSQL)  │
│   Redwood UI)   │    │   Gunicorn)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         │              │   (Caching)     │              │
         │              └─────────────────┘              │
         │                                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                         │
│              (SSL Termination + Load Balancing)                │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose v2.0+
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### Production Deployment
```bash
# Clone the repository
git clone https://github.com/walsh2232/oatie-ai-reporting.git
cd oatie-ai-reporting

# Configure environment
cp .env.example .env
# Edit .env with your production values

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
curl http://localhost/health
curl http://localhost:8000/health/live
```

### Development Setup
```bash
# Install dependencies
npm install
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# Start development servers
npm run dev
```

## 📊 Monitoring & Health

### Health Endpoints
- **Application Health**: `GET /health/live`
- **Readiness Check**: `GET /health/ready`
- **Detailed Health**: `GET /api/v1/health/detailed`

### Monitoring Dashboard
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Application Metrics**: http://localhost:8000/metrics

## 🛡️ Security Features

- **Container Security**: Non-root execution, minimal images, vulnerability scanning
- **Application Security**: CORS, rate limiting, input validation
- **Data Security**: Encrypted connections, secure secrets management
- **Compliance**: GDPR-ready with audit logs and data protection

## 🔄 CI/CD Pipeline

Our automated pipeline includes:
- **Code Quality**: ESLint, Prettier, Black, MyPy
- **Security Scanning**: CodeQL, Trivy, Safety, npm audit
- **Testing**: Unit tests, integration tests, coverage reports
- **Deployment**: Automated staging deployment, manual production approval

## 📈 Performance

- **Response Time**: <200ms average API response
- **Throughput**: 1000+ requests/minute
- **Availability**: 99.9% uptime SLA
- **Scalability**: Horizontal scaling with load balancing

## 🤝 API Reference

### Reports API
```bash
# Get all reports
GET /api/v1/reports/

# Create new report
POST /api/v1/reports/
{
  "name": "Sales Report",
  "description": "Monthly sales analysis",
  "oracle_report_path": "/reports/sales"
}

# Get specific report
GET /api/v1/reports/{id}
```

### AI Assistant API
```bash
# Process AI query
POST /api/v1/ai/query
{
  "query": "Create a sales report for Q4 2023",
  "context": "Financial reporting",
  "session_id": "unique_session_id"
}
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && pytest

# Integration tests
docker-compose -f docker-compose.prod.yml up -d
./scripts/integration-tests.sh
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production deployment and maintenance
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Architecture Decision Records](docs/adr/) - Technical decisions and rationale
- [Contributing Guide](CONTRIBUTING.md) - Development workflow and standards

## 🔧 Configuration

### Environment Variables
Key configuration options:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT signing key
- `ORACLE_BI_*` - Oracle BI Publisher connection settings
- `OPENAI_API_KEY` - AI service configuration

### Feature Flags
- `PROMETHEUS_ENABLED` - Enable/disable metrics collection
- `DEBUG` - Development mode (never use in production)
- `LOG_LEVEL` - Logging verbosity (INFO, DEBUG, WARNING, ERROR)

## 🎯 Roadmap

### Phase 1: Stabilization ✅
- Production infrastructure
- CI/CD pipeline
- Security hardening
- Monitoring setup

### Phase 2: Enhancement (Q1 2024)
- Advanced AI capabilities
- Oracle Cloud integration
- Real-time collaboration
- Advanced analytics

### Phase 3: Scale (Q2 2024)
- Multi-tenant architecture
- Enterprise SSO
- Advanced security features
- Performance optimization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the full test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/walsh2232/oatie-ai-reporting/issues)
- **Documentation**: [Wiki](https://github.com/walsh2232/oatie-ai-reporting/wiki)
- **Security**: Report security issues to security@your-domain.com

## 🙏 Acknowledgments

- Oracle Corporation for the Redwood Design System
- FastAPI and React communities
- All contributors and maintainers

---

Built with ❤️ for the Oracle community
