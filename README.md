# Oatie AI Reporting

**Transform Your Fusion Reporting with AI** - Oracle BI Publisher AI Assistant with Oracle Redwood Design System

[![Phase 2: Core Features](https://img.shields.io/badge/Phase-2%20Core%20Features-orange)](https://github.com/walsh2232/oatie-ai-reporting/issues/6)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-blue)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com)
[![Oracle](https://img.shields.io/badge/Oracle%20BI%20Publisher-Integrated-red)](https://oracle.com)

## 🚀 Overview

Oatie is an AI-powered reporting assistant that transforms natural language queries into optimized SQL and integrates seamlessly with Oracle BI Publisher. Built with Oracle Redwood Design System, it provides enterprise-grade reporting capabilities with >90% NLP accuracy.

### ✨ Key Features

- 🤖 **Enhanced SQL Intelligence**: GPT-4 powered natural language to SQL conversion with >90% accuracy
- 🏢 **Complete Oracle Integration**: Full Oracle BI Publisher API integration with automated report generation
- 📊 **Real-time Analytics Dashboard**: Interactive visualizations and performance monitoring
- 👥 **Multi-tenant User Management**: Enterprise-grade security and user management
- ⚡ **Performance Optimization**: Redis caching and intelligent query optimization
- 🎨 **Oracle Redwood Design**: Modern UI following Oracle design principles

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **GPT-4** - OpenAI language model for SQL generation
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management
- **Oracle BI Publisher** - Report generation engine

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Oracle Redwood Design System** - UI components
- **Tailwind CSS** - Utility-first styling
- **React Query** - API state management
- **Zustand** - Global state management

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Oracle BI Publisher (or mock for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/walsh2232/oatie-ai-reporting.git
   cd oatie-ai-reporting
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start Development Servers**
   
   **Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Frontend:**
   ```bash
   cd frontend
   npm start
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Required |
| `ORACLE_BI_URL` | Oracle BI Publisher URL | `https://demo.oracle.com` |
| `DATABASE_URL` | PostgreSQL connection string | Local DB |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | JWT signing secret | Required |
| `DEBUG` | Enable debug mode | `false` |

### Oracle BI Publisher Setup

1. Configure your Oracle BI Publisher instance
2. Create data sources and connection pools
3. Set up authentication credentials
4. Configure report templates

See [Oracle BI Publisher Documentation](https://docs.oracle.com/en/middleware/bi/publisher/) for detailed setup.

## 📖 API Documentation

### SQL Generation

```bash
# Generate SQL from natural language
curl -X POST "http://localhost:8000/api/sql/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "natural_language": "Show me top 5 sales reps by revenue this quarter",
    "optimization_level": "standard"
  }'
```

### Report Creation

```bash
# Create a new report
curl -X POST "http://localhost:8000/api/reports/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "template_id": "sales_report",
    "data_source": "oracle_prod",
    "parameters": {"quarter": "Q4", "year": 2024},
    "format": "PDF"
  }'
```

### Analytics Dashboard

```bash
# Get dashboard analytics
curl -X GET "http://localhost:8000/api/analytics/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests
```bash
# Run full test suite
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Production Deployment

1. **Build for Production**
   ```bash
   # Frontend
   cd frontend
   npm run build
   
   # Backend
   cd backend
   pip install -r requirements.txt --no-dev
   ```

2. **Environment Setup**
   ```bash
   # Set production environment variables
   export DEBUG=false
   export OPENAI_API_KEY=your_production_key
   export DATABASE_URL=your_production_db
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Cloud Deployment Options

- **Oracle Cloud Infrastructure (OCI)** - Recommended for Oracle integration
- **AWS ECS/EKS** - Container orchestration
- **Google Cloud Run** - Serverless containers
- **Azure Container Instances** - Managed containers

## 📊 Performance Metrics

### Target Performance (Phase 2)
- ✅ Natural language to SQL accuracy: >90%
- ✅ Query response time: <2 seconds
- ✅ Report generation time: <30 seconds
- ✅ System uptime: >99.9%
- ✅ Concurrent users: 100+

### Monitoring

- **Application Performance**: Built-in FastAPI metrics
- **Database Monitoring**: PostgreSQL and Oracle performance tracking
- **Cache Performance**: Redis hit rates and response times
- **User Analytics**: Query patterns and success rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation for API changes
- Follow Oracle Redwood Design System guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@oatie-ai.com
- 📖 Documentation: [docs.oatie-ai.com](https://docs.oatie-ai.com)
- 🐛 Issues: [GitHub Issues](https://github.com/walsh2232/oatie-ai-reporting/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/walsh2232/oatie-ai-reporting/discussions)

## 🙏 Acknowledgments

- Oracle Corporation for BI Publisher and Redwood Design System
- OpenAI for GPT-4 language model
- FastAPI and React communities
- All contributors and testers

---

**Made with ❤️ for Oracle BI Publisher users worldwide**
