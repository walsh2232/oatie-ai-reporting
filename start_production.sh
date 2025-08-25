#!/bin/bash
# Oatie AI Reporting Platform - Production Startup Script
# ======================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Oatie AI Reporting Platform - Production Environment${NC}"
echo "================================================================"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Set production environment variables
export ENVIRONMENT=production
export BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
export VERSION=${VERSION:-3.0.0}
export GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Load environment variables from .env.production if it exists
if [ -f .env.production ]; then
    echo -e "${YELLOW}📋 Loading production environment variables...${NC}"
    export $(grep -v '^#' .env.production | xargs)
else
    echo -e "${YELLOW}⚠️  No .env.production file found. Using default values.${NC}"
fi

# Validate critical environment variables
echo -e "${BLUE}🔍 Validating environment configuration...${NC}"

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-production-key-change-me" ]; then
    echo -e "${RED}❌ SECRET_KEY must be set to a secure value in production${NC}"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "your-jwt-secret-production-key-change-me" ]; then
    echo -e "${RED}❌ JWT_SECRET_KEY must be set to a secure value in production${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment validation passed${NC}"

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p logs uploads backups infrastructure/{nginx,postgres,redis,prometheus,grafana}

# Pull latest images
echo -e "${BLUE}⬇️  Pulling latest Docker images...${NC}"
docker-compose -f docker-compose.production.yml pull

# Build services
echo -e "${BLUE}🔨 Building services...${NC}"
docker-compose -f docker-compose.production.yml build --no-cache

# Start services
echo -e "${BLUE}🚀 Starting production services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo -e "${BLUE}🏥 Waiting for services to be healthy...${NC}"
sleep 30

# Check service health
echo -e "${BLUE}🔍 Checking service health...${NC}"

# Check database
if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U oatie_user -d oatie_production; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${RED}❌ Database health check failed${NC}"
fi

# Check Redis
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis health check failed${NC}"
fi

# Check backend API
if curl -f http://localhost:${BACKEND_PORT:-8000}/health &>/dev/null; then
    echo -e "${GREEN}✅ Backend API is healthy${NC}"
else
    echo -e "${RED}❌ Backend API health check failed${NC}"
fi

# Check frontend
if curl -f http://localhost:${FRONTEND_PORT:-3000}/health &>/dev/null; then
    echo -e "${GREEN}✅ Frontend is healthy${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Oatie AI Reporting Platform is now running in production!${NC}"
echo "================================================================"
echo -e "${BLUE}📊 Access Points:${NC}"
echo "• Frontend:    http://localhost:${FRONTEND_PORT:-3000}"
echo "• Backend API: http://localhost:${BACKEND_PORT:-8000}"
echo "• API Docs:    http://localhost:${BACKEND_PORT:-8000}/docs"
echo "• Health:      http://localhost:${BACKEND_PORT:-8000}/health"
echo "• Metrics:     http://localhost:${BACKEND_PORT:-8000}/metrics"
echo "• Prometheus:  http://localhost:${PROMETHEUS_PORT:-9090}"
echo "• Grafana:     http://localhost:${GRAFANA_PORT:-3001}"
echo ""
echo -e "${YELLOW}📋 To view logs: docker-compose -f docker-compose.production.yml logs -f${NC}"
echo -e "${YELLOW}🛑 To stop: docker-compose -f docker-compose.production.yml down${NC}"
echo ""
