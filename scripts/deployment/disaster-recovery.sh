#!/bin/bash
# Disaster Recovery and Backup Script
# Handles database backups, restore operations, and disaster recovery procedures

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-oatie-ai-production}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-oatie-backups}"
DB_NAME="${DB_NAME:-oatie_db}"

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
Disaster Recovery and Backup Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    backup              Create database backup
    restore             Restore from backup
    list-backups        List available backups
    cleanup             Remove old backups
    dr-plan             Execute disaster recovery plan
    health-check        Verify system health
    validate-backup     Validate backup integrity

Options:
    -n, --namespace NAMESPACE       Kubernetes namespace (default: $NAMESPACE)
    -b, --backup-name NAME          Specific backup name
    -r, --retention DAYS            Backup retention in days (default: $BACKUP_RETENTION_DAYS)
    -s, --s3-bucket BUCKET          S3 bucket for backups (default: $S3_BUCKET)
    -d, --database NAME             Database name (default: $DB_NAME)
    -f, --force                     Force operation without confirmation
    -h, --help                      Show this help message

Examples:
    $0 backup
    $0 restore --backup-name backup-20240125-120000
    $0 list-backups
    $0 cleanup --retention 7
    $0 dr-plan

Environment Variables:
    NAMESPACE               Kubernetes namespace
    BACKUP_RETENTION_DAYS   Backup retention period
    S3_BUCKET              S3 bucket for backup storage
    DB_NAME                Database name
EOF
}

# Get database pod
get_db_pod() {
    kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null
}

# Create database backup
create_backup() {
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
    local db_pod=$(get_db_pod)
    
    if [[ -z "$db_pod" ]]; then
        error "PostgreSQL pod not found in namespace $NAMESPACE"
        return 1
    fi
    
    log "Creating database backup: $backup_name"
    log "Database pod: $db_pod"
    
    # Create backup directory
    kubectl exec -n "$NAMESPACE" "$db_pod" -- mkdir -p /tmp/backups
    
    # Create database dump
    log "Creating database dump..."
    kubectl exec -n "$NAMESPACE" "$db_pod" -- \
        pg_dump -U postgres -h localhost "$DB_NAME" > "/tmp/${backup_name}.sql"
    
    # Copy backup from pod
    kubectl cp "$NAMESPACE/$db_pod:/tmp/${backup_name}.sql" "/tmp/${backup_name}.sql"
    
    # Compress backup
    log "Compressing backup..."
    gzip "/tmp/${backup_name}.sql"
    
    # Upload to S3 if configured
    if command -v aws &> /dev/null && [[ -n "$S3_BUCKET" ]]; then
        log "Uploading backup to S3..."
        aws s3 cp "/tmp/${backup_name}.sql.gz" "s3://$S3_BUCKET/database-backups/${backup_name}.sql.gz"
        
        # Add metadata
        aws s3api put-object-tagging \
            --bucket "$S3_BUCKET" \
            --key "database-backups/${backup_name}.sql.gz" \
            --tagging "TagSet=[{Key=Type,Value=DatabaseBackup},{Key=Database,Value=$DB_NAME},{Key=Namespace,Value=$NAMESPACE},{Key=Date,Value=$(date +%Y-%m-%d)}]"
    fi
    
    # Create backup metadata
    cat > "/tmp/${backup_name}.metadata.json" << EOF
{
    "backup_name": "$backup_name",
    "database": "$DB_NAME",
    "namespace": "$NAMESPACE",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "size_bytes": $(stat -c%s "/tmp/${backup_name}.sql.gz"),
    "checksum": "$(sha256sum "/tmp/${backup_name}.sql.gz" | cut -d' ' -f1)"
}
EOF
    
    if [[ -n "$S3_BUCKET" ]]; then
        aws s3 cp "/tmp/${backup_name}.metadata.json" "s3://$S3_BUCKET/database-backups/${backup_name}.metadata.json"
    fi
    
    success "Backup created: $backup_name"
    success "Local file: /tmp/${backup_name}.sql.gz"
    
    if [[ -n "$S3_BUCKET" ]]; then
        success "S3 location: s3://$S3_BUCKET/database-backups/${backup_name}.sql.gz"
    fi
    
    # Cleanup local files
    rm -f "/tmp/${backup_name}.sql.gz" "/tmp/${backup_name}.metadata.json"
    
    echo "$backup_name"
}

