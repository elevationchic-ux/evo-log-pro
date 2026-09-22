# Architecture Technique EVO-LOG SaaS

## Résumé Executif

**EVO-LOG SaaS** est structuré comme un monolithe modulaire haute performance avec découplage clair entre le backend API FastAPI et le frontend Next.js 14 PWA.

- **Frontend** : Next.js 14 (App Router), Vanilla CSS Design System 3D Métallique, PWA (`sw.js`).
- **Backend** : FastAPI 0.115, SQLAlchemy 2.0, PostgreSQL (Production) / SQLite (Dev).
- **Cache & Asynchrone** : Redis pour l'idempotence et les files d'attente Celery.
- **Documents & Fichiers** : WeasyPrint (Génération PDF) et MinIO (Stockage Objets).

---

## 🏗️ Topologie d'Exécution

### 1. Environnement Local (`docker-compose.yml`)
Stack complète démarrant avec `docker-compose up -d --build` :
- `db` : PostgreSQL 15
- `redis` : Redis 7
- `minio` : Stockage MinIO + Console (Port 9001)
- `api` : FastAPI backend sur le port 8000
- `frontend` : Next.js sur le port 3000

### 2. Environnement de Production (Railway & Vercel)
- **Railway** : Héberge le conteneur Docker multi-stage du backend avec auto-aplatissement de contexte (`cp -rn /app/EVO-LOG-backend/* /app/`).
- **Vercel** : Héberge le frontend Next.js compilé statiquement (153 pages).

---

## 🔌 Cartographie des Routeurs Backend (`EVO-LOG-backend/app/main.py`)

Les 19 routeurs enregistrés avec vérification de sécurité `safe_include_router()` :

1. `/api/auth` (Authentification, JWT, MFA, me)
2. `/api/tiers` (Gestion des clients et fournisseurs)
3. `/api/transport` (Missions, chauffeurs, camions)
4. `/api/finance` (Facturation et encaissements)
5. `/api/parc` (Yard, emplacements, conteneurs)
6. `/api/documents` (Génération PDF WeasyPrint et documents)
7. `/api/alerts` (Alertes d'exploitation)
8. `/api/magasin` (Stock WMS, réceptions, sorties)
9. `/api/gateway` (Passerelles inter-modules)
10. `/api/transactions` (Journal des mouvements)
11. `/api/transport/goods-declarations` (Déclarations de marchandises)
12. `/api/magasin/removal-slips` (Bons d'enlèvement Mag3)
13. `/api/magasin/receptions-mag3` (Réceptions Mag3)
14. `/api/master-data` (Données de référence)
15. `/api/admin` (Administration utilisateurs, rôles, `modules_allowed`)
16. `/api/admin/agencies` (Gestion des agences)
17. `/api/suppliers` (Répertoire fournisseurs)
18. `/api/notifications` (Notifications applicatives)
19. `/api/purchase` (Procurement et demandes d'achat)

---

## 🎨 Architecture Frontend & Système RBAC

### Rôles & Autorisations (`modules_allowed`)
Le composant `Sidebar` inspecte le rôle et le tableau `modules_allowed` de l'utilisateur connecté via NextAuth. Les modules non autorisés sont :
1. **Grisés visuellement** avec une opacité réduite.
2. **Verrouillés par une icône de cadenas 🔒**.
3. **Protégés par une modale d'accès restreint** lors de toute tentative de clic : *"Accès restreint : Votre profil [ROLE] n'est pas autorisé à accéder au module [MODULE]. Veuillez contacter l'Admin CADC."*

### PWA & Assets 3D
- **Service Worker** (`sw.js`) enregistré automatiquement dans `layout.tsx`.
- **Bannière d'installation PWA** réactive et responsive.
- **Icônes PWA 3D metallic** (`icon-512x512.png`, `icon-192x192.png`, `apple-touch-icon.png`, `favicon.ico`).
