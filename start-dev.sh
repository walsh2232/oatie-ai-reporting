#!/bin/bash
"""
Development startup script to run both backend and frontend
"""

echo "🚀 Starting Oatie AI Reporting Platform - Full Stack"
echo "=================================================="

# Start backend
echo "📡 Starting Backend API Server (Port 8000)..."
cd /workspaces/oatie-ai-reporting
source venv/bin/activate
uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend
echo "🌐 Starting Frontend Development Server (Port 5173)..."
cd /workspaces/oatie-ai-reporting/frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are starting up!"
echo ""
echo "📱 Access your application at:"
echo "   • Frontend (React): http://localhost:5173"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "⚡ Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