# Restore from backup
restore_backup() {
    local backup_name=$1
    local force=${2:-false}
    local db_pod=$(get_db_pod)
    
    if [[ -z "$backup_name" ]]; then
        error "Backup name is required"
        return 1
    fi
    
    if [[ -z "$db_pod" ]]; then
        error "PostgreSQL pod not found in namespace $NAMESPACE"
        return 1
    fi
    
    warning "This will restore database $DB_NAME from backup $backup_name"
    warning "ALL CURRENT DATA WILL BE LOST!"
    
    if [[ "$force" != "true" ]]; then
        read -p "Are you sure you want to continue? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log "Restore cancelled"
            return 0
        fi
    fi
    
    # Download backup from S3 if needed
    local backup_file="/tmp/${backup_name}.sql.gz"
    
    if [[ ! -f "$backup_file" ]] && [[ -n "$S3_BUCKET" ]]; then
        log "Downloading backup from S3..."
        aws s3 cp "s3://$S3_BUCKET/database-backups/${backup_name}.sql.gz" "$backup_file"
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Validate backup integrity
    log "Validating backup integrity..."
    if ! gzip -t "$backup_file"; then
        error "Backup file is corrupted"
        return 1
    fi
    
    # Create pre-restore backup
    log "Creating pre-restore backup..."
    local pre_restore_backup=$(create_backup)
    success "Pre-restore backup created: $pre_restore_backup"
    
    # Stop application pods to prevent writes
    log "Scaling down application pods..."
    kubectl scale deployment --all --replicas=0 -n "$NAMESPACE" -l app!=postgres
    
    # Wait for pods to terminate
    kubectl wait --for=delete pod -l app!=postgres -n "$NAMESPACE" --timeout=300s
    
    # Copy backup to pod
    log "Copying backup to database pod..."
    gunzip -c "$backup_file" > "/tmp/${backup_name}.sql"
    kubectl cp "/tmp/${backup_name}.sql" "$NAMESPACE/$db_pod:/tmp/${backup_name}.sql"
    
    # Drop and recreate database
    log "Dropping existing database..."
    kubectl exec -n "$NAMESPACE" "$db_pod" -- \
        psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
    
    kubectl exec -n "$NAMESPACE" "$db_pod" -- \
        psql -U postgres -c "CREATE DATABASE $DB_NAME;"
    
    # Restore database
    log "Restoring database from backup..."
    kubectl exec -n "$NAMESPACE" "$db_pod" -- \
        psql -U postgres -d "$DB_NAME" -f "/tmp/${backup_name}.sql"
    
    # Cleanup backup file from pod
    kubectl exec -n "$NAMESPACE" "$db_pod" -- rm -f "/tmp/${backup_name}.sql"
    
    # Scale up application pods
    log "Scaling up application pods..."
    kubectl scale deployment --all --replicas=3 -n "$NAMESPACE" -l app!=postgres
    
    # Wait for pods to be ready
    kubectl wait --for=condition=available --timeout=300s deployment --all -n "$NAMESPACE" -l app!=postgres
    
    success "Database restored from backup: $backup_name"
    
    # Cleanup local files
    rm -f "/tmp/${backup_name}.sql"
}

# List available backups
list_backups() {
    log "Available backups:"
    
    if [[ -n "$S3_BUCKET" ]] && command -v aws &> /dev/null; then
        echo "=== S3 Backups ==="
        aws s3 ls "s3://$S3_BUCKET/database-backups/" --recursive | \
            grep "\.sql\.gz$" | \
            awk '{print $4 " " $1 " " $2 " " $3}' | \
            sort -r
    fi
    
    echo "=== Local Backups ==="
    ls -la /tmp/backup-*.sql.gz 2>/dev/null || echo "No local backups found"
}

# Cleanup old backups
cleanup_backups() {
    local retention_days=${1:-$BACKUP_RETENTION_DAYS}
    
    log "Cleaning up backups older than $retention_days days"
    
    # Cleanup S3 backups
    if [[ -n "$S3_BUCKET" ]] && command -v aws &> /dev/null; then
        log "Cleaning up S3 backups..."
        
        # List old backups
        local cutoff_date=$(date -d "$retention_days days ago" +%Y-%m-%d)
        
        aws s3api list-objects-v2 \
            --bucket "$S3_BUCKET" \
            --prefix "database-backups/" \
            --query "Contents[?LastModified<='$cutoff_date'].Key" \
            --output text | \
        while read -r key; do
            if [[ -n "$key" && "$key" != "None" ]]; then
                log "Deleting old backup: $key"
                aws s3 rm "s3://$S3_BUCKET/$key"
            fi
        done
    fi
    
    # Cleanup local backups
    log "Cleaning up local backups..."
    find /tmp -name "backup-*.sql.gz" -mtime +$retention_days -delete
    
    success "Backup cleanup completed"
}

