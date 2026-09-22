# CLAUDE.md — Directives & Commandes EVO-LOG SaaS

Ce document contient les instructions et commandes de référence pour l'utilisation des assistants de code sur le dépôt **EVO-LOG SaaS**.

---

## 🛠️ Commandes Fréquentes

### Backend (`EVO-LOG-backend`)
- **Installation dépendances** : `cd EVO-LOG-backend && pip install -r requirements.txt`
- **Initialisation & Seeder BDD** : `cd EVO-LOG-backend && python scripts/seed_data.py`
- **Exécution migrations Alembic** : `cd EVO-LOG-backend && alembic upgrade head`
- **Création d'une migration** : `cd EVO-LOG-backend && alembic revision --autogenerate -m "description"`
- **Démarrage serveur dev** : `cd EVO-LOG-backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Exécution tests Pytest** : `cd EVO-LOG-backend && pytest`
- **Test unitaire ciblé** : `cd EVO-LOG-backend && pytest tests/unit/test_magasin_service.py`

### Frontend (`EVO-LOG-frontend`)
- **Installation dépendances** : `cd EVO-LOG-frontend && npm install`
- **Démarrage serveur dev** : `cd EVO-LOG-frontend && npm run dev`
- **Validation Build Production** : `cd EVO-LOG-frontend && npm run build` (Doit générer 153/153 pages statiques sans erreur)
- **Linter TypeScript/Next.js** : `cd EVO-LOG-frontend && npm run lint`
- **Exécution tests E2E (Playwright)** : `cd EVO-LOG-frontend && npx playwright test`

### Stack Docker Locale
- **Démarrer tous les services** : `docker-compose up -d --build`
- **Arrêter la stack** : `docker-compose down`
- **Voir les journaux API** : `docker logs -f EVO-LOG_api`

---

## 🏗️ Architecture du Projet

### Monolithe Modulaire Découplé
- **Frontend** : Next.js 14 (App Router), Vanilla CSS Design System, Icônes PWA 3D Métalliques (`512x512`, `192x192`, `apple-touch-icon.png`, `favicon.ico`).
- **Backend** : FastAPI 0.115, SQLAlchemy 2.0, PostgreSQL (ou SQLite dev local), Alembic, Celery, Redis, WeasyPrint.
- **Rôles & RBAC** : Rôles stricts (`ADMIN`, `MAGASINIER`, `DISPATCHER`, `QHSE`, `FINANCIER`, `DOUANE`, `PARC`, `AUDITOR`) avec contrôle dynamique `modules_allowed`.

### Organisation Backend (`EVO-LOG-backend`)
- `app/main.py` : Point d'entrée FastAPI, middleware d'audit, SlowAPI rate limiting, `safe_include_router()` pour l'enregistrement résilient des 22+ routeurs.
- `app/routers/v1/` : Routeurs v1 (auth, tiers, transport, finance, parc, magasin, qhse, acconage, maintenance, fuelguard, shift_planning, port_pricing, gps_tracking, port_incidents, container_lifecycle, notification_system, auto_invoicing, port_performance, real_customs, partner_api, etc.).
- `app/models/` : Modèles SQLAlchemy (User, RoleModel, PermissionModel, Agency, Tiers, Mission, Stock, etc.) + 10 nouveaux modules + 18 sous-modules.
- `app/schemas/` : Contrats de validation Pydantic v2.
- `app/services/` : Orchestration de la logique métier + 10 nouveaux services.
- `app/utils/` : Sécurité, hashage bcrypt, monitoring Prometheus, logs, WeasyPrint PDF.
- `scripts/seed_data.py` : Seeder idempotent alimentant la BDD avec 8 comptes opérationnels réels.

### Organisation Frontend (`EVO-LOG-frontend`)
- `src/app/(auth)` : Écrans de connexion CADC avec splash screen gold et gestion de thème.
- `src/app/(app)` : 14 espaces applicatifs métiers (153 routes Next.js compilées).
- `src/components/layout/` : Layout global, Sidebar dynamique avec cadenas 🔒 et modale d'accès restreint.
- `src/lib/auth.ts` : Configuration NextAuth v4 synchronisée avec le backend et le RBAC.
- `public/` : Manifest PWA, Service Worker `sw.js`, assets 3D metallic icons.

---

## 🔐 Règles Spécifiques & Sécurité

1. **Jamais de données factices en dur** : Tous les seeders créent de réelles entités métiers en base de données.
2. **Mots de passe par défaut** : Le mot de passe initial des utilisateurs de test est `admin123`. La politique `must_change_password` impose un renouvellement sous 90 jours.
3. **Résilience Docker Railway** : Le `Dockerfile` intègre la règle d'auto-aplatissement `cp -rn /app/EVO-LOG-backend/* /app/` pour fonctionner aussi bien depuis la racine `/` que depuis le sous-dossier `/EVO-LOG-backend`.

---

## 📦 Nouveaux Modules (Version 2.0)

### 10 Modules avec Couleurs Uniques
- **Shift Planning** (#FF6B6B) - Planification des shifts et ressources
- **Port Pricing** (#4ECDC4) - Tarification des services portuaires
- **GPS Tracking** (#45B7D1) - Tracking temps réel de la flotte
- **Real Customs Integration** (#96CEB4) - Intégration SYDONIA+ et GUICHET UNIQUE
- **Port Incidents** (#FFEAA7) - Gestion des incidents portuaires
- **Auto Invoicing** (#DDA0DD) - Facturation automatique OHADA
- **Port Performance Dashboard** (#98D8C8) - Dashboard de performance
- **Multi-Channel Notifications** (#F7DC6F) - Notifications multi-canal
- **Container Lifecycle** (#BB8FCE) - Cycle de vie des conteneurs
- **Partner API** (#85C1E9) - API pour intégration B2B

### 50 Sous-Modules (5 par Module)
Chaque module a 5 sous-modules distincts avec leurs propres fonctionnalités :
- Shift Planning: Shift Management, Staff Assignment, Template Management, Performance Metrics, Resource Planning
- Port Pricing: Tariff Management, Surcharge Management, Discount Management, Contract Pricing, Billing Engine
- GPS Tracking: Real-Time Tracking, Fleet Management, Route Optimization, Driver Behavior, Fuel Management
- Real Customs: Declaration Management, Risk Assessment, Duties Calculation, Document Management, Compliance Tracking
- Port Incidents: Incident Reporting, Investigation Management, Corrective Actions, Risk Assessment, Incident Analytics
- Auto Invoicing: Invoice Generation, Payment Processing, Credit Management, Dispute Resolution, Financial Reporting
- Port Performance: KPI Tracking, Benchmarking, Trend Analysis, Resource Optimization, Executive Reporting
- Notifications: Template Management, Channel Integration, Delivery Tracking, Preference Management, Analytics
- Container Lifecycle: Container Tracking, Maintenance Management, Inspection Management, Lease Management, Fleet Optimization
- Partner API: API Key Management, Rate Limiting, Webhook Management, Security Monitoring, Usage Analytics

### Statistiques Version 2.0
- **34 modèles SQLAlchemy** (16 originaux + 18 nouveaux)
- **12 services métier** (2 originaux + 10 nouveaux)
- **22 routeurs API** (12 originaux + 10 nouveaux)
- **120+ endpoints API** (originaux + 58 nouveaux)
- **38 tables** de base de données (20 principales + 18 sous-modules)
- **3 migrations Alembic** (add_accreditation_real_bl, add_10_new_modules, add_complete_submodules)
