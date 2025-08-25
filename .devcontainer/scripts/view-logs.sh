#!/bin/bash

# Oatie AI - Log Viewer Script
# Interactive log viewing for all services

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_menu() {
    clear
    echo -e "${CYAN}=================================================="
    echo -e "📋 Oatie AI Enterprise Platform Log Viewer"
    echo -e "=================================================="
    echo -e "${NC}"
    echo ""
    echo "Select a log to view:"
    echo ""
    echo -e "${GREEN}1.${NC} Backend API logs"
    echo -e "${GREEN}2.${NC} Frontend development logs"
    echo -e "${GREEN}3.${NC} Service startup logs"
    echo -e "${GREEN}4.${NC} PostgreSQL logs"
    echo -e "${GREEN}5.${NC} Redis logs"
    echo -e "${GREEN}6.${NC} Prometheus logs"
    echo -e "${GREEN}7.${NC} Grafana logs"
    echo -e "${GREEN}8.${NC} Docker Compose logs"
    echo -e "${GREEN}9.${NC} All logs (live tail)"
    echo ""
    echo -e "${YELLOW}a.${NC} API request logs (filtered)"
    echo -e "${YELLOW}e.${NC} Error logs only"
    echo -e "${YELLOW}p.${NC} Performance logs"
    echo ""
    echo -e "${RED}q.${NC} Quit"
    echo ""
    echo -n "Enter your choice: "
}

view_backend_logs() {
    echo -e "${BLUE}📊 Backend API Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "================================"
    
    if [ -f "logs/backend.log" ]; then
        tail -f logs/backend.log
    else
        echo "Backend log file not found. Starting live view..."
        if [ -f "tmp/backend.pid" ]; then
            local backend_pid=$(cat tmp/backend.pid)
            echo "Following backend process output (PID: $backend_pid)..."
        fi
        touch logs/backend.log
        tail -f logs/backend.log
    fi
}

view_frontend_logs() {
    echo -e "${BLUE}🎨 Frontend Development Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "================================="
    
    if [ -f "logs/frontend.log" ]; then
        tail -f logs/frontend.log
    else
        echo "Frontend log file not found. Starting live view..."
        touch logs/frontend.log
        tail -f logs/frontend.log
    fi
}

view_service_logs() {
    echo -e "${BLUE}🚀 Service Startup Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "==============================="
    
    if [ -f "logs/services.log" ]; then
        tail -f logs/services.log
    else
        echo "Service log file not found."
        echo "Services may not have been started yet."
    fi
}

view_docker_logs() {
    echo -e "${BLUE}🐳 Docker Container Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "==============================="
    
    echo "Available containers:"
    docker-compose -f .devcontainer/docker-compose.yml ps --services
    echo ""
    echo -n "Enter container name (or 'all' for all containers): "
    read container_name
    
    if [ "$container_name" = "all" ]; then
        docker-compose -f .devcontainer/docker-compose.yml logs -f
    else
        docker-compose -f .devcontainer/docker-compose.yml logs -f $container_name
    fi
}

view_postgres_logs() {
    echo -e "${BLUE}🗄️ PostgreSQL Database Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "==============================="
    
    docker-compose -f .devcontainer/docker-compose.yml logs -f postgres
}

view_redis_logs() {
    echo -e "${BLUE}💾 Redis Cache Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "======================="
    
    docker-compose -f .devcontainer/docker-compose.yml logs -f redis
}

view_prometheus_logs() {
    echo -e "${BLUE}📈 Prometheus Monitoring Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "=============================="
    
    docker-compose -f .devcontainer/docker-compose.yml logs -f prometheus
}

view_grafana_logs() {
    echo -e "${BLUE}📊 Grafana Dashboard Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "============================="
    
    docker-compose -f .devcontainer/docker-compose.yml logs -f grafana
}

