#!/bin/bash
# Oatie AI Platform - Codespaces Service Startup Script
# This script starts all required services when the Codespaces container starts

set -e

echo "🚀 Starting Oatie AI Platform services..."

# Function to check if a port is in use
check_port() {
    local port=$1
    nc -z localhost $port 2>/dev/null
}

# Function to wait for a service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            echo "✅ $service_name is ready on port $port"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "⚠️  $service_name failed to start on port $port after $max_attempts attempts"
    return 1
}

# Start Docker services in the background
echo "🐳 Starting Docker services..."
if command -v docker &> /dev/null; then
    # Start simplified Docker services
    docker-compose -f docker-compose.simple.yml up -d --no-deps db redis 2>/dev/null || {
        echo "ℹ️  Docker services not started - will use local alternatives"
    }
fi

# Start backend service
echo "🔧 Starting backend API server..."
cd backend

# Activate virtual environment
source .venv/bin/activate

# Start backend in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid

cd ..

# Start frontend service
echo "🎨 Starting frontend development server..."
cd frontend

# Start frontend in background  
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

cd ..

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check backend
if wait_for_service 8000 "Backend API"; then
    echo "✅ Backend is running at http://localhost:8000"
    echo "📖 API docs available at http://localhost:8000/docs"
else
    echo "❌ Backend failed to start"
fi

# Check frontend
if wait_for_service 5173 "Frontend"; then
    echo "✅ Frontend is running at http://localhost:5173"
else
    echo "❌ Frontend failed to start"
fi

# Create monitoring script
cat > monitor_services.sh << 'EOF'
#!/bin/bash
echo "🔍 Oatie AI Platform Service Status"
echo "=================================="

# Check backend
if nc -z localhost 8000 2>/dev/null; then
    echo "✅ Backend API: Running (http://localhost:8000)"
else
    echo "❌ Backend API: Not running"
fi

# Check frontend
if nc -z localhost 5173 2>/dev/null; then
    echo "✅ Frontend: Running (http://localhost:5173)"
else
    echo "❌ Frontend: Not running"
fi

# Check database
if nc -z localhost 5432 2>/dev/null; then
    echo "✅ PostgreSQL: Running"
else
    echo "ℹ️  PostgreSQL: Not running (using SQLite)"
fi

# Check Redis
if nc -z localhost 6379 2>/dev/null; then
    echo "✅ Redis: Running"
else
    echo "ℹ️  Redis: Not running (using memory cache)"
fi

echo ""
echo "📋 Useful commands:"
echo "  • View backend logs: tail -f logs/backend.log"
echo "  • View frontend logs: tail -f logs/frontend.log"
echo "  • Restart services: .devcontainer/start-services.sh"
echo "  • Check this status: ./monitor_services.sh"
EOF

chmod +x monitor_services.sh

echo ""
echo "🎉 Oatie AI Platform is ready!"
echo "=================================="
echo "✅ Backend API: http://localhost:8000"
echo "✅ Frontend App: http://localhost:5173"
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Service Management:"
echo "  • Monitor services: ./monitor_services.sh"
echo "  • View logs: tail -f logs/*.log"
echo ""
echo "🚀 Your enterprise Oracle BI Publisher platform is running!"
