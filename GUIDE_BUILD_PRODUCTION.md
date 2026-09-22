# GUIDE BUILD PRODUCTION - EVO-LOG SaaS

## 📋 Prérequis Système

### Backend (Python/FastAPI)
- Python 3.9+
- pip ou poetry
- PostgreSQL 12+ (ou SQLite pour dev)
- Redis (optionnel, pour cache/Celery)

### Frontend (Next.js/React)
- Node.js 18+
- npm ou yarn
- TypeScript 5+

---

## 🔧 Build Backend

### 1. Installation Dépendances
```bash
cd evo-log-backend
pip install -r requirements.txt
```

### 2. Configuration Environment
```bash
# Copier fichier .env.example vers .env
cp .env.example .env

# Éditer .env avec vos valeurs de production
DATABASE_URL=postgresql://user:password@localhost:5432/evo_log
SECRET_KEY=votre_secret_key_production
REDIS_URL=redis://localhost:6379/0
SENTRY_DSN=votre_sentry_dsn
```

### 3. Exécuter Migrations
```bash
# Créer toutes les migrations
alembic upgrade head
```

### 4. Seed Données (Optionnel)
```bash
python scripts/seed_data.py
```

### 5. Vérification Syntaxe
```bash
python -m py_compile app/main.py
python -m py_compile app/models/*.py
python -m py_compile app/services/*.py
```

### 6. Tests Unitaires
```bash
pytest tests/ -v
```

### 7. Build Production (Optionnel pour Docker)
```bash
# Si vous utilisez gunicorn
pip install gunicorn uvicorn
```

### 8. Démarrage Production
```bash
# Avec uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Avec gunicorn (recommandé production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🎨 Build Frontend

### 1. Installation Dépendances
```bash
cd evo-log-frontend
npm install
```

### 2. Configuration Environment
```bash
# Créer fichier .env.local
NEXT_PUBLIC_API_URL=https://votre-api-domain.com
NEXTAUTH_SECRET=votre_secret_nextauth
```

### 3. Vérification TypeScript
```bash
npm run lint
```

### 4. Build Production
```bash
npm run build
```

### 5. Vérification Build
- Le build doit générer le dossier `.next`
- Vérifier qu'il n'y a pas d'erreurs TypeScript
- Vérifier qu'il y a 153+ pages générées

### 6. Start Production
```bash
npm start
```

---

## 🐳 Docker Build (Recommandé)

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN alembic upgrade head

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./

RUN npm ci --production

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: evo_log
      POSTGRES_USER: evo_log
      POSTGRES_PASSWORD: evo_log_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: ./evo-log-backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://evo_log:evo_log_password@postgres:5432/evo_log
      REDIS_URL: redis://redis:6379/0

  frontend:
    build: ./evo-log-frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000

volumes:
  postgres_data:
```

### Build et Run Docker
```bash
docker-compose build
docker-compose up -d
```

---

## ✅ Checklist Production

### Backend
- [ ] Python 3.9+ installé
- [ ] Dépendances installées (requirements.txt)
- [ ] .env configuré avec valeurs production
- [ ] PostgreSQL configuré et accessible
- [ ] Migrations exécutées (alembic upgrade head)
- [ ] Données seedées (optionnel)
- [ ] Tests passent (pytest)
- [ ] API fonctionne sur port 8000
- [ ] Health check accessible: `GET /api/health`

### Frontend
- [ ] Node.js 18+ installé
- [ ] Dépendances installées (npm install)
- [ ] .env.local configuré
- [ ] TypeScript lint pass (npm run lint)
- [ ] Build réussi (npm run build)
- [ ] Build génère dossier .next
- [ ] App fonctionne sur port 3000
- [ ] Navigation fonctionne
- [ ] Pages Cameroun/CEMAC accessibles

### Infrastructure
- [ ] Domaine configuré
- [ ] SSL/TLS configuré (HTTPS)
- [ ] Firewall configuré
- [ ] Backup configuré
- [ ] Monitoring configuré (Sentry, Prometheus)
- [ ] Logs configurés

---

## 🚀 Déployment Railway (Optionnel)

### Backend Railway
```bash
# Créer service PostgreSQL sur Railway
# Créer service Redis sur Railway

# Deploy backend
railway up
```

### Frontend Vercel
```bash
# Connecter repo GitHub
# Configurer variables d'environnement
# Deploy automatique
```

---

## 🔍 Vérification Post-Deployment

### Backend
```bash
# Health check
curl https://votre-api.com/api/health

# OpenAPI docs
curl https://votre-api.com/api/docs
```

### Frontend
```bash
# Homepage
curl https://votre-domain.com

# Page Cameroun
curl https://votre-domain.com/integration-cameroun
```

---

## 📝 Variables Environment Production

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=votre_secret_key_aleatoire_32_chars_minimum
REDIS_URL=redis://host:6379/0
SENTRY_DSN=https://sentry.io/your-dsn
MINIO_ENABLED=true
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_DOCUMENTS=documents
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://votre-api.com
NEXTAUTH_SECRET=votre_secret_nextauth_32_chars_minimum
```

---

**Date:** 18 janvier 2026  
**Statut:** Guide de build ; exécution de staging et validation d'infrastructure encore requises
