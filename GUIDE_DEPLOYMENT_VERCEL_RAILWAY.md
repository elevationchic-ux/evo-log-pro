# EVO-LOG SaaS - Vercel & Railway Deployment Guide

## 🚀 Vercel (Frontend) Deployment

### 1. Configuration Vercel
Create `vercel.json` in project root:
```json
{
  "buildCommand": "cd evo-log-frontend && npm run build",
  "outputDirectory": "evo-log-frontend/.next",
  "framework": "nextjs",
  "installCommand": "cd evo-log-frontend && npm install"
}
```

### 2. Environment Variables Vercel
- `NEXT_PUBLIC_API_URL` - Railway backend URL
- `NEXTAUTH_SECRET` - Secret key for NextAuth

### 3. Deploy Command
```bash
vercel --prod
```

## 🚀 Railway (Backend) Deployment

### 1. Configuration Railway
- Create PostgreSQL service
- Create Redis service
- Add backend service

### 2. Environment Variables Railway
Use `.railway.env` file format:
```
DATABASE_URL=${{POSTGRES_URL}}
REDIS_URL=${{REDIS_URL}}
SECRET_KEY=${{SECRET_KEY}}
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

### 3. Deploy Command
```bash
railway up
```

## 🔧 Prerequisites for Production

### Backend
- ✅ All imports corrected (models/__init__.py)
- ✅ Dependencies restored to production versions
- ✅ PostgreSQL supported (psycopg2-binary)
- ✅ Redis supported
- ✅ Sentry, SlowAPI, Prometheus enabled
- ✅ Railway environment variables configured

### Frontend
- ✅ SWC Minify re-enabled (works on Linux)
- ✅ Vercel configuration created
- ✅ Environment variables defined
- ✅ Build command configured

## 📋 Railway-Specific Changes

### 1. Railway Service Type
Set service type to "Python" with:
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. Database Connection
Railway provides:
- `${{POSTGRES_URL}}` - PostgreSQL connection string
- `${{REDIS_URL}}` - Redis connection string

### 3. Secret Management
Generate secure keys:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## 🎯 Vercel-Specific Changes

### 1. Next.js Configuration
SWC Minify works on Vercel (Linux) without issues.

### 2. Environment Variables
- Set `NEXT_PUBLIC_API_URL` to Railway backend URL
- Set `NEXTAUTH_SECRET` to secure random string

### 3. Build Settings
Vercel automatically detects Next.js and uses:
- Build: `npm run build`
- Output: `.next`
- Start: `npm start`

## ✅ Corrections Applied

### Backend
1. **Models imports** - Removed duplicate imports and missing modules
2. **Dependencies** - Restored full production versions
3. **Optional imports** - Removed, using full functionality
4. **CORS format** - Fixed for Pydantic settings
5. **Railway env** - Configured for Railway variable substitution

### Frontend
1. **SWC Minify** - Re-enabled for Vercel Linux environment
2. **Vercel config** - Created for proper deployment
3. **Environment** - Configured for Railway backend

## 🚀 Deployment Steps

### 1. Deploy Backend to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Add backend service
railway add

# Deploy
railway up
```

### 2. Deploy Frontend to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### 3. Configure CORS
After Railway deployment:
1. Get Railway backend URL
2. Update Vercel environment variable `NEXT_PUBLIC_API_URL`
3. Update Railway CORS with Vercel frontend URL

## 📋 Checklist Production

### Backend (Railway)
- [ ] PostgreSQL service created
- [ ] Redis service created
- [ ] Backend service configured
- [ ] Environment variables set
- [ ] Secrets generated
- [ ] Railway deployment successful
- [ ] API accessible

### Frontend (Vercel)
- [ ] Vercel project created
- [ ] Environment variables set
- [ ] Railway backend URL configured
- [ ] Vercel deployment successful
- [ ] Frontend accessible
- [ ] API connection working

---

**Date:** 18 janvier 2026
**Status:** Configuration ready for Vercel + Railway deployment
