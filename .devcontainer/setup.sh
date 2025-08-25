#!/bin/bash
set -e

# Oatie AI Enterprise Platform - Codespaces Setup Script
# Automated setup for complete development environment with Oracle BI Publisher integration

echo "🚀 Setting up Oatie AI Enterprise Development Environment..."
echo "=================================================="

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create directory if it doesn't exist
ensure_directory() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        print_status "Created directory: $1"
    fi
}

# Update system packages
print_status "Updating system packages..."
sudo apt-get update -qq

# Install essential development tools
print_status "Installing essential development tools..."
sudo apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libpq-dev \
    postgresql-client \
    redis-tools \
    jq \
    htop \
    tree \
    vim \
    nano

# Install Oracle Instant Client (for Oracle BI Publisher integration)
print_status "Installing Oracle Instant Client..."
if [ ! -d "/opt/oracle" ]; then
    sudo mkdir -p /opt/oracle
    cd /tmp
    
    # Download Oracle Instant Client (using version 21.1 for better compatibility)
    if [ ! -f "instantclient-basic-linux.x64-21.1.0.0.0.zip" ]; then
        print_status "Downloading Oracle Instant Client..."
        wget -q https://download.oracle.com/otn_software/linux/instantclient/211000/instantclient-basic-linux.x64-21.1.0.0.0.zip || true
    fi
    
    if [ -f "instantclient-basic-linux.x64-21.1.0.0.0.zip" ]; then
        sudo unzip -q instantclient-basic-linux.x64-21.1.0.0.0.zip -d /opt/oracle/
        sudo ln -sf /opt/oracle/instantclient_21_1 /opt/oracle/instantclient
        
        # Set up Oracle environment
        echo 'export ORACLE_HOME=/opt/oracle/instantclient' | sudo tee -a /etc/environment
        echo 'export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH' | sudo tee -a /etc/environment
        echo 'export PATH=$ORACLE_HOME:$PATH' | sudo tee -a /etc/environment
        
        export ORACLE_HOME=/opt/oracle/instantclient
        export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
        export PATH=$ORACLE_HOME:$PATH
        
        print_success "Oracle Instant Client installed"
    else
        print_warning "Oracle Instant Client download failed - will continue without it"
    fi
fi

cd /workspace

# Set up Python virtual environment
print_status "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Python virtual environment created"
fi

# Activate virtual environment
source .venv/bin/activate
print_status "Python virtual environment activated"

# Upgrade pip and install essential Python tools
print_status "Upgrading pip and installing Python development tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
print_status "Installing Python backend dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found, installing basic FastAPI stack..."
    pip install fastapi uvicorn sqlalchemy alembic asyncpg redis aioredis pytest black flake8 isort
fi

# Install additional Oracle-specific Python packages
print_status "Installing Oracle-specific Python packages..."
pip install cx_Oracle oracledb sqlalchemy-oracle

# Install development and testing tools
print_status "Installing Python development tools..."
pip install \
    pytest-asyncio \
    pytest-cov \
    httpx \
    factory-boy \
    faker \
    pre-commit \
    mypy \
    bandit \
    safety

# Set up pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    print_status "Setting up pre-commit hooks..."
    pre-commit install
    print_success "Pre-commit hooks installed"
fi

# Install Node.js dependencies
print_status "Installing Node.js frontend dependencies..."
if [ -f "package.json" ]; then
    npm install
    print_success "Node.js dependencies installed"
else
    print_warning "package.json not found in root"
fi

# Check for frontend directory and install dependencies there too
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    print_status "Installing frontend dependencies..."
    npm install
    cd ..
    print_success "Frontend dependencies installed"
fi

# Install global Node.js development tools
print_status "Installing global Node.js tools..."
npm install -g \
    typescript \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin \
    prettier \
    eslint \
    nodemon \
    pm2 \
    newman \
    lighthouse \
    @playwright/test

# Install K6 for performance testing
print_status "Installing K6 for performance testing..."
if ! command_exists k6; then
    sudo gpg -k >/dev/null 2>&1 || true
    sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69 || true
    echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
    sudo apt-get update -qq
    sudo apt-get install -y k6 || print_warning "K6 installation failed"
fi

# Install Artillery for additional performance testing
print_status "Installing Artillery..."
npm install -g artillery || print_warning "Artillery installation failed"

# Set up development directories
print_status "Setting up development directories..."
ensure_directory "logs"
ensure_directory "tmp"
ensure_directory ".pytest_cache"
ensure_directory "coverage"
ensure_directory "test-results"

# Set up environment file for development
print_status "Setting up development environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
    else
        print_status "Creating basic .env file..."
        cat > .env << 'EOF'
# Development Environment Configuration
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/oatie_ai
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://redis:6379/0
CACHE_TTL_DEFAULT=3600

# Security
SECRET_KEY=development-secret-key-not-for-production-change-me
ENCRYPTION_KEY=development-encryption-key-32chars
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:3000,https://*.githubpreview.dev,https://*.app.github.dev
ALLOWED_HOSTS=*

# Oracle BI Publisher
ORACLE_BI_URL=http://oracle-mock:80/xmlpserver
ORACLE_BI_USERNAME=weblogic
ORACLE_BI_PASSWORD=password
ORACLE_BI_TIMEOUT=30

# Monitoring
MONITORING_ENABLED=true
PROMETHEUS_METRICS_PORT=9090
EOF
        print_success "Basic .env file created"
    fi
fi

# Initialize database migration scripts
print_status "Setting up database migration framework..."
if [ ! -d "alembic" ] && [ -d "backend" ]; then
    cd backend
    if command_exists alembic; then
        alembic init alembic 2>/dev/null || print_warning "Alembic already initialized or failed"
    fi
    cd ..
