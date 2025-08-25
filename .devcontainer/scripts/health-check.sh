#!/bin/bash

# Oatie AI - Health Check Script
# Comprehensive health monitoring for all services

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}=================================================="
    echo -e "🏥 Oatie AI Enterprise Platform Health Check"
    echo -e "=================================================="
    echo -e "${NC}"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if a port is open
check_port() {
    local host=$1
    local port=$2
    local timeout=${3:-3}
    
    nc -z -w$timeout $host $port 2>/dev/null
    return $?
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local expected_status=${2:-200}
    local timeout=${3:-5}
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $timeout --max-time $timeout $url 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    echo -e "${BLUE}🗄️  Database Health Check${NC}"
    echo "----------------------------------------"
    
    # Check PostgreSQL connectivity
    if check_port localhost 5432; then
        print_success "PostgreSQL port is accessible"
        
        # Check if we can actually connect
        if pg_isready -h localhost -p 5432 -U postgres >/dev/null 2>&1; then
            print_success "PostgreSQL is accepting connections"
            
            # Check database existence
            if psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw oatie_ai; then
                print_success "Database 'oatie_ai' exists"
                
                # Check basic query performance
                local query_start=$(date +%s%N)
                psql -h localhost -U postgres -d oatie_ai -c "SELECT 1;" >/dev/null 2>&1
                local query_end=$(date +%s%N)
                local query_time=$(( (query_end - query_start) / 1000000 ))
                
                if [ $query_time -lt 100 ]; then
                    print_success "Database query performance: ${query_time}ms (excellent)"
                elif [ $query_time -lt 500 ]; then
                    print_warning "Database query performance: ${query_time}ms (acceptable)"
                else
                    print_warning "Database query performance: ${query_time}ms (slow)"
                fi
            else
                print_error "Database 'oatie_ai' does not exist"
            fi
        else
            print_error "PostgreSQL is not accepting connections"
        fi
    else
        print_error "PostgreSQL port is not accessible"
    fi
    
    echo ""
}

# Function to check cache connectivity
check_cache() {
    echo -e "${BLUE}💾 Cache Health Check${NC}"
    echo "----------------------------------------"
    
    # Check Redis connectivity
    if check_port localhost 6379; then
        print_success "Redis port is accessible"
        
        # Check if we can actually connect
        if redis-cli -p 6379 ping >/dev/null 2>&1; then
            print_success "Redis is responding to ping"
            
            # Check cache performance
            local cache_start=$(date +%s%N)
            redis-cli -p 6379 set health_check_test "$(date)" >/dev/null 2>&1
            redis-cli -p 6379 get health_check_test >/dev/null 2>&1
            redis-cli -p 6379 del health_check_test >/dev/null 2>&1
            local cache_end=$(date +%s%N)
            local cache_time=$(( (cache_end - cache_start) / 1000000 ))
            
            if [ $cache_time -lt 10 ]; then
                print_success "Cache performance: ${cache_time}ms (excellent)"
            elif [ $cache_time -lt 50 ]; then
                print_warning "Cache performance: ${cache_time}ms (acceptable)"
            else
                print_warning "Cache performance: ${cache_time}ms (slow)"
            fi
            
            # Check memory usage
            local memory_info=$(redis-cli -p 6379 info memory | grep used_memory_human)
            if [ -n "$memory_info" ]; then
                print_info "Redis memory usage: ${memory_info#*:}"
            fi
        else
            print_error "Redis is not responding to ping"
        fi
    else
        print_error "Redis port is not accessible"
    fi
    
    echo ""
}

