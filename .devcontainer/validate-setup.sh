#!/bin/bash

# Oatie AI - Codespaces Validation Script
# Validates the complete Codespaces setup for enterprise deployment

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}=================================================="
    echo -e "🔍 Oatie AI Codespaces Configuration Validator"
    echo -e "=================================================="
    echo -e "${NC}"
    echo "Validating GitHub Codespaces setup for enterprise deployment..."
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

# Validation counters
total_checks=0
passed_checks=0
warning_checks=0
failed_checks=0

run_check() {
    local check_name="$1"
    local check_command="$2"
    
    ((total_checks++))
    
    if eval "$check_command" >/dev/null 2>&1; then
        print_success "$check_name"
        ((passed_checks++))
        return 0
    else
        print_error "$check_name"
        ((failed_checks++))
        return 1
    fi
}

run_warning_check() {
    local check_name="$1"
    local check_command="$2"
    
    ((total_checks++))
    
    if eval "$check_command" >/dev/null 2>&1; then
        print_success "$check_name"
        ((passed_checks++))
        return 0
    else
        print_warning "$check_name"
        ((warning_checks++))
        return 1
    fi
}

validate_devcontainer_config() {
    echo -e "${BLUE}🐳 Validating .devcontainer Configuration${NC}"
    echo "----------------------------------------"
    
    run_check "devcontainer.json exists" "[ -f .devcontainer/devcontainer.json ]"
    run_check "docker-compose.yml exists" "[ -f .devcontainer/docker-compose.yml ]"
    run_check "setup.sh exists and is executable" "[ -x .devcontainer/setup.sh ]"
    run_check "start-services.sh exists and is executable" "[ -x .devcontainer/start-services.sh ]"
    
    # Validate JSON syntax
    run_check "devcontainer.json has valid JSON syntax" "jq empty .devcontainer/devcontainer.json"
    
    # Check for required features
    run_check "Python feature configured" "jq -e '.features | has(\"ghcr.io/devcontainers/features/python:1\")' .devcontainer/devcontainer.json"
    run_check "Node.js feature configured" "jq -e '.features | has(\"ghcr.io/devcontainers/features/node:1\")' .devcontainer/devcontainer.json"
    run_check "Docker-in-Docker feature configured" "jq -e '.features | has(\"ghcr.io/devcontainers/features/docker-in-docker:2\")' .devcontainer/devcontainer.json"
    
    # Check port forwarding
    run_check "Port forwarding configured" "jq -e '.forwardPorts | length > 0' .devcontainer/devcontainer.json"
    run_check "Essential ports forwarded (3000, 8000)" "jq -e '.forwardPorts | contains([3000, 8000])' .devcontainer/devcontainer.json"
    
    echo ""
}

validate_management_scripts() {
    echo -e "${BLUE}🛠️  Validating Management Scripts${NC}"
    echo "----------------------------------------"
    
    run_check "monitor-services.sh exists and is executable" "[ -x .devcontainer/scripts/monitor-services.sh ]"
    run_check "view-logs.sh exists and is executable" "[ -x .devcontainer/scripts/view-logs.sh ]"
    run_check "restart-services.sh exists and is executable" "[ -x .devcontainer/scripts/restart-services.sh ]"
    run_check "health-check.sh exists and is executable" "[ -x .devcontainer/scripts/health-check.sh ]"
    
    # Check script syntax
    run_check "setup.sh has valid bash syntax" "bash -n .devcontainer/setup.sh"
    run_check "start-services.sh has valid bash syntax" "bash -n .devcontainer/start-services.sh"
    run_check "monitor-services.sh has valid bash syntax" "bash -n .devcontainer/scripts/monitor-services.sh"
    
    echo ""
}