view_all_logs() {
    echo -e "${BLUE}📋 All Service Logs (Live)${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "=============================="
    
    # Create a temporary script for parallel log tailing
    cat > /tmp/tail_all_logs.sh << 'EOF'
#!/bin/bash
trap 'kill $(jobs -p)' EXIT

# Start tailing all log files in background
if [ -f "logs/backend.log" ]; then
    tail -f logs/backend.log | sed 's/^/[BACKEND] /' &
fi

if [ -f "logs/frontend.log" ]; then
    tail -f logs/frontend.log | sed 's/^/[FRONTEND] /' &
fi

if [ -f "logs/services.log" ]; then
    tail -f logs/services.log | sed 's/^/[SERVICES] /' &
fi

# Also include Docker logs
docker-compose -f .devcontainer/docker-compose.yml logs -f --tail=0 | sed 's/^/[DOCKER] /' &

wait
EOF

    chmod +x /tmp/tail_all_logs.sh
    /tmp/tail_all_logs.sh
    rm -f /tmp/tail_all_logs.sh
}

view_api_logs() {
    echo -e "${YELLOW}🔌 API Request Logs (Filtered)${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "==============================="
    
    if [ -f "logs/backend.log" ]; then
        tail -f logs/backend.log | grep -E "(GET|POST|PUT|DELETE|PATCH)" --line-buffered
    else
        echo "Backend log file not found."
    fi
}

view_error_logs() {
    echo -e "${RED}❌ Error Logs Only${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "======================"
    
    echo "Scanning for errors in all log files..."
    echo ""
    
    # Create a script to monitor for errors
    cat > /tmp/error_monitor.sh << 'EOF'
#!/bin/bash
trap 'kill $(jobs -p)' EXIT

# Monitor backend errors
if [ -f "logs/backend.log" ]; then
    tail -f logs/backend.log | grep -iE "(error|exception|traceback|failed)" --line-buffered | sed 's/^/[BACKEND ERROR] /' &
fi

# Monitor frontend errors
if [ -f "logs/frontend.log" ]; then
    tail -f logs/frontend.log | grep -iE "(error|exception|failed|warning)" --line-buffered | sed 's/^/[FRONTEND ERROR] /' &
fi

# Monitor Docker errors
docker-compose -f .devcontainer/docker-compose.yml logs -f --tail=0 | grep -iE "(error|exception|failed|warning)" --line-buffered | sed 's/^/[DOCKER ERROR] /' &

wait
EOF

    chmod +x /tmp/error_monitor.sh
    /tmp/error_monitor.sh
    rm -f /tmp/error_monitor.sh
}

view_performance_logs() {
    echo -e "${GREEN}⚡ Performance Logs${NC}"
    echo "Press Ctrl+C to return to menu"
    echo "======================"
    
    if [ -f "logs/backend.log" ]; then
        echo "Monitoring for performance-related entries..."
        tail -f logs/backend.log | grep -iE "(slow|performance|timeout|latency|response.*time)" --line-buffered
    else
        echo "Backend log file not found."
    fi
}

# Main menu loop
main_loop() {
    while true; do
        print_menu
        read -n 1 choice
        echo ""
        
        case $choice in
            '1')
                view_backend_logs
                ;;
            '2')
                view_frontend_logs
                ;;
            '3')
                view_service_logs
                ;;
            '4')
                view_postgres_logs
                ;;
            '5')
                view_redis_logs
                ;;
            '6')
                view_prometheus_logs
                ;;
            '7')
                view_grafana_logs
                ;;
            '8')
                view_docker_logs
                ;;
            '9')
                view_all_logs
                ;;
            'a'|'A')
                view_api_logs
                ;;
            'e'|'E')
                view_error_logs
                ;;
            'p'|'P')
                view_performance_logs
                ;;
            'q'|'Q')
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "Invalid choice. Please try again."
                sleep 1
                ;;
        esac
    done
}

# Ensure we're in the right directory
if [ ! -f ".devcontainer/start-services.sh" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the main loop
main_loop