# EVO-LOG — Guide architecte

ERP logistique Cameroun/CEMAC. Backend FastAPI + frontend Next.js 14.
Doctrine : aucune donnée fictive, isolation tenant stricte, RBAC granulaire,
calculs depuis les données réelles — jamais de montants inventés.

## Commandes de vérification

Backend (`evo-log-backend/`, venv `.venv`) :
```bash
.venv/Scripts/python -m compileall -q app/
.venv/Scripts/python -c "import app.main"          # import check
.venv/Scripts/python -m alembic upgrade head       # migrations (SQLite OK)
.venv/Scripts/python -m pytest tests/unit -q       # suite unitaire
```

Frontend (`evo-log-frontend/`) :
```bash
npx tsc --noEmit && npx next lint && npx next build
```

Stack locale : backend `uvicorn app.main:app --reload` (:8000),
frontend `npm run dev` (:3000, `NEXT_PUBLIC_API_URL=http://localhost:8000`).

## Domaines normatifs couverts (backend + tests)

| Domaine | Références | Livré |
|---|---|---|
| Comptabilité | SYSCOHADA, CEMAC | 5 états (bilan, CR, TAFIRE, TFT, SIG), notes annexes, immobilisations amortissables, liasse fiscale TVA+IS, export PDF/HTML |
| GMAO | ISO 55000, IEC 60812 | Planification préventive par compteurs réels (heures/km/cycles), lubrifications, OT, équipements, priorités par criticité |
| Juridique | Droit OHADA/CEMAC | Contrats (reconduction, préavis), contentieux, échéances |
| RH / Paie | CEMAC CNPS, IRGM | Bulletin, charges salariales/patronales, DIPE, récapitulatif annuel |
| Magasin | FEFO/FIFO | Valorisation, allocation FEFO, inventaires tournants, écarts→écriture 603/37x |
| Ponts | — | Actif GMAO→immobilisation, écarts inventaire→compta |

## Points d'attention architecte

- **Permissions** : tout nouveau endpoint exige un code présent dans
  `app/core/permission_catalog.py` (sinon 403 silencieux). Modules :
  `comptabilite.*`, `fiscalite.*`, `immobilisations.*`, `maintindustrielle.*`,
  `juridique.*`, `magasin.*`, `rh.*`.
- **Tenant** : modèles avec `company_id` ; l'isolation est appliquée par
  `tenant_enforcement` (fail-open hors contexte tenant — les services
  doivent filtrer explicitement quand nécessaire).
- **Idempotence** : écritures comptables auto portent une clé unique
  (`AMORT-{id}-{periode}`, `INV-ECART-{id}`) ; rejouer = refus propre.
- **Honnêteté** : un montant non calculable est signalé, jamais estimé ;
  les taux CNPS/IRGM sont des barèmes simplifiés à valider par expert.
- **Migrations** : `sa.func.now()` (pas `sa.text('now()')`), idempotentes,
  SQLite-rejouables.
- **PDF** : WeasyPrint requiert Pango/Cairo (prod Linux) ; repli HTML
  automatique en dev Windows.

## Audit de couverture (réel, pas déclaratif)

**Profonds (logique métier normative + tests)** : comptabilité OHADA,
GMAO, juridique, paie CEMAC, magasin/FEFO/inventaires.

**Profonds existants (services métier, à auditer pour tests)** :
douane CEMAC (`taxation_douaniere.py` = moteur unique de liquidation :
DD + redevance 0.45 % + CCI 1 % + OHADA 0.05 % + TVA 19,25 % + IS 2,2 %),
QHSE (taux TF/TG par million d'heures, dénominateur réel
`HeuresExposition`, bilan CSST/CNPS, HACCP, permis IMDG), acconage,
transport international, transit, acquisition, finance, RH,
magasin douane, reporting, fiscalité Cameroun, documents, intégration.

**Surface (CRUD généré, profondeur à construire)** : port ops,
aménagement portuaire, ferroviaire, fluvial, aérien, cold chain,
log3pl, heavylift, conteneurs, b2b, chat, notifications, annuaire,
formation, pipeline, tracabilité — ~60 modules avec modèles+routeurs
mais services minces (0-3 fonctions). Priorité : audit fonction par
fonction avant d'ajouter du normatif.

## Reste à couvrir (prochains chantiers)

- Économie / analytique (rentabilité par mission/client/unité)
- Tests unitaires des services profonds non couverts (douane, QHSE,
  acconage, transport international, transit, acquisition)
- Surface CRUD → normatif : port, aménagement, modes de transport
- Paie : bulletin PDF, cumuls IRGM annuels progressifs
- Validation PostgreSQL + e2e Playwright
