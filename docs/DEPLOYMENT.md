# Guide de Déploiement Production & Local — EVO-LOG SaaS

Ce document contient la procédure officielle de déploiement pour les environnements de **Développement Local**, de **Production Railway (Backend FastAPI)** et de **Production Vercel (Frontend Next.js PWA)**.

---

## 🐋 1. Déploiement Local (Docker Compose)

Le fichier [`docker-compose.yml`](file:///d:/Projet/ERP/EVO-LOG/docker-compose.yml) orchestre la stack locale complète :

```bash
docker-compose up -d --build
```

### Services Exposés :
- **Frontend Next.js** : `http://localhost:3000`
- **Backend FastAPI** : `http://localhost:8000`
- **Swagger Documentation** : `http://localhost:8000/api/docs`
- **PostgreSQL 15** : `localhost:5432` (`EVO-LOG` / `EVO-LOG_pass`)
- **Redis 7** : `localhost:6379`
- **MinIO Storage** : `localhost:9000` (API) / `localhost:9001` (Console Web)

---

## 🚂 2. Déploiement Backend sur Railway (FastAPI + PostgreSQL + Redis)

Le backend FastAPI est déployé sur **Railway** sous forme de conteneur Docker multi-stage ultra-résilient.

### Caractéristiques de la Configuration Railway :
1. **Dockerfile Multi-Stage Auto-Résilient** :
   - Présent à la racine ([`Dockerfile`](file:///d:/Projet/ERP/EVO-LOG/Dockerfile)) et dans [`EVO-LOG-backend/Dockerfile`](file:///d:/Projet/ERP/EVO-LOG/EVO-LOG-backend/Dockerfile).
   - Intègre l'étape d'auto-aplatissement de contexte :
     `RUN if [ -d "/app/EVO-LOG-backend" ]; then cp -rn /app/EVO-LOG-backend/* /app/ && rm -rf /app/EVO-LOG-backend; fi`
   - Garantit le démarrage correct de Uvicorn et du Seeder quel que soit le dossier racine configuré dans Railway.
2. **Script de Démarrage (`start.sh`)** :
   - Attend la disponibilité de PostgreSQL (`pg_isready`).
   - Re-crée les tables via SQLAlchemy et applique Alembic stamp/migrations.
   - Exécute le seeder `python scripts/seed_data.py` si `SEED_DATA=true`.
   - Lance le worker Celery en arrière-plan et démarre Uvicorn sur le port 8000.

### Variables d'Environnement Recommandées sur Railway :

| Variable | Valeur Explication / Exemple |
| --- | --- |
| `DATABASE_URL` | Fourni automatiquement par le plugin PostgreSQL Railway |
| `REDIS_URL` | Fourni automatiquement par le plugin Redis Railway |
| `JWT_SECRET_KEY` | Clé secrète 32+ caractères pour la signature JWT |
| `SEED_DATA` | `true` (pour l'initialisation initiale avec les 8 comptes seeders) |
| `ALLOWED_ORIGINS` | `https://EVO-LOG-frontend.vercel.app,http://localhost:3000` |

---

## 📐 3. Déploiement Frontend sur Vercel (Next.js 14 PWA)

Le frontend Next.js 14 est déployé sur **Vercel**.

### Procédure de déploiement :
1. Connecter le dépôt `ERP-logistique-` sur Vercel.
2. Définir le **Root Directory** sur `EVO-LOG-frontend`.
3. Configurer les variables d'environnement suivantes :

| Variable | Valeur Exemple |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | `https://EVO-LOG-backend.up.railway.app` |
| `NEXTAUTH_URL` | `https://EVO-LOG-frontend.vercel.app` |
| `NEXTAUTH_SECRET` | Mêmes 32+ caractères que `JWT_SECRET_KEY` backend |

4. Exécuter le build Vercel (`npm run build`).

---

## ✅ 4. Procédure de Vérification Post-Déploiement

1. **Vérifier le Healthcheck Backend** :
   ```bash
   curl -i https://EVO-LOG-backend.up.railway.app/api/health
   # Réponse attendue : {"status":"ok","service":"EVO-LOG SaaS","version":"1.0.0"}
   ```
2. **Tester la Connexion d'un Compte Seeder** :
   - Tenter de se connecter sur l'interface Vercel avec `admin` / `admin123` ou `magasinier` / `admin123`.
   - Vérifier que la Sidebar affiche les menus autorisés et grise les modules non attribués avec le cadenas 🔒.
