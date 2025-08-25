# GitHub Codespaces Deployment Guide
## Oatie AI Oracle BI Publisher Platform - One-Click Enterprise Development

### 🚀 Quick Start

#### Option 1: Direct GitHub Codespaces Launch
1. Navigate to the [Oatie AI repository](https://github.com/walsh2232/oatie-ai-reporting)
2. Click the green **"Code"** button
3. Select **"Codespaces"** tab
4. Click **"Create codespace on main"**
5. Wait for the environment to initialize (5-10 minutes)
6. The platform will be automatically available at the forwarded ports

#### Option 2: Codespaces Configuration
If you need to customize the Codespaces environment:

```bash
# Clone the repository
git clone https://github.com/walsh2232/oatie-ai-reporting.git
cd oatie-ai-reporting

# Launch Codespaces with the preconfigured environment
# The .devcontainer configuration will automatically handle setup
```

### 🏗️ Architecture Overview

The Codespaces environment includes:

```
┌─────────────────────────────────────────────────────────────┐
│                GitHub Codespaces Environment                │
├─────────────────────────────────────────────────────────────┤
│  VS Code (Web) + Comprehensive Extensions                   │
│  ├── Python Development (FastAPI, SQLAlchemy, pytest)     │
│  ├── Frontend Development (React, TypeScript, Vite)       │
│  ├── Database Tools (PostgreSQL, Redis)                   │
│  ├── Oracle Tools (Oracle DevTools, SQL Developer)       │
│  └── DevOps Tools (Docker, Kubernetes, Terraform)        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Development Services                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React):        http://localhost:3000            │
│  Backend API (FastAPI):   http://localhost:8000            │
│  API Documentation:       http://localhost:8000/docs       │
│  PostgreSQL Database:     localhost:5432                   │
│  Redis Cache:             localhost:6379                   │
│  Grafana Dashboard:       http://localhost:3001            │
│  Prometheus Metrics:      http://localhost:9090            │
│  Oracle BI Mock:          http://localhost:9502            │
└─────────────────────────────────────────────────────────────┘
```

### 🔧 Automated Setup Features

The Codespaces environment automatically provides:

#### ✅ **Complete Development Stack**
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Alembic
- **Frontend**: Node.js 20, React 19, TypeScript, Vite
- **Database**: PostgreSQL 15 with development configuration
- **Cache**: Redis 7 with optimized settings
- **Monitoring**: Prometheus + Grafana with pre-configured dashboards

#### ✅ **Oracle BI Publisher Integration**
- Oracle Instant Client 21.1
- Oracle development tools and VS Code extensions
- Mock Oracle BI Publisher service for testing
- Pre-configured connection settings

#### ✅ **Enterprise Development Tools**
- Docker-in-Docker for containerization
- Kubernetes CLI and Helm for orchestration
- Terraform for infrastructure as code
- GitHub CLI for repository management

#### ✅ **Comprehensive VS Code Extensions**
- **Python**: Python, Black, Flake8, Pylint, Jupyter
- **Frontend**: TypeScript, ESLint, Prettier, React tools
- **Database**: PostgreSQL client, Oracle DevTools, SQL tools
- **DevOps**: Docker, Kubernetes, Terraform, Helm
- **Git**: GitLens, GitHub integration, Copilot

### 🌐 Service Access

Once the Codespaces environment is ready, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend Application** | `http://localhost:3000` | N/A |
| **Backend API** | `http://localhost:8000` | N/A |
| **API Documentation** | `http://localhost:8000/docs` | N/A |
| **Grafana Dashboard** | `http://localhost:3001` | admin / admin123 |
| **Prometheus Metrics** | `http://localhost:9090` | N/A |
| **PostgreSQL** | `localhost:5432` | postgres / password |
| **Redis** | `localhost:6379` | N/A |
| **Oracle BI Mock** | `http://localhost:9502` | weblogic / password |

### 🛠️ Development Workflow

#### Starting Development
The environment auto-starts all services, but you can also manage them manually:

```bash
# Start all services
.devcontainer/start-services.sh

# Start specific services
.devcontainer/start-services.sh infrastructure  # DB, Redis, monitoring
.devcontainer/start-services.sh backend        # API only
.devcontainer/start-services.sh frontend       # UI only

# Quick development start
scripts/dev/quick-start.sh
```

#### Service Management
```bash
# Monitor all services in real-time
.devcontainer/scripts/monitor-services.sh

# View logs
.devcontainer/scripts/view-logs.sh

# Restart services
.devcontainer/scripts/restart-services.sh

# Health check
.devcontainer/scripts/health-check.sh
```

#### Development Commands
```bash
# Backend development
cd backend
source ../.venv/bin/activate
python main.py

# Frontend development
npm run dev

# Run tests
scripts/dev/run-tests.sh

# Database operations
scripts/dev/reset-db.sh
```

### 🧪 Testing & Quality Assurance

#### Automated Testing
```bash
# Full test suite
npm run test:run                    # Frontend unit tests
pytest backend/tests/              # Backend unit tests
npm run test:e2e                   # End-to-end tests
npm run test:api                   # API integration tests
```

#### Performance Testing
```bash
# Load testing
npm run performance:load           # Python-based load tests
npm run performance:k6             # K6 performance tests
npm run performance:artillery      # Artillery load tests
```

#### Code Quality
```bash
# Linting and formatting
npm run lint                       # Frontend linting
black backend/                     # Python formatting
flake8 backend/                    # Python linting
```

### 🔐 Security & Authentication

#### Development Security
- All services run with development credentials
- CORS configured for Codespaces domains
- Debug mode enabled for detailed error messages
- Pre-commit hooks for security scanning

#### Oracle BI Publisher Integration
```bash
# Environment variables (already configured)
export ORACLE_BI_URL="http://localhost:9502/xmlpserver"
export ORACLE_BI_USERNAME="weblogic"
export ORACLE_BI_PASSWORD="password"
```

### 📊 Monitoring & Observability

#### Built-in Monitoring
- **Prometheus**: Metrics collection from all services
- **Grafana**: Pre-configured dashboards for:
  - Application performance
  - Database metrics
  - System resources
  - API response times

#### Log Management
```bash
# Centralized logging
tail -f logs/backend.log           # Backend logs
tail -f logs/frontend.log          # Frontend logs
tail -f logs/services.log          # Service startup logs

# Error monitoring
.devcontainer/scripts/view-logs.sh # Interactive log viewer
```

### 🚀 Production Deployment

#### From Codespaces to Production
1. **Test thoroughly** in the Codespaces environment
2. **Use provided deployment scripts**:
   ```bash
   # Build production containers
   docker-compose -f docker-compose.prod.yml build
   
   # Deploy with Kubernetes
   kubectl apply -f helm/oatie-ai/
   
   # Blue-green deployment
   scripts/deployment/blue-green-deploy.sh deploy production
   ```

3. **Configure production environment variables**
4. **Set up external Oracle BI Publisher connection**
5. **Enable production monitoring and alerting**

### 🔧 Customization

#### Adding Custom Extensions
Edit `.devcontainer/devcontainer.json`:
```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "your.custom.extension"
      ]
    }
  }
}
```

#### Custom Environment Variables
Edit `.devcontainer/docker-compose.yml`:
```yaml
environment:
  - YOUR_CUSTOM_VAR=value
```

#### Custom Setup Scripts
Add to `.devcontainer/setup.sh`:
```bash
# Your custom setup commands
echo "Installing custom tools..."
```

### 🆘 Troubleshooting

#### Common Issues

**Issue**: Services not starting
```bash
# Solution: Check service status and restart
.devcontainer/scripts/health-check.sh
.devcontainer/scripts/restart-services.sh all
```

**Issue**: Port conflicts
```bash
# Solution: Check port usage
netstat -tulpn | grep :3000
# Kill conflicting processes if needed
```

**Issue**: Database connection errors
```bash
# Solution: Reset database
scripts/dev/reset-db.sh
```

**Issue**: Oracle integration not working
```bash
# Solution: Check Oracle environment
echo $ORACLE_HOME
echo $LD_LIBRARY_PATH
# Restart Oracle mock service
docker-compose -f .devcontainer/docker-compose.yml restart oracle-mock
```

#### Getting Help
1. Check service logs: `.devcontainer/scripts/view-logs.sh`
2. Run health check: `.devcontainer/scripts/health-check.sh`
3. Monitor services: `.devcontainer/scripts/monitor-services.sh`
4. Review documentation in `docs/` directory

### 🎯 Next Steps

1. **Explore the API**: Visit `http://localhost:8000/docs`
2. **Test Oracle Integration**: Use the mock service at `http://localhost:9502`
3. **Monitor Performance**: Check Grafana at `http://localhost:3001`
4. **Run Tests**: Execute `scripts/dev/run-tests.sh`
5. **Deploy to Production**: Follow the deployment guides in `docs/`

### 📚 Additional Resources

- [Enterprise Deployment Guide](./ENTERPRISE_DEPLOYMENT.md)
- [Oracle Integration Documentation](./ORACLE_INTEGRATION.md)
- [DevOps Pipeline Documentation](./DEVOPS_PIPELINE.md)
- [Performance Testing Guide](../PERFORMANCE_TESTING.md)

---

**🎉 Welcome to the Oatie AI Enterprise Development Environment!**

You now have a fully configured, enterprise-grade development environment running in GitHub Codespaces with Oracle BI Publisher integration, comprehensive monitoring, and all the tools needed for professional development.

Happy coding! 🚀