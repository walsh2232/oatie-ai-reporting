#!/bin/bash
# Oatie AI Platform - Codespaces Setup Script
# This script runs after the container is created to set up the development environment

set -e

echo "🚀 Setting up Oatie AI Platform in GitHub Codespaces..."

# Create necessary directories
mkdir -p logs
mkdir -p uploads
mkdir -p backups

# Set up backend environment
echo "📦 Setting up Python backend environment..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "✅ Backend environment setup complete"

# Set up frontend environment  
echo "📦 Setting up Node.js frontend environment..."
cd ../frontend

# Install dependencies
npm install

echo "✅ Frontend environment setup complete"

# Copy environment files
echo "🔧 Setting up environment configuration..."
cd ..

# Copy development environment file
if [ ! -f ".env" ]; then
    cp .env.development .env
    echo "✅ Development environment file created"
fi

# Initialize database migrations
echo "🗄️ Setting up database..."
cd backend
source .venv/bin/activate

# Run database migrations
alembic upgrade head || echo "⚠️  Database migrations will run on first startup"

echo "✅ Database setup complete"

# Set permissions
echo "🔐 Setting up permissions..."
cd ..
chmod +x .devcontainer/start-services.sh
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x start_production.sh 2>/dev/null || true

echo "🎉 Oatie AI Platform setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Services will start automatically"
echo "2. Backend API will be available at http://localhost:8000"
echo "3. Frontend will be available at http://localhost:5173"
echo "4. View the README.md for more information"
echo ""
echo "🔗 Useful URLs:"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Frontend App: http://localhost:5173"
echo ""
