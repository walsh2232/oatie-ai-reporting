#!/bin/bash

# Oatie AI - Service Restart Script
# Intelligent restart management for all services

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

print_header() {
    echo -e "${CYAN}=================================================="
    echo -e "🔄 Oatie AI Enterprise Platform Service Restart"
    echo -e "=================================================="
    echo -e "${NC}"
}

# Function to stop application services
stop_application_services() {
    print_status "Stopping application services..."
    
    # Stop backend service
    if [ -f "tmp/backend.pid" ]; then
        local backend_pid=$(cat tmp/backend.pid)
        if ps -p $backend_pid > /dev/null 2>&1; then
            print_status "Stopping backend service (PID: $backend_pid)..."
            kill $backend_pid
            
            # Wait for graceful shutdown
            local count=0
            while ps -p $backend_pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                ((count++))
            done
            
            if ps -p $backend_pid > /dev/null 2>&1; then
                print_warning "Force killing backend service..."
                kill -9 $backend_pid
            fi
            
            rm -f tmp/backend.pid
            print_success "Backend service stopped"
        else
            print_warning "Backend process not running"
            rm -f tmp/backend.pid
        fi
    else
        print_warning "Backend PID file not found"
    fi
    
    # Stop frontend service
    if [ -f "tmp/frontend.pid" ]; then
        local frontend_pid=$(cat tmp/frontend.pid)
        if ps -p $frontend_pid > /dev/null 2>&1; then
            print_status "Stopping frontend service (PID: $frontend_pid)..."
            kill $frontend_pid
            
            # Wait for graceful shutdown
            local count=0
            while ps -p $frontend_pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                ((count++))
            done
            
            if ps -p $frontend_pid > /dev/null 2>&1; then
                print_warning "Force killing frontend service..."
                kill -9 $frontend_pid
            fi
            
            rm -f tmp/frontend.pid
            print_success "Frontend service stopped"
        else
            print_warning "Frontend process not running"
            rm -f tmp/frontend.pid
        fi
    else
        print_warning "Frontend PID file not found"
    fi
    
    # Kill any remaining node or python processes related to the project
    print_status "Cleaning up any remaining processes..."
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "npm.*run.*dev" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
}

# Function to restart Docker containers
restart_docker_services() {
    print_status "Restarting Docker infrastructure services..."
    
    cd .devcontainer
    
    # Stop all services
    print_status "Stopping Docker containers..."
    docker-compose down
    
    # Start services again
    print_status "Starting Docker containers..."
    docker-compose up -d postgres redis prometheus grafana oracle-mock
    
    cd ..
    
    # Wait for services to be ready
    print_status "Waiting for infrastructure services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    # Wait for PostgreSQL
    while [ $attempt -le $max_attempts ]; do
        if pg_isready -h localhost -p 5432 -U postgres >/dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            break
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_status "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 1
        ((attempt++))
    done
    
    # Wait for Redis
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if redis-cli -p 6379 ping >/dev/null 2>&1; then
            print_success "Redis is ready"
            break
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_status "Waiting for Redis... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 1
        ((attempt++))
    done
    
    print_success "Infrastructure services restarted"
}

# Function to start application services
start_application_services() {
    print_status "Starting application services..."
    
    # Ensure virtual environment is activated
    if [ ! -f ".venv/bin/activate" ]; then
        print_error "Python virtual environment not found. Please run setup.sh first."
        return 1
    fi
    
    source .venv/bin/activate
    
    # Create necessary directories
    mkdir -p logs tmp
    
    # Start backend service
    print_status "Starting backend service..."
    cd backend
    nohup python main.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../tmp/backend.pid
    cd ..
    
    # Wait for backend to be ready
    local attempt=1
    local max_attempts=60
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend service is ready (PID: $BACKEND_PID)"
            break
        fi
        
        if [ $((attempt % 10)) -eq 0 ]; then
            print_status "Waiting for backend... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 1
        ((attempt++))
    done
    
    # Start frontend service
    print_status "Starting frontend service..."
    nohup npm run dev > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > tmp/frontend.pid
    
    # Wait for frontend to be ready
    attempt=1
    max_attempts=60
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:3000 >/dev/null 2>&1; then
            print_success "Frontend service is ready (PID: $FRONTEND_PID)"
            break
        fi
        
        if [ $((attempt % 10)) -eq 0 ]; then
            print_status "Waiting for frontend... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 1
        ((attempt++))
    done
    
    print_success "Application services started"
}

