# GUIDE DOCKER - EVO-LOG SaaS

## 🚀 Déploiement Docker - Solution Recommandée

Docker est la solution recommandée pour déployer EVO-LOG SaaS en production car:
- **Isole l'environnement** du système hôte
- **Évite les problèmes système** (Rust/Cargo, chemins Unicode)
- **Garantit la reproductibilité** en dev et prod
- **Fonctionne cross-platform** (Windows, Linux, Mac)

---

## 📋 Prérequis

1. **Docker Desktop** - Installer depuis [docker.com](https://www.docker.com/products/docker-desktop)
2. **Docker Compose** - Inclus avec Docker Desktop
3. **8GB RAM minimum** - Pour les containers PostgreSQL + Redis + Frontend + Backend

---

## 🔧 Installation Rapide

### 1. Cloner le projet (si pas déjà fait)
```bash
cd C:\Users\chris\Documents\Projet\Documents\evo-log\ERP-logistique-
```

### 2. Configurer les variables d'environnement
```bash
# Copier le fichier d'exemple
copy docker.env.example docker.env

# Éditer docker.env avec vos valeurs de production
# Au minimum, changer SECRET_KEY et NEXTAUTH_SECRET
```

### 3. Build et démarrage
```bash
# Build tous les services
docker-compose build

# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

### 4. Vérification
```bash
# Vérifier que tous les services sont actifs
docker-compose ps

# Tester l'API backend
curl http://localhost:8000/api/health

# Tester le frontend
# Ouvrir http://localhost:3000 dans le navigateur
```

---

## 🐳 Services Docker

### Services créés:
1. **postgres** - PostgreSQL 15 (port 5432)
2. **redis** - Redis 7 (port 6379)
3. **backend** - FastAPI (port 8000)
4. **frontend** - Next.js (port 3000)

### Health checks:
- PostgreSQL: Vérifie que la base est prête
- Redis: Vérifie que Redis répond
- Backend: Vérifie `/api/health`
- Frontend: Vérifie que le port 3000 répond

---

## 🛠️ Commandes Docker Utiles

### Gestion des services
```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Redémarrer un service spécifique
docker-compose restart backend

# Voir les logs d'un service
docker-compose logs backend
docker-compose logs -f frontend

# Voir l'état des services
docker-compose ps
```

### Gestion des données
```bash
# Voir les volumes
docker volume ls

# Sauvegarder les données PostgreSQL
docker exec evo-log-postgres pg_dump -U evo_log evo_log > backup.sql

# Restaurer les données PostgreSQL
cat backup.sql | docker exec -i evo-log-postgres psql -U evo_log evo_log
```

### Debug
```bash
# Entrer dans un container
docker exec -it evo-log-backend bash
docker exec -it evo-log-frontend sh

# Voir les ressources utilisées
docker stats
```

---

## 🔒 Sécurité Production

### Variables d'environnement à modifier:
```bash
# Dans docker.env
SECRET_KEY=générer-une-clé-32-caractères-aléatoire
NEXTAUTH_SECRET=générer-une-clé-32-caractères-aléatoire
```

### Génération de clés sécurisées:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

## 📊 Monitoring

### Vérifier les logs en temps réel:
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Statistiques des containers:
```bash
docker stats
```

---

## 🔄 Mise à jour

### Mettre à jour l'application:
```bash
# Arrêter les services
docker-compose down

# Rebuild les images
docker-compose build

# Redémarrer
docker-compose up -d
```

### Mettre à jour uniquement le backend:
```bash
docker-compose build backend
docker-compose up -d backend
```

---

## 🐛 Dépannage

### Problème: Port déjà utilisé
```bash
# Voir ce qui utilise le port
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Changer les ports dans docker-compose.yml
ports:
  - "3001:3000"  # Changer 3000 vers 3001
```

### Problème: Migrations échouent
```bash
# Entrer dans le container backend
docker exec -it evo-log-backend bash

# Exécuter les migrations manuellement
alembic upgrade head
```

### Problème: Database connection refused
```bash
# Vérifier que PostgreSQL est prêt
docker-compose logs postgres

# Redémarrer PostgreSQL
docker-compose restart postgres
```

---

## 🚀 Déploiement Production

### Pour Railway:
```bash
# Créer les services PostgreSQL et Redis sur Railway
# Déployer backend et frontend avec:
railway up
```

### Pour VPS (DigitalOcean, AWS, etc.):
```bash
# Installer Docker sur le serveur
# Copier les fichiers du projet
# docker-compose up -d
# Configurer nginx comme reverse proxy
```

---

## 📁 Structure Fichiers Docker

```
evo-log-/
├── docker-compose.yml          # Configuration des services
├── docker.env.example          # Variables d'environnement
├── docker.env                  # Variables réelles (à créer)
├── evo-log-backend/
│   ├── Dockerfile             # Configuration backend
│   ├── requirements.txt        # Dépendances Python
│   └── ...
└── evo-log-frontend/
    ├── Dockerfile             # Configuration frontend
    ├── package.json           # Dépendances Node
    └── ...
```

---

## ✅ Checklist Production

- [ ] Docker Desktop installé
- [ ] docker.env créé avec clés sécurisées
- [ ] docker-compose build réussi
- [ ] docker-compose up -d réussi
- [ ] Services actifs (docker-compose ps)
- [ ] Backend accessible sur http://localhost:8000
- [ ] Frontend accessible sur http://localhost:3000
- [ ] Migrations appliquées
- [ ] Logs sans erreurs
- [ ] Health checks OK

---

**Date:** 18 janvier 2026
**Statut:** Docker Compose documenté ; build et déploiement réel à valider dans un environnement Docker
