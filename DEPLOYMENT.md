# Comprehensive deployment and maintenance documentation

# Oatie AI Reporting - Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose v2.0+
- Git
- Minimum 4GB RAM, 20GB disk space
- SSL certificate (for production)

### Environment Setup
```bash
# Clone repository
git clone https://github.com/walsh2232/oatie-ai-reporting.git
cd oatie-ai-reporting

# Create environment file
cp .env.example .env
# Edit .env with your production values

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check health
curl http://localhost/health
curl http://localhost:8000/health/live
```

## 📊 Architecture Overview

### Components
- **Frontend**: React with Oracle Redwood Design, served by Nginx
- **Backend**: FastAPI with Gunicorn, PostgreSQL database
- **Monitoring**: Prometheus + Grafana
- **Security**: TLS termination, container scanning, dependency auditing

### Network Architecture
```
Internet → Nginx (80/443) → Backend (8000) → PostgreSQL (5432)
                         ↓
                     Redis (6379)
                         ↓
                   Prometheus (9090) → Grafana (3000)
```

## 🔧 Configuration

### Environment Variables
See `.env.example` for all configuration options:
- Database credentials
- API keys and secrets
- Oracle BI Publisher connection
- Monitoring settings

### SSL/TLS Setup
```bash
# Place certificates in docker/ssl/
mkdir -p docker/ssl
cp your-cert.crt docker/ssl/
cp your-key.key docker/ssl/

# Update nginx configuration for HTTPS
```

## 📈 Monitoring & Observability

### Health Checks
- **Application**: `GET /health/live` (K8s liveness)
- **Readiness**: `GET /health/ready` (K8s readiness)
- **Detailed**: `GET /api/v1/health/detailed` (with DB check)

### Metrics Endpoints
- **Application Metrics**: `http://localhost:8000/metrics`
- **Prometheus UI**: `http://localhost:9090`
- **Grafana Dashboards**: `http://localhost:3000`

### Logging
- Structured JSON logging with correlation IDs
- Log aggregation via Docker logs
- Error tracking and alerting

## 🛡️ Security

### Container Security
- Non-root user execution
- Minimal base images (Alpine Linux)
- Regular vulnerability scanning with Trivy
- Dependency auditing with Safety/npm audit

### Application Security
- CORS protection
- Rate limiting
- Security headers (HSTS, CSP, etc.)
- Input validation and sanitization

### Database Security
- Connection encryption
- Least privilege access
- Regular backup encryption

## 🔄 Deployment & Updates

### Zero-Downtime Deployment
```bash
# Pull latest changes
git pull origin main

# Build new images
docker-compose -f docker-compose.prod.yml build

# Rolling update
docker-compose -f docker-compose.prod.yml up -d

# Verify health
./scripts/health-check.sh
```

### Database Migrations
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create new migration
docker-compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "Description"
```

### Backup & Recovery
```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U oatie oatie_ai > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U oatie oatie_ai < backup.sql
```

## 🔍 Troubleshooting

### Common Issues

**Service won't start**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs -f [service]

# Check resource usage
docker stats

# Verify network connectivity
docker-compose -f docker-compose.prod.yml exec backend ping postgres
```

**Database connection errors**
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Verify database initialization
docker-compose -f docker-compose.prod.yml exec postgres psql -U oatie -d oatie_ai -c "\dt"
```

**Performance issues**
```bash
# Check metrics
curl http://localhost:8000/metrics

# Monitor resource usage
docker-compose -f docker-compose.prod.yml exec backend top

# Database performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U oatie -d oatie_ai -c "SELECT * FROM pg_stat_activity;"
```

## 📋 Maintenance

### Regular Tasks
- Weekly security scans
- Monthly dependency updates
- Quarterly performance reviews
- Daily backup verification

### Scaling
- Horizontal: Multiple backend replicas
- Vertical: Increase container resources
- Database: Read replicas, connection pooling

### Monitoring Alerts
- High error rates (>5%)
- Response time degradation (>2s p95)
- Resource exhaustion (>80% CPU/Memory)
- Database connection failures

## 🆘 Emergency Procedures

### Service Recovery
```bash
# Complete restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Individual service restart
docker-compose -f docker-compose.prod.yml restart [service]
```

### Data Recovery
```bash
# Restore from backup
docker-compose -f docker-compose.prod.yml down
docker volume rm oatie-ai-reporting_postgres_data
docker-compose -f docker-compose.prod.yml up -d postgres
# Wait for initialization
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U oatie oatie_ai < backup.sql
```

## 📞 Support

### Log Collection
```bash
# Collect all logs
docker-compose -f docker-compose.prod.yml logs > debug-logs.txt

# Application logs only
docker-compose -f docker-compose.prod.yml logs backend frontend > app-logs.txt
```

### Performance Profiling
```bash
# Database queries
docker-compose -f docker-compose.prod.yml exec postgres psql -U oatie -d oatie_ai -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Application metrics
curl http://localhost:8000/metrics | grep -E "(http_request|response_time)"
```

---

For additional support, please refer to:
- GitHub Issues: https://github.com/walsh2232/oatie-ai-reporting/issues
- Documentation: README.md
- Security Issues: security@your-domain.com