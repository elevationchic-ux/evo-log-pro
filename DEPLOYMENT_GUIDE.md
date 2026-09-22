# Guide de Déploiement EVO-LOG

## 📋 Prérequis

- Compte GitHub
- Compte Vercel (pour le frontend)
- Compte Railway (pour le backend)
- Compte Supabase ou Railway PostgreSQL (pour la base de données)
- Compte Redis Cloud ou Railway Redis (pour le cache)

---

## 🚀 Déploiement Backend sur Railway

### 1. Connecter GitHub à Railway

1. Allez sur [railway.app](https://railway.app)
2. Cliquez sur "New Project" → "Deploy from GitHub repo"
3. Connectez votre compte GitHub
4. Sélectionnez le dépôt `elevationchic-ux/evo-log-pro`
5. Sélectionnez le dossier `evo-log-backend`

### 2. Variables d'Environnement

Dans Railway, ajoutez ces variables d'environnement dans le backend :

```bash
# Base de données
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis
REDIS_URL=redis://host:port

# Sécurité
SECRET_KEY=votre-secret-key-unique-production
JWT_SECRET=votre-jwt-secret-unique-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS
ALLOWED_ORIGINS=https://votre-vercel-domain.vercel.app

# PostgreSQL Pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
POOL_RECYCLE=1800
POOL_PRE_PING=True

# Monitoring
SENTRY_DSN=votre-sentry-dsn-optionnel
```

### 3. Services à Créer

#### PostgreSQL Database
1. Dans Railway, cliquez sur "New Service" → "Database" → "PostgreSQL"
2. Railway va créer et connecter automatiquement la base de données
3. Copiez le `DATABASE_URL` dans les variables d'environnement du backend

#### Redis
1. Cliquez sur "New Service" → "Add Service" → "Redis"
2. Copiez le `REDIS_URL` dans les variables d'environnement du backend

### 4. Exécuter les Migrations

Une fois le backend déployé, vous devez exécuter les migrations :

1. Ouvrez le backend service dans Railway
2. Cliquez sur "Console" (icône terminal)
3. Exécutez :
```bash
alembic upgrade head
```

4. Exécutez le seeder (optionnel pour les données de test) :
```bash
python scripts/seed_data.py
```

### 5. Health Check

Le backend expose un endpoint `/health` pour les health checks.

---

## 🎨 Déploiement Frontend sur Vercel

### 1. Connecter GitHub à Vercel

1. Allez sur [vercel.com](https://vercel.com)
2. Cliquez sur "Add New..." → "Project"
3. Importez le dépôt `elevationchic-ux/evo-log-pro`
4. Sélectionnez le dossier `evo-log-frontend`

### 2. Configuration du Projet

Dans les settings du projet Vercel :

**Root Directory** : `evo-log-frontend`

**Framework Preset** : Next.js

**Environment Variables** :
```bash
NEXT_PUBLIC_API_URL=https://votre-backend-domain.railway.app
```

### 3. Build Settings

Vercel détectera automatiquement Next.js. Les commandes sont :

- **Build Command** : `npm run build`
- **Output Directory** : `.next`
- **Install Command** : `npm install`

### 4. Domain Custom (Optionnel)

1. Dans Settings → Domains
2. Ajoutez votre domaine personnalisé
3. Configurez le DNS selon les instructions Vercel

---

## 🔗 Configuration API Client

Dans le frontend, assurez-vous que `src/lib/api-client.ts` utilise correctement la variable d'environnement :

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

---

## 📊 Monitoring et Logs

### Railway (Backend)

- **Logs** : Cliquez sur le service backend → "Logs"
- **Metrics** : Cliquez sur "Metrics" pour CPU, mémoire, réseau
- **Health Check** : Accédez à `https://votre-backend.railway.app/health`

### Vercel (Frontend)

- **Logs** : Cliquez sur le projet → "Functions" → "_app" → "Logs"
- **Analytics** : Cliquez sur "Analytics" pour les visites et performance

---

## 🔐 Sécurité Production

Avant le déploiement en production :

1. **Changez tous les secrets par défaut**
   - `SECRET_KEY`
   - `JWT_SECRET`
   - Mots de passe des utilisateurs par défaut

2. **Configurez CORS correctement**
   - Ajoutez uniquement les domaines autorisés
   - Activez HTTPS obligatoire

3. **Activez HTTPS**
   - Railway le fait automatiquement
   - Vercel le fait automatiquement

4. **Configurez rate limiting**
   - Déjà implémenté avec SlowAPI
   - Ajustez les limites selon vos besoins

---

## 📝 Checklist Déploiement

- [ ] Backend Railway créé
- [ ] PostgreSQL Railway créé
- [ ] Redis Railway créé
- [ ] Variables d'environnement configurées
- [ ] Migrations exécutées (`alembic upgrade head`)
- [ ] Seeder exécuté (optionnel)
- [ ] Frontend Vercel créé
- [ ] `NEXT_PUBLIC_API_URL` configuré
- [ ] Build Vercel réussi
- [ ] Test connexion frontend → backend
- [ ] Test authentification
- [ ] Test multi-tenant isolation
- [ ] Monitoring configuré

---

## 🆘 Dépannage

### Erreur de connexion Frontend → Backend

1. Vérifiez que `NEXT_PUBLIC_API_URL` est correct
2. Vérifiez les CORS dans le backend
3. Vérifiez que le backend est accessible (testez `/api/docs`)

### Erreur de connexion Backend → PostgreSQL

1. Vérifiez `DATABASE_URL`
2. Vérifiez que PostgreSQL est actif dans Railway
3. Vérifiez les migrations sont exécutées

### Erreur de connexion Backend → Redis

1. Vérifiez `REDIS_URL`
2. Vérifiez que Redis est actif dans Railway
3. Vérifiez que le cache fonctionne

### Build Vercel échoue

1. Vérifiez les logs de build dans Vercel
2. Vérifiez que `package.json` est correct
3. Vérifiez que les dépendances sont installables

---

## 📚 Ressources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
