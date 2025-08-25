# Enterprise DevOps Pipeline Documentation
## Phase 4.7: Production Deployment Automation

### Overview

This document provides comprehensive information about the enterprise-grade DevOps pipeline implemented for the Oatie AI Oracle BI Publisher platform. The pipeline includes blue-green deployments, automated database migrations, security scanning, performance testing, and disaster recovery capabilities.

### Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [GitHub Actions Workflows](#github-actions-workflows)
3. [Blue-Green Deployment System](#blue-green-deployment-system)
4. [Database Migration Automation](#database-migration-automation)
5. [Infrastructure as Code](#infrastructure-as-code)
6. [Security and Compliance](#security-and-compliance)
7. [Performance Testing](#performance-testing)
8. [Disaster Recovery](#disaster-recovery)
9. [Monitoring and Observability](#monitoring-and-observability)
10. [Deployment Procedures](#deployment-procedures)
11. [Troubleshooting Guide](#troubleshooting-guide)

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub        │────│   CI/CD         │────│   Kubernetes    │
│   Repository    │    │   Pipeline      │    │   Cluster       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Blue/Green    │────│   Database      │────│   Monitoring    │
│   Controller    │    │   Migration     │    │   & Alerting    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

- **CI/CD Pipeline**: GitHub Actions workflows for automated testing, building, and deployment
- **Blue-Green Deployment**: Zero-downtime deployment strategy with automatic rollback
- **Database Migration**: Automated Alembic migrations with backup and rollback support
- **Infrastructure as Code**: Terraform modules for consistent environment provisioning
- **Security Scanning**: SAST, DAST, dependency, and container vulnerability scanning
- **Performance Testing**: Automated load testing with K6, Artillery, and custom Python scripts
- **Disaster Recovery**: Automated backup and recovery procedures
- **Monitoring**: Prometheus, Grafana, and comprehensive alerting

## GitHub Actions Workflows

### 1. Production Deployment (`deploy-production.yml`)

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch with deployment strategy selection

**Features:**
- Security scanning with Trivy
- Multi-architecture container builds
- Database migration automation
- Blue-green deployment with health checks
- Automatic rollback on failure
- Post-deployment monitoring

**Usage:**
```bash
# Automatic deployment on push to main
git push origin main

# Manual deployment with specific strategy
gh workflow run deploy-production.yml \
  -f deployment_strategy=blue-green \
  -f rollback=false
```

### 2. Staging Deployment (`deploy-staging.yml`)

**Triggers:**
- Push to `develop` branch
- Pull requests to `main`
- Manual workflow dispatch

**Features:**
- Comprehensive testing (unit, integration, E2E)
- Security scanning
- Performance testing
- Smoke tests
- Team notifications

### 3. Database Migration (`database-migration.yml`)

**Triggers:**
- Workflow call from other workflows
- Manual workflow dispatch

**Features:**
- Pre-migration validation
- Automatic database backups
- Migration execution with rollback support
- Post-migration validation
- Performance impact assessment

### 4. Security Scanning (`security-scan.yml`)

**Triggers:**
- Push to main branches
- Pull requests
- Daily scheduled scans
- Manual workflow dispatch

**Features:**
- SAST (Static Application Security Testing)
- DAST (Dynamic Application Security Testing)
- Dependency vulnerability scanning
- Container image scanning
- Secrets detection
- Infrastructure security scanning
- Compliance validation

### 5. Performance Testing (`performance-test.yml`)

**Triggers:**
- Workflow call from deployments
- Daily scheduled tests
- Manual workflow dispatch

**Features:**
- Load testing with K6
- Performance testing with Artillery
- Custom Python performance scripts
- Performance regression detection
- Detailed reporting and analysis

## Blue-Green Deployment System

### Overview

The blue-green deployment system provides zero-downtime deployments by maintaining two identical production environments (blue and green) and switching traffic between them.

### Components

1. **Blue Environment**: `infrastructure/kubernetes/blue-green/blue-deployment.yaml`
2. **Green Environment**: `infrastructure/kubernetes/blue-green/green-deployment.yaml`
3. **Active Services**: `infrastructure/kubernetes/blue-green/active-services.yaml`
4. **Deployment Controller**: `scripts/deployment/blue-green-deploy.sh`

### Deployment Process

1. **Determine Target Environment**: Identify inactive environment (blue or green)
2. **Deploy to Target**: Update container images and deploy to inactive environment
3. **Health Checks**: Validate deployment health and readiness
4. **Traffic Switch**: Update active service selectors to point to new environment
5. **Verification**: Confirm traffic switch and run final health checks
6. **Cleanup**: Keep old environment for quick rollback

### Usage

```bash
# Check current deployment status
./scripts/deployment/blue-green-deploy.sh status

# Deploy new version to inactive environment
./scripts/deployment/blue-green-deploy.sh deploy --image v1.2.3

# Switch traffic to new deployment
./scripts/deployment/blue-green-deploy.sh switch

# Rollback to previous deployment
./scripts/deployment/blue-green-deploy.sh rollback

# Run health checks
./scripts/deployment/blue-green-deploy.sh health-check
```

## Database Migration Automation

### Features

- **Pre-migration Validation**: Database connectivity and state checks
- **Automatic Backups**: Create backups before applying migrations
- **Migration Execution**: Run Alembic migrations with proper error handling
- **Rollback Support**: Automatic rollback on migration failure
- **Data Validation**: Post-migration integrity checks
- **Performance Monitoring**: Track migration performance impact

### Migration Workflow

1. **Pre-flight Checks**: Validate database connection and current state
2. **Backup Creation**: Create timestamped database backup
3. **Migration Planning**: Show migration plan and validate changes
4. **Execution**: Apply migrations with monitoring
5. **Validation**: Verify data integrity and application health
6. **Rollback**: Automatic rollback on failure

### Usage

```bash
# Run database migration for staging
gh workflow run database-migration.yml \
  -f environment=staging \
  -f migration_direction=upgrade

# Dry run migration
gh workflow run database-migration.yml \
  -f environment=staging \
  -f dry_run=true

# Rollback migration
gh workflow run database-migration.yml \
  -f environment=staging \
  -f migration_direction=downgrade \
  -f target_revision=abc123
```

## Infrastructure as Code

### Terraform Modules

#### Kubernetes Module (`infrastructure/terraform/modules/kubernetes/`)

Provisions:
- Kubernetes namespaces with proper labeling
- Service accounts with RBAC
- Secrets and configuration management
- Network policies for security
- Resource quotas and limits
- Pod disruption budgets

#### Monitoring Module (`infrastructure/terraform/modules/monitoring/`)

Provisions:
- Prometheus for metrics collection
- Grafana for visualization
- Alertmanager for alerting
- Service monitors and rules
- Dashboards and data sources

#### Networking Module (`infrastructure/terraform/modules/networking/`)

Provisions:
- Ingress controllers
- Load balancers
- SSL/TLS certificates
- DNS configuration
- Network security policies

### Environment Configurations

- **Development**: `infrastructure/terraform/environments/dev/`
- **Staging**: `infrastructure/terraform/environments/staging/`
- **Production**: `infrastructure/terraform/environments/production/`

### Usage

```bash
# Initialize Terraform
cd infrastructure/terraform/environments/production
terraform init

# Plan deployment
terraform plan -var-file="terraform.tfvars"

# Apply changes
terraform apply -var-file="terraform.tfvars"

# Destroy resources (if needed)
terraform destroy -var-file="terraform.tfvars"
```

## Security and Compliance

### Security Scanning

#### SAST (Static Application Security Testing)
- **Bandit**: Python security linting
- **Semgrep**: Multi-language security analysis
- **CodeQL**: GitHub's semantic code analysis
- **ESLint**: JavaScript/TypeScript security rules

#### DAST (Dynamic Application Security Testing)
- **OWASP ZAP**: Web application security testing
- **Custom security tests**: API endpoint validation

#### Dependency Scanning
- **Safety**: Python dependency vulnerability scanning
- **pip-audit**: Python package auditing
- **npm audit**: Node.js dependency scanning
- **Snyk**: Comprehensive vulnerability database

#### Container Security
- **Trivy**: Container image vulnerability scanning
- **Grype**: Additional container security analysis
- **Docker Bench**: Docker security best practices

#### Infrastructure Security
- **Checkov**: Terraform security scanning
- **Kubesec**: Kubernetes security analysis
- **Helm security**: Helm chart validation

### Compliance Features

- **GDPR Compliance**: Data protection and privacy checks
- **SOC2 Compliance**: Security controls validation
- **License Compliance**: Software license tracking
- **Audit Logging**: Comprehensive audit trails

## Performance Testing

### Testing Tools

#### K6 Load Testing
- **Scenarios**: Homepage, dashboard, API endpoints
- **Metrics**: Response time, throughput, error rate
- **Thresholds**: 95th percentile < 5s, error rate < 1%

#### Artillery Performance Testing
- **Mixed Workload**: Realistic user scenarios
- **Ramp-up Testing**: Gradual load increase
- **Sustained Load**: Extended duration testing

#### Custom Python Scripts
- **API Testing**: Comprehensive API endpoint testing
- **Database Performance**: Database query performance
- **Integration Testing**: End-to-end performance validation

### Performance Thresholds

- **Average Response Time**: < 2s
- **95th Percentile**: < 5s
- **99th Percentile**: < 10s
- **Error Rate**: < 1%
- **Throughput**: > 100 RPS

## Disaster Recovery

### Backup Strategy

- **Automated Backups**: Daily database backups
- **Retention Policy**: 30-day backup retention
- **Storage**: AWS S3 with versioning and encryption
- **Validation**: Backup integrity checks

### Recovery Procedures

1. **Backup Creation**: Automated daily backups with metadata
2. **Backup Validation**: Integrity and restoration testing
3. **Recovery Testing**: Regular disaster recovery drills
4. **Documentation**: Detailed recovery procedures

### Usage

```bash
# Create database backup
./scripts/deployment/disaster-recovery.sh backup

# List available backups
./scripts/deployment/disaster-recovery.sh list-backups

# Restore from specific backup
./scripts/deployment/disaster-recovery.sh restore --backup-name backup-20240125-120000

# Execute disaster recovery plan
./scripts/deployment/disaster-recovery.sh dr-plan

# Validate backup integrity
./scripts/deployment/disaster-recovery.sh validate-backup --backup-name backup-20240125-120000
```

## Monitoring and Observability

### Metrics Collection

- **Application Metrics**: Custom business metrics
- **Infrastructure Metrics**: CPU, memory, network, storage
- **Database Metrics**: Query performance, connections
- **Container Metrics**: Pod resource usage

### Alerting Rules

- **High CPU Usage**: > 80% for 5 minutes
- **High Memory Usage**: > 90% for 5 minutes
- **High Error Rate**: > 1% for 2 minutes
- **Response Time**: > 5s 95th percentile
- **Database Connections**: > 80% of pool

### Dashboards

- **Application Dashboard**: Business metrics and KPIs
- **Infrastructure Dashboard**: System resource usage
- **Database Dashboard**: Database performance metrics
- **Deployment Dashboard**: Deployment status and history

## Deployment Procedures

### Production Deployment

1. **Pre-deployment Checklist**:
   - [ ] Code review completed
   - [ ] Tests passing
   - [ ] Security scan clean
   - [ ] Database migrations tested
   - [ ] Rollback plan prepared

2. **Deployment Process**:
   ```bash
   # Check current status
   ./scripts/deployment/blue-green-deploy.sh status
   
   # Deploy to inactive environment
   ./scripts/deployment/blue-green-deploy.sh deploy --image v1.2.3
   
   # Run health checks
   ./scripts/deployment/blue-green-deploy.sh health-check
   
   # Switch traffic
   ./scripts/deployment/blue-green-deploy.sh switch
   
   # Monitor for issues
   # If issues detected, rollback immediately
   ./scripts/deployment/blue-green-deploy.sh rollback
   ```

3. **Post-deployment Verification**:
   - [ ] Health checks passing
   - [ ] Performance metrics normal
   - [ ] Error rates acceptable
   - [ ] User acceptance testing

### Emergency Rollback

```bash
# Immediate rollback
./scripts/deployment/blue-green-deploy.sh rollback

# Check rollback status
./scripts/deployment/blue-green-deploy.sh status

# Verify system health
./scripts/deployment/blue-green-deploy.sh health-check
```

## Troubleshooting Guide

### Common Issues

#### Deployment Failures

**Symptom**: Deployment stuck or failing
**Solutions**:
1. Check pod logs: `kubectl logs -f deployment/oatie-backend-blue -n oatie-ai-production`
2. Check events: `kubectl get events -n oatie-ai-production --sort-by='.lastTimestamp'`
3. Verify resources: `kubectl describe pod <pod-name> -n oatie-ai-production`

#### Health Check Failures

**Symptom**: Health checks failing after deployment
**Solutions**:
1. Check application logs for errors
2. Verify database connectivity
3. Check resource limits and requests
4. Validate configuration and secrets

#### Traffic Switch Issues

**Symptom**: Traffic not switching to new environment
**Solutions**:
1. Verify service selector labels
2. Check ingress configuration
3. Validate DNS propagation
4. Test endpoint connectivity

#### Database Migration Issues

**Symptom**: Migration failures or data corruption
**Solutions**:
1. Check migration logs
2. Validate database state
3. Restore from backup if necessary
4. Run data integrity checks

### Log Analysis

```bash
# Application logs
kubectl logs -f deployment/oatie-backend-blue -n oatie-ai-production

# Database logs
kubectl logs -f deployment/postgres -n oatie-ai-production

# System events
kubectl get events -n oatie-ai-production --sort-by='.lastTimestamp'

# Performance metrics
kubectl top pods -n oatie-ai-production
```

### Support Contacts

- **Platform Engineering**: platform@oatie.company.com
- **Security Team**: security@oatie.company.com
- **On-call Engineer**: +1-555-ONCALL
- **Slack Channel**: #platform-support

---

**Version**: 3.0.0  
**Last Updated**: January 2025  
**Maintained By**: Platform Engineering Team