#!/usr/bin/env python3
"""
Oatie AI Platform - Cloud Deployment Helper
Generates deployment configurations for various cloud platforms
"""

import json
import os
from pathlib import Path

def create_vercel_config():
    """Create Vercel deployment configuration"""
    config = {
        "framework": "vite",
        "buildCommand": "cd frontend && npm run build",
        "outputDirectory": "frontend/dist",
        "installCommand": "cd frontend && npm install",
        "env": {
            "VITE_API_URL": "https://oatie-backend.railway.app",
            "VITE_ORACLE_BI_ENABLED": "true"
        },
        "headers": [
            {
                "source": "/api/(.*)",
                "headers": [
                    {
                        "key": "Access-Control-Allow-Origin",
                        "value": "*"
                    }
                ]
            }
        ]
    }
    
    with open("vercel.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created vercel.json for frontend deployment")

def create_railway_config():
    """Create Railway deployment configuration"""
    config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health"
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Create Railway Procfile
    with open("Procfile", "w") as f:
        f.write("web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT\n")
    
    print("✅ Created railway.json and Procfile for backend deployment")

def create_render_config():
    """Create Render deployment configuration"""
    config = {
        "services": [
            {
                "type": "web",
                "name": "oatie-backend",
                "env": "python",
                "buildCommand": "cd backend && pip install -r requirements.txt",
                "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
                "healthCheckPath": "/health"
            },
            {
                "type": "static",
                "name": "oatie-frontend", 
                "buildCommand": "cd frontend && npm install && npm run build",
                "staticPublishPath": "frontend/dist"
            }
        ],
        "databases": [
            {
                "name": "oatie-postgres",
                "databaseName": "oatie_production",
                "user": "oatie_user"
            }
        ]
    }
    
    with open("render.yaml", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created render.yaml for full-stack deployment")

def create_github_actions_deploy():
    """Create GitHub Actions workflow for cloud deployment"""
    workflow = """name: Deploy to Cloud

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: cd frontend && npm ci
    
    - name: Build frontend
      run: cd frontend && npm run build
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        working-directory: ./frontend

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: cd backend && pip install -r requirements.txt
    
    - name: Deploy to Railway
      uses: railway-deploy@v1
      with:
        railway-token: ${{ secrets.RAILWAY_TOKEN }}
        service: oatie-backend
"""

    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/deploy.yml", "w") as f:
        f.write(workflow)
    
    print("✅ Created GitHub Actions workflow for automated deployment")

def create_codespaces_config():
    """Create GitHub Codespaces configuration"""
    config = {
        "name": "Oatie AI Platform",
        "image": "mcr.microsoft.com/devcontainers/universal:2",
        "features": {
            "ghcr.io/devcontainers/features/docker-in-docker:2": {},
            "ghcr.io/devcontainers/features/node:1": {
                "version": "18"
            },
            "ghcr.io/devcontainers/features/python:1": {
                "version": "3.11"
            }
        },
        "forwardPorts": [3000, 8000, 9090, 3001],
        "postCreateCommand": "cd backend && pip install -r requirements.txt && cd ../frontend && npm install",
        "customizations": {
            "vscode": {
                "extensions": [
                    "ms-python.python",
                    "bradlc.vscode-tailwindcss",
                    "esbenp.prettier-vscode"
                ]
            }
        }
    }
    
    os.makedirs(".devcontainer", exist_ok=True)
    with open(".devcontainer/devcontainer.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created Codespaces configuration")

def create_docker_compose_simple():
    """Create simplified Docker Compose for cloud deployment"""
    compose = """version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/oatie
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: oatie
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
"""

    with open("docker-compose.simple.yml", "w") as f:
        f.write(compose)
    
    print("✅ Created simplified Docker Compose configuration")

def generate_deployment_instructions():
    """Generate deployment instructions"""
    instructions = """
# 🚀 Oatie AI Platform - Cloud Deployment Instructions

## Generated Deployment Configurations

The following files have been created for cloud deployment:

### 📁 Configuration Files
- `vercel.json` - Vercel frontend deployment
- `railway.json` - Railway backend deployment  
- `render.yaml` - Render full-stack deployment
- `.devcontainer/devcontainer.json` - GitHub Codespaces
- `.github/workflows/deploy.yml` - Automated CI/CD
- `docker-compose.simple.yml` - Simplified local Docker

## 🌐 Quick Start Options

### Option 1: GitHub Codespaces (Immediate)
1. Go to your GitHub repository
2. Click "Code" → "Codespaces" → "Create codespace"
3. Wait for environment to load
4. Run: `docker-compose -f docker-compose.simple.yml up -d`

### Option 2: Vercel + Railway (Production)
1. **Frontend (Vercel):**
   - Connect GitHub repo to Vercel
   - Deploy automatically using `vercel.json`
   
2. **Backend (Railway):**
   - Connect GitHub repo to Railway
   - Deploy automatically using `railway.json`

### Option 3: Render (Full-Stack)
1. Connect GitHub repo to Render
2. Deploy using `render.yaml` configuration
3. Automatic PostgreSQL database provisioning

## 🔧 Environment Variables Needed

### Frontend (Vercel/Netlify)
```
VITE_API_URL=https://your-backend-url.com
VITE_ORACLE_BI_ENABLED=true
```

### Backend (Railway/Render)
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your_secret_key
ORACLE_BI_ENABLED=true
ORACLE_BI_URLS=your_oracle_servers
```

## 📊 Cost Estimates
- GitHub Codespaces: FREE (180 hours/month with Pro)
- Vercel: FREE (hobby tier)
- Railway: $5/month
- Render: FREE tier available

Your Oatie AI Platform is ready for cloud deployment! 🌟
"""

    with open("DEPLOYMENT_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("✅ Created deployment instructions")

def main():
    """Generate all cloud deployment configurations"""
    print("🚀 Generating Cloud Deployment Configurations for Oatie AI Platform")
    print("=" * 70)
    print()
    
    try:
        create_vercel_config()
        create_railway_config()
        create_render_config()
        create_github_actions_deploy()
        create_codespaces_config()
        create_docker_compose_simple()
        generate_deployment_instructions()
        
        print()
        print("✅ All cloud deployment configurations generated successfully!")
        print()
        print("🎯 Next Steps:")
        print("1. Choose your preferred cloud platform")
        print("2. Follow the instructions in DEPLOYMENT_INSTRUCTIONS.md")
        print("3. Deploy your Oatie AI Platform to the cloud!")
        print()
        print("🌟 Your enterprise Oracle Fusion reporting platform is ready!")
        
    except Exception as e:
        print(f"❌ Error generating configurations: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
