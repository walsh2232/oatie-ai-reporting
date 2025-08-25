#!/bin/bash
set -e

# Oatie AI Enterprise Platform - Service Management Script
# Automated startup and management for all development services

echo "🚀 Starting Oatie AI Enterprise Services..."
echo "============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    print_status "Checking $service_name on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            print_success "$service_name is ready on port $port"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_status "Waiting for $service_name... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 1
        ((attempt++))
    done
    
    print_error "$service_name failed to start on port $port"
    return 1
}

# Function to wait for database to be ready
wait_for_postgres() {
    print_status "Waiting for PostgreSQL to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if pg_isready -h postgres -p 5432 -U postgres >/dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_status "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 1
        ((attempt++))
    done
    
    print_error "PostgreSQL failed to start"
    return 1
}

# Function to wait for Redis to be ready
wait_for_redis() {
    print_status "Waiting for Redis to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if redis-cli -h redis -p 6379 ping >/dev/null 2>&1; then
            print_success "Redis is ready"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_status "Waiting for Redis... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 1
        ((attempt++))
    done
    
    print_error "Redis failed to start"
    return 1
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if [ -d "backend/alembic" ]; then
        cd backend
        
        # Wait for database to be ready
        wait_for_postgres
        
        # Run migrations
        if command -v alembic >/dev/null 2>&1; then
            alembic upgrade head
            print_success "Database migrations completed"
        else
            print_warning "Alembic not available, skipping migrations"
        fi
        
        cd ..
    else
        print_warning "No Alembic migrations found, skipping"
    fi
}

# Function to create database if it doesn't exist
create_database() {
    print_status "Ensuring database exists..."
    
    wait_for_postgres
    
    # Check if database exists, create if not
    if ! psql -h postgres -U postgres -lqt | cut -d \| -f 1 | grep -qw oatie_ai; then
        print_status "Creating oatie_ai database..."
        psql -h postgres -U postgres -c "CREATE DATABASE oatie_ai;"
        print_success "Database created"
    else
        print_status "Database oatie_ai already exists"
    fi
}

# Function to start infrastructure services
start_infrastructure() {
    print_status "Starting infrastructure services..."
    
    # Start Docker Compose services in the background
    cd /workspace/.devcontainer
    docker-compose up -d postgres redis prometheus grafana oracle-mock
    cd /workspace
    
    # Wait for core services
    wait_for_postgres
    wait_for_redis
    
    # Create database and run migrations
    create_database
    run_migrations
    
    # Check other services
    check_service "Prometheus" 9090 20
    check_service "Grafana" 3001 20
    
    print_success "Infrastructure services started"
}

# Function to start backend service
start_backend() {
    print_status "Starting backend service..."
    
    # Ensure virtual environment is activated
    if [ ! -f ".venv/bin/activate" ]; then
        print_error "Python virtual environment not found. Please run setup.sh first."
        return 1
    fi
    
    source .venv/bin/activate
    
    # Start backend service in background
    cd backend
    nohup python main.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../tmp/backend.pid
    cd ..
    
    # Wait for backend to be ready
    check_service "Backend API" 8000 60
    
    print_success "Backend service started (PID: $BACKEND_PID)"
}

# Function to start frontend service
start_frontend() {
    print_status "Starting frontend service..."
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi
    
    # Start frontend service in background
    nohup npm run dev > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > tmp/frontend.pid
    
    # Wait for frontend to be ready
    check_service "Frontend Dev Server" 3000 60
    
    print_success "Frontend service started (PID: $FRONTEND_PID)"
}

