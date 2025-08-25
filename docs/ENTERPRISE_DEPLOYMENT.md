# Enterprise Deployment Guide
## Oatie AI Oracle BI Publisher Platform - Production Deployment

### Overview

This guide provides comprehensive instructions for deploying the Oatie AI Oracle BI Publisher platform in enterprise production environments, targeting 1000+ concurrent users with <2s response times and enterprise compliance readiness.

### Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Database Configuration](#database-configuration)
5. [Redis Cluster Setup](#redis-cluster-setup)
6. [Application Deployment](#application-deployment)
7. [Load Balancer Configuration](#load-balancer-configuration)
8. [CDN Setup](#cdn-setup)
9. [Monitoring & Observability](#monitoring--observability)
10. [Security Configuration](#security-configuration)
11. [Performance Testing](#performance-testing)
12. [Backup & Disaster Recovery](#backup--disaster-recovery)
13. [Troubleshooting](#troubleshooting)

## Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     CDN         │────│  Load Balancer  │────│   Web Server    │
│  (CloudFlare)   │    │    (nginx)      │    │    (nginx)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────┐
                       │                                 │                 │
                ┌─────────────┐              ┌─────────────┐    ┌─────────────┐
                │  Backend 1  │              │  Backend 2  │    │  Backend N  │
                │  (FastAPI)  │              │  (FastAPI)  │    │  (FastAPI)  │
                └─────────────┘              └─────────────┘    └─────────────┘
                       │                                 │                 │
                       └─────────────────────────────────┼─────────────────┘
                                                         │
        ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
        │ Redis Cluster   │    │  Database       │    │   Monitoring    │
        │   (Cache)       │    │ (PostgreSQL)    │    │ (Prometheus)    │
        └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Description

- **CDN**: Content delivery network for static assets and global edge caching
- **Load Balancer**: High-availability nginx with SSL termination and rate limiting
- **Web Server**: nginx reverse proxy with intelligent caching strategies
- **Backend**: FastAPI applications with auto-scaling capabilities
- **Redis Cluster**: Multi-layer caching and session storage
- **Database**: PostgreSQL with read replicas and connection pooling
- **Monitoring**: Prometheus, Grafana, and structured logging

## Prerequisites

### Hardware Requirements

#### Production Environment (1000+ Users)

**Load Balancer/Web Server:**
- 2-4 vCPUs
- 8-16 GB RAM
- 100 GB SSD storage
- 10 Gbps network

**Backend Servers (minimum 3 instances):**
- 4-8 vCPUs per instance
- 16-32 GB RAM per instance
- 200 GB SSD storage per instance
- 1 Gbps network per instance

**Database (Primary + 2 Replicas):**
- Primary: 8-16 vCPUs, 64-128 GB RAM, 1TB SSD
- Replicas: 4-8 vCPUs, 32-64 GB RAM, 1TB SSD each

**Redis Cluster (3-6 nodes):**
- 4 vCPUs per node
- 16-32 GB RAM per node
- 100 GB SSD per node

**Monitoring Stack:**
- 4 vCPUs
- 16 GB RAM
- 500 GB SSD storage

### Software Requirements

- **Container Runtime**: Docker 20.10+ or containerd
- **Orchestration**: Kubernetes 1.24+ (recommended) or Docker Compose
- **Database**: PostgreSQL 14+
- **Cache**: Redis 7.0+
- **Load Balancer**: nginx 1.20+
- **Monitoring**: Prometheus 2.40+, Grafana 9.0+

### Network Requirements

- **Bandwidth**: Minimum 1 Gbps, recommended 10 Gbps
- **Latency**: <10ms between components
- **Ports**: 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL), 6379 (Redis), 9090 (Prometheus)

## Infrastructure Setup

### Kubernetes Deployment (Recommended)

#### 1. Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace oatie-ai

# Create secrets
kubectl create secret generic oatie-secrets -n oatie-ai \
  --from-literal=database-url="postgresql://oatie_user:secure_password@postgres:5432/oatie_db" \
  --from-literal=redis-url="redis://redis-cluster:6379/0" \
  --from-literal=secret-key="your-super-secret-jwt-key-here" \
  --from-literal=encryption-key="your-32-character-encryption-key"
```

#### 2. Deploy Infrastructure Components

```bash
# Deploy PostgreSQL
kubectl apply -f infrastructure/kubernetes/postgresql-deployment.yaml

# Deploy Redis Cluster
kubectl apply -f infrastructure/kubernetes/redis-cluster.yaml

# Deploy backend services
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml

# Deploy frontend
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml

# Deploy ingress controller
kubectl apply -f infrastructure/kubernetes/ingress.yaml
```

### Docker Compose Deployment (Development/Small Scale)

```bash
# Copy environment configuration
cp .env.example .env

# Edit configuration
nano .env

# Deploy stack
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

## Database Configuration

### PostgreSQL Setup

#### 1. Database Initialization

```sql
-- Create database and user
CREATE DATABASE oatie_db;
CREATE USER oatie_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE oatie_db TO oatie_user;

-- Enable required extensions
\c oatie_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

#### 2. Performance Tuning

Edit `postgresql.conf`:

```ini
# Connection settings
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 1GB

# Write-ahead logging
wal_level = replica
wal_buffers = 16MB
checkpoint_completion_target = 0.7
wal_compression = on

# Query performance
random_page_cost = 1.1
effective_io_concurrency = 200
default_statistics_target = 100

# Monitoring
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
```

#### 3. Read Replica Configuration

```bash
# On replica servers
echo "standby_mode = 'on'" >> recovery.conf
echo "primary_conninfo = 'host=primary-db port=5432 user=replicator'" >> recovery.conf
echo "trigger_file = '/tmp/postgresql.trigger'" >> recovery.conf
```

## Redis Cluster Setup

### Cluster Configuration

```bash
# Create Redis configuration
cat > redis.conf << EOF
port 6379
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000
maxmemory 2gb
maxmemory-policy allkeys-lru
EOF

# Start cluster nodes
for port in 7001 7002 7003 7004 7005 7006; do
    redis-server --port $port --cluster-enabled yes --cluster-config-file nodes-${port}.conf --cluster-node-timeout 5000 --appendonly yes --daemonize yes
done

# Create cluster
redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 127.0.0.1:7006 --cluster-replicas 1
```

## Application Deployment

### Environment Configuration

Create comprehensive `.env` file:

```env
# Application
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://oatie_user:password@postgres-primary:5432/oatie_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://redis-cluster:6379/0
REDIS_CLUSTER_NODES=redis-1:6379,redis-2:6379,redis-3:6379

# Security
SECRET_KEY=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-32-character-encryption-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

# CORS
CORS_ORIGINS=https://oatie.company.com,https://app.oatie.company.com
ALLOWED_HOSTS=oatie.company.com,app.oatie.company.com

# Performance
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100
TIMEOUT=300

# Monitoring
PROMETHEUS_METRICS_PORT=9090
SENTRY_DSN=https://your-sentry-dsn-here

# External Services
ORACLE_BI_SERVER_URL=https://bi.company.com
OKTA_DOMAIN=company.okta.com
AZURE_TENANT_ID=your-tenant-id
```

### SSL/TLS Configuration

```bash
# Generate SSL certificates (using Let's Encrypt)
certbot certonly --nginx -d oatie.company.com -d app.oatie.company.com

# Or use custom certificates
cp oatie.company.com.crt /etc/ssl/certs/
cp oatie.company.com.key /etc/ssl/private/
chmod 600 /etc/ssl/private/oatie.company.com.key
```

## Load Balancer Configuration

### nginx Configuration

Use the enterprise nginx configuration from `infrastructure/docker/nginx-cdn.conf` with these production modifications:

```nginx
# Add real IP configuration
set_real_ip_from 10.0.0.0/8;
set_real_ip_from 172.16.0.0/12;
set_real_ip_from 192.168.0.0/16;
real_ip_header X-Forwarded-For;

# Add rate limiting for different zones
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=static:10m rate=100r/s;

# Add geo-blocking if needed
geo $blocked_country {
    default 0;
    CN 1;  # Example: block China
    RU 1;  # Example: block Russia
}

if ($blocked_country) {
    return 403;
}
```

### High Availability Setup

```bash
# Setup keepalived for HA
cat > /etc/keepalived/keepalived.conf << EOF
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass your_password
    }
    virtual_ipaddress {
        192.168.1.100
    }
}
EOF

systemctl enable keepalived
systemctl start keepalived
```

## CDN Setup

### CloudFlare Configuration

1. **Add Domain to CloudFlare**
   - Point DNS to load balancer IP
   - Enable "Proxy status" (orange cloud)

2. **Configure Caching Rules**
   ```javascript
   // Page Rules
   https://oatie.company.com/static/*
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 month
   - Browser Cache TTL: 1 year

   https://oatie.company.com/api/*
   - Cache Level: Bypass
   ```

3. **Security Settings**
   - SSL/TLS: Full (strict)
   - Security Level: Medium
   - Bot Fight Mode: On
   - DDoS Protection: Enabled

### AWS CloudFront (Alternative)

```json
{
  "DistributionConfig": {
    "CallerReference": "oatie-ai-cdn-2024",
    "Comment": "Oatie AI CDN Distribution",
    "DefaultCacheBehavior": {
      "TargetOriginId": "oatie-origin",
      "ViewerProtocolPolicy": "redirect-to-https",
      "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
      "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf"
    },
    "Origins": [
      {
        "Id": "oatie-origin",
        "DomainName": "oatie.company.com",
        "CustomOriginConfig": {
          "HTTPPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      }
    ],
    "Enabled": true,
    "PriceClass": "PriceClass_All"
  }
}
```

## Performance Testing

### Run Load Tests

```bash
# Install dependencies
pip install aiohttp structlog

# Run performance test
python scripts/performance_test.py \
  --base-url https://oatie.company.com \
  --users 1000 \
  --duration 10 \
  --ramp-up 60 \
  --output performance_results.json

# Analyze results
python scripts/analyze_performance.py performance_results.json
```

### Performance Benchmarks

Target metrics for 1000 concurrent users:
- **Response Time**: <2s average, <5s p95
- **Success Rate**: >99%
- **Throughput**: >100 RPS
- **Error Rate**: <1%

---

**Version**: 3.0.0  
**Last Updated**: January 2025  
**Maintained By**: Platform Engineering Team