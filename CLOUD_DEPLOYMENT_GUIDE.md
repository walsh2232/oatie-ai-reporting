# Oatie AI Platform - Cloud Deployment Guide

## 🌐 Cloud Hosting Options for GitHub Pro Users

Since you have GitHub Pro, you have access to several excellent cloud hosting options that don't require Docker on your local machine.

## 🚀 Option 1: GitHub Codespaces (RECOMMENDED)

**Why This is Perfect:**
- ✅ **FREE** with GitHub Pro (180 core hours/month)
- ✅ Full Docker support in the cloud
- ✅ VS Code environment in your browser
- ✅ Direct access to your repository
- ✅ Can run the complete stack

**Setup Steps:**
1. Go to https://github.com/walsh2232/oatie-ai-reporting
2. Click the green **"Code"** button
3. Click the **"Codespaces"** tab
4. Click **"Create codespace on main"**
5. Wait 2-3 minutes for the environment to initialize
6. In the Codespaces terminal, run:
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```
7. Use port forwarding to access the application

**Access Points in Codespaces:**
- Frontend: Forward port 3000
- Backend API: Forward port 8000
- Prometheus: Forward port 9090
- Grafana: Forward port 3001

## ⚡ Option 2: Cloud Platform Deployment

### A. Frontend Deployment (Vercel - FREE)

**Setup:**
1. Go to https://vercel.com
2. Sign in with GitHub
3. Import the `oatie-ai-reporting` repository
4. Configure build settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

**Environment Variables for Vercel:**
```
VITE_API_URL=https://your-backend-url.railway.app
VITE_ORACLE_BI_ENABLED=true
```

### B. Backend Deployment (Railway - $5/month, free trial)

**Setup:**
1. Go to https://railway.app
2. Sign in with GitHub
3. Create new project from GitHub repo
4. Select `backend` folder as root
5. Railway will auto-detect Python and deploy

**Environment Variables for Railway:**
```
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://user:pass@host:port
SECRET_KEY=your_secret_key
ORACLE_BI_ENABLED=true
ORACLE_BI_URLS=your_oracle_servers
```

### C. Alternative: Render (FREE tier available)

**Frontend on Render:**
- Static site deployment
- GitHub integration
- Automatic deployments

**Backend on Render:**
- Web service deployment
- PostgreSQL database included
- Redis add-on available

## 🗄️ Option 3: Database Services

### Managed PostgreSQL:
- **Railway:** Included with backend deployment
- **Render:** Free PostgreSQL addon
- **Supabase:** Free tier with 500MB
- **PlanetScale:** Free tier available

### Managed Redis:
- **Railway:** Redis addon ($1/month)
- **Render:** Redis addon available
- **Upstash:** Free tier with 10K requests/day

## 🔧 Quick Start with GitHub Codespaces

**Immediate Steps:**
1. Visit: https://github.com/walsh2232/oatie-ai-reporting
2. Click **Code** → **Codespaces** → **Create codespace**
3. Once loaded, run these commands:

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

cd ../frontend
npm install

# Start the development servers
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

cd ../frontend
npm run dev -- --host 0.0.0.0 --port 3000
```

4. Forward ports 3000 and 8000 in Codespaces
5. Access your application!

## 🏗️ Production Deployment Architecture

```
┌─────────────────────────────────────────┐
│           CLOUD ARCHITECTURE            │
├─────────────────────────────────────────┤
│  Frontend (Vercel/Netlify)             │
│  • React + TypeScript                  │
│  • Global CDN                          │
│  • Automatic HTTPS                     │
│  • Custom domain support               │
├─────────────────────────────────────────┤
│  Backend API (Railway/Render)          │
│  • FastAPI application                 │
│  • Oracle BI Publisher integration     │
│  • Auto-scaling                        │
│  • Health monitoring                   │
├─────────────────────────────────────────┤
│  Database Layer                        │
│  • PostgreSQL (managed service)        │
│  • Redis (managed cache)               │
│  • Automatic backups                   │
│  • High availability                   │
└─────────────────────────────────────────┘
```

## 💰 Cost Breakdown

**FREE Options:**
- GitHub Codespaces (180 hours/month with Pro)
- Vercel (frontend hosting)
- Netlify (frontend hosting)
- Render (free tier for backend)

**Low-Cost Options:**
- Railway: $5/month (backend + database)
- Render Pro: $7/month (better performance)

**Total Monthly Cost: $0-$5** for full production deployment!

## 🎯 Recommended Path

1. **Start with GitHub Codespaces** for immediate testing and development
2. **Deploy frontend to Vercel** for production (free)
3. **Deploy backend to Railway** for production ($5/month)
4. **Use managed databases** (included with Railway)

This gives you a complete, scalable, enterprise-ready deployment without needing Docker on your local machine!

## 🚀 Ready to Deploy?

Choose your path:
- **Quick Start:** GitHub Codespaces (available now)
- **Production:** Vercel + Railway deployment
- **Enterprise:** Contact for advanced cloud architecture

Your Oatie AI Platform is ready for the cloud! 🌟
