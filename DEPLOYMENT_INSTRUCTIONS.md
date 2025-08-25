# Oatie AI Platform - Cloud Deployment Instructions

## Generated Deployment Configurations

The following files have been created for cloud deployment:

### Configuration Files
- `vercel.json` - Vercel frontend deployment
- `railway.json` - Railway backend deployment  
- `render.yaml` - Render full-stack deployment
- `.devcontainer/devcontainer.json` - GitHub Codespaces
- `.github/workflows/deploy.yml` - Automated CI/CD
- `docker-compose.simple.yml` - Simplified local Docker

## Quick Start Options

### Option 1: GitHub Codespaces (Immediate - FREE with Pro)
1. Go to your GitHub repository
2. Click "Code" -> "Codespaces" -> "Create codespace"
3. Wait for environment to load (2-3 minutes)
4. Run: `docker-compose -f docker-compose.simple.yml up -d`
5. Access your app at the forwarded ports

### Option 2: Vercel + Railway (Production)
1. **Frontend (Vercel):**
   - Connect GitHub repo to Vercel
   - Deploy automatically using `vercel.json`
   - FREE tier available
   
2. **Backend (Railway):**
   - Connect GitHub repo to Railway
   - Deploy automatically using `railway.json`
   - $5/month for backend

### Option 3: Render (Full-Stack)
1. Connect GitHub repo to Render
2. Deploy using `render.yaml` configuration
3. Automatic PostgreSQL database provisioning
4. FREE tier available

## Environment Variables Needed

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

## Cost Summary
- **GitHub Codespaces**: FREE (180 hours/month with Pro)
- **Vercel Frontend**: FREE (hobby tier)
- **Railway Backend**: $5/month
- **Render**: FREE tier available
- **Total Cost**: $0-5/month

## Ready to Deploy!

Your Oatie AI Platform with Oracle BI Publisher integration is fully configured for cloud deployment. Choose your preferred option above and follow the setup instructions.

All enterprise features are included:
- Oracle Fusion Reporting Integration
- Advanced SQL Agent with AI
- Real-time Analytics Dashboard
- Enterprise Security (RBAC/MFA/ABAC)
- Comprehensive Monitoring Stack

**Recommended Quick Start**: Use GitHub Codespaces for immediate testing, then deploy to Vercel + Railway for production.
