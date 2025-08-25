#!/bin/bash
# Blue-Green Deployment Controller Script
# Manages blue-green deployments with automated traffic switching

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-oatie-ai-production}"
TIMEOUT="${TIMEOUT:-600}"
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-10}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Blue-Green Deployment Controller

Usage: $0 [OPTIONS] COMMAND

Commands:
    status          Show current deployment status
    deploy          Deploy to inactive environment
    switch          Switch traffic to new deployment
    rollback        Rollback to previous deployment
    health-check    Run health checks on target environment
    cleanup         Remove old deployments

Options:
    -n, --namespace NAMESPACE   Kubernetes namespace (default: $NAMESPACE)
    -t, --timeout TIMEOUT       Deployment timeout in seconds (default: $TIMEOUT)
    -i, --image IMAGE           Container image tag to deploy
    -c, --component COMPONENT   Component to deploy (backend|frontend|all)
    -e, --env ENVIRONMENT       Target environment (blue|green)
    -h, --help                  Show this help message

Examples:
    $0 status
    $0 deploy --image v1.2.3 --component backend
    $0 switch --env green
    $0 rollback
    $0 health-check --env blue

Environment Variables:
    NAMESPACE               Kubernetes namespace
    TIMEOUT                 Deployment timeout
    HEALTH_CHECK_RETRIES    Number of health check retries
    HEALTH_CHECK_INTERVAL   Interval between health checks
EOF
}

# Get current active environment
get_active_environment() {
    kubectl get service oatie-frontend-active -n "$NAMESPACE" \
        -o jsonpath='{.spec.selector.environment}' 2>/dev/null || echo "unknown"
}

# Get inactive environment
get_inactive_environment() {
    local active=$(get_active_environment)
    if [[ "$active" == "blue" ]]; then
        echo "green"
    elif [[ "$active" == "green" ]]; then
        echo "blue"
    else
        echo "blue"  # Default to blue if unknown
    fi
}

# Check deployment status
check_deployment_status() {
    local env=$1
    local component=$2
    
    kubectl rollout status deployment/oatie-${component}-${env} \
        -n "$NAMESPACE" --timeout=${TIMEOUT}s
}

# Health check function
health_check() {
    local env=$1
    local retries=${HEALTH_CHECK_RETRIES}
    local interval=${HEALTH_CHECK_INTERVAL}
    
    log "Running health checks for $env environment"
    
    # Get service endpoints
    local backend_service="oatie-backend-${env}"
    local frontend_service="oatie-frontend-${env}"
    
    # Check if services exist
    if ! kubectl get service "$backend_service" -n "$NAMESPACE" &>/dev/null; then
        error "Backend service $backend_service not found"
        return 1
    fi
    
    if ! kubectl get service "$frontend_service" -n "$NAMESPACE" &>/dev/null; then
        error "Frontend service $frontend_service not found"
        return 1
    fi
    
    # Health check with retries
    for ((i=1; i<=retries; i++)); do
        log "Health check attempt $i/$retries"
        
        # Check backend health
        if kubectl exec -n "$NAMESPACE" \
           deployment/oatie-backend-${env} -- \
           curl -f http://localhost:8000/health &>/dev/null; then
            success "Backend health check passed"
            return 0
        else
            warning "Backend health check failed, attempt $i/$retries"
        fi
        
        if [[ $i -lt $retries ]]; then
            log "Waiting ${interval}s before next attempt..."
            sleep "$interval"
        fi
    done
    
    error "Health checks failed after $retries attempts"
    return 1
}

# Deploy function
deploy() {
    local image_tag=${1:-"latest"}
    local component=${2:-"all"}
    local target_env=${3:-"$(get_inactive_environment)"}
    
    log "Starting deployment to $target_env environment"
    log "Image tag: $image_tag"
    log "Component: $component"
    
    # Update image tags in manifests
    if [[ "$component" == "backend" || "$component" == "all" ]]; then
        log "Deploying backend to $target_env"
        
        # Update backend deployment
        kubectl set image deployment/oatie-backend-${target_env} \
            backend=ghcr.io/walsh2232/oatie-ai-reporting/backend:${image_tag} \
            -n "$NAMESPACE"
        
        # Wait for rollout
        check_deployment_status "$target_env" "backend"
    fi
    
    if [[ "$component" == "frontend" || "$component" == "all" ]]; then
        log "Deploying frontend to $target_env"
        
        # Update frontend deployment
        kubectl set image deployment/oatie-frontend-${target_env} \
            frontend=ghcr.io/walsh2232/oatie-ai-reporting/frontend:${image_tag} \
            -n "$NAMESPACE"
        
        # Wait for rollout
        check_deployment_status "$target_env" "frontend"
    fi
    
    success "Deployment to $target_env completed"
    
    # Run health checks
    if health_check "$target_env"; then
        success "Health checks passed"
        return 0
    else
        error "Health checks failed"
        return 1
    fi
}

