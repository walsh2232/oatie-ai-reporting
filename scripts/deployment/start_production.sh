#!/bin/bash
# Cross-platform production startup script for Oatie AI Platform
# Supports Linux, macOS, and Windows (via WSL/Git Bash)

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Default configuration
DEFAULT_PORT=8000
DEFAULT_WORKERS=4
DEFAULT_LOG_LEVEL="info"
DEFAULT_HOST="0.0.0.0"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Cross-platform production startup script for Oatie AI Platform.

OPTIONS:
    -p, --port PORT         Port to bind to (default: $DEFAULT_PORT)
    -w, --workers WORKERS   Number of worker processes (default: $DEFAULT_WORKERS)
    -l, --log-level LEVEL   Log level (default: $DEFAULT_LOG_LEVEL)
    -h, --host HOST         Host to bind to (default: $DEFAULT_HOST)
    --env-file FILE         Environment file to load (default: .env)
    --dev                   Development mode (enables debug, hot reload)
    --docker                Run in Docker mode
    --kubernetes           Run in Kubernetes mode
    --health-check         Perform health check after startup
    --pid-file FILE        Write PID to file
    --daemon               Run as daemon
    --help                 Show this help message

ENVIRONMENT VARIABLES:
    PORT                   Override default port
    WORKERS                Override default workers
    LOG_LEVEL              Override default log level
    HOST                   Override default host
    ENV_FILE               Override default environment file
    
EXAMPLES:
    # Basic startup
    $0
    
    # Development mode
    $0 --dev
    
    # Production with specific configuration
    $0 --port 8080 --workers 8 --log-level warning
    
    # Docker mode
    $0 --docker
    
    # Daemon mode with health check
    $0 --daemon --health-check --pid-file /var/run/oatie.pid

EOF
}

# Platform detection
detect_platform() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

# Environment detection
detect_environment() {
    if [[ "${CODESPACES:-}" == "true" ]]; then
        echo "codespaces"
    elif [[ -f "/.dockerenv" ]] || [[ "${DOCKER_CONTAINER:-}" == "true" ]]; then
        echo "docker"
    elif [[ -d "/var/run/secrets/kubernetes.io" ]]; then
        echo "kubernetes"
    elif [[ -n "${AWS_REGION:-}${GOOGLE_CLOUD_PROJECT:-}${AZURE_RESOURCE_GROUP:-}" ]]; then
        echo "cloud"
    else
        echo "local"
    fi
}

# Check if running in supported environment
check_environment() {
    local platform
    platform=$(detect_platform)
    
    log "Detected platform: $platform"
    log "Detected environment: $(detect_environment)"
    
    if [[ "$platform" == "unknown" ]]; then
        error "Unsupported platform. Supported platforms: Linux, macOS, Windows (WSL/Git Bash)"
        exit 1
    fi
    
    # Check for required commands
    local required_commands=("python3" "pip3")
    if [[ "${USE_DOCKER:-false}" == "true" ]]; then
        required_commands+=("docker")
    fi
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command '$cmd' not found"
            exit 1
        fi
    done
}

# Load environment file
load_environment() {
    local env_file="${ENV_FILE:-$PROJECT_ROOT/.env}"
    
    if [[ -f "$env_file" ]]; then
        log "Loading environment from $env_file"
        # Use set -a to automatically export variables
        set -a
        # shellcheck source=/dev/null
        source "$env_file"
        set +a
    else
        warning "Environment file $env_file not found"
        
        # Create from example if available
        local env_example="$PROJECT_ROOT/.env.example"
        if [[ -f "$env_example" ]]; then
            log "Creating $env_file from $env_example"
            cp "$env_example" "$env_file"
            
            # Apply environment-specific modifications
            local environment
            environment=$(detect_environment)
            
            case "$environment" in
                "codespaces")
                    sed -i 's/DEBUG=false/DEBUG=true/g' "$env_file" 2>/dev/null || true
                    sed -i 's/CORS_ORIGINS=.*/CORS_ORIGINS=*/g' "$env_file" 2>/dev/null || true
                    ;;
                "cloud"|"kubernetes")
                    sed -i 's/DEBUG=true/DEBUG=false/g' "$env_file" 2>/dev/null || true
                    echo "CLOUD_DEPLOYMENT=true" >> "$env_file"
                    ;;
            esac
            
            # Load the newly created file
            set -a
            # shellcheck source=/dev/null
            source "$env_file"
            set +a
        fi
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    local requirements_file="$PROJECT_ROOT/requirements.txt"
    if [[ -f "$requirements_file" ]]; then
        python3 -m pip install --user -r "$requirements_file"
    else
        # Install minimal required packages
        warning "requirements.txt not found, installing minimal dependencies"
        python3 -m pip install --user fastapi uvicorn structlog prometheus-client
    fi
}

