@echo off
REM Oatie AI Reporting Platform - Production Startup Script (Windows)
REM ==================================================================

echo.
echo 🚀 Starting Oatie AI Reporting Platform - Production Environment
echo ================================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Set production environment variables
set ENVIRONMENT=production
set BUILD_DATE=%date:~10,4%-%date:~4,2%-%date:~7,2%T%time:~0,2%:%time:~3,2%:%time:~6,2%Z
if "%VERSION%"=="" set VERSION=3.0.0

REM Load environment variables from .env.production if it exists
if exist .env.production (
    echo 📋 Loading production environment variables...
    for /f "usebackq delims=" %%a in (".env.production") do (
        for /f "tokens=1,2 delims==" %%b in ("%%a") do (
            if not "%%b"=="" if not "%%c"=="" set "%%b=%%c"
        )
    )
) else (
    echo ⚠️  No .env.production file found. Using default values.
)

REM Validate critical environment variables
echo 🔍 Validating environment configuration...

if "%SECRET_KEY%"=="" (
    echo ❌ SECRET_KEY must be set in production
    exit /b 1
)
if "%SECRET_KEY%"=="your-super-secret-production-key-change-me" (
    echo ❌ SECRET_KEY must be changed from default value
    exit /b 1
)

if "%JWT_SECRET_KEY%"=="" (
    echo ❌ JWT_SECRET_KEY must be set in production
    exit /b 1
)
if "%JWT_SECRET_KEY%"=="your-jwt-secret-production-key-change-me" (
    echo ❌ JWT_SECRET_KEY must be changed from default value
    exit /b 1
)

echo ✅ Environment validation passed

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist backups mkdir backups
if not exist infrastructure mkdir infrastructure
if not exist infrastructure\nginx mkdir infrastructure\nginx
if not exist infrastructure\postgres mkdir infrastructure\postgres
if not exist infrastructure\redis mkdir infrastructure\redis
if not exist infrastructure\prometheus mkdir infrastructure\prometheus
if not exist infrastructure\grafana mkdir infrastructure\grafana

REM Pull latest images
echo ⬇️  Pulling latest Docker images...
docker-compose -f docker-compose.production.yml pull

REM Build services
echo 🔨 Building services...
docker-compose -f docker-compose.production.yml build --no-cache

REM Start services
echo 🚀 Starting production services...
docker-compose -f docker-compose.production.yml up -d

REM Wait for services to be healthy
echo 🏥 Waiting for services to be healthy...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...

REM Check database
docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U oatie_user -d oatie_production >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Database is healthy
) else (
    echo ❌ Database health check failed
)

REM Check Redis
docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping | findstr "PONG" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis is healthy
) else (
    echo ❌ Redis health check failed
)

REM Check backend API
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8000
curl -f http://localhost:%BACKEND_PORT%/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is healthy
) else (
    echo ❌ Backend API health check failed
)

REM Check frontend
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=3000
curl -f http://localhost:%FRONTEND_PORT%/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is healthy
) else (
    echo ❌ Frontend health check failed
)

echo.
echo 🎉 Oatie AI Reporting Platform is now running in production!
echo ================================================================
echo 📊 Access Points:
echo • Frontend:    http://localhost:%FRONTEND_PORT%
echo • Backend API: http://localhost:%BACKEND_PORT%
echo • API Docs:    http://localhost:%BACKEND_PORT%/docs
echo • Health:      http://localhost:%BACKEND_PORT%/health
echo • Metrics:     http://localhost:%BACKEND_PORT%/metrics
if not "%PROMETHEUS_PORT%"=="" echo • Prometheus:  http://localhost:%PROMETHEUS_PORT%
if not "%GRAFANA_PORT%"=="" echo • Grafana:     http://localhost:%GRAFANA_PORT%
echo.
echo 📋 To view logs: docker-compose -f docker-compose.production.yml logs -f
echo 🛑 To stop: docker-compose -f docker-compose.production.yml down
echo.
pause