# Switch traffic function
switch_traffic() {
    local target_env=${1:-"$(get_inactive_environment)"}
    local current_env=$(get_active_environment)
    
    log "Switching traffic from $current_env to $target_env"
    
    # Final health check before switching
    if ! health_check "$target_env"; then
        error "Pre-switch health check failed"
        return 1
    fi
    
    # Update active service selectors
    log "Updating frontend active service selector"
    kubectl patch service oatie-frontend-active -n "$NAMESPACE" \
        -p "{\"spec\":{\"selector\":{\"environment\":\"$target_env\"}}}"
    
    log "Updating backend active service selector"
    kubectl patch service oatie-backend-active -n "$NAMESPACE" \
        -p "{\"spec\":{\"selector\":{\"environment\":\"$target_env\"}}}"
    
    # Wait for DNS propagation
    log "Waiting for DNS propagation..."
    sleep 60
    
    # Verify traffic switch
    local new_active=$(get_active_environment)
    if [[ "$new_active" == "$target_env" ]]; then
        success "Traffic successfully switched to $target_env"
        
        # Final verification
        log "Running final verification..."
        sleep 30
        
        # You can add additional verification here
        success "Traffic switch verified"
        return 0
    else
        error "Traffic switch failed"
        return 1
    fi
}

# Rollback function
rollback() {
    local current_env=$(get_active_environment)
    local previous_env
    
    if [[ "$current_env" == "blue" ]]; then
        previous_env="green"
    elif [[ "$current_env" == "green" ]]; then
        previous_env="blue"
    else
        error "Cannot determine current environment for rollback"
        return 1
    fi
    
    warning "Rolling back from $current_env to $previous_env"
    
    # Verify previous environment is healthy
    if ! health_check "$previous_env"; then
        error "Previous environment $previous_env is not healthy"
        return 1
    fi
    
    # Switch traffic back
    switch_traffic "$previous_env"
}

# Status function
show_status() {
    local active_env=$(get_active_environment)
    local inactive_env=$(get_inactive_environment)
    
    echo "=== Blue-Green Deployment Status ==="
    echo "Namespace: $NAMESPACE"
    echo "Active Environment: $active_env"
    echo "Inactive Environment: $inactive_env"
    echo ""
    
    echo "=== Active Environment ($active_env) ==="
    kubectl get pods -n "$NAMESPACE" -l environment="$active_env" --no-headers 2>/dev/null | \
        awk '{print $1 "\t" $3 "\t" $5}' | column -t
    echo ""
    
    echo "=== Inactive Environment ($inactive_env) ==="
    kubectl get pods -n "$NAMESPACE" -l environment="$inactive_env" --no-headers 2>/dev/null | \
        awk '{print $1 "\t" $3 "\t" $5}' | column -t
    echo ""
    
    echo "=== Services ==="
    kubectl get services -n "$NAMESPACE" --no-headers 2>/dev/null | \
        grep -E "(frontend|backend)" | awk '{print $1 "\t" $2 "\t" $4}' | column -t
}

# Cleanup function
cleanup() {
    local active_env=$(get_active_environment)
    local cleanup_env
    
    if [[ "$active_env" == "blue" ]]; then
        cleanup_env="green"
    elif [[ "$active_env" == "green" ]]; then
        cleanup_env="blue"
    else
        error "Cannot determine environment for cleanup"
        return 1
    fi
    
    warning "Cleaning up inactive environment: $cleanup_env"
    
    # Scale down inactive deployments
    kubectl scale deployment oatie-backend-${cleanup_env} --replicas=0 -n "$NAMESPACE"
    kubectl scale deployment oatie-frontend-${cleanup_env} --replicas=0 -n "$NAMESPACE"
    
    success "Inactive environment $cleanup_env scaled down"
}

# Main function
main() {
    local command=""
    local image_tag="latest"
    local component="all"
    local target_env=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -i|--image)
                image_tag="$2"
                shift 2
                ;;
            -c|--component)
                component="$2"
                shift 2
                ;;
            -e|--env)
                target_env="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            status|deploy|switch|rollback|health-check|cleanup)
                command="$1"
                shift
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        error "Namespace $NAMESPACE does not exist"
        exit 1
    fi
    
    # Execute command
    case "$command" in
        status)
            show_status
            ;;
        deploy)
            deploy "$image_tag" "$component" "$target_env"
            ;;
        switch)
            if [[ -n "$target_env" ]]; then
                switch_traffic "$target_env"
            else
                switch_traffic
            fi
            ;;
        rollback)
            rollback
            ;;
        health-check)
            if [[ -n "$target_env" ]]; then
                health_check "$target_env"
            else
                health_check "$(get_active_environment)"
            fi
            ;;
        cleanup)
            cleanup
            ;;
        "")
            error "No command specified"
            show_help
            exit 1
            ;;
        *)
            error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"