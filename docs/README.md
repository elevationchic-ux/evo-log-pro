# Documentation EVO-LOG SaaS

## Vue d'ensemble

EVO-LOG SaaS est aujourd'hui un monorepo compose de:

- un backend FastAPI 0.115 en Python 3.12;
- un frontend Next.js 14 en TypeScript;
- une stack locale Docker avec PostgreSQL 17, Redis 7 et MinIO;
- un workflow CI versionne dans `.github/workflows/ci-cd.yml` (`test-backend` sur
  PostgreSQL service, `test-frontend` lint + type-check + build, `security-scan`,
  puis deploiements staging/production).

## Etat reel du depot

Inventaire releve sur le code actuel (04 octobre 2026):

- `evo-log-backend/app/models`: 48 fichiers Python hors `__init__.py`
- `evo-log-backend/app/schemas`: 39 fichiers
- `evo-log-backend/app/routers/v1`: 106 fichiers de routeur (1 333 endpoints declares;
  a recompter avec `python evo-log-backend/scripts/cartographie_routeur.py --total`)
- `evo-log-backend/app/services`: 48 fichiers
- `evo-log-frontend/src/app`: 360 pages `page.tsx`

Il n'y a **pas** de repertoire `app/repositories` : l'acces aux donnees se fait par
les services et par des requetes SQLAlchemy dans les routeurs.

## Structure utile

```text
EVO-LOG/
├── docs/
├── EVO-LOG-backend/
│   ├── app/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   ├── scripts/
│   └── tests/
├── EVO-LOG-frontend/
│   ├── e2e/
│   ├── src/app/
│   ├── src/components/
│   ├── src/lib/
│   ├── src/stores/
│   └── src/types/
├── references/
├── scripts/
└── tools/
```

## Domaines deja presents

### Backend

- Authentification, JWT, MFA, RBAC
- Tiers et master data
- Transport
- Finance
- Parc
- Magasin
- Documents
- Alerts
- Gateway
- Transactions
- Notifications
- Administration et agences
- Purchase / requisitions
- Aménagement portuaire & domaine public (département autonome `amenagement_portuaire`,
  Douala / Kribi / Limbé : schémas directeurs, projets, programmation PIP/CDMT, marchés
  & PPP, titres domaniaux, concessions, infrastructures, dragage, autorisations EIES,
  et l'alimentation du référentiel national `ports_cameroun`)

### Frontend

Les espaces les plus visibles du frontend sont deja presents:

- `admin`
- `amenagement-portuaire`
- `audit`
- `dashboard`
- `documents`
- `finance`
- `magasin`
- `master-data`
- `parc`
- `reports`
- `security`
- `support`
- `tiers`
- `transport`

## Documentation a consulter

- `ARCHITECTURE.md`: architecture actuelle du monolithe modulaire
- `API_DOCUMENTATION.md`: cartographie des prefixes API exposes
- `RBAC_ACCREDITATIONS.md`: permissions granulaires, visibilite hierarchique, accreditations et espaces communs
- `DEPLOYMENT.md`: execution locale et deploiement VPS
- `../GUIDE_DEPLOYMENT_VERCEL_RAILWAY.md` et `../GUIDE_DOCKER.md`: deploiement herberge et stack conteneurisee (il n'existe pas de `RAILWAY_DEPLOYMENT.md` dans `docs/`)
- `STATUT_GLOBAL_PROJET.md`: synthese de l'etat reel et des manques
- `TESTING_CHECKLIST.md`: checklist de verification et commandes de test
- `TODO.md`: backlog restant
- `archive/`: rapports d'expertise historiques (instantanes dates), conserves pour tracer l'historique mais **ne reflétant pas l'etat courant**

## Ce qui manque encore

Le projet est avance, mais plusieurs sujets restent a consolider:

- couverture de tests backend encore inegale selon les modules;
- documentation endpoint par endpoint non maintenue a la main : elle se relit dans
  Swagger (`/api/docs`) et s'audite avec `scripts/cartographie_routeur.py` ;
- absence de worker d'arriere-plan effectivement cable dans la stack locale;
- absence de documentation produit ou parcours utilisateurs par module;
- besoin de clarifier ce qui est pret pour production et ce qui reste placeholder cote frontend.
