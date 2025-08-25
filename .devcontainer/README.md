# GitHub Codespaces Setup for Oatie AI Enterprise Platform

This directory contains the complete GitHub Codespaces configuration for enterprise-grade development of the Oatie AI Oracle BI Publisher platform.

## 🚀 Quick Start

### Launch Codespaces
1. Go to the [repository](https://github.com/walsh2232/oatie-ai-reporting)
2. Click the green **"Code"** button
3. Select **"Codespaces"** tab
4. Click **"Create codespace on main"**
5. Wait for initialization (5-10 minutes)

### Verify Setup
```bash
# Validate the complete setup
.devcontainer/validate-setup.sh

# Start all services
.devcontainer/start-services.sh

# Check health of all services
.devcontainer/scripts/health-check.sh
```

## 📁 File Structure

```
.devcontainer/
├── devcontainer.json           # Main Codespaces configuration
├── docker-compose.yml          # Development services orchestration
├── setup.sh                    # Automated environment setup
├── start-services.sh           # Service startup and management
├── validate-setup.sh           # Configuration validation
├── postgres-dev.conf           # PostgreSQL development config
├── init-db.sql                 # Database initialization
├── prometheus-dev.yml          # Prometheus monitoring config
├── grafana/                    # Grafana dashboard configuration
│   ├── datasources/
│   └── dashboards/
├── oracle-mock/                # Mock Oracle BI Publisher service
│   ├── index.html
│   ├── nginx.conf
│   └── mock-api.json
└── scripts/                    # Management utilities
    ├── monitor-services.sh
    ├── view-logs.sh
    ├── restart-services.sh
    └── health-check.sh
```

## 🛠️ Configuration Details

### Development Environment
- **OS**: Ubuntu 24.04 with universal dev container
- **Python**: 3.11 with comprehensive package ecosystem
- **Node.js**: 20 LTS with modern tooling
- **Database**: PostgreSQL 15 with development optimizations
- **Cache**: Redis 7 with performance tuning
- **Monitoring**: Prometheus + Grafana with pre-built dashboards

### Oracle BI Publisher Integration
- **Oracle Instant Client**: 21.1 for connectivity
- **Mock Service**: Nginx-based mock for development
- **VS Code Extensions**: Oracle DevTools, SQL Developer
- **Authentication**: Pre-configured development credentials

### Port Forwarding
| Port | Service | Description |
|------|---------|-------------|
| 3000 | Frontend | React development server |
| 8000 | Backend | FastAPI application server |
| 5432 | PostgreSQL | Database connection |
| 6379 | Redis | Cache server |
| 9090 | Prometheus | Metrics collection |
| 3001 | Grafana | Monitoring dashboards |
| 9502 | Oracle Mock | Mock BI Publisher service |

## 🎯 Key Features

### Automated Setup
- ✅ Complete Python virtual environment with all dependencies
- ✅ Node.js with frontend toolchain installation
- ✅ Database initialization with proper schemas
- ✅ Oracle client libraries and development tools
- ✅ VS Code with 40+ pre-configured extensions

### Service Management
- ✅ One-command startup for all services
- ✅ Real-time monitoring and health checks
- ✅ Intelligent restart and recovery
- ✅ Comprehensive logging and debugging

### Enterprise Features
- ✅ Oracle BI Publisher mock service for testing
- ✅ Performance monitoring with Prometheus/Grafana
- ✅ Security-hardened development environment
- ✅ Production-ready containerization

### Developer Experience
- ✅ IntelliSense for Python, TypeScript, SQL, Oracle
- ✅ Integrated debugging for all components
- ✅ Git integration with GitHub Copilot
- ✅ Terminal-based service management

## 🔧 Management Commands

### Service Control
```bash
# Start all services
.devcontainer/start-services.sh

# Start specific services
.devcontainer/start-services.sh infrastructure  # DB + Cache + Monitoring
.devcontainer/start-services.sh backend        # API server
.devcontainer/start-services.sh frontend       # React dev server

# Monitor services (real-time dashboard)
.devcontainer/scripts/monitor-services.sh

# Restart services
.devcontainer/scripts/restart-services.sh

# Health check
.devcontainer/scripts/health-check.sh
```

### Log Management
```bash
# Interactive log viewer
.devcontainer/scripts/view-logs.sh

# Tail specific logs
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/services.log
```

### Development Utilities
```bash
# Quick development start
scripts/dev/quick-start.sh

# Run comprehensive tests
scripts/dev/run-tests.sh

# Reset development database
scripts/dev/reset-db.sh

# Validate setup
.devcontainer/validate-setup.sh
```

## 🔍 Troubleshooting

### Common Issues

**Services not starting**
```bash
# Check service status
.devcontainer/scripts/health-check.sh

# Restart problematic services
.devcontainer/scripts/restart-services.sh

# Check logs for errors
.devcontainer/scripts/view-logs.sh
```

**Port conflicts**
```bash
# Check what's using ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Kill conflicting processes
pkill -f "node.*3000"
pkill -f "python.*8000"
```

**Database issues**
```bash
# Reset database
scripts/dev/reset-db.sh

# Check PostgreSQL status
pg_isready -h localhost -p 5432 -U postgres

# Manual database access
psql -h localhost -U postgres -d oatie_ai
```

**Oracle integration problems**
```bash
# Check Oracle environment
echo $ORACLE_HOME
echo $LD_LIBRARY_PATH

# Test Oracle mock service
curl http://localhost:9502/xmlpserver

# Restart Oracle mock
docker-compose -f .devcontainer/docker-compose.yml restart oracle-mock
```

### Performance Issues

**High resource usage**
```bash
# Check system resources
.devcontainer/scripts/health-check.sh system

# Monitor process usage
.devcontainer/scripts/monitor-services.sh

# Scale down non-essential services
docker-compose -f .devcontainer/docker-compose.yml stop grafana prometheus
```

**Slow startup times**
```bash
# Use cached volumes for faster subsequent starts
# (Automatically configured in docker-compose.yml)

# Quick restart without full rebuild
.devcontainer/scripts/restart-services.sh quick
```

## 🛡️ Security Considerations

### Development Security
- All services use development credentials (change for production)
- CORS configured for Codespaces domains
- Debug mode enabled for detailed error messages
- Mock services for external dependencies

### Production Deployment
- Use provided production configurations in `docs/`
- Replace development credentials with secure alternatives
- Enable proper SSL/TLS certificates
- Configure production Oracle BI Publisher connections

## 📚 Additional Resources

- [Codespaces Deployment Guide](../docs/CODESPACES_DEPLOYMENT.md)
- [Enterprise Deployment Guide](../docs/ENTERPRISE_DEPLOYMENT.md)
- [Oracle Integration Documentation](../docs/ORACLE_INTEGRATION.md)
- [DevOps Pipeline Documentation](../docs/DEVOPS_PIPELINE.md)

## 🎉 Success Indicators

When everything is working correctly, you should see:

1. ✅ All services show "healthy" in health check
2. ✅ Frontend accessible at http://localhost:3000
3. ✅ Backend API documentation at http://localhost:8000/docs
4. ✅ Grafana dashboard at http://localhost:3001
5. ✅ Oracle mock service at http://localhost:9502
6. ✅ No errors in service logs
7. ✅ Database and cache connections working

---

**🚀 You're now ready for enterprise-grade Oracle BI Publisher development with Oatie AI!**