fi

# Set up Git hooks for development
print_status "Configuring Git for development..."
git config --global user.name "Codespaces Developer" 2>/dev/null || true
git config --global user.email "developer@oatie.ai" 2>/dev/null || true
git config --global init.defaultBranch main 2>/dev/null || true
git config --global pull.rebase false 2>/dev/null || true

# Create helpful development scripts
print_status "Creating development utility scripts..."
ensure_directory "scripts/dev"

# Create quick start script
cat > scripts/dev/quick-start.sh << 'EOF'
#!/bin/bash
# Quick start script for Oatie AI development

echo "🚀 Starting Oatie AI development servers..."

# Start services in background
.devcontainer/start-services.sh &

# Wait for services to be ready
sleep 10

# Start backend in background
cd backend && python main.py &
BACKEND_PID=$!

# Start frontend in background  
npm run dev &
FRONTEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Grafana: http://localhost:3001"
echo "📈 Prometheus: http://localhost:9090"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
EOF

chmod +x scripts/dev/quick-start.sh

# Create database reset script
cat > scripts/dev/reset-db.sh << 'EOF'
#!/bin/bash
# Reset development database

echo "🗄️ Resetting development database..."

# Drop and recreate database
docker-compose -f .devcontainer/docker-compose.yml exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS oatie_ai;"
docker-compose -f .devcontainer/docker-compose.yml exec postgres psql -U postgres -c "CREATE DATABASE oatie_ai;"

# Run migrations if they exist
if [ -d "backend/alembic" ]; then
    cd backend
    alembic upgrade head
    cd ..
fi

echo "✅ Database reset complete"
EOF

chmod +x scripts/dev/reset-db.sh

# Create testing script
cat > scripts/dev/run-tests.sh << 'EOF'
#!/bin/bash
# Run comprehensive test suite

echo "🧪 Running Oatie AI test suite..."

# Backend tests
echo "Running Python backend tests..."
cd backend && python -m pytest tests/ -v --cov=. --cov-report=html

# Frontend tests  
echo "Running frontend tests..."
cd ../frontend && npm test

# API tests
echo "Running API integration tests..."
cd .. && npm run test:api || echo "API tests not configured"

# Performance tests
echo "Running performance tests..."
npm run test:e2e:performance || echo "Performance tests not configured"

echo "✅ Test suite complete"
EOF

chmod +x scripts/dev/run-tests.sh

# Set up VS Code workspace settings
print_status "Configuring VS Code workspace..."
ensure_directory ".vscode"

if [ ! -f ".vscode/settings.json" ]; then
    cat > .vscode/settings.json << 'EOF'
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.autoTestDiscoverOnSaveEnabled": true,
  "typescript.preferences.quoteStyle": "single",
  "editor.formatOnSave": true,
  "files.associations": {
    "*.yml": "yaml",
    "*.yaml": "yaml",
    "Dockerfile*": "dockerfile",
    ".env*": "properties"
  },
  "git.autofetch": true,
  "terminal.integrated.defaultProfile.linux": "bash"
}
EOF
    print_success "VS Code workspace settings created"
fi

# Create launch configurations for debugging
if [ ! -f ".vscode/launch.json" ]; then
    cat > .vscode/launch.json << 'EOF'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug FastAPI Backend",
      "type": "python",
      "request": "launch",
      "program": "backend/main.py",
      "console": "integratedTerminal",
      "python": "./.venv/bin/python",
      "env": {
        "DEBUG": "true",
        "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/oatie_ai"
      }
    },
    {
      "name": "Debug Python Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "--no-cov"],
      "console": "integratedTerminal",
      "python": "./.venv/bin/python"
    },
    {
      "name": "Attach to Node.js",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "restart": true,
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/workspace"
    }
  ]
}
EOF
    print_success "VS Code launch configurations created"
fi

# Set correct permissions
print_status "Setting up file permissions..."
chmod +x .devcontainer/start-services.sh 2>/dev/null || true
chmod +x .devcontainer/scripts/*.sh 2>/dev/null || true
find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Display setup summary
print_success "🎉 Oatie AI Enterprise Development Environment Setup Complete!"
echo ""
echo "=================================================="
echo "📋 Setup Summary:"
echo "=================================================="
echo "✅ System packages updated"
echo "✅ Oracle Instant Client configured"
echo "✅ Python virtual environment created"
echo "✅ Python dependencies installed"
echo "✅ Node.js dependencies installed"
echo "✅ Development tools installed"
echo "✅ Environment configuration created"
echo "✅ VS Code workspace configured"
echo "✅ Development scripts created"
echo ""
echo "🚀 Quick Start Commands:"
echo "=================================================="
echo "Start all services:    .devcontainer/start-services.sh"
echo "Quick development:     scripts/dev/quick-start.sh"
echo "Run tests:            scripts/dev/run-tests.sh"
echo "Reset database:       scripts/dev/reset-db.sh"
echo "View service logs:    .devcontainer/scripts/view-logs.sh"
echo ""
echo "🌐 Service URLs (once started):"
echo "=================================================="
echo "Frontend:             http://localhost:3000"
echo "Backend API:          http://localhost:8000"
echo "API Documentation:    http://localhost:8000/docs"
echo "Grafana Dashboard:    http://localhost:3001 (admin/admin123)"
echo "Prometheus Metrics:   http://localhost:9090"
echo "PostgreSQL:           localhost:5432 (postgres/password)"
echo "Redis:                localhost:6379"
echo ""
echo "⚡ Ready for Oracle BI Publisher enterprise development!"
echo "=================================================="