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

`app/main.py` enregistre **121 routeurs** via `safe_include_router()` (un routeur
qui s'importe mal n'enterre pas l'application). La liste ci-dessous donne les
préfixes structurants, pas l'inventaire exhaustif ; pour le recompter :
`python scripts/cartographie_routeur.py --total` (déclare 1333 endpoints pour les
routeurs `app/routers/v1/`).

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
20. `/api/v1/rbac` (RBAC multi-tenant : catalogue de permissions, rôles, permissions granulaires d'un rôle, vérification)
21. `/api/v1/accreditations` (Accréditations nominatives datées + espaces communs `/api/v1/shared-access`)
22. `/api/v1/comptabilite-avance`, `/api/v1/magasin` (domaines cœur sécurisés par `require_perm`)
23. `/api/v1/amenagement-portuaire` (département autonome d'aménagement portuaire  voir § dédié)

### Département autonome : Aménagement Portuaire & Domaine Public

Un **département** (batch 29), pas une extension du module d'exploitation du quai :
il gère l'aménagement et le domaine public des ports de **Douala, Kribi et Limbe**
(autorité portuaire loi n°2012/021, PPP loi n°2023/008, visa de maturité décret
n°2018/0492, EIES loi n°96/012  vocabulaire juridique identique à celui du
modèle `app/models/amenagement_portuaire.py`).

- **Backend** : `app/models/amenagement_portuaire.py` (9 entites),
  `app/schemas/amenagement_portuaire.py`, `app/routers/v1/amenagement_portuaire.py`
  (60 endpoints : 54 ecritures/lectures reelles, 6 teleprocedures annoncees `501`),
  migrations `038` (tables), `039` et `042` (grants RBAC), `041` (colonnes
  `ports_cameroun`). Autorisation par `require_perm("amenagement.<sous_module>.<action>")`.
- **Frontend** : `src/app/(app)/amenagement-portuaire/*` (10 ecrans : tableau de
  bord + 9 registres), composants dedies dans `src/components/amenagement-portuaire/`
  dont `ReferentielPlaces` (declaration des places dans le referentiel national,
  montee sur le tableau de bord  le sous-module `place` n'a pas de registre propre
  parce qu'il n'enregistre rien d'annuel : il alimente la liste que tous les autres
  proposent).
- **Theme propre** : `#0E7490` (`modulePalette.ts`, `moduleColors.ts`, `navI18n.ts`,
  icone 📐), isole des teintes des autres departements.
- **Independance** : `navigationRegistry.ts` le declare comme famille autonome
  (`domainLoadingConfig.ts` = dpt 29) ; ses codes de permission ne recoupent aucun
  autre module, a l'exception lue du referentiel `ports_cameroun` que quatre
  routeurs consultent et que seul `place` alimente.
- **Zero donnee inventee** : aucune ligne seedee, `NULL` reste `NULL`, les
  libelles des listes deriveant de `/nomenclatures` et les valeurs de
  `/synthese` des seules saisies des agents.

---

## 🎨 Architecture Frontend & Système RBAC

### Rôles & Autorisations (`modules_allowed` + permissions granulaires)
Le contrôle d'accès est **d'abord appliqué côté serveur** (`app/core/permissions.py`,
`require_perm`, `visible_user_ids` ; voir `docs/RBAC_ACCREDITATIONS.md`). Côté
frontend, la session NextAuth propage `permissions`, `shared_modules`, `role_level`,
`department_id`. La `Sidebar` et `PermissionGuard` combinent :
1. les **permissions granulaires effectives** (`module.sous_module.action`, hook `useCan`) quand elles existent ;
2. à défaut, le tableau legacy `modules_allowed` (comportement historique inchangé).

Les modules non autorisés sont :
1. **Grisés visuellement** avec une opacité réduite.
2. **Verrouillés par une icône de cadenas 🔒**.
3. **Protégés par une modale d'accès restreint** lors de toute tentative de clic : *"Accès restreint : Votre profil [ROLE] n'est pas autorisé à accéder au module [MODULE]. Veuillez contacter l'Admin CADC."*

### PWA & Assets 3D
- **Service Worker** (`sw.js`) enregistré automatiquement dans `layout.tsx`.
- **Bannière d'installation PWA** réactive et responsive.
- **Icônes PWA 3D metallic** (`icon-512x512.png`, `icon-192x192.png`, `apple-touch-icon.png`, `favicon.ico`).
