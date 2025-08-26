#!/usr/bin/env python3
"""
Development server startup script
Gracefully handles missing dependencies and provides helpful error messages
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables for development
os.environ.setdefault("PYTHONPATH", str(project_root))


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []

    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")

    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")

    try:
        import structlog
    except ImportError:
        missing_deps.append("structlog")

    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Install with: pip install -r requirements-dev.txt")
        return False

    return True


def run_server():
    """Run the FastAPI development server"""
    if not check_dependencies():
        sys.exit(1)

    print("🚀 Starting Oatie AI Reporting Platform...")
    print("📍 Oracle BI Publisher Integration Platform")
    print("🔧 Development Mode")
    print()

    try:
        import uvicorn

        # Configuration for development
        config = {
            "app": "backend.main:app",
            "host": "0.0.0.0",
            "port": 8000,
            "reload": True,
            "reload_dirs": ["backend", "src"],
            "log_level": "info",
            "access_log": True,
        }

        print("📱 Server will be available at:")
        print("   • API: http://localhost:8000")
        print("   • Interactive Docs: http://localhost:8000/docs")
        print("   • Alternative Docs: http://localhost:8000/redoc")
        print("   • Health Check: http://localhost:8000/health")
        print()
        print("🔄 Hot reload enabled - files will be watched for changes")
        print("⚡ Press Ctrl+C to stop the server")
        print()

        uvicorn.run(**config)

    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Check the logs above for more details")
        sys.exit(1)


if __name__ == "__main__":
    run_server()