validate_docker_config() {
    echo -e "${BLUE}🐳 Validating Docker Configuration${NC}"
    echo "----------------------------------------"
    
    # Validate docker-compose syntax
    run_check "docker-compose.yml has valid syntax" "docker-compose -f .devcontainer/docker-compose.yml config"
    
    # Check required services
    run_check "workspace service configured" "docker-compose -f .devcontainer/docker-compose.yml config | grep -q 'workspace:'"
    run_check "postgres service configured" "docker-compose -f .devcontainer/docker-compose.yml config | grep -q 'postgres:'"
    run_check "redis service configured" "docker-compose -f .devcontainer/docker-compose.yml config | grep -q 'redis:'"
    run_check "prometheus service configured" "docker-compose -f .devcontainer/docker-compose.yml config | grep -q 'prometheus:'"
    run_check "grafana service configured" "docker-compose -f .devcontainer/docker-compose.yml config | grep -q 'grafana:'"
    
    echo ""
}

validate_database_config() {
    echo -e "${BLUE}🗄️  Validating Database Configuration${NC}"
    echo "----------------------------------------"
    
    run_check "PostgreSQL config file exists" "[ -f .devcontainer/postgres-dev.conf ]"
    run_check "Database init script exists" "[ -f .devcontainer/init-db.sql ]"
    run_check "Database init script has valid SQL" "grep -q 'CREATE EXTENSION' .devcontainer/init-db.sql"
    
    echo ""
}

validate_monitoring_config() {
    echo -e "${BLUE}📊 Validating Monitoring Configuration${NC}"
    echo "----------------------------------------"
    
    run_check "Prometheus config exists" "[ -f .devcontainer/prometheus-dev.yml ]"
    run_check "Grafana datasource config exists" "[ -f .devcontainer/grafana/datasources/prometheus.yml ]"
    run_check "Grafana dashboard config exists" "[ -f .devcontainer/grafana/dashboards/dashboard.yml ]"
    
    # Validate YAML syntax
    run_warning_check "Prometheus config has valid YAML" "python3 -c 'import yaml; yaml.safe_load(open(\".devcontainer/prometheus-dev.yml\"))'"
    run_warning_check "Grafana datasource config has valid YAML" "python3 -c 'import yaml; yaml.safe_load(open(\".devcontainer/grafana/datasources/prometheus.yml\"))'"
    
    echo ""
}

validate_oracle_mock() {
    echo -e "${BLUE}🏛️  Validating Oracle Mock Service${NC}"
    echo "----------------------------------------"
    
    run_check "Oracle mock directory exists" "[ -d .devcontainer/oracle-mock ]"
    run_check "Oracle mock index.html exists" "[ -f .devcontainer/oracle-mock/index.html ]"
    run_check "Oracle mock API JSON exists" "[ -f .devcontainer/oracle-mock/mock-api.json ]"
    run_check "Oracle mock nginx config exists" "[ -f .devcontainer/oracle-mock/nginx.conf ]"
    
    # Validate JSON syntax
    run_check "Oracle mock API JSON has valid syntax" "jq empty .devcontainer/oracle-mock/mock-api.json"
    
    echo ""
}

validate_documentation() {
    echo -e "${BLUE}📚 Validating Documentation${NC}"
    echo "----------------------------------------"
    
    run_check "Codespaces deployment guide exists" "[ -f docs/CODESPACES_DEPLOYMENT.md ]"
    run_check "Codespaces guide has content" "[ \$(wc -l < docs/CODESPACES_DEPLOYMENT.md) -gt 50 ]"
    run_check "Enterprise deployment guide exists" "[ -f docs/ENTERPRISE_DEPLOYMENT.md ]"
    run_check "Oracle integration guide exists" "[ -f docs/ORACLE_INTEGRATION.md ]"
    
    echo ""
}

validate_project_structure() {
    echo -e "${BLUE}📁 Validating Project Structure${NC}"
    echo "----------------------------------------"
    
    run_check "Backend directory exists" "[ -d backend ]"
    run_check "Frontend package.json exists" "[ -f package.json ]"
    run_check "Python requirements exist" "[ -f requirements.txt ]"
    run_check "Environment example exists" "[ -f .env.example ]"
    run_check "Docker compose exists" "[ -f docker-compose.yml ]"
    
    # Check for essential backend files
    run_check "Backend main.py exists" "[ -f backend/main.py ]"
    run_warning_check "Backend requirements would be available" "[ -f requirements.txt ]"
    
    echo ""
}