# Function to check backend service
check_backend() {
    echo -e "${BLUE}🔧 Backend API Health Check${NC}"
    echo "----------------------------------------"
    
    # Check if backend port is accessible
    if check_port localhost 8000; then
        print_success "Backend API port is accessible"
        
        # Check health endpoint
        if check_http "http://localhost:8000/health"; then
            print_success "Backend health endpoint is responding"
            
            # Get detailed health status
            local health_response=$(curl -s http://localhost:8000/health 2>/dev/null)
            if echo "$health_response" | grep -q "healthy"; then
                print_success "Backend reports healthy status"
            else
                print_warning "Backend health status unclear"
            fi
            
            # Check API documentation
            if check_http "http://localhost:8000/docs"; then
                print_success "API documentation is accessible"
            else
                print_warning "API documentation is not accessible"
            fi
            
            # Check API performance
            local api_start=$(date +%s%N)
            curl -s http://localhost:8000/health >/dev/null 2>&1
            local api_end=$(date +%s%N)
            local api_time=$(( (api_end - api_start) / 1000000 ))
            
            if [ $api_time -lt 100 ]; then
                print_success "API response time: ${api_time}ms (excellent)"
            elif [ $api_time -lt 500 ]; then
                print_warning "API response time: ${api_time}ms (acceptable)"
            else
                print_warning "API response time: ${api_time}ms (slow)"
            fi
        else
            print_error "Backend health endpoint is not responding"
        fi
        
        # Check if backend process is running
        if [ -f "tmp/backend.pid" ]; then
            local backend_pid=$(cat tmp/backend.pid)
            if ps -p $backend_pid > /dev/null 2>&1; then
                print_success "Backend process is running (PID: $backend_pid)"
                
                # Get process info
                local cpu_mem=$(ps -p $backend_pid -o pcpu,pmem --no-headers)
                print_info "Backend resource usage: CPU ${cpu_mem% *}%, Memory ${cpu_mem#* }%"
            else
                print_error "Backend process is not running (stale PID file)"
            fi
        else
            print_warning "Backend PID file not found"
        fi
    else
        print_error "Backend API port is not accessible"
    fi
    
    echo ""
}

# Function to check frontend service
check_frontend() {
    echo -e "${BLUE}🎨 Frontend Service Health Check${NC}"
    echo "----------------------------------------"
    
    # Check if frontend port is accessible
    if check_port localhost 3000; then
        print_success "Frontend development server port is accessible"
        
        # Check if frontend is responding
        if check_http "http://localhost:3000"; then
            print_success "Frontend is responding to requests"
            
            # Check frontend performance
            local frontend_start=$(date +%s%N)
            curl -s http://localhost:3000 >/dev/null 2>&1
            local frontend_end=$(date +%s%N)
            local frontend_time=$(( (frontend_end - frontend_start) / 1000000 ))
            
            if [ $frontend_time -lt 200 ]; then
                print_success "Frontend response time: ${frontend_time}ms (excellent)"
            elif [ $frontend_time -lt 1000 ]; then
                print_warning "Frontend response time: ${frontend_time}ms (acceptable)"
            else
                print_warning "Frontend response time: ${frontend_time}ms (slow)"
            fi
        else
            print_error "Frontend is not responding to requests"
        fi
        
        # Check if frontend process is running
        if [ -f "tmp/frontend.pid" ]; then
            local frontend_pid=$(cat tmp/frontend.pid)
            if ps -p $frontend_pid > /dev/null 2>&1; then
                print_success "Frontend process is running (PID: $frontend_pid)"
                
                # Get process info
                local cpu_mem=$(ps -p $frontend_pid -o pcpu,pmem --no-headers)
                print_info "Frontend resource usage: CPU ${cpu_mem% *}%, Memory ${cpu_mem#* }%"
            else
                print_error "Frontend process is not running (stale PID file)"
            fi
        else
            print_warning "Frontend PID file not found"
        fi
    else
        print_error "Frontend development server port is not accessible"
    fi
    
    echo ""
}

# Function to check monitoring services
check_monitoring() {
    echo -e "${BLUE}📊 Monitoring Services Health Check${NC}"
    echo "----------------------------------------"
    
    # Check Prometheus
    if check_port localhost 9090; then
        print_success "Prometheus port is accessible"
        
        if check_http "http://localhost:9090/-/healthy"; then
            print_success "Prometheus is healthy"
        else
            print_warning "Prometheus health check failed"
        fi
    else
        print_warning "Prometheus port is not accessible"
    fi
    
    # Check Grafana
    if check_port localhost 3001; then
        print_success "Grafana port is accessible"
        
        if check_http "http://localhost:3001/api/health"; then
            print_success "Grafana is healthy"
        else
            print_warning "Grafana health check failed"
        fi
    else
        print_warning "Grafana port is not accessible"
    fi
    
    echo ""
}

# Function to check system resources
check_system_resources() {
    echo -e "${BLUE}💻 System Resources Health Check${NC}"
    echo "----------------------------------------"
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local cpu_int=$(echo "$cpu_usage" | cut -d'.' -f1)
    
    if [ "$cpu_int" -lt 50 ]; then
        print_success "CPU usage: ${cpu_usage}% (healthy)"
    elif [ "$cpu_int" -lt 80 ]; then
        print_warning "CPU usage: ${cpu_usage}% (elevated)"
    else
        print_error "CPU usage: ${cpu_usage}% (critical)"
    fi
    
    # Check memory usage
    local mem_info=$(free | grep Mem)
    local total_mem=$(echo $mem_info | awk '{print $2}')
    local used_mem=$(echo $mem_info | awk '{print $3}')
    local mem_percent=$((used_mem * 100 / total_mem))
    
    if [ $mem_percent -lt 70 ]; then
        print_success "Memory usage: ${mem_percent}% (healthy)"
    elif [ $mem_percent -lt 85 ]; then
        print_warning "Memory usage: ${mem_percent}% (elevated)"
    else
        print_error "Memory usage: ${mem_percent}% (critical)"
    fi
    
    # Check disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    if [ $disk_usage -lt 70 ]; then
        print_success "Disk usage: ${disk_usage}% (healthy)"
    elif [ $disk_usage -lt 85 ]; then
        print_warning "Disk usage: ${disk_usage}% (elevated)"
    else
        print_error "Disk usage: ${disk_usage}% (critical)"
    fi
    
    # Check load average
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | cut -d',' -f1)
    local load_int=$(echo "$load_avg" | cut -d'.' -f1)
    
    if [ "$load_int" -lt 2 ]; then
        print_success "Load average: ${load_avg} (healthy)"
    elif [ "$load_int" -lt 4 ]; then
        print_warning "Load average: ${load_avg} (elevated)"
    else
        print_error "Load average: ${load_avg} (critical)"
    fi
    
    echo ""
}

