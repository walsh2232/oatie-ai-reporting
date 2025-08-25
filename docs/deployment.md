# 🚀 Deployment Guide

## Overview

This guide covers deploying Oatie AI Reporting in various environments, from local development to production clusters.

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Access to Oracle BI Publisher instance
- OpenAI API key (optional, for AI features)

## Local Development

### Quick Start

```bash
# Clone the repository
git clone https://github.com/walsh2232/oatie-ai-reporting.git
cd oatie-ai-reporting

# Copy environment configuration
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Install dependencies and run locally (alternative)
pip install -e ".[dev]"
npm install
```

### Development Workflow

```bash
# Start database and Redis
docker-compose up -d database redis

# Terminal 1: Backend
uvicorn backend.oatie.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
npm run dev
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Deployment

### Docker Compose (Recommended for single server)

```bash
# Production environment
cp .env.example .env.prod
# Configure production values in .env.prod

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f
```

### Kubernetes (Recommended for clusters)

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: oatie-ai-reporting
```

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oatie-backend
  namespace: oatie-ai-reporting
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oatie-backend
  template:
    metadata:
      labels:
        app: oatie-backend
    spec:
      containers:
      - name: backend
        image: oatie-ai-reporting:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: oatie-secrets
              key: database-url
```

Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
```

### Cloud Platforms

#### AWS ECS

```yaml
# docker-compose.aws.yml
version: '3.8'
services:
  backend:
    image: your-registry/oatie-backend:latest
    cpu: 512
    memory: 1024
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
```

Deploy:
```bash
ecs-cli compose --file docker-compose.aws.yml service up
```

#### Google Cloud Run

```bash
# Build and push
docker build -t gcr.io/your-project/oatie-backend .
docker push gcr.io/your-project/oatie-backend

# Deploy
gcloud run deploy oatie-backend \
  --image gcr.io/your-project/oatie-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances

```bash
# Create resource group
az group create --name oatie-rg --location eastus

# Deploy container
az container create \
  --resource-group oatie-rg \
  --name oatie-backend \
  --image your-registry/oatie-backend:latest \
  --dns-name-label oatie-api \
  --ports 8000
```

## Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=your-super-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=https://your-frontend-domain.com

# Oracle BI Publisher
BI_PUBLISHER_URL=https://your-bi-publisher-instance.com
BI_PUBLISHER_USERNAME=your-username
BI_PUBLISHER_PASSWORD=your-password

# AI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key
AI_MODEL=gpt-3.5-turbo

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

```bash
# .env.production
VITE_API_BASE_URL=https://your-api-domain.com/api/v1
VITE_APP_TITLE=Oatie AI Reporting
```

## Database Setup

### PostgreSQL (Recommended for production)

```sql
-- Create database and user
CREATE DATABASE oatie;
CREATE USER oatie WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE oatie TO oatie;

-- Run migrations
alembic upgrade head
```

### Migration Management

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## SSL/TLS Configuration

### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
}
```

### Let's Encrypt SSL

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Logging

### Health Checks

The application provides health check endpoints:

```bash
# Backend health
curl https://your-domain.com/health

# Response
{
  "status": "healthy",
  "database": "connected",
  "oracle": "connected",
  "ai_service": "available"
}
```

### Application Monitoring

#### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

#### Log Aggregation

```yaml
# ELK Stack
elasticsearch:
  image: elasticsearch:8.5.0
  environment:
    - discovery.type=single-node

logstash:
  image: logstash:8.5.0
  volumes:
    - ./logstash/pipeline:/usr/share/logstash/pipeline

kibana:
  image: kibana:8.5.0
  ports:
    - "5601:5601"
```

### Error Tracking

#### Sentry Integration

```python
# backend/oatie/core/logging.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

## Performance Optimization

### Caching Strategy

```python
# Redis caching
from redis import Redis
import json

redis_client = Redis(host='redis', port=6379, db=0)

async def get_cached_report(report_id: str):
    cached = redis_client.get(f"report:{report_id}")
    return json.loads(cached) if cached else None
```

### CDN Configuration

```bash
# CloudFlare, AWS CloudFront, or Azure CDN
# Cache static assets for 1 year
Cache-Control: public, max-age=31536000, immutable

# Cache API responses for 5 minutes
Cache-Control: public, max-age=300
```

## Backup & Disaster Recovery

### Database Backup

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h database -U oatie oatie > ${BACKUP_DIR}/oatie_${DATE}.sql

# Compress
gzip ${BACKUP_DIR}/oatie_${DATE}.sql

# Clean old backups (keep 30 days)
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 4 hours
2. **RPO (Recovery Point Objective)**: 1 hour
3. **Backup Frequency**: Every 6 hours
4. **Geographic Redundancy**: Multi-region deployment

## Security Checklist

### Pre-deployment Security

- [ ] Update all dependencies to latest versions
- [ ] Change default passwords and secrets
- [ ] Enable HTTPS with valid certificates
- [ ] Configure security headers
- [ ] Set up Web Application Firewall (WAF)
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Configure CORS properly
- [ ] Scan for vulnerabilities

### Post-deployment Security

- [ ] Monitor security logs
- [ ] Regular security updates
- [ ] Penetration testing
- [ ] Access review (quarterly)
- [ ] Backup testing
- [ ] Incident response plan

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database status
docker-compose ps database
docker-compose logs database

# Test connection
psql -h localhost -U oatie -d oatie
```

#### Frontend Build Fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### High Memory Usage
```bash
# Monitor resource usage
docker stats
htop

# Optimize queries
EXPLAIN ANALYZE SELECT * FROM reports WHERE ...;
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug
uvicorn main:app --reload --log-level debug
```

## Scaling Guidelines

### Horizontal Scaling

- **Database**: Use read replicas for reporting queries
- **Backend**: Scale to multiple instances behind load balancer
- **Frontend**: Serve from CDN with edge caching
- **Cache**: Redis cluster for high availability

### Vertical Scaling

- **CPU**: 2-4 cores per backend instance
- **Memory**: 2-4 GB per backend instance
- **Storage**: SSD with IOPS optimization

---

For additional support, please refer to our [troubleshooting guide](troubleshooting.md) or [create an issue](https://github.com/walsh2232/oatie-ai-reporting/issues).