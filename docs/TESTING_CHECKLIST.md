# Testing Checklist

## Objectif

Verifier le depot tel qu'il existe aujourd'hui, sans s'appuyer sur d'anciens chemins HTML ou sur des pages qui n'existent plus.

## Commandes utiles

### Backend

```bash
cd EVO-LOG-backend
pytest
```

### Frontend

```bash
cd EVO-LOG-frontend
npm run lint
npm run build
npx playwright test
```

## Verification backend

- `GET /api/health` retourne `ok` ou `degraded`
- `GET /api/health/detailed` repond sans crash
- Swagger est accessible sur `/api/docs`
- login, refresh et `me` fonctionnent
- les modules suivants repondent au moins sur leurs routes principales:
  - `tiers`
  - `transport`
  - `finance`
  - `parc`
  - `magasin`
  - `master-data`
  - `admin`
  - `notifications`
  - `purchase`

## Verification frontend

### Auth

- `/login`
- `/forgot-password`
- `/mfa`
- `/register`

### Administration et audit

- `/admin/user-management/listing`
- `/admin/user-management/create`
- `/admin/configuration-des-roles-rbac`
- `/admin/role-assignment`
- `/admin/journal`
- `/admin/audit/operation-trace`
- `/admin/audit/system-health`
- `/admin/security/mfa`

### Finance

- `/finance/overview`
- `/finance/billing`
- `/finance/factures`
- `/finance/gateway`
- `/finance/requisitions`
- `/finance/saisie-transaction-bancaire`
- `/finance/banking/reconciliation`

### Magasin

- `/magasin`
- `/magasin/dashboard`
- `/magasin/articles`
- `/magasin/declarations`
- `/magasin/reception-mag3`
- `/magasin/removal-slip`
- `/magasin/stocks`
- `/magasin/stocks/search`
- `/magasin/transactions`
- `/magasin/commandes`
- `/magasin/saisie-inventaire-physique`
- `/magasin/mouvement-de-stocEVO-manuel`

### Transport

- `/transport`
- `/transport/control`
- `/transport/dispatch`
- `/transport/drivers`
- `/transport/drivers/new`
- `/transport/flotte`
- `/transport/fuel`
- `/transport/fuel/history`
- `/transport/fuel/ticket`
- `/transport/goods-declaration`
- `/transport/map`
- `/transport/missions`

### Parc et autres

- `/parc`
- `/parc/overview`
- `/parc/gestion-de-la-flotte`
- `/parc/vehicles/new`
- `/parc/worEVO-orders/create`
- `/parc/workshop`
- `/documents/archive`
- `/reports/templates/library`
- `/reports/custom/builder`
- `/security/dashboard`

## Verification visuelle

- le layout commun charge correctement
- la navigation laterale pointe vers des routes existantes
- les themes de module restent coherents
- les pages critiques ne plantent pas au rendu serveur
- les formulaires n'affichent pas d'erreurs console triviales

## Suites deja presentes

### Backend

- `tests/integration/test_auth.py`
- `tests/integration/test_finance.py`
- `tests/integration/test_magasin.py`
- `tests/integration/test_parc.py`
- `tests/integration/test_tiers.py`
- `tests/integration/test_transport.py`
- `tests/unit/test_finance_service.py`
- `tests/unit/test_magasin_service.py`
- `tests/unit/test_parc_service.py`
- `tests/unit/test_transport_service.py`

### Frontend

- `e2e/login.spec.ts`

## Ce qui manque encore

- davantage de tests sur `admin`, `notifications`, `purchase` et `master-data`
- une matrice de smoke tests par role
- une checklist de validation des pages uniquement demonstratives
