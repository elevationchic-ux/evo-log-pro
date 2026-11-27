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

**Profonds + testés** (40+ nouveaux tests, suite complète 987 verts) :
comptabilité OHADA (5 états + TFT/SIG + immo + liasse + export),
GMAO (planification compteurs + préventif parc), juridique, paie CEMAC,
magasin (FEFO + inventaires + écarts→compta), douane CEMAC
(`taxation_douaniere.py` = moteur unique : DD + redevance 0.45 % +
CCI 1 % + OHADA 0.05 % + TVA 19,25 % + IS 2,2 %), transit CEMAC,
acconage (surestarie, redevances port), QHSE (accidentologie TF/TG),
acquisition (notation offres), transport international (stats/rapport),
RH (congés/absentéisme/paie), finance (balance âgée, clôture),
fiscalité Cameroun (TVA/CNPS/IRPP/IS), conformité RGPD (rétention),
WMS (écarts/cross-dock), BSC/CNCC, reporting (notifications/documents/
ruptures), magasin douane.

**Profonds existants (services métier, tests partiels)** : finance
avancée (DSO, scoring client), documents, notifications, tiers, RBAC,
intégrations externes (SYDONIA+, APIES, BEAC — gabarits documentés).

**Surface → services métier livrés** (chaque module modèle possède
désormais un service `app/services/*_service.py` + tests unitaires
`tests/unit/*` — données réelles uniquement, verdicts honnêtes) :
cold chain, heavylift, aménagement portuaire, log3pl/SLA, port ops,
cycle conteneur, ferroviaire, aérien, fluvial, coursier, pipeline,
b2b, transit CEMAC, port Cameroun, B/C/D/E-séries (transport,
fluvial, ferroviaire, aérien, courier, ops portuaires, b2b, transit,
3pl, pipeline, QHSE, parc, chat, frais, RH, finance, admin, superadmin,
dashboard, reports, compta, magasin, organisation, prestataires,
annuaire, accréditation, commercial, employé, support, chauffeur,
déclarant, collaborateur, chef personnel, départements, capteurs
carburant, traçabilité, gap bridge, technicien, formation,
réglementaire, numérotation, magasinier, mission, rapports,
commercial D2 veille concurrentielle).

**Modules sans service métier (justifiés)** : `fix_tables.py`
(script utilitaire, pas un domaine), `rbac.py` (enums uniquement).

## Reste à couvrir (prochains chantiers)

- ~~Économie / analytique~~ : fait (`economie_service`, `rentabilite_service`,
  `rentabilite_mission_service` — recette fret vs couts par mission)
- ~~Paie cumuls~~ : fait (`paie_service` — cumuls annuels, méthode du taux
  cumulé IRGM sur barème source unique `rh_avance_service`, bulletin + PDF
  WeasyPrint avec repli)
- ~~Exposition API~~ : fait (`/api/v1/metier` — 57 endpoints
  (49 GET analytiques + 7 POST calculateurs + paramètres), permissions
  catalogue réel) + page frontend `/app/(app)/metier` couvrant tous les
  GET analytiques en 7 sections par domaine + `metierAPI` typé
- Endpoints en écriture : déjà couverts par les routeurs CRUD dédiés
  (`*_deep.py`, `new_k_modules.py`) — les services analytiques sont
  volontairement read-only
- ~~Registres deep sans écran~~ : fait — `src/lib/deep-crud.tsx` +
  `src/lib/deep-configs/*.ts` (générés depuis routers `*_deep` + schémas
  Create) → **61 pages `/<domaine>/donnees`** couvrant ~579 ressources
  CRUD (liste + création + **édition/suppression** via PUT/DELETE `/{id}`,
  pagination client 100/page, datalists de suggestion pour les FK
  `employe_id`/`client_id`/`fournisseur_id`/`user_id`/`tiers_id`) + index
  `/referentiels` + module nav « Pilotage & Registres » dans
  `navigationRegistry.ts`. Régénérer via `_analyse/gen_deep_pages.py`
- ~~Préfixes API sans UI~~ : fait — page `/app/(app)/outils` couvre les 6
  derniers préfixes (`privacy` RGPD, `e-invoicing`, `marketplace` clés API,
  `freight-exchange` offres, `digital-twin` yard-state, `gamification`
  driver-scores) + `deepAPI` ; entrée « Outils & conformité » dans le
  module nav Pilotage
- Validation PostgreSQL : environnement local sans serveur PG ni Docker ;
  schéma validé par `create_all` SQLite (986 tables, 0 erreur via
  `import app.main`)
- ~~e2e Playwright~~ : fait en local — `playwright.config.ts` (timeout
  120 s : `next dev` compile les routes à la demande) + `auth.spec.ts`
  (**7 verts** : login, erreur 401, logout, RBAC admin + magasinier +
  CLIENT_B2B → `/client-portal` via rôle `CLIENT_B2B` seedé et règle
  d'atterrissage dans `src/lib/auth.ts`) + `process-end-to-end.spec.ts`
  réécrit sur l'UI réelle (**7 verts** : chaîne de domaines
  port→douane→magasin→transport→finance + pages transverses `/metier`,
  `/metier/calculs`, `/referentiels`, `/outils` + vrai appel calculateur
  congés). Login e2e : `page.press(password, 'Enter')` + fallback clic —
  un overlay d'intro (`fixed inset-0 z-[100]`) intercepte parfois le clic
  submit. Backend `/auth/login` : rate-limit slowapi 10/min — espacer les
  runs complets.
  Commande : `node node_modules/@playwright/test/cli.js test`
  (channel chrome système — téléchargement chromium impossible).