# Setup monitoring
setup_monitoring() {
    if [[ "${MONITORING_ENABLED:-true}" == "true" ]]; then
        log "Setting up monitoring..."
        
        # Create monitoring directory if it doesn't exist
        local monitoring_dir="$PROJECT_ROOT/monitoring"
        mkdir -p "$monitoring_dir/logs"
        
        # Export monitoring environment variables
        export PROMETHEUS_MULTIPROC_DIR="$monitoring_dir/prometheus"
        mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
        
        # Setup log rotation if logrotate is available
        if command -v logrotate &> /dev/null; then
            cat > "$monitoring_dir/logrotate.conf" << 'EOF'
/var/log/oatie/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
        fi
    fi
}

# Health check function
perform_health_check() {
    local port="$1"
    local max_attempts="${HEALTH_CHECK_ATTEMPTS:-30}"
    local interval="${HEALTH_CHECK_INTERVAL:-2}"
    
    log "Performing health check on port $port..."
    
    for ((i=1; i<=max_attempts; i++)); do
        if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
            success "Health check passed (attempt $i/$max_attempts)"
            return 0
        fi
        
        if [[ $i -lt $max_attempts ]]; then
            log "Health check attempt $i/$max_attempts failed, retrying in ${interval}s..."
            sleep "$interval"
        fi
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Start application
start_application() {
    local port="${PORT:-$DEFAULT_PORT}"
    local workers="${WORKERS:-$DEFAULT_WORKERS}"
    local log_level="${LOG_LEVEL:-$DEFAULT_LOG_LEVEL}"
    local host="${HOST:-$DEFAULT_HOST}"
    
    log "Starting Oatie AI Platform..."
    log "Configuration:"
    log "  Port: $port"
    log "  Workers: $workers"
    log "  Log Level: $log_level"
    log "  Host: $host"
    log "  Backend Directory: $BACKEND_DIR"
    
    # Change to backend directory
    cd "$BACKEND_DIR"
    
    # Construct uvicorn command
    local uvicorn_cmd=(
        "python3" "-m" "uvicorn" "main:app"
        "--host" "$host"
        "--port" "$port"
        "--log-level" "$log_level"
    )
    
    # Add workers for production (only if not in development mode)
    if [[ "${DEV_MODE:-false}" != "true" ]] && [[ "$workers" -gt 1 ]]; then
        uvicorn_cmd+=("--workers" "$workers")
    fi
    
    # Add development-specific options
    if [[ "${DEV_MODE:-false}" == "true" ]]; then
        uvicorn_cmd+=("--reload" "--reload-dir" ".")
        log "Development mode enabled - hot reload active"
    fi
    
    # Add SSL configuration if enabled
    if [[ "${SSL_ENABLED:-false}" == "true" ]]; then
        local ssl_keyfile="${SSL_KEYFILE:-/etc/ssl/private/oatie.key}"
        local ssl_certfile="${SSL_CERTFILE:-/etc/ssl/certs/oatie.crt}"
        
        if [[ -f "$ssl_keyfile" ]] && [[ -f "$ssl_certfile" ]]; then
            uvicorn_cmd+=("--ssl-keyfile" "$ssl_keyfile" "--ssl-certfile" "$ssl_certfile")
            log "SSL enabled"
        else
            warning "SSL enabled but certificate files not found"
        fi
    fi
    
    # Write PID file if requested
    if [[ -n "${PID_FILE:-}" ]]; then
        mkdir -p "$(dirname "$PID_FILE")"
    fi
    
    # Start the application
    log "Executing: ${uvicorn_cmd[*]}"
    
    if [[ "${DAEMON_MODE:-false}" == "true" ]]; then
        # Start as daemon
        nohup "${uvicorn_cmd[@]}" > "$PROJECT_ROOT/monitoring/logs/oatie.log" 2>&1 &
        local pid=$!
        
        if [[ -n "${PID_FILE:-}" ]]; then
            echo "$pid" > "$PID_FILE"
            log "PID $pid written to $PID_FILE"
        fi
        
        log "Application started as daemon with PID $pid"
        
        # Perform health check if requested
        if [[ "${HEALTH_CHECK:-false}" == "true" ]]; then
            sleep 5  # Give the service time to start
            if perform_health_check "$port"; then
                success "Application is healthy and running as daemon"
            else
                error "Application health check failed"
                exit 1
            fi
        fi
    else
        # Start in foreground
        exec "${uvicorn_cmd[@]}"
    fi
}

# Docker mode
start_docker() {
    log "Starting in Docker mode..."
    
    local compose_file="docker-compose.yml"
    local environment
    environment=$(detect_environment)
    
    # Use production compose file for cloud environments
    if [[ "$environment" == "cloud" ]] || [[ "$environment" == "kubernetes" ]]; then
        if [[ -f "$PROJECT_ROOT/docker-compose.prod.yml" ]]; then
            compose_file="docker-compose.prod.yml"
        fi
    fi
    
    cd "$PROJECT_ROOT"
    
    log "Using compose file: $compose_file"
    docker-compose -f "$compose_file" up -d
    
    if [[ "${HEALTH_CHECK:-false}" == "true" ]]; then
        local port="${PORT:-$DEFAULT_PORT}"
        sleep 10  # Give Docker services time to start
        if perform_health_check "$port"; then
            success "Docker deployment is healthy"
        else
            error "Docker deployment health check failed"
            exit 1
        fi
    fi
}

# Kubernetes mode
start_kubernetes() {
    log "Starting in Kubernetes mode..."
    
    local k8s_dir="$PROJECT_ROOT/infrastructure/kubernetes"
    if [[ ! -d "$k8s_dir" ]]; then
        error "Kubernetes manifests directory not found: $k8s_dir"
        exit 1
    fi
    
    # Apply Kubernetes manifests
    kubectl apply -f "$k8s_dir/"
    
    # Wait for deployment to be ready
    kubectl rollout status deployment/oatie-backend
    
    success "Kubernetes deployment completed"
}

# Signal handlers for graceful shutdown
cleanup() {
    local exit_code=$?
    log "Shutting down..."
    
    # Kill background processes if any
    if [[ -n "${PID_FILE:-}" ]] && [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log "Stopping process $pid"
            kill "$pid"
            rm -f "$PID_FILE"
        fi
    fi
    
    exit $exit_code
}

trap cleanup EXIT INT TERM

# Main function
main() {
    log "Oatie AI Platform Production Startup Script"
    log "============================================"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -w|--workers)
                WORKERS="$2"
                shift 2
                ;;
            -l|--log-level)
                LOG_LEVEL="$2"
                shift 2
                ;;
            -h|--host)
                HOST="$2"
                shift 2
                ;;
            --env-file)
                ENV_FILE="$2"
                shift 2
                ;;
            --dev)
                DEV_MODE="true"
                shift
                ;;
            --docker)
                USE_DOCKER="true"
                shift
                ;;
            --kubernetes)
                USE_KUBERNETES="true"
                shift
                ;;
            --health-check)
                HEALTH_CHECK="true"
                shift
                ;;
            --pid-file)
                PID_FILE="$2"
                shift 2
                ;;
            --daemon)
                DAEMON_MODE="true"
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Check environment
    check_environment
    
    # Load environment variables
    load_environment
    
    # Choose startup method
    if [[ "${USE_KUBERNETES:-false}" == "true" ]]; then
        start_kubernetes
    elif [[ "${USE_DOCKER:-false}" == "true" ]]; then
        start_docker
    else
        # Install dependencies for standalone mode
        install_dependencies
        
        # Setup monitoring
        setup_monitoring
        
        # Start application
        start_application
    fi
}

# Run main function
main "$@"