# Disaster recovery plan
execute_dr_plan() {
    log "Executing disaster recovery plan..."
    
    # Check cluster status
    log "Checking cluster status..."
    if ! kubectl cluster-info &> /dev/null; then
        error "Kubernetes cluster is not accessible"
        return 1
    fi
    
    # Check namespace
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        warning "Namespace $NAMESPACE does not exist, creating..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    # Deploy base infrastructure
    log "Deploying base infrastructure..."
    kubectl apply -f infrastructure/kubernetes/
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    kubectl wait --for=condition=available --timeout=600s deployment -l app=postgres -n "$NAMESPACE"
    
    # Restore from latest backup
    log "Finding latest backup..."
    local latest_backup
    if [[ -n "$S3_BUCKET" ]] && command -v aws &> /dev/null; then
        latest_backup=$(aws s3 ls "s3://$S3_BUCKET/database-backups/" | \
            grep "\.sql\.gz$" | \
            sort -k1,1 -k2,2 | \
            tail -1 | \
            awk '{print $4}' | \
            sed 's/\.sql\.gz$//')
    fi
    
    if [[ -n "$latest_backup" ]]; then
        log "Restoring from latest backup: $latest_backup"
        restore_backup "$latest_backup" true
    else
        warning "No backup found for restoration"
    fi
    
    # Verify system health
    health_check
    
    success "Disaster recovery plan executed successfully"
}

# Health check
health_check() {
    log "Performing system health check..."
    
    # Check database
    local db_pod=$(get_db_pod)
    if [[ -n "$db_pod" ]]; then
        if kubectl exec -n "$NAMESPACE" "$db_pod" -- pg_isready -U postgres &> /dev/null; then
            success "Database is healthy"
        else
            error "Database health check failed"
            return 1
        fi
    else
        error "Database pod not found"
        return 1
    fi
    
    # Check application pods
    local unhealthy_pods
    unhealthy_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers | \
        grep -v "Running\|Completed" | wc -l)
    
    if [[ "$unhealthy_pods" -eq 0 ]]; then
        success "All application pods are healthy"
    else
        warning "$unhealthy_pods unhealthy pods found"
        kubectl get pods -n "$NAMESPACE" --no-headers | grep -v "Running\|Completed"
    fi
    
    # Check services
    local services
    services=$(kubectl get services -n "$NAMESPACE" --no-headers | wc -l)
    success "$services services are running"
    
    success "Health check completed"
}

# Validate backup
validate_backup() {
    local backup_name=$1
    
    if [[ -z "$backup_name" ]]; then
        error "Backup name is required"
        return 1
    fi
    
    log "Validating backup: $backup_name"
    
    # Download backup if needed
    local backup_file="/tmp/${backup_name}.sql.gz"
    
    if [[ ! -f "$backup_file" ]] && [[ -n "$S3_BUCKET" ]]; then
        log "Downloading backup from S3..."
        aws s3 cp "s3://$S3_BUCKET/database-backups/${backup_name}.sql.gz" "$backup_file"
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Test compression integrity
    if gzip -t "$backup_file"; then
        success "Backup compression is valid"
    else
        error "Backup compression is corrupted"
        return 1
    fi
    
    # Test SQL syntax
    log "Validating SQL syntax..."
    if gunzip -c "$backup_file" | head -100 | grep -q "PostgreSQL database dump"; then
        success "Backup appears to be a valid PostgreSQL dump"
    else
        error "Backup does not appear to be a valid PostgreSQL dump"
        return 1
    fi
    
    # Check metadata if available
    local metadata_file="/tmp/${backup_name}.metadata.json"
    if [[ -n "$S3_BUCKET" ]]; then
        aws s3 cp "s3://$S3_BUCKET/database-backups/${backup_name}.metadata.json" "$metadata_file" 2>/dev/null || true
    fi
    
    if [[ -f "$metadata_file" ]]; then
        log "Validating checksum..."
        local stored_checksum=$(jq -r '.checksum' "$metadata_file")
        local actual_checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
        
        if [[ "$stored_checksum" == "$actual_checksum" ]]; then
            success "Checksum validation passed"
        else
            error "Checksum validation failed"
            return 1
        fi
        
        rm -f "$metadata_file"
    fi
    
    success "Backup validation completed successfully"
}

# Main function
main() {
    local command=""
    local backup_name=""
    local retention_days="$BACKUP_RETENTION_DAYS"
    local force=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -b|--backup-name)
                backup_name="$2"
                shift 2
                ;;
            -r|--retention)
                retention_days="$2"
                shift 2
                ;;
            -s|--s3-bucket)
                S3_BUCKET="$2"
                shift 2
                ;;
            -d|--database)
                DB_NAME="$2"
                shift 2
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            backup|restore|list-backups|cleanup|dr-plan|health-check|validate-backup)
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
    
    # Execute command
    case "$command" in
        backup)
            create_backup
            ;;
        restore)
            restore_backup "$backup_name" "$force"
            ;;
        list-backups)
            list_backups
            ;;
        cleanup)
            cleanup_backups "$retention_days"
            ;;
        dr-plan)
            execute_dr_plan
            ;;
        health-check)
            health_check
            ;;
        validate-backup)
            validate_backup "$backup_name"
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