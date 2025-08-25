#!/bin/bash

# Oatie AI - Service Monitoring Script
# Real-time monitoring of all development services

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    clear
    echo -e "${CYAN}=================================================="
    echo -e "🔍 Oatie AI Enterprise Platform Monitor"
    echo -e "Real-time Service Status & Performance"
    echo -e "=================================================="
    echo -e "${NC}"
    echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

check_service_status() {
    local service_name=$1
    local port=$2
    local host=${3:-"localhost"}
    
    if nc -z $host $port 2>/dev/null; then
        echo -e "${GREEN}✅ $service_name${NC} (Port $port)"
        return 0
    else
        echo -e "${RED}❌ $service_name${NC} (Port $port)"
        return 1
    fi
}

check_http_service() {
    local service_name=$1
    local url=$2
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 $url 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ $service_name${NC} (HTTP 200)"
        return 0
    elif [ -n "$response" ]; then
        echo -e "${YELLOW}⚠️  $service_name${NC} (HTTP $response)"
        return 1
    else
        echo -e "${RED}❌ $service_name${NC} (No response)"
        return 1
    fi
}

get_container_status() {
    local container_name=$1
    
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q $container_name; then
        local status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep $container_name | awk '{print $2" "$3}')
        echo -e "${GREEN}✅ $container_name${NC} ($status)"
    elif docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep -q $container_name; then
        local status=$(docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep $container_name | awk '{print $2" "$3}')
        echo -e "${RED}❌ $container_name${NC} ($status)"
    else
        echo -e "${YELLOW}⚠️  $container_name${NC} (Not found)"
    fi
}

show_process_info() {
    echo -e "${BLUE}📊 Process Information:${NC}"
    echo "----------------------------------------"
    
    # Backend process
    if [ -f "tmp/backend.pid" ]; then
        local backend_pid=$(cat tmp/backend.pid)
        if ps -p $backend_pid > /dev/null 2>&1; then
            local cpu_mem=$(ps -p $backend_pid -o pcpu,pmem --no-headers)
            echo -e "Backend API (PID $backend_pid): CPU: ${cpu_mem% *}%, MEM: ${cpu_mem#* }%"
        else
            echo -e "${RED}Backend API: Process not running${NC}"
        fi
    else
        echo -e "${YELLOW}Backend API: No PID file found${NC}"
    fi
    
    # Frontend process
    if [ -f "tmp/frontend.pid" ]; then
        local frontend_pid=$(cat tmp/frontend.pid)
        if ps -p $frontend_pid > /dev/null 2>&1; then
            local cpu_mem=$(ps -p $frontend_pid -o pcpu,pmem --no-headers)
            echo -e "Frontend Dev: CPU: ${cpu_mem% *}%, MEM: ${cpu_mem#* }%"
        else
            echo -e "${RED}Frontend Dev: Process not running${NC}"
        fi
    else
        echo -e "${YELLOW}Frontend Dev: No PID file found${NC}"
    fi
    
    echo ""
}

show_docker_containers() {
    echo -e "${BLUE}🐳 Docker Containers:${NC}"
    echo "----------------------------------------"
    
    get_container_status "oatie-dev-postgres"
    get_container_status "oatie-dev-redis"
    get_container_status "oatie-dev-prometheus"
    get_container_status "oatie-dev-grafana"
    get_container_status "oatie-oracle-mock"
    
    echo ""
}

show_service_endpoints() {
    echo -e "${BLUE}🌐 Service Endpoints:${NC}"
    echo "----------------------------------------"
    
    check_http_service "Frontend Dev Server" "http://localhost:3000"
    check_http_service "Backend API Health" "http://localhost:8000/health"
    check_http_service "API Documentation" "http://localhost:8000/docs"
    check_service_status "PostgreSQL Database" 5432
    check_service_status "Redis Cache" 6379
    check_http_service "Prometheus Metrics" "http://localhost:9090/-/healthy"
    check_http_service "Grafana Dashboard" "http://localhost:3001/api/health"
    
    echo ""
}

show_resource_usage() {
    echo -e "${BLUE}💻 System Resources:${NC}"
    echo "----------------------------------------"
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "CPU Usage: ${cpu_usage}%"
    
    # Memory usage
    local mem_info=$(free | grep Mem)
    local total_mem=$(echo $mem_info | awk '{print $2}')
    local used_mem=$(echo $mem_info | awk '{print $3}')
    local mem_percent=$((used_mem * 100 / total_mem))
    echo "Memory Usage: ${mem_percent}% ($(($used_mem / 1024)) MB / $(($total_mem / 1024)) MB)"
    
    # Disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    echo "Disk Usage: ${disk_usage}%"
    
    echo ""
}

show_recent_logs() {
    echo -e "${BLUE}📋 Recent Log Entries:${NC}"
    echo "----------------------------------------"
    
    if [ -f "logs/backend.log" ]; then
        echo -e "${YELLOW}Backend (last 3 lines):${NC}"
        tail -n 3 logs/backend.log 2>/dev/null | sed 's/^/  /'
        echo ""
    fi
    
    if [ -f "logs/frontend.log" ]; then
        echo -e "${YELLOW}Frontend (last 3 lines):${NC}"
        tail -n 3 logs/frontend.log 2>/dev/null | sed 's/^/  /'
        echo ""
    fi
}

show_quick_actions() {
    echo -e "${CYAN}⚡ Quick Actions:${NC}"
    echo "----------------------------------------"
    echo "r - Restart all services"
    echo "l - View logs"
    echo "h - Run health check"
    echo "s - Show service status"
    echo "q - Quit monitor"
    echo ""
}

monitor_loop() {
    while true; do
        print_header
        show_docker_containers
        show_service_endpoints
        show_process_info
        show_resource_usage
        show_recent_logs
        show_quick_actions
        
        # Wait for user input with timeout
        read -t 5 -n 1 action
        
        case $action in
            'r'|'R')
                echo "🔄 Restarting services..."
                .devcontainer/scripts/restart-services.sh
                ;;
            'l'|'L')
                echo "📋 Opening log viewer..."
                .devcontainer/scripts/view-logs.sh
                ;;
            'h'|'H')
                echo "🏥 Running health check..."
                .devcontainer/scripts/health-check.sh
                read -p "Press Enter to continue..."
                ;;
            's'|'S')
                echo "📊 Showing service status..."
                .devcontainer/start-services.sh status
                read -p "Press Enter to continue..."
                ;;
            'q'|'Q')
                echo "👋 Exiting monitor..."
                exit 0
                ;;
        esac
    done
}

# Check if we're in the right directory
if [ ! -f ".devcontainer/start-services.sh" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Start monitoring loop
monitor_loop