# Function to perform health check after restart
health_check() {
    print_status "Performing post-restart health check..."
    
    local all_healthy=true
    
    # Check PostgreSQL
    if pg_isready -h localhost -p 5432 -U postgres >/dev/null 2>&1; then
        print_success "✅ PostgreSQL: Healthy"
    else
        print_error "❌ PostgreSQL: Unhealthy"
        all_healthy=false
    fi
    
    # Check Redis
    if redis-cli -p 6379 ping >/dev/null 2>&1; then
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
        print_success "🎉 All critical services are healthy after restart!"
        return 0
    else
        print_error "⚠️  Some critical services are unhealthy after restart"
        return 1
    fi
}

# Function to show restart menu
show_restart_menu() {
    print_header
    echo ""
    echo "Select restart option:"
    echo ""
    echo -e "${GREEN}1.${NC} Restart all services (infrastructure + applications)"
    echo -e "${GREEN}2.${NC} Restart application services only (backend + frontend)"
    echo -e "${GREEN}3.${NC} Restart infrastructure only (database + cache + monitoring)"
    echo -e "${GREEN}4.${NC} Restart backend only"
    echo -e "${GREEN}5.${NC} Restart frontend only"
    echo -e "${GREEN}6.${NC} Quick restart (graceful application restart)"
    echo ""
    echo -e "${RED}q.${NC} Cancel"
    echo ""
    echo -n "Enter your choice: "
}

# Main restart function
main() {
    local restart_type=${1:-"menu"}
    
    case $restart_type in
        "all")
            print_header
            stop_application_services
            restart_docker_services
            start_application_services
            health_check
            ;;
        "apps"|"applications")
            print_header
            stop_application_services
            start_application_services
            health_check
            ;;
        "infrastructure"|"infra")
            print_header
            restart_docker_services
            ;;
        "backend")
            print_header
            print_status "Restarting backend service only..."
            if [ -f "tmp/backend.pid" ]; then
                kill $(cat tmp/backend.pid) 2>/dev/null || true
                rm -f tmp/backend.pid
            fi
            source .venv/bin/activate
            cd backend
            nohup python main.py > ../logs/backend.log 2>&1 &
            echo $! > ../tmp/backend.pid
            cd ..
            print_success "Backend service restarted"
            ;;
        "frontend")
            print_header
            print_status "Restarting frontend service only..."
            if [ -f "tmp/frontend.pid" ]; then
                kill $(cat tmp/frontend.pid) 2>/dev/null || true
                rm -f tmp/frontend.pid
            fi
            nohup npm run dev > logs/frontend.log 2>&1 &
            echo $! > tmp/frontend.pid
            print_success "Frontend service restarted"
            ;;
        "quick")
            print_header
            print_status "Performing quick graceful restart..."
            stop_application_services
            sleep 2
            start_application_services
            ;;
        "menu"|*)
            while true; do
                show_restart_menu
                read -n 1 choice
                echo ""
                
                case $choice in
                    '1')
                        main "all"
                        break
                        ;;
                    '2')
                        main "apps"
                        break
                        ;;
                    '3')
                        main "infra"
                        break
                        ;;
                    '4')
                        main "backend"
                        break
                        ;;
                    '5')
                        main "frontend"
                        break
                        ;;
                    '6')
                        main "quick"
                        break
                        ;;
                    'q'|'Q')
                        echo "👋 Restart cancelled"
                        exit 0
                        ;;
                    *)
                        echo "Invalid choice. Please try again."
                        sleep 1
                        ;;
                esac
            done
            ;;
    esac
    
    echo ""
    echo "=================================================="
    echo "🎉 Restart operation completed!"
    echo ""
    echo "🌐 Service URLs:"
    echo "  Frontend:          http://localhost:3000"
    echo "  Backend API:       http://localhost:8000"
    echo "  API Docs:          http://localhost:8000/docs"
    echo "  Grafana:           http://localhost:3001"
    echo "  Prometheus:        http://localhost:9090"
    echo "=================================================="
}

# Ensure we're in the right directory
if [ ! -f ".devcontainer/start-services.sh" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Run main function with arguments
main "$@"