# Function to perform health checks
health_check() {
    print_status "Performing health checks..."
    
    local all_healthy=true
    
    # Check PostgreSQL
    if pg_isready -h postgres -p 5432 -U postgres >/dev/null 2>&1; then
        print_success "✅ PostgreSQL: Healthy"
    else
        print_error "❌ PostgreSQL: Unhealthy"
        all_healthy=false
    fi
    
    # Check Redis
    if redis-cli -h redis -p 6379 ping >/dev/null 2>&1; then
        print_success "✅ Redis: Healthy"
    else
        print_error "❌ Redis: Unhealthy"
        all_healthy=false
    fi
    
    # Check Backend API
    if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "✅ Backend API: Healthy"
    else
        print_error "❌ Backend API: Unhealthy"
        all_healthy=false
    fi
    
    # Check Frontend
    if curl -s -f http://localhost:3000 >/dev/null 2>&1; then
        print_success "✅ Frontend: Healthy"
    else
        print_error "❌ Frontend: Unhealthy"
        all_healthy=false
    fi
    
    # Check Prometheus
    if curl -s -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
        print_success "✅ Prometheus: Healthy"
    else
        print_warning "⚠️  Prometheus: Unhealthy (non-critical)"
    fi
    
    # Check Grafana
    if curl -s -f http://localhost:3001/api/health >/dev/null 2>&1; then
        print_success "✅ Grafana: Healthy"
    else
        print_warning "⚠️  Grafana: Unhealthy (non-critical)"
    fi
    
    if [ "$all_healthy" = true ]; then
        print_success "🎉 All critical services are healthy!"
        return 0
    else
        print_error "⚠️  Some critical services are unhealthy"
        return 1
    fi
}

# Function to display service status
show_status() {
    echo ""
    echo "=================================================="
    echo "🌟 Oatie AI Enterprise Platform Status"
    echo "=================================================="
    echo ""
    echo "🌐 Service URLs:"
    echo "  Frontend:          http://localhost:3000"
    echo "  Backend API:       http://localhost:8000"
    echo "  API Docs:          http://localhost:8000/docs"
    echo "  API Redoc:         http://localhost:8000/redoc"
    echo "  Grafana:           http://localhost:3001 (admin/admin123)"
    echo "  Prometheus:        http://localhost:9090"
    echo ""
    echo "🔗 Database Connections:"
    echo "  PostgreSQL:        localhost:5432 (postgres/password)"
    echo "  Redis:             localhost:6379"
    echo ""
    echo "📊 Monitoring:"
    echo "  Health Check:      http://localhost:8000/health"
    echo "  Metrics:           http://localhost:8000/metrics"
    echo ""
    echo "📁 Log Files:"
    echo "  Backend:           logs/backend.log"
    echo "  Frontend:          logs/frontend.log"
    echo ""
    echo "🛠️  Management Commands:"
    echo "  View logs:         .devcontainer/scripts/view-logs.sh"
    echo "  Restart services:  .devcontainer/scripts/restart-services.sh"
    echo "  Monitor services:  .devcontainer/scripts/monitor-services.sh"
    echo "  Health check:      .devcontainer/scripts/health-check.sh"
    echo ""
    echo "=================================================="
}

# Function to create log directories
setup_logging() {
    mkdir -p logs tmp
    
    # Ensure log files exist
    touch logs/backend.log
    touch logs/frontend.log
    touch logs/services.log
    
    # Redirect this script's output to log file
    exec > >(tee -a logs/services.log)
    exec 2>&1
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up on exit..."
    
    # Kill background processes
    if [ -f "tmp/backend.pid" ]; then
        kill $(cat tmp/backend.pid) 2>/dev/null || true
        rm -f tmp/backend.pid
    fi
    
    if [ -f "tmp/frontend.pid" ]; then
        kill $(cat tmp/frontend.pid) 2>/dev/null || true
        rm -f tmp/frontend.pid
    fi
}

# Set up signal handling
trap cleanup EXIT

# Main execution
main() {
    # Parse command line arguments
    local start_mode=${1:-"all"}
    
    case $start_mode in
        "all")
            setup_logging
            start_infrastructure
            start_backend
            start_frontend
            health_check
            show_status
            ;;
        "infrastructure")
            setup_logging
            start_infrastructure
            ;;
        "backend")
            setup_logging
            start_infrastructure
            start_backend
            ;;
        "frontend")
            setup_logging
            start_frontend
            ;;
        "health")
            health_check
            ;;
        "status")
            show_status
            ;;
        *)
            echo "Usage: $0 [all|infrastructure|backend|frontend|health|status]"
            echo ""
            echo "  all            Start all services (default)"
            echo "  infrastructure Start only infrastructure services"
            echo "  backend        Start infrastructure and backend"
            echo "  frontend       Start only frontend"
            echo "  health         Perform health checks"
            echo "  status         Show service status"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"