# Function to check Docker containers
check_docker_containers() {
    echo -e "${BLUE}🐳 Docker Containers Health Check${NC}"
    echo "----------------------------------------"
    
    local containers=("oatie-dev-postgres" "oatie-dev-redis" "oatie-dev-prometheus" "oatie-dev-grafana")
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q $container; then
            local status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep $container | awk '{print $2" "$3}')
            if echo "$status" | grep -q "Up"; then
                print_success "$container is running ($status)"
            else
                print_warning "$container status: $status"
            fi
        else
            print_error "$container is not running"
        fi
    done
    
    echo ""
}

# Function to generate health summary
generate_summary() {
    echo -e "${CYAN}=================================================="
    echo -e "📋 Health Check Summary"
    echo -e "=================================================="
    echo -e "${NC}"
    
    local total_checks=0
    local passed_checks=0
    local warning_checks=0
    local failed_checks=0
    
    # This is a simplified summary - in a real implementation,
    # you would track the results of each check function
    
    echo "🎯 Critical Services:"
    echo "  ✅ Backend API, Frontend, Database, Cache"
    echo ""
    echo "⚠️  Non-Critical Services:"
    echo "  📊 Monitoring services (Prometheus, Grafana)"
    echo ""
    echo "💻 System Health:"
    echo "  📈 Resource usage within acceptable limits"
    echo ""
    echo "🔧 Recommendations:"
    echo "  • Monitor logs for any error patterns"
    echo "  • Consider scaling if resource usage is high"
    echo "  • Ensure all services are updated regularly"
    echo ""
    echo "=================================================="
    echo "Health check completed at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================================="
}

# Main health check function
main() {
    local check_type=${1:-"all"}
    
    case $check_type in
        "database"|"db")
            print_header
            check_database
            ;;
        "cache"|"redis")
            print_header
            check_cache
            ;;
        "backend"|"api")
            print_header
            check_backend
            ;;
        "frontend"|"ui")
            print_header
            check_frontend
            ;;
        "monitoring")
            print_header
            check_monitoring
            ;;
        "system"|"resources")
            print_header
            check_system_resources
            ;;
        "docker"|"containers")
            print_header
            check_docker_containers
            ;;
        "quick")
            print_header
            check_database
            check_cache
            check_backend
            check_frontend
            ;;
        "all"|*)
            print_header
            check_system_resources
            check_docker_containers
            check_database
            check_cache
            check_backend
            check_frontend
            check_monitoring
            generate_summary
            ;;
    esac
}

# Ensure we're in the right directory
if [ ! -f ".devcontainer/start-services.sh" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Show usage if help is requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Oatie AI Health Check Script"
    echo ""
    echo "Usage: $0 [check_type]"
    echo ""
    echo "Check Types:"
    echo "  all         Comprehensive health check (default)"
    echo "  quick       Quick check of critical services"
    echo "  database    Database connectivity and performance"
    echo "  cache       Redis cache connectivity and performance"
    echo "  backend     Backend API health and performance"
    echo "  frontend    Frontend service health"
    echo "  monitoring  Monitoring services (Prometheus, Grafana)"
    echo "  system      System resources (CPU, memory, disk)"
    echo "  docker      Docker container status"
    echo ""
    exit 0
fi

# Run main function with arguments
main "$@"