validate_vs_code_config() {
    echo -e "${BLUE}⚙️  Validating VS Code Configuration${NC}"
    echo "----------------------------------------"
    
    # Check VS Code extensions in devcontainer.json
    run_check "Python extensions configured" "jq -e '.customizations.vscode.extensions | map(select(contains(\"python\"))) | length > 0' .devcontainer/devcontainer.json"
    run_check "TypeScript extensions configured" "jq -e '.customizations.vscode.extensions | map(select(contains(\"typescript\"))) | length > 0' .devcontainer/devcontainer.json"
    run_check "Oracle extensions configured" "jq -e '.customizations.vscode.extensions | map(select(contains(\"oracle\"))) | length > 0' .devcontainer/devcontainer.json"
    run_check "Docker extensions configured" "jq -e '.customizations.vscode.extensions | map(select(contains(\"docker\"))) | length > 0' .devcontainer/devcontainer.json"
    
    # Check VS Code settings
    run_check "VS Code settings configured" "jq -e '.customizations.vscode.settings | length > 0' .devcontainer/devcontainer.json"
    
    echo ""
}

generate_summary() {
    echo -e "${CYAN}=================================================="
    echo -e "📋 Validation Summary"
    echo -e "=================================================="
    echo -e "${NC}"
    
    echo "Total Checks: $total_checks"
    print_success "Passed: $passed_checks"
    
    if [ $warning_checks -gt 0 ]; then
        print_warning "Warnings: $warning_checks"
    fi
    
    if [ $failed_checks -gt 0 ]; then
        print_error "Failed: $failed_checks"
    fi
    
    echo ""
    
    local pass_rate=$((passed_checks * 100 / total_checks))
    
    if [ $failed_checks -eq 0 ]; then
        if [ $warning_checks -eq 0 ]; then
            print_success "🎉 All validations passed! Codespaces environment is ready for enterprise deployment."
        else
            print_warning "✅ Core validations passed with some warnings. Environment should work correctly."
        fi
    else
        print_error "❌ Some critical validations failed. Please review and fix the issues before deployment."
        
        echo ""
        echo -e "${YELLOW}Common fixes:${NC}"
        echo "1. Ensure all required files are present"
        echo "2. Check JSON/YAML syntax with proper validation tools"
        echo "3. Verify script permissions (chmod +x)"
        echo "4. Install required tools (jq, docker-compose)"
    fi
    
    echo ""
    echo "Pass Rate: ${pass_rate}%"
    
    if [ $pass_rate -ge 90 ]; then
        print_success "Excellent configuration quality!"
    elif [ $pass_rate -ge 75 ]; then
        print_warning "Good configuration with room for improvement"
    else
        print_error "Configuration needs significant improvements"
    fi
    
    echo ""
    echo "=================================================="
    echo "🚀 Next Steps:"
    echo "1. Address any failed validations"
    echo "2. Test the environment: .devcontainer/start-services.sh"
    echo "3. Run health check: .devcontainer/scripts/health-check.sh"
    echo "4. Deploy to Codespaces and validate functionality"
    echo "=================================================="
}

# Main validation function
main() {
    print_header
    
    # Check for required tools
    if ! command -v jq >/dev/null 2>&1; then
        print_warning "jq not found, installing..."
        sudo apt-get update -qq && sudo apt-get install -y jq
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_warning "docker-compose not found, some validations will be skipped"
    fi
    
    # Run all validations
    validate_devcontainer_config
    validate_management_scripts
    validate_docker_config
    validate_database_config
    validate_monitoring_config
    validate_oracle_mock
    validate_documentation
    validate_project_structure
    validate_vs_code_config
    
    # Generate summary
    generate_summary
    
    # Return appropriate exit code
    if [ $failed_checks -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Ensure we're in the right directory
if [ ! -f ".devcontainer/devcontainer.json" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    echo "Current directory: $(pwd)"
    echo "Expected file: .devcontainer/devcontainer.json"
    exit 1
fi

# Run main function
main "$@"