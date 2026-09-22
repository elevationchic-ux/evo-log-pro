# Documentation EVO-LOG SaaS

## Vue d'ensemble

EVO-LOG SaaS est aujourd'hui un monorepo compose de:

- un backend FastAPI 0.115 en Python 3.12;
- un frontend Next.js 14 en TypeScript;
- une stack locale Docker avec PostgreSQL 17, Redis 7 et MinIO;
- pas de workflow CI versionne actuellement dans `.github/workflows/`.

## Etat reel du depot

Inventaire releve sur le code actuel:

- `EVO-LOG-backend/app/models`: 22 fichiers Python hors `__init__.py`
- `EVO-LOG-backend/app/schemas`: 16 fichiers
- `EVO-LOG-backend/app/routers`: 19 routeurs
- `EVO-LOG-backend/app/services`: 16 fichiers
- `EVO-LOG-backend/app/repositories`: 12 fichiers
- `EVO-LOG-frontend/src/app`: 92 pages `page.tsx`

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

### Frontend

Les espaces les plus visibles du frontend sont deja presents:

- `admin`
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
- `DEPLOYMENT.md`: execution locale et deploiement VPS
- `RAILWAY_DEPLOYMENT.md`: configuration Railway/Vercel
- `STATUT_GLOBAL_PROJET.md`: synthese de l'etat reel et des manques
- `TESTING_CHECKLIST.md`: checklist de verification et commandes de test
- `TODO.md`: backlog restant

## Ce qui manque encore

Le projet est avance, mais plusieurs sujets restent a consolider:

- couverture de tests backend encore inegale selon les modules;
- documentation endpoint par endpoint non maintenue manuellement;
- absence de worker d'arriere-plan effectivement cable dans la stack locale;
- absence de documentation produit ou parcours utilisateurs par module;
- besoin de clarifier ce qui est pret pour production et ce qui reste placeholder cote frontend.
