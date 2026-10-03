# Rapport  Corrections P0 "Honnêteté & Sécurité" (batch exécuté)

> Suite de l'audit à 3 volets (Cameroun/CEMAC 3/10, UX novice 3/10, couverture chaîne ~55-60%).
> Principe appliqué : **le système ne doit jamais simuler un acte juridique, financier ou
> opérationnel qui n'a pas eu lieu.** Convention existante `app/core/not_implemented.py`
> (HTTP 501 explicite) étendue partout où elle était violée.

## Vérifications finales (exécutées)

| Contrôle | Résultat |
|---|---|
| `python -m compileall app tests` | ✅ EXIT=0 |
| `python -m pytest tests` (commande exacte de la CI, suite complete batches 2 a 23) | ✅ **705 passed, 2 xfailed, 0 failed** (442 s) au run definitif du batch 23, `PYTEST_EXIT=0`. Le batch 23 ajoute 14 tests (delta 691 → 705 exactement cela) ; les evoluations precedentes (625 → 645 → 659 → 691) incluent aussi des tests d'une session concurrente (tranches devis 030, maintenance 031/032, RBAC transport/comptabilite/magasin), sans echec imputable aux lots 16 a 23. Historique : le run du batch 18 etait **rouge de cause externe** (commits WIP concurrents, attribution prouvee par worktree temoin), re-vert des le batch 19 (§20/§21). Les 2 « failures » annoncees a tort en batch 12 ne se reproduisaient pas (§15, retraction) ; la vraie cause des fluctuations d'ordre etait un trou d'isolation du harnais pytest qui **ecrivait dans la base de dev `kamlog_erp.db`**  corrige, verrouille par meta-tests et `DB_CHANGED=False` sur chaque run definitif (§16, confirme aux §17 a §25 ; au run du batch 21 le hash etait **illisible**  base verrouillee par un process de dev concurrent  declare comme tel plutot que pretendu ; aux runs des batches 22 et 23 il etait **lisible et vierge**  horodatage de la base anterieur aux runs, voir §24/§25). |
| `import app.main` (tous routers chargés, plus aucun ImportError avalé) | ✅ OK  endpoint `/api/v1/finance/factures/{id}/pdf` déclaré (**1142** routes OpenAPI au batch 23 ; +1 d'origine concurrente depuis 1141 au batch 22 — les conversions RBAC n'ajoutent aucune route) |
| `npx tsc --noEmit` (frontend) | ❌ au run du batch 23 : `TS1005 '}' expected` dans `portail-commercial/page.tsx`, fichier **non committe** (etat `M`) d'une session concurrente active, aucun lien avec le lot 16-23  voir §25. ✅ EXIT=0 au run du batch 22 (l'erreur `ReceiptText` du §23, cause concurrente, avait ete reparee par son auteur). |

---

## 1. Backend  Faux succès légaux → 501 honnêtes

| Fichier | Avant (mensonge) | Après (vérité) |
|---|---|---|
| `routers/v1/real_customs.py` | Circuit CAMCIS via `hash % 4`, quittances `QUIT-DGD-{random}`, formalités GUCE inventées, cautions "apurées" en dur | **Tous les endpoints → 501** avec le besoin réel explicité (connecteur SYDONIA World/identifiants DGD ou saisie manuelle notifiée) |
| `routers/v1/bill_of_loading.py` | Validation BSC auto + référence `CNCC-VAL-` fabriquée | `reference_cncc` **obligatoire, saisie manuellement** (400 sinon) ; réponse avec `validation_automatique_cncc: False` |
| `services/transit_douane_avance_service.py` | `teletransmettre_guce` renvoyait "ACQUITTE_ELECTRONIQUE" | 501 ; statut DUM réaliste `PREPAREE_LOCALEMENT` (plus de `DEPOSEE_SYDONIA` simulé) |
| `routers/v1/goods_declaration.py` | Taux de change codé en dur 615.0 (≠ parité BEAC 655.957), `reference_sydonia` fabriquée | Taux lu dans `TauxReferenceBEAC` (ou 400 si absent) ; `reference_sydonia=None` jusqu'au retour réel du déclarant |
| `services/paiement_local.py` | MTN/Orange Money/virements : `"statut": "succes"` inconditionnel | `BROUILLON_LOCAL, provider_contacte: False` ; vérification/annulation/relevé → 501 |
| `routers/v1/paiement_local.py` | Endpoints **publics** (sans auth) | `get_current_user` partout + `except HTTPException: raise` (les 501 ne sont plus transformés en 400) |
| `services/b2b_portal_service.py` | Checkout B2B simulé | 501 + docstring d'avertissement |
| `routers/v1/subscription.py` | Webhook Mobile Money sans aucune vérification de signature (n'importe qui pouvait marquer un abonnement payé) | **HMAC-SHA256 fail-closed** (503 si secret non configuré), comparaison timing-safe, contrôle du montant vs `PLANS_CATALOG` |
| `core/config.py` |  | `MOBILE_MONEY_WEBHOOK_SECRET` ajouté |
| `services/rh_avance_service.py` | 4 × `500000  # Placeholder` pour CNPS/IR/bulletins/DIPE | Calculs réels depuis la table `Salaire` (`TAUX_CNPS_PENSION=4.2%`, `ACCIDENTS=0.5%`, barème IRGM progressif) ; **refuse de générer un bulletin sans salaire enregistré** |
| `services/rh_service.py` | `taux_impot = 0.02  # Placeholder` | Délégué à `PaieOHADAService` (source unique de vérité CNPS/IRGM) |
| `scripts/seed_data.py` | Message "SYDONIA+ opérationnels à 100%" | Supprimé (c'était faux) |
| `app/main.py` | 6 blocs `except ImportError: logger.warning(...)` avalant silencieusement la perte des modules Cameroun/CEMAC, avancés, v2.0, WS… | **Chaque bloc `raise`** (+ `logger.critical`) : un déploiement qui casse vaut mieux qu'un SaaS amputé en silence (les 292 tests prouvent que tous les modules s'importent bien aujourd'hui) |

## 2. Frontend  P0 UX & données inventées

| Fichier | Correction |
|---|---|
| `lib/utils.ts` | `formatCurrency` plantait (`RangeError: Invalid currency code : FCFA`) → normalisation **FCFA → XAF**, 0 décimale pour XAF |
| `app/layout.tsx` | Zoom désactivé (`maximumScale: 1, userScalable: false`, contraire WCAG 1.4.4, gênant pour seniors) → **zoom réactivé** |
| `(app)/qhse/create`, `acconage/create`, `maintenance/create` | Pages "en construction" mortes → `redirect('/<module>/edit')` (les vrais formulaires existent) |
| `(app)/portail-magasinier/page.tsx` | Articles de picking **inventés** (ART-PKG-01…) → lignes réelles via `removalSlipAPI.getById` ; 3 articles d'inventaire fictifs → stocks réels (`magasinAPI.getStocks`) avec quantités théoriques ; bouton "Valider le Bon de Sortie" mort (simple toast) → branché sur `removalSlipAPI.validate` (stock réellement décrémenté) ; faux "transmis au chef magasin" et "archivé" → messages honnêtes ; fallbacks `Client Industriel`/`Zone Expédition Quai 4` → `` ; états vides ajoutés |
| `(app)/acconage/view/page.tsx` | Fallbacks inventés (`22 mouvements/heure`, `Portique STS 01 & STS 02`, `Effectué par PAD Harbour`, `Conforme au plan de tirage`…) → `Non renseigné(e)` / `Non mesurée` |
| `components/ui/GenericDataPage.tsx` | Bug `hasRowActions = !!(... || true)` (colonne d'actions toujours affichée) → corrigé ; actions en `opacity-0 group-hover` **invisibles au tactile** → toujours visibles + `aria-label` + cible 40px ; bouton "Filtrer" sans `onClick` (UI mensongère) → retiré ; export CSV `,` → **`;` + CRLF + BOM** (Excel FR/Afrique) ; valeur nulle dans le tiroir détail → "Non renseigné" |

---

## 3. Reste à faire  structurel (P1/P2), hors périmètre d'un batch de correction

Ces points demandent des semaines de travail (données officielles, connectors, refonte),
pas des correctifs. Ils sont listés ici pour ne pas être oubliés :

### P1  Conformité & justesse des calculs
1. **Tables de références** : ✅ **INFRASTRUCTURE PRÊTE (batch 5, voir §7)**  pipeline d'import `scripts/import_tarif_cemac.py` (validation stricte, provenance, aucune invention de taux) + colonnes de traçabilité + CRUD admin. ⏳ **IL MANQUE ENCORE LA DONNEE OFFICIELLE** : l'operateur doit fournir le fichier du tarif CEMAC reel (arrete / export DGD-CAMCIS). Tant qu'il n'est pas importe, le moteur reste en `simulation=True`  c'est explicite, jamais masque.
2. ~~**Unifier les 3 calculateurs `TaxationDouaniereService` divergents**~~ → **CORRIGÉ (batch 4, voir §6)** : un moteur UNIQUE piloté par la position SH, partagé par transit / transit-avance / fiscalité cameroun / intégration / K-modules.
3. ~~**Numérotation légale des factures**~~ → **CORRIGÉ (batch 3, voir §5)** : séquence continue sans trou par (entreprise, type, année)  remplace les IDs recyclables et les numéros uuid/timestamp.
4. ~~**PDF facturation cassé**~~ → **CORRIGÉ (batch 2, voir §4)** : template restauré, générateur WeasyPrint branché, endpoint `GET /api/v1/finance/factures/{id}/pdf`.
5. ~~**Tests fiscaux tautologiques**~~ → **CORRIGÉ (batch 9, voir §11)** : formules parallèles supprimées, tests réécris sur `PaieOHADAService.calculer_irmg()` + constantes CNPS réelles, valeurs de référence main-calculées.
6. **Connecteurs réels ou exports manuels conformes** : SYDONIA/GUCE (format DUM officiel), CNPS (fichier OD), DGI  décider par module : intégration API payante ou export imprimable signé.

### P2  Couverture métier de la chaîne portuaire
7. ~~**Dossier unique de marchandise** (BL → déclaration → acconage → magasin → livraison → facture)~~ → **VUE CONSOLIDÉE HONNÊTE LIVRÉE (batch 6, voir §8) + CHAÎNE FERMÉE (batch 8, voir §10)** : `GET /api/v1/acconage/dossier-marchandise` retrace tout ce qui est **réellement relié** (clé étrangère, numéro physique de conteneur, ou colonnes `conteneur_id`/`escale_id`/`numero_bl` de la migration 024). Les 4 étapes jadis `non_liciable_en_base` sont désormais jointurables par lien saisi → état `reel` ou `absent`, jamais inventé.
8. ~~**Moteur de tarification magasinage/détention** (redevances portuaires, surestaries, barèmes)~~ → **FAUX CALCUL CORRIGÉ (batch 7, voir §9)** : `calculate_port_dues_cemac` inventait 9 taux « officiels » **et** des quantités (45/62/3 jours) en ignorant l'`escale_id`, puis le routeur estampillait `GENEREE_VALIDEE`. Désormais quantités dérivées de l'escale réelle + prix depuis la table officielle `TarifPortuaire` (501 si non importés, jamais un taux inventé), statut brouillon non certifié. Surestaries : le calcul exige un taux réel (aucun défaut fantaisiste).
9. **Cycle Order-to-Cash / Order-to-ship complet** pour le port (réservation créneau → PAD → facturation client automatique).
10. **Édition de bon de sortie / bon de livraison et circuit de signature** (le magasinier ne peut que valider, pas corriger une ligne).
11. ~~**PWA hors-ligne réel**~~ → **CORRIGÉ (batch 2, voir §4)** : `sw.js` créé et enregistré, `Authorization` ajoutée aux syncs, base d'API corrigée, page `/offline`.

### Qualité de vie (quick wins restants)
- ~~Remplacer les `any` des pages branchées cette semaine par les types existants de `src/types/`.~~ → **PARTIELLEMENT FAIT (batch 10, voir §12)** : `src/types/transport.ts` était un **contrat mort** dont les champs ne correspondaient à aucun schéma backend  réaligné sur le vrai contrat et adopté par `transport/planning` + `transport/control`. Les ~700 `any` restants dans `src/` exigent la même réécriture module par module.
- ~~Ajouter un linteau CI (`tsc --noEmit` + `pytest`) sur les rapports de coverage par module.~~ → **VERROU ZERO-MOCK AJOUTE (batch 11, voir §13)** : `audit_frontend.py --strict-honesty` est désormais une étape bloquante de `test-frontend` dans `.github/workflows/ci-cd.yml`. `pytest` (backend) et `tsc --noEmit` (frontend) y étaient déjà ; la regression sur `fake_data` / `dead_buttons` / `broken_links` / `ghost_routes` est ce qui manquait. Le coverage par module (codecov) reste a affiner.

---

## 4. Batch 2  PDF facturation & PWA hors-ligne (corrigés)

### PDF de facture (chaîne réellement créée, elle n'existait pas)

| Fichier | Ce qui a été fait |
|---|---|
| `app/templates/pdf/facture.html.j2` | Était **corrompu (2880 octets NUL, et lisible depuis git uniquement)** → restauré (188 lignes, mentions DGI/OHADA : NIF, RCCM, capital, RIB, TVA 19,25%, montant en lettres, badge statut, avertissement "Document provisoire" pour brouillon, états vides honnêtes). Note : les outils d'édition échouaient silencieusement sur ce fichier binaire → restauration via `scripts/restore_facture_template.py` (réexécutable). |
| `app/utils/pdf_generator.py` (nouveau) | Jinja2 → HTML → WeasyPrint. Échec **honnête** : 501 si jinja2/WeasyPrint/Pango-Cairo manquent (cas des postes de dev Windows), jamais de faux PDF. Inclut `montant_en_lettres` (français : 71 = "soixante et onze", 1000 = "mille", 80 = "quatre-vingts"…). |
| `app/routers/v1/finance.py` | Nouveau endpoint `GET /api/v1/finance/factures/{id}/pdf` (auth requise) : facture + lignes réelles + client (`Tiers`) + société (`Company`) → PDF `application/pdf`, nom de fichier = numéro de facture. |
| `requirements.txt` | `jinja2==3.1.4` épinglé explicitement (utilisé directement par le code). |
| `tests/unit/test_pdf_generator.py` (nouveau) | 23 tests : régression orthographe des nombres, intégrité binaire du template, 501 honnête quand WeasyPrint absent, `%PDF-` réel sinon. |

➡️ En production Docker (weasyprint==60.1 + Pango/Cairo dans l'image), l'endpoint renvoie le vrai PDF. En local sans ces DLL : 501 explicite.

### PWA hors-ligne (le "offline" promis fonctionne désormais)

| Fichier | Correction |
|---|---|
| `src/utils/offlineSync.ts` | Le fetch de synchronisation **n'envoyait pas l'en-tête `Authorization`** → ajouté (token mémoire/localStorage, refresh automatique sur 401) ; `baseUrl` par défaut = `''` → résout désormais la **base de l'API** ; sans session, l'opération reste PENDING (pas de FAILED mensonger). |
| `src/components/layout/ModuleHeader.tsx` | Passait `window.location.origin` (origine **frontend**) comme base de sync → chaque opération en file aurait fait un 404 contre Next.js → retiré (base API résolue par api-client). |
| `src/lib/api-client.ts` | Exports `getAccessToken()`, `getApiBaseUrl()`, `tryRefreshToken()` (mêmes sources de vérité que l'intercepteur axios). |
| `public/sw.js` (nouveau) | N'existait **nulle part** (aucun service worker, aucune inscription dans tout le dépôt). Créé : precache de `/offline` + manifest, cache-first des assets statiques immuables, réseau-d'abord pour les navigations avec repli cache puis page offline. **Ne touche jamais aux appels API** : aucune donnée métier inventée ni périmée. |
| `src/app/offline/page.tsx` (nouveau) | Page hors connexion franche (aucun appel API, explication de la file d'attente). |
| `src/components/shared/ServiceWorkerRegistrar.tsx` (nouveau) | Inscription du sw **en production seulement** (monté dans `Providers.tsx`), silencieuse si le navigateur ne supporte pas. |

---

## 5. Batch 3  Numérotation légale des factures (exigence DGI : suite continue sans trou)

**Problème** : les numéros de pièce étaient fabriqués localement par 4 mécanismes non conformes 
ID auto-incrémenté recyclable, `uuid`, `FAC-AUTO-{company}-{timestamp}`, `FAC-POD-{mission}-{timestamp}`.
Un numéro annulé/libéré pouvait être ré-attribué, et l'ordre dépendait de l'horloge : contraire à
l'obligation DGI d'une **séquence chronologique continue sans rupture**.

| Fichier | Ce qui a été fait |
|---|---|
| `app/models/numerotation.py` (nouveau) | `SequenceNumerotation` : compteur par `(company_id, type_document, exercice)` avec contrainte d'unicité. |
| `app/utils/numerotation.py` (nouveau) | `prochaine_reference(db, type, company_id, date_reference)` : verrouille la ligne de séquence (`with_for_update`), **amorce au max des numéros historiques déjà posés**, incrémente, format `FAC-AAAA-0001`. **Ne commite pas** : vit dans la transaction appelante → un rollback restitue le numéro (aucun trou). Type inconnu → **400 honnête** (jamais de préfixe inventé). |
| `migrations/versions/022_add_sequences_numerotation.py` (nouveau) | Création idempotente de `sequences_numerotation` (même patron que 021, parité stricte ORM). |
| `app/services/finance_service.py` | `creer_facture` réécrit : auto-numérotation quand aucun numéro fourni, calcul réel TVA/TTC, statut `brouillon`. **Suppression de 2 monkey-patches legacy** (`_legacy_facture_creer`, `_legacy_ligne_facture_ajouter`) qui **cassaient `POST /finance/factures`** (TypeError : 9 params attendus vs 7 passés). |
| `app/routers/v1/auto_invoicing.py` | `numero = FAC-{uuid}` → `prochaine_reference(...)` (préfixe selon le type de pièce). |
| `app/services/events/workflow_orchestrator.py` | `FAC-AUTO-{company}-{timestamp}` → `prochaine_reference(db, "FACTURE", company_id)`. |
| `app/routers/v1/transport_exploitation.py` | Facturation e-POD `FAC-POD-{mission}-{timestamp}` → `prochaine_reference(...)` ; marqueur d'idempotence `[epod:{mission.id}]` conservé dans les notes (rejeu = même facture). |
| `app/schemas/finance.py` | `numero_facture` devient **optionnel** (le serveur délivre le numéro légal). |
| `tests/unit/test_numerotation.py` (nouveau) | 8 tests : suite continue, reprise à l'année, préfixe AVOIR distinct, type inconnu → 400, amorçage au max historique, rollback sans trou, isolation par entreprise, et `POST /finance/factures` sans numéro → séquence légale + TVA réelle. |

➡️ Aucun numéro déjà émis ne peut être ré-attribué ni sauté ; la parité création facturation / transport / workflow est garantie par un compteur unique par entreprise et par nature de pièce.

---

## 6. Batch 4  Moteur UNIQUE de liquidation douanière CEMAC (fin de la divergence)

**Problème** : cinq sites calculaient séparément les droits/taxes d'un même conteneur, avec des
formules **incohérentes**  base de la TVA tantôt `(valeur)` seule, tantôt `(valeur + DD)`, tantôt
`(valeur + DD + redevance + CCI)` ; taux exprimés en fraction (`0.20`) ici, en pourcentage (`20.0`)
là ; composantes divergentes (CCI à 1 % pour l'un, 0,4 % pour l'autre ; redevance 0,45 % ou forfait
fixe 15 000 F ; précompte IS présent ou absent) ; droit de douane **codé en dur à 20 %** ignorant
la position SH réellement saisie. Résultat : un même conteneur pouvait donner 4 montants différents
selon l'écran.

| Fichier | Ce qui a été fait |
|---|---|
| `app/services/taxation_douaniere.py` (nouveau) | **Source de vérité unique** : `calculer_liquidation()` applique LA formule CEMAC centralisée (DD + redevance 0,45 % + CCI 1 % + OHADA 0,05 % ; base TVA = valeur+DD+redevance+CCI ; TVA 19,25 % ; précompte IS 2,2 %). Résolution du taux DD par ordre strict : nomenclature SH en base → taux explicite → catégorie TEC → défaut de simulation, **sinon `ValueError`** (aucun taux fantôme). Normalise %/fraction, gère l'exonération d'origine (CEMAC/ZLECAF) et le régime (seul IM4 liquide). Chaque résultat porte `source_taux`, `simulation` et une `note`. |
| `services/transit_douane_avance_service.py` | `TaxationDouaniereService.calculer_droits_et_taxes` ne code plus 20 % en dur : délègue au moteur, consulte la nomenclature (`db` threaded through `DUMService.creer_dum`). |
| `services/transit_avance_service.py` | `NomenclatureCEMACService.calculer_droits` et `creer_declaration` délèguent au moteur → **correction du bug de base TVA** (la TVA n'est plus calculée sur la seule valeur déclarée). |
| `services/cameroun_cemac_service.py` | `calculer_droits_douane` délègue (clés legacy conservées + `detail`). |
| `routers/v1/integration_cameroun.py` & `routers/v1/new_k_modules.py` | Les deux calculateurs inline (`/calculer-droits`, `/transit/calculateur-taxe-cemac`) appellent le moteur ; **table TEC alignée** sur `{0:0%,1:5%,2:10%,3:20%}`. |
| `tests/unit/test_taxation_douaniere.py` (nouveau) | 9 tests à **valeurs de référence calculées à la main** (non tautologiques) + test de non-régression prouvant que les modules jadis divergents convergent désormais vers le même total ; échec honnête si taux irresoluble. |

➡️ Le même conteneur donne désormais **exactement le même montant** sur tous les écrans. Les taux
restent une **estimation** tant que le tarif officiel CEMAC n'est pas importé (P1 #1, toujours ouvert) :
c'est explicite via `simulation` / `source_taux` / `note`, jamais masqué.

---

## 7. Batch 5  Tarif CEMAC : pipeline d'import OFFICIEL + traçabilité (P1 #1, partie infra)

**Contrainte d'honnêteté** : P1 #1 réclame le **tarif officiel CEMAC** (positions SH → taux). Cette
donnée est un **input réglementaire externe** que le projet ne peut pas inventer (c'est exactement le
genre de « donnée légale/financière fabriquée » que la politique « zéro-mock » interdit). Ce batch livre
donc **toute la machinerie honnête** pour charger cette donnée, et **jamais de taux fictif**.

| Fichier | Ce qui a été fait |
|---|---|
| `scripts/import_tarif_cemac.py` (nouveau) | Import CLI d'un fichier **officiel** (CSV/TSV/JSON). Validation stricte : `code_hs` 6–8 chiffres, `taux_dd`/`taux_tva` numériques ∈ [0..100]. **Toute ligne douteuse est rejetée, jamais complétée par un défaut.** Upsert par `code_hs`, `--dry-run`, `--source` (référence officielle obligatoire pour écrire), `--print-template` (en-tête seule, sans faux taux). Echec bruyant si fichier absent/vide/0 ligne valide. |
| `app/models/transit_avance.py` (`NomenclatureCEMAC`) | + `source_reference` (provenance du taux) et `date_fin_effet` (validité) : un taux sans origine identifiable est traçable comme « saisie manuelle ». |
| `migrations/versions/023_add_tarif_cemac_provenance.py` (nouveau) | Ajout **idempotent** (inspection colonnes) des 2 colonnes de provenance ; `downgrade` en batch mode SQLite ; n'écrit **aucune valeur**. |
| `app/schemas/transit_avance.py` | Champs de provenance exposés en Create/Update/Response. |
| `app/routers/v1/transit_avance.py` | Nouveau `GET /nomenclature-cemac` (liste/recherche) + `PUT /nomenclature-cemac/{code_hs}` qui **refuse (400)** toute correction de taux sans `source_reference`. Le `POST` de création horodate « saisie manuelle (agent) ». |
| `tests/unit/test_import_tarif_cemac.py` (nouveau) | 9 tests : rejet sans invention, dérivation déterministe chapitre/position, **import → le moteur consomme un taux réel (`simulation=False`)**, dry-run sans écriture, upsert + provenance, refus admin sans source. |

➡️ Dès que l'opérateur dépose le fichier du tarif officiel, `import_tarif_cemac.py` peuple la
nomenclature et le moteur de liquidation (batch 4) bascule **automatiquement** des taux simulés vers
des taux réels tracés. **Aucune valeur tarifaire n'a été inventée** par ces corrections.

---

## 8. Batch 6  Dossier unique de marchandise : vue consolidée HONNÊTE (P2 #7)

**Problème** : la chaîne portuaire (arrivée navire → acconage → B/L → douane → magasin → livraison
→ facture) vit dans 5 modules aux identifiants propres, sans vue consolidée. Mais une « fiche
dossier » qui **relierait** ces étapes par des correspondances inventées violerait la politique
zéro-mock (un lien fantaisiste est un faux acte opérationnel).

**État des lieux des liens RÉELS** (cartographié avant tout codage) :
- **Relié par clé étrangère enforcee** : `connaissements.conteneur_id → conteneurs`,
  `packing_lists.conteneur_id`, `conteneurs.navire_id → navires`, `connaissements.escale_id`,
  `operations_acconage.escale_id`.
- **Relié par numéro physique de conteneur** (identifiant universel du port, légitime) :
  `conteneurs_cycle.numero`, `parc_mouvements.numero_conteneur` (gate in/out, cycle déchargement→stocké→sorti).
- **AUCUNE colonne ne relie au conteneur** : `declarations_douaniere_avance`, `declarations_entrepot`
  (magasin), `missions` (transport) et `factures_ohada` ne portent ni `numero_conteneur` ni référence
  de B/L. Ces étapes sont donc **non liciables en base** aujourd'hui.

| Fichier | Ce qui a été fait |
|---|---|
| `app/services/dossier_marchandise.py` (nouveau) | `consigner_dossier_marchandise(db, numero_conteneur, numero_bl)` : ancre = numéro de conteneur **ou** de B/L. Parcourt chaque étape et ne renvoie que ce qui est **réellement** joint (FK ou numéro physique). Chaque étape porte `etat ∈ {reel, absent, non_liciable_en_base}`, un `mode_correspondance` explicite, et des `enregistrements` lus dans les colonnes réelles. **Rien n'est deviné.** Ancre inconnue → **404** franche ; aucun identifiant → **400**. |
| `app/routers/v1/acconage.py` | Nouveau `GET /api/v1/acconage/dossier-marchandise?numero_conteneur=… ou numero_bl=…` (lecture seule). |
| `tests/unit/test_dossier_marchandise.py` (nouveau) | 8 tests : chaîne réelle exposée (conteneur/arrivee/B-L/acconage/packing = `reel`), ancre par B/L résout le conteneur, cycle+parc joints par numéro, **étapes non reliées = `non_liciable_en_base` et `enregistrements == []`**, absence = `absent` (jamais un faux `reel`), 404 ancre inconnue, 400 sans clé, endpoint de bout en bout. |

➡️ L'opérateur saisit un numéro de conteneur (ou de B/L) et obtient **tout le parcours réellement
documenté**, avec les maillons manquants **explicitement signalés** plutôt que comblés par des
fakes. **Écart d'architecture mis en évidence** (à traiter en P1) : ajouter une colonne
`numero_conteneur`/`dossier_id` sur la déclaration douanière, le magasin, la mission et la facture
pour fermer la chaîne de bout en bout.

---

## 9. Batch 7  Redevances portuaires PAD/PAK : fin du faux calcul certifié (P2 #8, urgence honnêteté)

**Problème (de nature P0)** : `PortAdvancedTOSService.calculate_port_dues_cemac(escale_id, …)`
**ignorait complètement `escale_id`** (aucune requête) et **recodait en dur** 9 taux présentés comme
« officiels » (chenal 425 000, pilotage, remorquage, stationnement 185 000/jour, droits de quai,
THC, ISPS) **ainsi que des quantités inventées** : `nb_tc20 = 45`, `nb_tc40 = 62`,
`duree_escale_jours = 3`. Elle renvoyait donc **la même facture fantaisiste pour n'importe quelle
escale**, avec une `reference_facture` fabriquée. Le routeur `POST /facturation-quai/{id}/generer-facture`
ajoutait `statut_facturation = "GENEREE_VALIDEE"` + `date_validation` : un **faux document financier
certifié**, montant exigible d'un armateur jamais réellement calculé.

Pourtant la **vraie source de tarifs** existait déjà : le modèle `TarifPortuaire` (table
`tarifs_portuaires`, code/categorie/unité/prix TVA/référence réglementaire/date d'application) et son
CRUD `app/routers/v1/port_pricing.py`  entièrement **ignorés** par le calcul.

| Fichier | Ce qui a été fait |
|---|---|
| `app/services/acconage_service.py` (`calculate_port_dues_cemac`) | Réécriture pilotée par données réelles. Signature `(db, escale_id, port_code)`. Escale inconnue → **404**. **Quantités dérivées de la base** : conteneurs rattachés via `connaissements.escale_id` (répartis 20'/40' selon le type réellement saisi), durée de stationnement depuis les dates réelles arrivée/départ. **Prix unitaires lus dans `TarifPortuaire`** (`code_tarif` actif) : si un tarif requis manque → **501** nommant les codes à importer  **aucun taux inventé** (même politique que le tarif douanier CEMAC). TVA depuis le tarif. Durée inconnue → la ligne stationnement est **exclue avec avertissement**, jamais un forfait deviné. Statut honnête `BROUILLON_ESTIMATION_NON_CERTIFIE`. |
| `app/routers/v1/acconage.py` | Les deux endpoints passent désormais `db` au service. Suppression du tampon mensonger `GENEREE_VALIDEE`/`date_validation` : `generer-facture` renvoie le brouillon d'estimation + une note explicite « aucune émission signée n'a eu lieu ». |
| `tests/unit/test_redevances_portuaires.py` (nouveau) | 6 tests à **valeurs vérifiées à la main** (non tautologiques) : 404 escale inconnue, 501 tarifs non importés (détail nomme les codes), total réel correct pour 2×20′+1×40′ sur 3 jours, quantités à 0 (jamais 45/62) quand aucun conteneur rattaché, exclusion honnête du stationnement si durée inconnue, et le routeur ne certifie plus (`GENEREE_VALIDEE` absent, `statut == BROUILLON_…`). |

➡️ La facture de redevances est désormais **le reflet chiffré d'une escale réelle** et des **tarifs
officiels importés**, ou répond **501** en disant quoi importer. Aucun montant, aucune quantité,
aucune certification ne sont fabriqués. ⏳ Les taux PAD/PAK officiels doivent être chargés dans
`TarifPortuaire` par l'opérateur (comme le tarif CEMAC) pour que l'estimation passe de 501 à un total réel.

**Vérification batch 7** : suite complète `python -m pytest tests` → **374 passed, 0 failed** (896 s).
Une exécution antérieure avait affiché 3 échecs dans `tests/unit/test_audit_api_gaps.py`
(tests de logique pure sur regex, sans lien avec ce batch) : **non reproductibles** sur 3 runs
depuis (isolation, combinaisons ciblées, suite complète), avec le même code. Le décompte de ce
run anormal (373 collectés) ne correspondait pas non plus à l'état final du disque (374) 
signature d'un run effectué pendant que des fichiers étaient encore en cours d'écriture.

---

## 10. Batch 8  Chaîne documentaire close par liens saisis (P1 : fin des 4 étapes « non liciables »)

**Problème** : la vue consolidée du dossier de marchandise (batch 6) affichait honnêtement
4 étapes en `non_liciable_en_base`  **déclaration douanière, magasin sous douane, mission de
livraison, facture**  faute de tout chemin les rattachant au conteneur/B/L de l'ancre. Ces tables
(`declarations_douaniere_avance`, `declarations_entrepot`, `missions`, `factures_ohada`) ne
portaient **aucune colonne** `conteneur_id` / `escale_id` / `numero_bl` : le chaînon manquant était
structurel, pas logique.

| Fichier | Ce qui a été fait |
|---|---|
| `migrations/versions/024_add_chaine_documentaire_links.py` (nouveau) | Ajout de colonnes **nullables** `conteneur_id` (FK→`conteneurs`), `escale_id` (FK→`escales`) et/ou `numero_bl` sur les 4 tables, + index `ix_<table>_<col>`. **Idempotent** (garde `sa.inspect`), `batch_alter_table` pour SQLite, FK créée seulement si la table parente existe. `downgrade` supprime d'abord les index puis les colonnes (sinon la recréation SQLite échoue sur « no such column »). |
| `app/models/transit_avance.py`, `magasin_douane.py`, `transport.py`, `finance_ohada.py` | Colonnes ORM correspondantes ajoutées aux 4 modèles (`conteneur_id`, `escale_id`, `numero_bl` selon la table). |
| `app/schemas/transit_avance.py`, `magasin_douane.py`, `transport.py` | Champs `Optional` ajoutés aux `*Base` → propagés aux Create/Response : les API acceptent désormais les liens à la saisie. |
| `app/routers/v1/auto_invoicing.py` | La création de facture propagate `conteneur_id`/`escale_id` depuis le corps vers `FactureNew` (au lieu de les ignorer silencieusement). |
| `app/services/dossier_marchandise.py` | La boucle codée en dur « 8-11. étapes NON LICIEES » est **remplacée par `_aval()`** : chaque étape interroge réellement sa table par `conteneur_id = ancre` **OU** `numero_bl ∈ B/L` **OU** `escale_id ∈ escales`. Renvoie `reel` si des lignes existent, `absent` sinon. **Aucun lien deviné** par proximité de date, client ou montant. |

**Régression corrigée au passage** : `transport.py` déclarait des doublons
(`/missions/chauffeur/{id}`, `/missions/client/{id}`, `/chauffeurs/{id}`, `/chauffeurs/{id}/documents`)
qui, `transport.router` étant monté **avant** `transport_exploitation.router` sur le même préfixe,
**masquaient** les versions riches de ce dernier (objet `origine`/`camion`/`chauffeur` imbriqué,
`statut` dérivé, dossier de pièces en tableau nu). Doublons supprimés, commentaire NOTE laissé pour
empêcher toute réintroduction.

| `tests/unit/test_chaine_documentaire.py` (nouveau) | 5 tests : idempotence + aller-retour de la migration 024, facture reliée par `escale_id` visible dans le dossier, mission reliée par `numero_bl` visible, API mission accepte `conteneur_id` à la création, API facture accepte `escale_id`. |
| `tests/unit/test_dossier_marchandise.py` | Assertions mises à jour (`non_liciable_en_base` → `absent` pour les étapes sans lien saisi) + 2 tests : chaîne aval entièrement fermée par liens saisis, et **négatif** (une mission d'un autre conteneur n'apparaît jamais). |

**Vérification batch 8** : `test_transport_exploitation.py` → **34 passed** (régression levée) ;
suite complète `python -m pytest tests` → **384 passed, 0 failed** (1 103 s).

➡️ Les 4 étapes ne sont plus « Structurellement impossibles » : dès que l'opérateur **saisit le lien**
sur la ligne, le document apparaît dans le dossier ; tant qu'il n'est pas saisi, l'étape est
`absent` (et non un faux `reel`). La chaîne est fermée **par la donnée réelle, jamais par une déduction**.

---

## 11. Batch 9  Tests fiscaux : suppression des tautologies (P1 #5)

**Problème** : `tests/test_calculs_metiers.py` (278 lignes) définissait **5 formules
parallèles locales** (IRGM, CNPS, TEC, FIFO/FEFO, TCO) et testait **ces formules contre
elles-mêmes** sans JAMAIS importer ni appeler le code applicatif. Pire, les valeurs
étaient **incohérentes avec les services réels** :

| Domaine | Ce que le test tautologique inventait | Ce que le service réel utilise |
|---|---|---|
| IRGM | Barème 0/11/16,5/25/35% à 62k/310k/620k/1,035M | `PaieOHADAService.calculer_irmg()` : 0/10/15/20/25/30% à 50k/100k/200k/500k/1M |
| CNPS | Part salariale 2,8%, patronale 17,2%, plafond 750k | `TAUX_CNPS_PENSION` 4,2% + `TAUX_CNPS_ACCIDENTS` 0,5% = 4,7%, **sans plafond** |
| TEC | Redevance informatique 0,35%, pas d'OHADA, pas de précompte IS | `calculer_liquidation()` : RI 0,45%, OHADA 0,05%, précompte IS 2,2% |
| FEFO/TCO | `sorted()` et `sum()` locaux | Service réel non fonctionnel (colonne inexistante / mock) |

➡️ **Ces 20 tests passaient mais ne vérifiaient RIEN sur le code en production.** Un bug dans `calculer_irmg` ou un changement de taux CNPS n'aurait JAMAIS été détecté.

| Fichier | Ce qui a été fait |
|---|---|
| `tests/test_calculs_metiers.py` (réécrit, 144 lignes) | **Suppression de toutes les formules parallèles.** 13 tests IRGM appellent directement `PaieOHADAService.calculer_irmg()` et vérifient 5 paliers + boundaries + progressivité. 5 tests CNPS vérifient les **constantes réelles** du service (4,2%/0,5%, pas de plafond). 1 test TEC pointe vers `test_taxation_douaniere.py` (smoke check : RI 0,45% et non 0,35%). 2 xfail `strict=True` : FEFO (service référence `Stock.article_id` inexistant) et TCO (service retourne un mock codé en dur). |

**Vérification batch 9** : suite complète `python -m pytest tests` → **393 passed, 2 xfailed, 0 failed** (858 s).

➡️ Les tests IRGM/CNPS sont désormais un **contrat de non-régression sur le VRAI barème** :
si un développeur modifie `calculer_irmg()` ou change un taux CNPS sans mise à jour
légale, le test **échoue**. Le FEFO et le TCO sont explicitement marqués comme des
P1-gap (xfail strict = si le service est réparé sans activer le test, pytest le signale).

---

## 12. Batch 10  Frontend transport : suppression des `any` (quick win)

**Problème** : `src/types/transport.ts::Mission` était un type **mort**  0 import
dans tout `src/` (`grep "from '@/types/transport'"` → 0 résultat)  dont les champs
(`id: string`, `origin`, `destination`, `merchandise`, `status: 'pending' | 'in_progress' | …`)
ne correspondaient à **aucun** schéma backend. Le vrai `MissionResponse`
(`app/schemas/transport.py`) expose `id: number`, `point_depart`, `point_arrivee`,
`statut: 'planifiee' | 'en_cours' | 'terminee' | 'annulee' | 'en_retard'`. Comme
le type était faux, les pages transport roulaient en `any`, ce qui masquait les
fautes de frappe (statut comparé `'EN_ROUTE'` qui ne matchait jamais, clés
`m.immatriculation` / `m.conducteur` / `m.client` lues sur `MissionResponse` alors
qu'elles n'existent nulle part dans le schéma → colonnes systématiquement vides).

| Fichier | Ce qui a été fait |
|---|---|
| `src/types/transport.ts` (159 lignes, entièrement réécrit) | Types **alignés sur le contrat backend réel** : `MissionResponse` (avec `conteneur_id?` et `numero_bl?` ajoutés par la migration 024), `CamionResponse`, `ConducteurResponse`, `CorridorCEMAC`, `CorridorsCEMACResponse`, `AlerteMaintenancePredictive`, `TcoFleetResponse` ; unions littérales `MissionStatut` / `CamionStatut`. Un alias `Mission = MissionResponse` est conservé pour faire **casser explicitement** les anciens consumers qui lisaient `origin`/`destination`/`status`. |
| `src/app/(app)/transport/planning/page.tsx` | `useState<any[]>` → `useState<MissionResponse[]>` ; suppression des `(m: any)` dans les filtres. |
| `src/app/(app)/transport/control/page.tsx` | 5 `useQuery` typés (`MissionResponse[]`, `CorridorsCEMACResponse \| null`, `TcoFleetResponse \| null`, `CamionResponse[]`, `ConducteurResponse[]`), `useMutation<{ kms_a_vide_economises?: number } \| null>` typé, `new Map<number, string>(...)`, interface locale `MissionRow` (view model distinct du contrat API, pour garder `origin/destination/status/eta` côté vue sans mentir sur l'API), suppression de tous les `(x: any)`. Les jointures camion/chauffeur passent par deux requêtes séparées (`immatriculations.get(m.camion_id)`, `nomsChauffeurs.get(m.conducteur_id)`) : le contrat `MissionResponse` ne renvoie que les FK brutes. |

**Bug latent débusqué par le typage strict** (ligne 317 de `transport/control/page.tsx`) :
le JSX affichait `-{alt.echeance_km} km` dans le panneau des alertes TCO. Le backend
ne renvoie **jamais** de champ `echeance_km` : les deux branches de
`get_tco_fleet_analytics` exposent `echeance: string | null` (ISO date pour
maintenance périodique, `None` pour panne) et `priorite: 'CRITIQUE' | 'HAUTE' | 'MOYENNE'`.
Sans typage, le rendu affichait `undefined km`  un faux chiffre. **Correction** :
badge coloré sur `alt.priorite` (rouge CRITIQUE / ambre HAUTE / ardoise MOYENNE)
+ libellé "Echeance : {date fr-FR}" uniquement quand `alt.echeance != null`.
Aucun km n'est inventé ; le champ fantôme disparaît du type.

**Vérification batch 10** : `npx tsc --noEmit` → **EXIT=0** ;
`python scripts/audit_frontend.py` → `broken_links: 0, dead_buttons: 0, fake_data: 0, ghost_routes: 0`.
Les 33 `api_gaps` restants sont des endpoints backend non implémentés (`/api/parc/*`,
`/api/v1/customers`, `/api/v1/telematics/positions`…) : hors périmètre d'un batch de typage.

➡️ Ce n'est qu'une **première brique** : 717 occurrences d'`any` restent dans `src/`.
Le vrai gain structurel est que `src/types/transport.ts` est désormais **adoptable** 
avant ce batch, aucun consumer n'aurait pu l'utiliser sans réécrire tous ses appels,
ce qui explique pourquoi le fichier est resté mort si longtemps.

---

## 13. Batch 11  Verrou CI "Zero-Mock" (quick win restant)

**Problème** : les 10 premiers batches ont ete vérifies **manuellement** a chaque
tour (`python scripts/audit_frontend.py`, `npx tsc --noEmit`, `pytest`). Rien n'empeche
un PR futur de reintroduire un `MOCK_DATA = [...]`, un `href="#"`, un `alert("a faire")`
ou un fichier `.BAK` dans `src/` : la convention etait explicite dans le rapport
mais **pas executable par la CI**. Le pipeline `.github/workflows/ci-cd.yml` courait
deja `pytest` (backend) et `tsc --noEmit` (frontend) mais ignorait completement le
script d'audit.

| Fichier | Ce qui a été fait |
|---|---|
| `evo-log-frontend/scripts/audit_frontend.py` | Ajout du flag `--strict-honesty` : exit 1 **uniquement** si l'une des 4 metriques d'honnetete (`broken_links`, `dead_buttons`, `fake_data`, `ghost_routes`) repasse au-dessus de 0. Les `api_gaps` restent affiches et enregistres dans `audit_report.json` mais ne font plus echouer le script. Justification consignee dans le `help` : un appel frontend vers un endpoint backend non implemente est un **trou de couverture** (reponse 501 explicite du backend), pas une regression Zero-Mock  l'inverse d'un faux succes. |
| `.github/workflows/ci-cd.yml` | Nouvelle etape **"Honesty gate (Zero-Mock)"** dans le job `test-frontend`, placee **apres** `tsc --noEmit` et **avant** `next build` : `python scripts/audit_frontend.py --strict-honesty`. Le job echoue donc si une PR reintroduit une donnee inventee, avant meme de tenter le build. Un commentaire dans le YAML rattache l'etape au present rapport (§13). |

**Vérification batch 11** (localement) :

```
$ python scripts/audit_frontend.py --strict-honesty
=== AUDIT FRONTEND EVO-LOG ===
  broken_links   : 0
  dead_buttons   : 0
  fake_data      : 0
  api_gaps       : 33
  ghost_routes   : 0
...
STRICT-HONESTY OK : broken_links/dead_buttons/fake_data/ghost_routes = 0 (api_gaps=33 tolere, hors perimetre d'honnetete).
EXIT=0
```

Sans `--strict-honesty`, le comportement historique est preserve (`api_gaps > 0` → exit 1)
pour ne pas casser les usages existants du script.

➡️ Les batches 1-10 qui ont supprime les donnees inventees sont desormais **verrouilles** :
un developpeur qui remet un `MOCK_DATA = [...]` dans une page verra sa PR bloquee par
la CI avec le nom exact du fichier et la ligne en cause. Les 33 `api_gaps` tolere
sont la liste des endpoints backend restant a ecrire (voir `audit_report.json`), pas
une dette d'honnetete.

---

## 14. Batch 12  Transport International : l'ecran ne pouvait pas marcher

**Declencheur** : meme logique que batch 10 (typer un ecran `any` pour forcer tsc a
signaler les fautes de frappe). La surprise : ici, le typage n'a pas seulement
corrige 4-5 champs  il a montre que **la page entiere etait structurellement
cassée** depuis son ecriture.

| # | Ce que faisait la page | Ce que le backend expose reellement | Consequence |
|---|---|---|---|
| 1 | `apiClient.get('/api/v1/transport-international/ordres-transport')` | **Aucune route GET list** sur le router (seuls POST/PUT et un GET `/ordres-transport/{id}/rapport` existaient) | `Promise.allSettled` avalait le 404 → liste **systematiquement vide** |
| 2 | `apiClient.get('/api/v1/transport-international/carnets-tir')` | **Aucune route GET list** idem | Carnets TIR jamais affiches, compteur "0" permanent |
| 3 | `o.numero_ordre` | `OrdreTransportResponse.numero_ot` | Colonne "N° OTI" toujours `undefined` |
| 4 | `o.mode_transport` | **N'EXISTE PAS** (le backend a `type_transit` avec enum `tir/t1/t2/national`) | Colonne "Mode" `undefined` |
| 5 | `o.pays_depart` | **N'EXISTE PAS** (le backend a `lieu_chargement`) | Flux "Départ → Destination" moitie vide |
| 6 | `o.incoterm` | **N'EXISTE PAS** (aucun incoterm dans `OrdreTransport`) | Colonne "Incoterm" inventee |
| 7 | `o.poids_kg` | `poids_net` et `poids_brut` (deux champs distincts) | Colonne "Poids" `undefined` |
| 8 | `o.statut === 'créé'` / `'livré'` / `'annulé'` | `StatutTransport.PLANIFIE = "planifie"`, `LIVRE = "livre"`, `ANNULE = "annule"` (**sans accent**) | **Aucun** filtre, **aucun** bouton d'action ne se declenchait, tous les OT tombaient dans le badge defaut ambre |
| 9 | POST avec `{numero_ordre, mode_transport, pays_depart, pays_destination, marchandise, poids_kg, incoterm}` | `OrdreTransportCreate` exige 16 champs dont 4 FK `client_id / transporteur_id / camion_id / conducteur_id` + `poids_net, poids_brut, nombre_colis, valeur_marchandise, montant_freight, type_transit, lieu_chargement, lieu_livraison, code_pays_destination` | **Toujours 422**, erreur avalee par un `catch { console.error }` silencieux |

➡️ 9 fautes differentes, **toutes invisibles** car portees par `useState<any[]>`.
Aucun utilisateur n'a jamais pu creer un OTI par cette UI, et le tableau restait
vide meme apres insertion reussie par API.

| Fichier | Ce qui a été fait |
|---|---|
| `app/services/transport_international_service.py` | Ajout de `OrdreTransportService.lister(db, statut?, offset, limit)` et `CarnetTIRService.lister(db, statut?, offset, limit)` : requetes SQLAlchemy reelles, pagination bornee a 500, filtre `statut` optionnel. Docstring explicite sur la limitation de scoping entreprise (`company_id` nullable, non aligne avec le POST/PUT du meme router) pour eviter toute fausse assurance. |
| `app/routers/v1/transport_international.py` | Ajout de **2 nouvelles routes GET list** : `GET /ordres-transport` → `List[OrdreTransportResponse]` et `GET /carnets-tir` → `List[CarnetTIRResponse]`, toutes deux protegees par `Depends(get_current_user)` et branchees sur les nouveaux `lister()`. |
| `tests/unit/test_transport_international.py` | 4 tests supplementaires : `test_lister_retourne_les_ot_crees`, `test_lister_filtre_par_statut`, `test_lister_pagination_bornee`, `test_lister_carnets`. 13 passed sur le fichier. |
| `src/types/transport_international.ts` (nouveau, 97 lignes) | Types **alignes Pydantic par Pydantic** : `OrdreTransportResponse` (25 champs), `CarnetTIRResponse` (16 champs), unions `StatutTransport` (7 valeurs backend, non accentuees) et `TypeTransitRoutier` (4 valeurs). Le header du fichier consigne l'expediteur : "neuf fautes differentes, toutes invisibles car portees par `useState<any[]>`". |
| `src/app/(app)/transport-international/page.tsx` (reecrite) | `useState<OrdreTransportResponse[]>` / `<CarnetTIRResponse[]>` ; tous les acces aux champs corriges (`numero_ot`, `type_transit`, `lieu_chargement`/`lieu_livraison`, `poids_net`) ; objet `STATUTS` centralise avec les valeurs backend sans accent ; compteur "En transit" et "Livres" recalculs sur `STATUTS.EN_TRANSIT` / `STATUTS.LIVRE` qui matchent enfin ; **formulaire de creation remplace par un bouton "N.I."** (Non Implemente) qui ouvre un `toast()` expliquant precisement pourquoi (4 FK + 5 numeriques obligatoires non collectes)  Zero-Mock : un bouton qui affiche une UI mensongere et declenche un 422 avale est **pire** qu'un bouton absent. |

**Vérifications batch 12**
- `npx tsc --noEmit` → **EXIT=0**
- `python scripts/audit_frontend.py --strict-honesty` → **EXIT=0** ; le compteur global `api_gaps` **descend de 33 a 32** (les routes GET backend ajoutees ferment un trou)
- Suite backend complete `python -m pytest tests` → **446 passed, 2 xfailed, 0 failed** en ~958 s sous la commande exacte de la CI (verification reexecutee en batch 13). Dans un premier temps le batch 12 avait annonce « 2 failures preexistantes » (`test_requisition_requires_auth`, `test_endpoint_facture_pdf_exige_auth`) ; cette affirmation etait **fausse** et n'a pas tenu la re-execution. Detail complet en §15.

➡️ Ce batch illustre la valeur reelle du typage strict : **la page transport-international
etait ecrite contre un contrat backend imaginaire**. Sans `useState<OrdreTransportResponse[]>`,
chacune des 9 erreurs ci-dessus passait silencieusement en production. Le pattern est
exactement celui du bug `echeance_km` (batch 10) mais a plus grande echelle.

---

## 15. Batch 13  Rectification : les 2 « failures d'auth » du batch 12 n'existaient pas

**Declencheur** : la derniere ligne utile du backlog herite du batch 12 annoncait
« 2 failures preexistantes, veritable trou de securite a traiter en batch suivant ».
En Zero-Mock, on ne peut pas laisser une affirmation fausse trainer dans un rapport 
surtout quand elle accuse un systeme d'auth d'etre troue alors qu'il ne l'est pas.

**Reproduction tentative** (dans l'ordre) :

| Commande | Resultat |
|---|---|
| `pytest tests/unit/test_parc_purchase_store.py::test_requisition_requires_auth tests/unit/test_pdf_generator.py::test_endpoint_facture_pdf_exige_auth` | ✅ 2 passed (reproduce 3/3) |
| `pytest tests/unit/test_parc_purchase_store.py tests/unit/test_pdf_generator.py` (2 fichiers complets) | ✅ 34 passed |
| `pytest tests` ( commande exacte de la CI, `.github/workflows/ci-cd.yml::Run tests`) | ✅ **446 passed, 2 xfailed, 0 failed** en 958 s |
| `pytest tests/unit` (sous-selection qui **n'est pas** la commande CI) | Run 1 : 431 passed / Run 2 : 13 failed, 414 passed |

**Verdict** : les 2 tests incrimines **reussissent systematiquement** sous la commande
que la CI execute reellement. Le `pytest tests/unit` intermediaire echoue sur un autre
ensemble de tests (`test_magasin_stock_analytics.py`) mais **jamais** sur les 2 tests
cites par le batch 12. La « fragilite » de la suite est donc reelle mais **d'une toute
autre nature** que celle decrite par erreur.

**Ce que le code dit reellement** (verifie en lecture) :

| Route | Protegee par | Preuve |
|---|---|---|
| `GET /api/v1/purchase/requisitions` | `Depends(get_current_user)` (declare au niveau `APIRouter(dependencies=[...])`, `parc_purchase_store.py:210`) | `TestClient(app).get(...)` sans token → **401** body `"Not authenticated"` (verifie en direct) |
| `GET /api/v1/finance/factures/{id}/pdf` | `Depends(get_current_user)` (`finance.py:250`) | `TestClient(app).get('/api/v1/finance/factures/1/pdf')` sans token → **401** body `"Not authenticated"` (verifie en direct) |

Il n'y a donc **aucun trou d'auth** sur ces routes. L'affirmation du batch 12 etait fausse.

**Cause probable de l'erreur du batch 12** : *[RETRACTEE EN BATCH 14  voir §16. La
« contention arriere-plan » etait une hypothese fausse : la cause reelle etait un
trou d'isolation dans le harnais pytest (`dependency_overrides.clear()` en milieu
de test supprimait l'override `get_db`, et les requetes suivantes touchaient la
VRAIE base de dev `kamlog_erp.db`). Trace material : le fichier a ete mute a
02:37 pendant un run.]*

**Mesures prises** :
- Table « Verifications finales » en-tete du rapport : remplacee par le chiffre exact
  `446 passed, 2 xfailed, 0 failed` + lien vers §15.
- § « Verification batch 12 » : la claim des 2 failures est explicitement retractee.

**Ce qu'il reste vraiment a faire** (recatgorise) :
- **Non bloquant, qualite** : la suite presente une fragilite d'ordre d'execution sous
  `pytest tests/unit`. Elle ne touche PAS les routes d'auth (les 2 tests restent verts)
  mais fait fluctuer 13 tests de `test_magasin_stock_analytics.py` selon l'ordre de
  collecte. A traiter sous forme de tâche dedicated "isolation des fixtures pytest" 
  **pas** sous forme de security P0 comme le laissait entendre le batch 12.
- **Aucune action immediate** sur les 2 tests cites.

➡️ Le principe Zero-Mock s'applique aussi aux **rapports** : une fausse accusation de
trou de securite coutera plus cher a corriger plus tard qu'une retractation immediate.

**Bonus : 2 vraies regressions front capturees par le verrou CI batch 11**

En re-activant `python scripts/audit_frontend.py --strict-honesty` et `npx tsc --noEmit`
en toute fin de batch 13, deux bugs reels sont tombes  preuve que le gate CI place en
batch 11 n'etait pas decoratif :

| Fichier | Bug | Correction |
|---|---|---|
| `src/config/navigationRegistry.ts` (l.1156) | Le lien "Profil Entreprise (SaaS)" pointait vers `/admin-entreprise/profil` ; **aucun `page.tsx` n'existait** a ce chemin. Le clic dans la sidebar partait en 404. | Repointe vers `/company` (page existante qui rend deja `GET/PUT /api/v1/tenant/company-profile` avec bouton "Enregistrer le Profil Entreprise"). Commentaire Zero-Mock dans le registre. |
| `src/app/(app)/admin-entreprise/modules/page.tsx` (l.149) | (a) chaine `'Votre demande est en cours d'examen.'` **cassait la syntaxe JS** (apostrophe non escapee a l'interieur d'un single-quote)  `tsc` sortait en TS1005/TS1381 ; (b) comparaison `m.etat === 'alloué' \|\| m.etat === 'alloue'` : la premiere branche etait **morte** (le backend `company_admin.py:421` renvoie systematiquement `alloue` sans accent), TS2367 le signale. | (a) remplacee par double-quote `"Votre demande est en cours d'examen."` ; (b) branche accentuee supprimee + commentaire Zero-Mock. |

Les deux bugs etaient presents **avant** batch 13 : `tsc` et l'audit du batch 12
n'ont pas ete re-execute en fin de course (seule l'audit `--strict-honesty` global
avait passe, sans re-run de `tsc`). Le batch 13 les rattrape et verrouille : `tsc` +
audit passent desormais EXIT=0 tous les deux.

**Verifications batch 13 (re-cap)** :
- `python -m compileall -q app` (backend) → **EXIT=0**
- `python -m pytest tests` (CI-equivalent) → **446 passed, 2 xfailed, 0 failed**
- `npx tsc --noEmit` (frontend) → **EXIT=0** (etait EXIT=2 avant correction)
- `python scripts/audit_frontend.py --strict-honesty` → **EXIT=0** avec `broken_links=0`
  (etait 1 avant reorientation du lien `admin-entreprise/profil`)

➡️ Le batch 13 est le premier ou le **verrou CI herite du batch 11** fait son travail
tout seul : je n'avais aucune raison de re-auditer le frontend, le gate m'est tombe
dessus et m'a force a comprendre, corriger et tracer. C'est exactement le scenario
pour lequel le flag `--strict-honesty` a ete ecrit.

---

## 16. Batch 14  L'isolation des tests ecrivait dans la VRAIE base de dev

**Declencheur** : la tache « isolation des fixtures pytest » heritee du batch 13.
Reponse a la question la plus importante du lot : la « fragilite » signalee etait le
symptome visible d'un bien pire  **les runs de tests mutaient `kamlog_erp.db`, la
base SQLite reelle de developpement**.

**Preuve materielle** : `LastWriteTime` du fichier = **28/09 02:37:47**, soit EN PLEIN
run pytest (avant ce batch, le fichier ne devait plus bouger que par l'app en local).

**Chaine causale complete** :

1. La fixture `client` du conftest surcharge `get_db` (base memoire) ET
   `get_current_user` (faux super-utilisateur)  contrat en vigueur depuis le
   commit `a18e78f` (28/09 00:44), **respecte et documente, pas revert**e.
2. Plusieurs tests appelaient `app.dependency_overrides.clear()` **en cours
   d'execution** pour simuler un anonyme. `clear()` est atomique : il emporte
   AUSSI l'override `get_db`.
3. La requete suivante resolution alors l'engine REEL de l'app, dont le defaut
   `Settings.DATABASE_URL` est `sqlite:///./kamlog_erp.db`.
4. Pire cas : `test_rbac_permissions_engine.py::test_rbac_router_requires_superadmin`
   faisait 3 `clear()` en milieu de test ; son assertion finale
   « SuperAdmin → 200 list tenants » **listait les tenants de la base de dev**.
5. La suite restait verte car les assertions 401/403 abortent avant toute lecture
   DB : la pollution etait **invisible par construction**. C'est la classe exacte
   de faux-vert que le Zero-Mock interdit  appliquee ici a l'infra de test.
6. Les 13 fluctuations de `test_magasin_stock_analytics.py` (batch 13) et la
   fausse « contention arriere-plan » (retractee en §15) partagent cette cause.

**Corrections** :

| Fichier | Probleme | Correction |
|---|---|---|
| `tests/conftest.py` | Aucun garde-fou : tout override `get_db` perdu partait sur le fichier de dev | **Guard Zero-Pollution** : `os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")` AVANT l'import de l'app (une requete perdue echoue bruyamment « no such table » au lieu d'ecrire dans la base de dev) ; docstring CONTRAT ; nouvelle fixture `unauthenticated` (ne pop QUE `get_current_user`, la restaure en finally) |
| `test_rbac_permissions_engine.py` | 3 `dependency_overrides.clear()` en milieu de test  source material de la mutation du fichier | Helper local `_anonyme()` qui ne pop que `get_current_user` |
| `test_cadc_arbitrage_phase3.py`, `test_company_admin_phase2.py`, `test_saas_console_cadc.py`, `test_tenant_console_rbac.py` | Helper `_clear()` = `.clear()` (mine endormie : aucun test ne requetait apres, mais suffisait d'un futur ajout) | Corps de `_clear()` → `pop(get_current_user, None)` + commentaire |
| `test_transport_international.py` | `test_endpoint_exige_auth` creait un `TestClient(app)` **nu** apres clear : aucun override `get_db` du tout | Fixture `unauthenticated` |
| `test_parc_purchase_store.py`, `test_pdf_generator.py` | Patterns manuels de pop pour les tests 401 | Migres vers `unauthenticated` |
| `tests/unit/test_isolation_guards.py` (**nouveau**) | Le contrat n'etait verrouille par rien | 3 meta-tests : `client` porte les 2 overrides ; `unauthenticated` CONSERVE `get_db` (verifie avant ET apres une requete 401) ; l'engine/`settings` applicatifs ne pointent JAMAIS sur `kamlog_erp.db` |
| `test_real_backend.py`, `test_simple_real.py` | `test_database_tables_exist` inspectait l'engine global : vert uniquement parce qu'il lisait le fichier de dev (et dependant de l'ordre apres le garde-fou) | Fixture `client` : le startup du TestClient (lifespan → `create_all`) rend l'assertion hermetique et reellement executee. Variante `skipif` (test toujour saute en local/CI) ecartee : **un test saute n'est pas un test** |

**Verification** :
- Subset 8 fichiers (les plus touches) : **112 passed**, `DB_CHANGED=False`
  (mtime 02:37:47 identique avant/apres le run).
- `test_isolation_guards.py` : 3 passed.
- Premier run complet posterieur aux correctifs : 3 failed / 479 passed  les 3
  echecs sont des tests non hermetiques dependant de l'etat de l'engine global
  (corriges ci-dessus, dont 1 deja en cours de reprise par la session parallele).
- Run complet definitif (commande CI `pytest tests`) : ✅ **485 passed, 2 xfailed,
  0 failed** en 305 s, `PYTEST_EXIT=0` et **`DB_CHANGED=False`** (mtime de
  `kamlog_erp.db` identique avant/apres le run).

**Laisse-pour-compte honnete** : `kamlog_erp.db` a bien ete ecrit par des runs AVANT
la correction (02:37, possiblement avant). La base de dev peut donc contenir des
**residus de tests** (lignes creees par les requetes parties hors override). Action
recommandee hors perimetre : purger/ verifier la base de dev locale (regarder du cote
de `scripts/seed_data.py` pour la reconstruire proprement si necessaire).
→ **Traite au batch 15 (voir §17)** : pollution confirmee mais circonscrite a
`audit_logs` ; residus purges, donnees de dev intactes.

➡️ Zero-Mock applique a l'infra : un test vert qui lit/ecrit la base de prod-dev
reelle est un faux-vert avec effet de bord reel. Le contrat des fixtures est
desormais (1) force par l'environnement (`DATABASE_URL` memoire), (2) documente
(docstring du conftest), et (3) verrouille par des meta-tests qui rougissent des
qu'un maillon saute.

---

## 17. Batch 15  Purge des residus de tests dans la base de dev

**Declencheur** : le laisse-pour-compte signale en fin de §16  « la base de dev
peut contenir des residus ecrits par les runs d'avant correction ». Plutot que de
le laisser en note d'execution, on a **verifie dans les donnees**.

**Metodologie** (scriptes dans `evo-log-backend/scripts/scratch_dev_db_residue.py`,
`scratch_b15_audit_quant.py`, `scratch_b15_purge.py`, `scratch_b15_verify.py`) :
backup via l'API SQLite `backup()` (jamais le fichier actif), puis scan
**lecture seule** de la copie : 332 tables, regex des signatures de fixtures
(`@test.local`, `sonde*`, `sahttp`, `acme`, `testserver`…).

**Ce qu'on a trouve** :

| Constat | Chiffre | Lecture |
|---|---|---|
| Tables metier presque toutes vides | 323/332 vides ; users=21, companies=2, agencies=5 | **aucune contamination metier** : les pollutions du batch 14 etaient des GET (lecture seule)  les users/companies sont les seeds legitimes (`@evolog.cm`, LPC/TCL) |
| `audit_logs` explose | **16 237 lignes dont 15 663 (96 %) en `http://testserver/...`** | Chaque requete TestClient d'un run pytest ecrivait une ligne d'audit dans la base de dev |

**Le canal que le batch 14 n'avait pas identifie** : `app/middleware/audit.py`
(AuditMiddleware) n'utilise PAS `get_db`  il ouvre son propre `SessionLocal()` du
module `app.core.database`. Donc meme avec l'override `get_db` intact, **chaque
requete de test passait par l'engine reel** et ecrivait dans `kamlog_erp.db`.
Bonne nouvelle : ce canal est lui aussi ferme par le garde-fou batch 14  le
middleware est lie au MEME engine singleton construit depuis `DATABASE_URL`,
desormais `:memory:` pendant les tests. Preuve en §Verification ci-dessous.

**Purge executee** :
- Critere cible, chirurgical : `url LIKE 'http://testserver%'` (host fixe du
  TestClient). CONSERVES : 511 lignes `127.0.0.1:8000` (sonde dev/openapi), 60
  `loadtest` (`scripts/load_test.py`), 3 `localhost:8000` (navigateur) = 574 lignes.
- Dry-run d'abord (16 237 → 574), puis `--apply` avec backup requis + invariant
  `assert restant == attendu` ; resultat : **16 237 → 574**, `PRAGMA integrity_check=ok`,
  fichier 6,0 MB → 4,0 MB.
- Filet de securite conserve : `kamlog_erp.db.bak-pre-b15` (a supprimer manuellement
  une fois la confiance installee).

**Verification** :
- Post-purge : `testserver restants=0`, users=21 / companies=2 intacts.
- Smoke boot applicatif (`TestClient`, `/api/health` → **200 OK**) avec le meme
  garde-fou `DATABASE_URL=:memory:` que le conftest : mtime de `kamlog_erp.db`
  **inchange** (`DB_TOUCHED=False`) → le canal AuditMiddleware est bien coupe aussi.
- Aucun code applicatif ou de test modifie dans ce batch → suite pytest inchangee
  (485 passed, 2 xfailed du batch 14 toujours valable).

➡️ Ce batch illustre la limite d'une correction « par les overrides » : le Zero-Mock
d'isolation doit couvrir **tous** les chemins d'acces a la base  middleware inclus.
L'environnement (`DATABASE_URL`) est le seul garde-fou qui les couvre tous, puisqu'il
agit a la source de l'engine  raison pour laquelle le batch 14 l'avait choisi comme
premiere ligne de defense.

---

## 18. Batch 16  Bon de sortie & circuit de signature (backlog P2 #10)

**Declencheur** : item 10 du backlog structurel §3  « Edition de bon de sortie /
bon de livraison et circuit de signature (le magasinier ne peut que valider, pas
corriger une ligne) ». Les items P1 restants exigeront des donnees externes
(GUCE, operateurs mobiles reels) ; celui-ci est 100 % executable et verifiable
en interne.

### Constat

Deux implementations paralleles du bon de sortie coexistaient (même pattern que
les arbres de routes transport dupliques) :

| Voie | Etat | Realite |
|---|---|---|
| `/api/v1/magasin-avance/sorties` (trio creer/ligne/valider) | **MORTE** | construisait `BonSortie(destinataire_id=...)`, `LigneBonSortie(bon_id=..., quantite=...)`, lisait `stock.quantite`  champs **inexistants** sur les modeles → TypeError systematique, 500 garanti a chaque appel. Jamais appelee par le frontend. |
| `/api/v1/magasin/removal-slips` (route connectee au portail magasinier) | VIVANTE mais **non sure** | voir lignes critiques ci-dessous. |

Lignes critiques de la route vivante (avant correction) :
- `valider` faisait `max(0, dispo - qte)` : le stock ne descendait **jamais** sous
  0 quel que soit l'ecart demande  une sortie de 1 000 sacs sur 5 disponibles
  « passait » en silence avec un faux 200.
- **Aucune ecriture dans `MouvementStock`** : le mouvement physique n'avait aucune
  trace comptable matiere (quantite_avant/apres inexistantes).
- Le `PUT` acceptait un champ `statut` : n'importe qui pouvait poser
  `statut="valide"` **sans aucun decript**  faux document signe.
- Pas de `/refuse` : l'etat `refuse` etait filtre dans la liste/stats mais
  aucune porte n'y menait.
- Numeration `BE-YYYYMMDD-<count>+1` avec trous de suppression → collision UNIQUE
  possible en 500.
- Aucun controle d'existence des FK (SQLite n'applique pas les FK par defaut) :
  bons pointant vers clients/entrepots/stocks fantomes.
- Pas d'edition PDF du bon.

### Corrections

| Fichier | Action |
|---|---|
| `app/routers/v1/removal_slip.py` | Durcissement complet : validations d'existence (client/entrepot/stock, quantite > 0) ; numeration avec boucle anti-collision ; `PUT` refuse tout `statut` explicite (400 pedagogique) et tout document deja signe (**immuabilite**) ; `validate` = **tout-ou-rien** (400 avec detail structure `lignes_en_rupture[]`, zero decript partiel) + decret reel + une ecriture `MouvementStock` (SORTIE, avant/apres, document_reference) par ligne ; nouveau `POST /{id}/refuse` (motif obligatoire, trace dans notes, zero mouvement, non revalidable) ; nouveau `GET /{id}/pdf`. |
| `app/templates/pdf/bon_sortie.html.j2` | **Cree** : A4 complete, badge de statut, avertissement explicite « document NON valide : quantites pas encore sorties », montant indicatif (jamais facture), **3 zones de signature IMPRIMEES** (operateur, responsable  nom/date reels si signe, recepisse destinataire) : le systeme ne simule aucune signature. |
| `app/routers/v1/magasin_avance.py` | Trio mort `/sorties` **supprime** (commentaire pointant vers la route vivante). Imports schemas nettoyes. |
| `app/schemas/magasin_avance.py` + `__init__.py` | Schemas fantomes `BonSortie*`/`LigneBonSortie*` (champs inventes) **supprimes** de defs, imports et `__all__`. |
| `tests/unit/test_removal_slips.py` | **Cree** (10 tests) : seeds reels via fixtures `client`/`db`, verification du decret exact et du registre, rupture tout-ou-rien (aucun decript, meme sur la ligne qui passait), double validation, PUT-bypass statut, immuabilite apres signature, refus motive (0 mouvement, non revalidable), garde DELETE, numeration unique, PDF = 200 reel **ou** 501 honnete. |
| `src/lib/api-client.ts` | `removalSlipAPI.refuse(id, motif)` + `getPdf(id)` (blob). |
| `src/app/(app)/portail-magasinier/page.tsx` | Boutons **Refuser** (motif obligatoire, cache si deja signe) et **PDF** a cote de Valider ; toast adapte au detail structure de rupture (affiche article demande/dispo) ; bouton Valider desactive aussi sur `refuse`. |

### Verification

- `python -m pytest tests/unit/test_removal_slips.py -v` : ✅ **10 passed**, EXIT=0.
- Suite complete (commande CI `pytest tests`) : ✅ **516 passed, 2 xfailed,
  0 failed** (427 s), `PYTEST_EXIT=0` et **`DB_CHANGED=False`** (mtime/taille de
  `kamlog_erp.db` identiques avant/apres  le garde-fou du batch 14 tient).
- `python -m compileall app` : ✅ EXIT=0 ; `import app.main` apres suppression du
  trio mort : ✅ OK.
- `npx tsc --noEmit` : ✅ EXIT=0.
- `python scripts/audit_frontend.py --strict-honesty` : ✅ OK (dead_buttons /
  fake_data / ghost_routes = 0).

### Reste (hors perimetre du batch, signale)

- `/magasin-avance/retours` et `/magasin-avance/litiges` sont **morts de la meme
  facon** (champs fantomes dans les schemas modeles) : supprimes ou reconstruits
  au prochain batch magasin, sur le meme modele.
- Signature manuscrite numerisee (canvas → base64 → PDF) : le circuit
  d'habilitation (qui a signe, quand, pourquoi refuse) est reel ; la signature
  griffonnee reste a imprimer/emarger  conformement a Zero-Mock, rien n'est
  simule a l'ecran.

➡️ Le Zero-Mock applique au magasin : un « bon valide » qui ne decremente pas
reellement le stock est une ecriture mensongere ; un refus sans motif n'est pas
opposable ; une signature que le systeme ne peut pas imprimer avec un nom et une
date reels n'existe pas.

---

## 19. Batch 17  Retours clients, litiges transporteurs et KPI : 6 endpoints morts reconstruits sur le modele reel

Annonces au §18 (« Reste ») : `/magasin-avance/retours` et `/litiges` etaient morts
du meme syndrome « champs fantomes » que le trio `/sorties` du batch 16. A la
difference de ces derniers, ils n'avaient **aucun equivalent live** : la seule
option honnete etait la **reconstruction sur le modele reel**, pas la suppression.

### Constat (audit)

| Endpoint | Cause de mort | Ce qui se passait vraiment |
|---|---|---|
| `POST /retours` | Schema inventait `article_id`, `etat` | `RetourClient(article_id=…)` → TypeError → 500 garanti a chaque appel |
| `PUT /retours/{id}/traiter` | Ecrivait `date_traitement`, `action_effectuee` | Colonnes inexistantes : l'ORM accepte l'attribut non declare mais **ne le persiste jamais** → perte silencieuse |
| `POST /litiges` | `date_litige` (reel : `date_incident`) | TypeError → 500 garanti |
| `PUT /litiges/{id}/resoudre` | Champs fantomes + code inatteignable | 500 |
| `GET /kpi/rotation/{article_id}` | `Stock.quantite`, `MouvementStock.article_id` | AttributeError → 500 (reels : `quantite_disponible`, `stock_id`) |
| `GET /kpi/precision/{entrepot_id}` | `InventaireTournant.date_inventaire` (reel : `date_debut`) + statut `"valide"` | 500 ; et meme corrige, le workflow reel est `planifie/en_cours/termine/annule` → `"valide"` ne matchait **jamais** |

Modeles reels : `RetourClient` (numero_retour unique, client_id NOT NULL,
bon_sortie_id FK, **aucun stock_id**), `LitigeTransporteur` (transporteur_id FK
`fournisseurs.id`, statut `en_cours → resolu/refuse/justice`, date_resolution reel).

### Corrections

| Fichier | Correction |
|---|---|
| `schemas/magasin_avance.py` | Schemas Retour/Litige remplaces par des versions **alignees modele** (`RetourClientCreate/Traitement/Response`, `LitigeTransporteurCreate/Resolution/Response`) ; `RotationStockResponse` enrichi (`sorties`, `stock_actuel`, `rotation: Optional[float]`) |
| `routers/v1/magasin_avance.py` | 8 endpoints reconstruits : GET/POST/PATCH + `/traiter` pour les retours, GET/POST/PATCH + `/resoudre` pour les litiges, 2 KPI recalculs sur le registre reel ; numerotation anti-collision `RT-/LI-YYYYMMDD-NNNN` ; verifications d'existence Client/BonSortie/Fournisseur en explicite (FK SQLite desactivees par defaut) |
| tests | `tests/unit/test_magasin_avance_retours_litiges.py` : 9 tests reels (400 de validation, immunite apres decision, decision unique, KPI calculees sur mouvements seeds) |

Circuit de decision (meme patron que le batch 16) : `statut` jamais modifiable
par PATCH ; transitions uniquement via `/traiter` (accepte **exige** une action
remplacement/remboursement/destruction ; refuse l'interdit ; cout >= 0) et
`/resoudre` (resolution ecrite obligatoire, montant_indemnise seulement si
`resolu`, double cloture = 400).

### Decisions d'honnetete

- **Aucun mouvement de stock invente** a la reception d'un retour : le modele
  RetourClient n'a pas de stock_id, la reintegration stock n'est pas modelisee.
  Un test assertion `MouvementStock.count() == 0` apres traitement  si quelqu'un
  «oublie» ce garde-fou, le test rouge.
- Date de traitement tracee dans `notes` (`[TRAITE {date} par utilisateur {id}]`) :
  pas de colonne `date_traitement` → pas de migration inventee pour l'occase.
- `montant_indemnise` remplace `montant_reclame` lors d'une resolution partielle :
  seule representation honnete sans migration ; documente dans le schema.
- KPI : `rotation = None` si stock a zero (pas de division par zero deguisee en
  0.0) ; `precision = None` + message « non mesuree » si aucun inventaire
  `termine`  un KPI jamais mesure n'est pas un KPI a 0 %.

### Pitfall annexe decouvert (Python 3.14 / pydantic 2.13)

`Optional` non importe dans le router → `PydanticUserError: TypeAdapter[…
ForwardRef('Optional[str]')…] is not fully defined` **seulement quand le query
param est fourni** (un param absent saute la validation : les GET filtres
plantaient, les GET simples passaient). Correction : `from typing import
List, Optional`. A retenir : ce n'est pas un probleme de lazy annotations, c'est
un nom simplement pas importe.

### Verification

- `python -m pytest tests/unit/test_magasin_avance_retours_litiges.py -q` : ✅ **9 passed**.
- Suite complete (commande CI) : ✅ **527 passed, 2 xfailed, 0 failed** (370 s),
  `PYTEST_EXIT=0`, **`DB_CHANGED=False`** (mtime/taille `kamlog_erp.db` identiques).
- `python -m compileall app` : ✅ EXIT=0 ; `import app.main` : ✅ OK.
- Batch **sans aucun changement frontend** (aucun ecran ne consomme ces routes) ;
  `npx tsc --noEmit` ✅ EXIT=0 et `audit_frontend.py --strict-honesty` ✅ OK
  re-lances en simple confirmation de non-regression.

### Reste (hors perimetre du batch, signale)

- `POST /magasin-avance/reapprovisionnement/automatique/{fournisseur_id}` est
  **mort autrement** : `stock.article_id` n'existe pas sur Stock (lien reel :
  `code_article`) → AttributeError 500 des qu'un stock passe sous le seuil ;
  et `prix_unitaire=0.0` invente dans la ligne de commande.
- `GET /magasin-avance/fournisseurs/{id}/performance` rend `note: 0` quand il n'y
  a aucune commande  faux zero (devrait etre `null` + « non evalue ») ; aucune
  verification d'existence du fournisseur.
- Signature manuscrite numerisee (report du §18, toujours d'actualite).

➡️ Zero-Mock applique aux KPI : un taux de precision a 0 % calcule sur un
inventaire qui ne porte jamais le statut « valide » attendu n'est pas une mesure,
c'est un chiffre invente. `None` + « non mesure » est la seule reponse honnete.

---

## 20. Batch 18  Inventaires tournants, evaluations/performance fournisseur, reappro : 7 endpoints morts reconstruits (+ suite rouge de cause externe)

Annonce au §19 (« Reste ») : le reappro et la performance fournisseur etaient
morts. L'audit exhaustif de la section restante du router a montre que **tout le
bloc l.445–661 etait du meme tonneau**  7 endpoints, 500 garantis ou pertes
silencieuses. Ce batch les reconstruit sur les modeles reels.

### Constat (audit)

| Endpoint | Cause de mort | Effet reel |
|---|---|---|
| `POST /inventaires` | `InventaireTournant(date_inventaire=…)` + `numero_inventaire` (unique NOT NULL) jamais fourni | TypeError → 500 garanti |
| `POST /inventaires/{id}/lignes` | lecture `stock.quantite` (reel : `quantite_disponible`) ; `compteur_id` (reel : `operateur`) | AttributeError → 500 |
| `PUT /inventaires/{id}/valider` | ecriture `stock.quantite`, `validateur_id`, `date_validation` (inexistants) + statut `"valide"` hors workflow reel | **reponse 200 menteuse** : l'ajustement theorique etait perdu en silence, le statut pollue la donnee, et aucune ligne du registre MouvementStock |
| `GET /inventaires/{id}/precision` | faux `0.0` sans ligne comptee ; `l.ecart == 0` sur Numeric | mesure inventee |
| `POST /fournisseurs-stock` | `FournisseurStock(delai_livraison_jours, qualite, fiabilite)` : 3 kwargs fantomes | TypeError → 500 |
| `GET /fournisseurs/{id}/performance` | `cmd.date_livraison`/`cmd.date_prevue` (reels : `_reelle`/`_prevue`) ; `statut=="recu"` (reel : `"livree"`) ; `note: 0` sans commande | AttributeError → 500 ; et faux 0/100 |
| `POST /reapprovisionnement/automatique/{id}` | `CommandeFournisseur(reference, date_prevue)` + `LigneCommandeFournisseur(article_id=stock.article_id)`  article_id n'existe NI sur la ligne NI sur Stock ; `prix_unitaire=0.0` invente ; 1 commande par stock | TypeError → 500 ; pollution tarifaire si ca avait tourne |

Schemas associes reconstruits alignes modele (`InventaireTournant*`,
`LigneInventaire*`, `FournisseurStock*`) ; les schemas `CommandeFournisseur*/
LigneCommandeFournisseur*` (fantomes et **non consommes par les routes**) ont ete
supprimes avec commentaire pointeur, retire des re-exports.

### Corrections

- `PUT /inventaires/{id}/valider` : le validateur est l'utilisateur authentifie
  (plus de query param `validateur_id` non verifie) ; refus sur inventaire vide
  (« rien a valider ») et sur decision deja prise ; statut **`termine`** (workflow
  reel) ; l'ajustement porte sur `quantite_disponible` **et chaque ecart corrige
  est journalise dans MouvementStock (type `inventaire`)** avec
  `reference = {numero_inventaire}/L{id_ligne}`  aucune correction invisible ;
  trace date+utilisateur dans `notes`.
- Comptage : theorique = colonne reelle, unicite stock/inventaire (pas de
  fusion silencieuse), comptage refuse si inventaire `termine`/`annule`.
- Precision : `None` + « non mesuree » sans ligne (plus de faux 0 %) ; 404 si
  inventaire inconnu.
- Evaluation fournisseur : notes 1–10 et taux 0–100 valides ; `note_globale`
  calculee sur les notes fournies sinon `None` ; evaluateur = authentifie.
- Performance : 404 si fournisseur inconnu ; periode invalide 400 ; statut reel
  `livree` ; delais calcules sur `date_livraison_reelle − date_livraison_prevue` ;
  **sans commande → note `None` + message, plus de 0/100** ; sans delai mesurable,
  note = taux brut sans composante delai inventee.
- Reappro : **une seule commande groupee** (le modele relie les lignes a des
  `stock_id`, et l'ancien code creait N commandes pour un fournisseur) ;
  numerotation anti-collision `CMD-YYYYMMDD-NNNN` ; `montant_total` sommant les
  lignes reelles ; stock sans prix sur sa fiche = **ignore et declare** dans
  `ignorees` (jamais price a 0.0) ; 400 si rien de commandable.

### Tests

`tests/unit/test_magasin_avance_inventaires_fournisseurs.py` : 9 tests reels
(404/400 de validation, theorique/ecart sur colonnes reelles, journalisation
MouvementStock verifiee avec quantite_avant/apres, decision unique, precision
None-vs-75 %, note_globale calculee, performance sans faux zero avec note 64.4
verifiee a la main, commande groupee a prix reel, refus total du prix invente).

### Verification  batch VERT, suite globale ROUGE de cause externe

- Tests cibles (re-verifie a la fin du batch, 4 fichiers joues ensemble) :
  ✅ **41 passed**  b18 : 9 (`test_magasin_avance_inventaires_fournisseurs`),
  b17 : 9 (`test_magasin_avance_retours_litiges`), batch 16 : 10
  (`test_removal_slips`), magasin live : 14 (`test_magasin_store`).
- `compileall app` : ✅ EXIT=0 ; `import app.main` : ✅ OK ; **`DB_CHANGED=False`**.
- Suite complete : ❌ **48 failed / 487 passed / 240 errors**  mais **aucun
  echec dans les fichiers de ce batch ni des batches 16–17**. Attribution prouvee,
  pas d'alibi :
  1. worktree temoin au commit `42b7c6b` (01:12, etat batch 17 **sans** batch 18)
     rejouee a l'instant : ✅ **539 passed, 0 failed** ;
  2. les clusters en echec (transport_exploitation/international, saas_console,
     tenant_console_rbac, rbac_permissions_engine, numerotation, reporting…)
     tombent sur `UNIQUE tiers.code/companies.code` (fuites de seeds) et sur
     `ImportError: BulletinPaieResponse from app.schemas.rh`  fichiers `rh*`,
     `transport*` et `_rbac_patch*` edites **pendant ce batch par une session
     concurrente** (commits auto-push 01:12→01:58, `rh_service.py` modifie non
     commité, erreur de syntaxe `transport_exploitation.py` observee en direct,
     puis corrigee par son auteur) ;
  3. mes fichiers n'ont jamais ete dans la liste des echecs.
  Decision Zero-Mock : **le rouge est constate, non camoufle** ; le re-run de la
  suite complete reste a faire quand le WIP concurrent sera stabilise (inscrit au
  « Reste »). Aucun fichier de la session concurrente n'a ete touche.
- Incident pendant la verification, corrige et declare : une chaine de commandes
  sandboxee a echoue **apres** ses premieres instructions et a revert mes 3
  fichiers batch 18 dans l'arbre principal (plus supprime mon fichier de tests,
  suppression happee par l'auto-push). Restauration depuis le snapshot complet
  `1cc4ecb`, re-verifiee par les 41 tests cibles verts ci-dessus.

### Reste (hors perimetre du batch, signale)

- **Batch 19  meme module, dernier bloc** : le trio `/receptions` (3 endpoints
  morts : `BonReception(commande_id=…)`, `LigneBonReception(bon_id, article_id,
  emplacement_id=…)`, `Stock.article_id`  pendant que le frontend
  `saisie-inventaire-physique` poste un payload d'inventaire sur
  `/api/magasin-avance/receptions`, donc 422 permanent) et le trio `/colis`
  (`ColisService` fantome : `reference_colis`, `date_creation`, `code_barres`,
  `palette_id`  le modele reel porte `numero_colis`, `emplacement`,
  `date_etiquetage` ; les schemas `Colis*` sont fantomes eux aussi). Egalement :
  `magasin_avance_service.traiter_retour` ecrit toujours `action_effectuee`/
  `date_traitement` (colonnes inexistantes)  code mort, a purger.
- **Re-run de la suite complete** des que les commits concurrents (rh/transport/
  rbac) se stabilisent ; retablir la ligne pytest de l'en-tete.

➡️ Zero-Mock applique a l'inventaire : un 200 « inventaire valide » qui ne
corrige rien de visible et ecrit un statut hors workflow est une double
ecriture mensongere ; la version reconstruite ne peut repondre 200 qu'avec des
lignes comptees, un stock reellement ajuste et une ligne de registre par ecart.

---

## 21. Batch 19  Réceptions fournisseur, colis et service fantôme : le dernier bloc de `magasin_avance` reconstruit

Annonce au §20 (« Reste ») : apres les sorties (batch 16), les retours/litiges/KPI
(batch 17), les inventaires/fournisseurs/reappro (batch 18), il restait dans
`/api/v1/magasin-avance` le trio `/receptions`, le trio `/colis` et le service
`magasin_avance_service.py`  tous morts du meme syndrome « champs fantomes ».
Le module est desormais **integralement reconstruit sur les modeles reels**.

### Constat (audit)

| Element | Cause de mort | Ce qui se passait vraiment |
|---|---|---|
| `POST /receptions` | `BonReception(commande_id=…)` | colonne reelle `commande_fournisseur_id` → TypeError → 500 garanti |
| `POST /receptions/{id}/lignes` | `LigneBonReception(bon_id, article_id, emplacement_id=…)` | colonnes reelles `bon_reception_id`, `stock_id`, `emplacement` (chaine) → 500 garanti |
| `PUT /receptions/{id}/valider` | lisait `LigneBonReception.bon_id`, `Stock.article_id`, ecrivait `stock.quantite`, inventait `Stock(...article_id=…)`, signait `date_validation=utcnow()` sur une colonne **Date** | AttributeError 500 ; et si le code etait passe, **tout l'apport en stock etait perdu silencieusement** (`quantite` n'existe pas, la colonne reelle est `quantite_disponible`) |
| `POST /colis` (via `ColisService`) | `reference_colis`, `date_creation`, `code_barres`, `palette_id`, `date_palettisation` | modele reel : `numero_colis`, `date_etiquetage`, `emplacement` → TypeError ou ecriture sur attribut Python sans colonne = perte silencieuse |
| `magasin_avance_service.py` | **5 classes fantomes** (`ReceptionService`, `SortieService`, `RetourService`, `ColisService`, `KPIStockService`) sans consommateur reel, ecrivant toutes sur des colonnes inexistantes | code mort  purgue avec commentaire pointant vers les vrais circuits (batches 16 a 19) ; le `ReceptionService` des tests d'acquisition est une AUTRE classe (`acquisition_service.py`), non touchee |
| Frontend `saisie-inventaire-physique` | postait un payload d'**inventaire** sur `/magasin-avance/receptions` (route morte de surcroit) | **422 permanent** : l'ecran « enregistrer les ecarts » n'enregistrait rien |

### Corrections Zero-Mock

| Qui | Quoi |
|---|---|
| `schemas/magasin_avance.py` | Schemas alignes sur le modele : `BonReceptionCreate/Update/Response`, `LigneBonReceptionCreate/Response`, `RefusBonReception` (motif obligatoire), `ColisCreate/Update/Response` ; schemas fantomes `Colis*` supprimes |
| Receptions (6 endpoints) | `GET /receptions` (filtres reels statut/fournisseur/entrepot), `POST` (BR-YYYYMMDD-NNNN anti-collision, verification existence fournisseur + entrepot + commande liee, statut initial `en_attente`), `PATCH` (seulement `en_attente`  bon valide/refuse immuable), `POST /{id}/lignes` (stock reel, quantite > 0, **conformite CALCULEE** : `conforme` seulement si quantite commandee fournie et egale, sinon `ecart`  jamais de saisie libre), `PUT /{id}/valider` (exige des lignes ; augmente reellement `quantite_disponible` ; **un `MouvementStock` ENTREE journalise par ligne** avec avant/apres/prix/operateur ; met a jour le registre `LigneCommandeFournisseur.quantite_recue/date_reception/statut=recu` ; bascule la commande en `livree` + `date_livraison_reelle` quand toutes ses lignes sont recues ; tracabilite `[VALIDE …]` dans notes ; decision unique), `PUT /{id}/refuser` (**motif ecrit obligatoire**, aucun stock ne bouge  la marchandise refusee n'est pas entree) |
| Colis (5 endpoints) | `GET /colis`, `POST` (CO-YYYYMMDD-NNNN, poids/volume non negatifs, type dans la liste metier, bon de sortie lie verifie), `PATCH` (numero immuable), `PUT /{id}/etiqueter` (`date_etiquetage` = jour reel, **decision unique** : un colis deja etiquete ne recoit pas une 2e date), `PUT /{id}/palettiser` (le modele n'a **aucune** colonne palette → la ref est tracee dans `emplacement`, seule localisation reelle, au lieu d'inventer une donnee perduee) |
| Frontend | Nouvelle `inventaireAPI` branchee sur le vrai circuit inventaire du batch 18 (creation campagne → comptages → validation) ; la page `magasin/saisie-inventaire-physique` n'appelle plus `/receptions` ; `StockItem` porte desormais `entrepot_id` (colonne reelle du `StockResponse`) et un garde « une campagne = un entrepot » presente l'erreur au lieu de poster un payload invalide ; methode morte `completeReception` supprimee ; methodes receptions de `magasinAPI` realineees sur le nouveau contrat |

### Piège technique rencontré et corrigé (declare)

La session applicative tourne avec `autoflush=False` : le COUNT qui decide si
toutes les lignes d'une commande sont recues lisait les statuts **PRECEDENTS**
en base, et la commande restait eternellement « en cours » malgre un 200 de
validation. Un `db.flush()` explicite avant le comptage corrige le cas 
decouvert par le test `test_reception_valider_avec_commande_met_jour_le_registre`,
pas par la relecture.

### Verification

- `python -m pytest tests/unit/test_magasin_avance_receptions_colis.py -q` : ✅ **9 passed**  dont les assertions d'honnetete « le refus ne bouge pas le stock », « la validation cree bien un MouvementStock par ligne » et « le service fantome est purge » (`test_service_fantome_purge`).
- Tests cibles magasin (5 fichiers joues ensemble, re-verifie a la fin du batch) : ✅ **50 passed**  b19 : 9, b18 : 9, b17 : 9, b16 : 10, `test_magasin_store` : 14.
- **Suite complete (commande CI `pytest tests`) : ✅ 625 passed, 2 xfailed, 0 failed**, `PYTEST_EXIT=0`  le rouge du batch 18 etait bien externe ; le re-run promis au §20 est fait et **vert**. `DB_CHANGED=False` (mtime/taille `kamlog_erp.db` identiques avant/apres chaque run definitif).
- `python -m compileall -q app` : ✅ EXIT=0 ; `import app.main` : ✅ OK (1137 chemins OpenAPI).
- `npx tsc --noEmit` : ✅ EXIT=0 ; `python evo-log-frontend/scripts/audit_frontend.py --strict-honesty` : ✅ EXIT=0.

### Reste (hors perimetre du batch, signale)

- Le module `magasin_avance` n'a plus d'endpoint mort identifie ; les prochains
  lots portent hors du module (ex. : `KPIStockService` etant purges, d'eventuels
  tableaux de bord qui consommeraient `/kpi/*` restent a verifier cote frontend,
  et la reintegration physique en stock des **retours clients** n'est pas
  modelisee  le modele `RetourClient` n'a pas de `stock_id`, le batch 17 a donc
  refuse d'inventer un mouvement ; une migration ajouteant cette liaison serait
  le seul moyen honnete de la rendre reelle).

➡️ Zero-Mock applique a la reception : un 200 « bon valide » qui n'augmente
aucune quantite reelle et ne journalise aucun mouvement est une ecriture
mensongere au sens comptable du mot ; la version reconstruite ne peut repondre
200 qu'avec un stock reellement augmente, une ligne de registre par apport et
un validateur identifie.

---

## 22. Batch 20  Réintégration en stock des retours clients : la liaison promise au §21 est devenue réelle (migration 029)

Annonce au §21 (« Reste ») : la reintegration physique en stock des retours
n'etait **pas modelisee**  `RetourClient` n'avait aucune colonne vers une
ligne de stock, et le batch 17 avait donc (à juste titre) refuse d'inventer un
mouvement. Le rapport posait la condition : « une migration ajoutant cette
liaison serait le seul moyen honnete de la rendre reelle ». Le batch 20 est
cette migration, plus le circuit qui l'exploite.

### Audit prealable

- Frontend : `grep kpi/rotation|kpi/precision|magasin-avance/kpi` sur tout
  `src/` → **0 consommateur**. Le point « reste » equivalent du §21 est clos
  sans correction : aucun ecran n'affiche ces KPI, donc aucun faux chiffre
  n'est visible.
- Chaîne Alembic : lineaire, tete `028_full_orm_parity` au debut du batch ;
  conventions 024 (colonne + FK par introspection, batch SQLite) et 027
  (non-destructive, downgrade sans effet assume) appliquees.

### Corrections Zero-Mock

| Qui | Quoi |
|---|---|
| `migrations/versions/029_add_retour_stock_link.py` | `retours_client.stock_id` (Integer, **NULLable**, index, FK vers `stocks.id` en mode batch SQLite / natif PostgreSQL). IDEMPOTENT par introspection, NON DESTRUCTIF, **aucune valeur ecrite** : les retours existants restent « ligne non precisee ». Downgrade volontairement sans effet (convention 027 : une colonne en trop ne casse rien, une donnee perdue est irreversible). |
| `app/models/magasin_avance.py` | Colonne `stock_id` avec commentaire de contrat : NULL = `/traiter` ne reintegre RIEN. |
| Schémas | `RetourClientCreate.stock_id: Optional[int]` (saisie explicite), `RetourClientResponse.stock_id` echo reel. `RetourClientUpdate` **n'inclut pas** `stock_id` : la liaison se declare a la creation, pas en retouche. |
| `POST /retours` | Verifie l'existence de la ligne de stock si fournie (400 explicite  FK SQLite non controlee par defaut). |
| `PUT /retours/{id}/traiter` | Reintegration **reelle** quand elle est modelisee : si `stock_id` renseignee, decision `accepte` et action ≠ `destruction` → `quantite_disponible` augmentee + **un `MouvementStock` ENTREE journalise** (avant/apres/raison/`reference = numero_retour`/operateur), dans le MEME commit que la decision (tout ou rien). Garde : quantite retournee absente ou nulle → **400 avant toute ecriture** (la decision reste `en_attente`, verrouillee par test). Sinon : **zero mouvement**, et la raison est tracee dans notes (`PAS DE REINTEGRATION STOCK : ligne de stock non precisee…`). `destruction` et `refuse` ne bougent jamais le stock. |

### Verification

- `python -m pytest tests/unit/test_magasin_avance_retour_stock.py -q` : ✅ **6 passed**  dont « la migration n'invente aucune valeur » (ancien retour reste NULL apres upgrade), « re-execution sure » (no-op), et le 400 tout-ou-rien sur quantite absente.
- Non-régression : `test_magasin_avance_retours_litiges.py` (batch 17) ✅ **9 passed** sans modification  son verrou « aucun mouvement quand la liaison n'existe pas » reste exact (les retours sans `stock_id` ne produisent toujours rien).
- `test_migrations_chain.py` ✅ **2 passed** : la chaine complete (029 inclus) monte jusqu'a la tete et redescend a `base` proprement  le test est head-agnostique, aucune edition necessaire.
- Suite complete (commande CI) : ✅ **645 passed, 2 xfailed, 0 failed** (344 s), `PYTEST_EXIT=0`, **`DB_CHANGED=False`** (mtime/taille `kamlog_erp.db` identiques avant/apres).
- `compileall` ✅ EXIT=0 ; `import app.main` ✅ OK (1138 chemins OpenAPI) ; `tsc --noEmit` ✅ EXIT=0 ; `audit_frontend.py --strict-honesty` ✅ EXIT=0 (batch sans changement frontend).

### Reste (hors perimetre du batch, signale)

- Etat reel verifie par introspection : la base de dev `kamlog_erp.db` porte
  DEJA la colonne `retours_client.stock_id` (creee par `create_all` a la
  derniere startup, la table ayant ete materialisee apres le changement de
  modele)  assertion controlee, pas supposee. Le chemin de production reste
  `alembic upgrade head` (029, puis les tranches concurrentlyes au-dela).
  - Side effect declare : la table de dev porte encore les colonnes heritees
  `article_id`/`etat`/`action_effectuee`/`date_traitement` des anciens schemas
  fantomes (NULLables, jamais lues par le code reconstruit) ; la convention
  027 est non-destructive, elles seront purgees le jour ou une decision de
  nettoyage de schema est prise  pas silencieusement.
- La **valeur** du retour reintegre (prix unitaire, lot, etat « bon pour
  réemploi ») n'est pas modelisee non plus : le mouvement est journalise au
  prix existant de la ligne de stock, et c'est la stricte verite du modele.

➡️ Zero-Mock applique au retour : refuser d'inventer une reintegration tant
que la liaison n'existe pas etait la bonne decision ; ne la rendre possible
que par une migration reelle, puis journaliser un `MouvementStock` seulement
quand l'operateur a designe la ligne de retour ET que la marchandise n'est pas
detruite, est la suite logique  une absence de reintegration se declare dans
les notes, elle ne se simule pas.

---

## 23. Batch 21  RBAC granulaire sur `/magasin-avance` : 43 endpoints qui n'attendaient qu'un droit

### Contexte et choix de la cible

Le backlog (`TODO.md`, phase 6) porte une ligne ⏳ : « Étendre `require_perm`
au-dela des domaines coeur (~323 routes restantes) ». Audit de l'etat reel :
une session concurrente a deja converti transport/comptabilite/magasin
(8 fichiers, ~180 appels `require_perm`). Les 43 endpoints de
`magasin_avance.py`  reconstruits aux batches 16-20  etaient les plus gros
restants proteges par la **seule authentification** : n'importe quel
utilisateur connecte pouvait valider une reception, traiter un retour ou
exporter les KPI. C'est cette cible qui a ete traitee, sans chevauchement
avec la session concurrente (aucun de ses fichiers n'est touche).

### Conversion (mapping explicite, pas de default)

Un script one-shot (`scripts/scratch_apply_magasin_perms.py`) remplace
chaque `Depends(get_current_user)` par `Depends(require_perm("…"))` avec une
table (methode + chemin) → code : **toute route sans mapping ou tout mapping
sans route fait echouer le script**  pas de protection « par defaut »
inventee. Resultat : 43/43 converties, 19 codes distincts, zero code fantome
(reverifie contre `iter_permission_rows()` du catalogue).

| Secteur | Codes appliques |
|---|---|
| Peremptions / FEFO | lecture `magasin.stock.read` ; poser une peremption `magasin.mouvement.create` |
| Reservations / kits / colis | execution `magasin.picking.*` ; consommer/assembler (mouvement reel) `magasin.mouvement.create` |
| Transferts | `magasin.mouvement.create` (un transfert EST un couple de mouvements) |
| Inventaires | `magasin.inventaire.read/create/modify` ; **valider** `…approve` |
| Receptions | `achats.reception.read/create/modify` ; **valider/refuser** `…approve` |
| Retours / litiges | declaration `magasin.mouvement.create` ; **traiter/resoudre** `…approve` |
| Reappro automatique | `achats.commande.create`  un vrai acte d'achat, pas un geste de depot |
| KPI rotation | `magasin.mouvement.export` ; precision = lecture d'inventaire |

### Roles : le catalogue complet, avec deux bugs reels trouves par les tests

La conversion aurait pu verrouiller le metier ; le moteur `can()` est additif
(level 0/1 bypass, repli `modules_allowed` pour un tenant jamais seede), mais
les roles granulaires devaient etre alignes. `MAGASINIER` etendu a toute
l'execution (14 codes, **aucune approval**) ; nouveau `CHEF_MAGASIN` level 2
(`magasin.*.*` + approvals + `achats.commande.create`). Deux premieres
versions des tests ont signale deux vraies incoherences de conception,
corrigees dans le catalogue : le chef ne pouvait pas **creer** une reception
(pourtant il les valide), et regle « tout sauf approve pour le magasinier »
lui aurait donne la commande d'achat automatique  refusee desormais, avec
assertion rouge explicite.

### Migration 033 + tests

- `migrations/versions/033_rbac_magasin_grants.py` : seed **purement additif**
  (codes manquants, role CHEF_MAGASIN, liens supplementaires MAGASINIER) ;
  ne supprime rien, downgrade = pass (convention 027). Garde explicite :
  tables RBAC absentes → **RuntimeError nommant la precondition** au lieu de
  passer en silence. Tete de chaine verifiee : `033_rbac_magasin_grants`.
- `tests/unit/test_rbac_magasin_perms.py` : ✅ **7 passed**  parite
  catalogue, coverage MAGASINIER/CHEF_MAGASIN dans les deux sens (vert
  autorise, rouge interdit), **403 HTTP reel** avec utilisateur limite
  (lecture 200 / declaration 403 / approval 403 **avant toute ecriture**,
  verrouillee par comptage), seed 033 rejoue sans duplication, et refus
  explicite sur base sans tables RBAC.

### Verification

- Non-régression ciblée : moteur RBAC + batches 17/18/19/20 + chaîne migrations ✅ **45 passed**  dont `test_magasin_avance_inventaires_fournisseurs.py` (batch 19) dont les utilisateurs SuperAdmin passent par le bypass level 0/1 du moteur, aucun test d'identité à réécrire.
- Suite complete (commande CI) : ✅ **659 passed, 2 xfailed, 0 failed** (538 s), `PYTEST_EXIT=0`. Le delta vs 645 inclut les 7 tests du batch 21 et des tests d'une session concurrente. Control `DB_CHANGED` **impossible ce run** : `kamlog_erp.db` verrouille par un process de dev concurrent (Get-FileHash echoue) ; l'absence de pollution repose sur le contrat conftest (`DATABASE_URL=:memory:` force, exit 0 = aucun fallback vers l'engine reel), et le hash n'a pas ete declare a tort.
- `compileall` ✅ EXIT=0 ; `import app.main` ✅ OK (**1140** chemins OpenAPI, derive concurrente inclue).
- Frontend : **aucun changement batch 21** ; `audit_frontend.py --strict-honesty` ✅ EXIT=0. `tsc --noEmit` ❌ **rouge de cause externe** : import `ReceiptText` inexistant dans `lucide-react`, committe par la session concurrente sur `transit-douane/dashboard/page.tsx` (ni mon fichier, ni mon lot)  signale, volontairement **ne corrige pas** pour ne pas ecraser une session active.

### Reste (hors perimetre du batch, signale)

- ~40 autres routeurs restent proteges par la seule authentification (rh 43,
  qhse 43, transit_avance 40, acconage_avance 38, finance 37…)  la ligne ⏳
  du TODO phase 6 n'est pas close ; chaque future tranche devra le meme
  mapping explicite + alignement roles.
- `visible_user_ids` n'est toujours pas branche sur les listes portant
  `created_by`/`department_id` (2e moitie de la ligne ⏳).
- La description de role `MAGASINIER` changee dans le catalogue ne remet pas
  a jour la colonne `description` des lignes existantes (033 est additive
  sur les liens, pas sur les metastadonnees)  cosmetique, declare.
- L'erreur `tsc` concurrente devra etre reparee par son auteur ou dans un
  lot dedie transit-douane.

➡️ Zero-Mock applique a l'autorisation : un endpoint qui « reussit » devant
n'importe qui est une faille habillee en fonctionnalite ; ici chaque droit
 requis existe au catalogue, chaque role qui doit agir peut agir  et la
 preuve du 403 est un appel HTTP reel, pas une assertion sur un mock.

---

## 24. Batch 22  RBAC granulaire sur `/api/v1/finance` : 37 endpoints, la meme discipline

### Contexte et choix de la cible

Toujours la ligne ⏳ du `TODO.md` (phase 6, « etendre `require_perm` au-dela des
domaines coeur »). Audit de l'etat reel : apres les conversions deja faites
(domaines coeur par une session concurrente, puis `magasin_avance` batch 21),
**49 routeurs `v1` restent proteges par la seule authentification** ; `finance.py`
(37 endpoints, 0 `require_perm`, aucun commit concurrent depuis 2026-09-30 18:00)
est choisi : domaine sensible (factures,
ecritures, fiscal, tresorerie), aucun chevauchement avec la session concurrente.
N'importe quel utilisateur connecte pouvait creer une facture, cloturer un exercice
ou exporter le PDF signe.

### Conversion (mapping explicite, table (methode + chemin) → code)

Meme script one-shot (`scripts/scratch_apply_finance_perms.py`) que le batch 21 :
toute route sans mapping ou tout mapping sans route fait echouer le script, aucun
code par defaut. Resultat : **37/37 converties, 24 codes distincts**, zero code
fantome (revue contre `iter_permission_rows()` ; `scripts/scratch_check_perm_codes.py`
→ « inconnus au catalogue : AUCUN »).

| Secteur | Decisions semantiques |
|---|---|
| Plan comptable SYSCOHADA | `comptabilite.plan_comptable.read/create/modify`  creer un compte n'est **pas** une ecriture de journal |
| Ecritures | saisie `journal.create`, corriger `journal.modify`, **valider** `journal.approve` (l'approbation reste un acte distinct, jamais donne au comptable par defaut) |
| Exercices | ouvrir `exercice.create`, **cloturer** `exercice.approve` |
| Facturation | creer/lignes/maj `facture.create/modify`, PDF `facture.export`, **signature electronique** `facture.approve` |
| Reglements / encaissements | = mouvements de **tresorerie** (`mouvement.read/create/modify`) |
| Declarations fiscales CEMAC | preparer seulement `declarations.create/modify` ; le depot reel reste **501** (aucune integration GUCE) donc **aucun approve expose**  les endpoints sont des brouillons |
| Etats de synthese | creer/modifier bilan/CR ≠ les approuver (`bilan.approve` reserve aux etats validates) |
| KPI / series | `facturation.facture.read`  convention alignee sur `transport_avance` (kpi → read du domaine qui calcule) |

### Catalogue : sous-modules dedies, pas de plaquage

Faute de code existant adapte honnetement, le catalogue a ete **etendu** (nouveau
sous-module plutot que plaquer sur « journal », ce qui aurait ete du bricolage) :
`comptabilite.plan_comptable`/`exercice`/`compte_resultat`, `bilan` enrichi
create/modify, `fiscalite.declarations` enrichi modify. Cotes roles : nouveau
**`CAISSIER`** level 3 (mouvements de tresorerie + lecture facture),
`CHEF_COMPTABLE` enrichi (facture/declarations create+modify), `COMPTABLE` enrichi
(plan lecture, ecriture modify, facture modify/export), `AUDITEUR` +lecture fiscale.

### Migration 034 + tests

- `migrations/versions/034_rbac_finance_grants.py` : seed **purement additif**
  (codes manquants, role CAISSIER, liens supplementaires par role cible) ; ne
  supprime rien, `downgrade = pass`, garde **RuntimeError** nommant la precondition
  si les tables RBAC absentes. Tete de chaine verifiee : `034_rbac_finance_grants`.
- `tests/unit/test_rbac_finance_perms.py` : ✅ **12 passed des le premier run** 
  parite catalogue (24 codes), **matrice complete role × code** avec attentes
  explicites par role (DIRECTEUR tout, CHEF tout sauf mouvement create/modify,
  COMPTABLE 11 codes, CAISSIER 4 codes, AUDITEUR lecture seule), test « chaque code
  a au moins un role porteur » (aucun endpoint fonctionnellement inatteignable),
  **403 HTTP reels** côté caissier (encaissements 200 / creation facture 403 verifie
  sur les **deux** tables de factures / cloturer exercice 403, **avant toute
  ecriture**), et seed 034 rejoue sans duplication + refus sur base sans tables.

### Fallout : deux faux utilisateurs repares (convention reutilisable)

Le run de non-regression cible a d'abord donne **2 failed, 50 passed** :
`test_numerotation.py` et `test_pdf_generator.py` planaient sur
`AttributeError: '_FakeUser' object has no attribute 'is_superuser'`. Cause reelle
et non masquee : des que `/finance` exige `require_perm`, un utilisateur sans lignes
de permissions granulaires tombe sur le repli `can_access_module`, qui lit
directement `user.is_superuser`  les faux minimalistes (id/username/company_id)
n'avaient pas cette colonne. Choix : **reparer les faux** (un vrai `User` ORM porte
toujours `is_superuser`, `role_level`, `email`, `is_active`) plutot qu'affaiblir
l'acces securite du moteur. Les deux leurres portent desormais les attributs
complets, commentaire a l'appui. Apres reparation : non-regression ciblee ✅
**64 passed**.

### Verification

- Suite complete (commande CI) : ✅ **691 passed, 2 xfailed, 0 failed** (475 s),
  `PYTEST_EXIT=0`. Delta vs 659 (batch 21) = 12 tests du batch 22 + tests ajoutes
  par la session concurrente ; **aucun echec imputable au lot**.
- Control `DB_CHANGED` **lisible et vierge ce run** : `kamlog_erp.db` date de
  9/28/2026 03:35, anterieur au run du jour → la suite n'a pas ecrit dans la base
  de dev (contrat conftest `:memory:` respecte), contrairement au batch 21 ou le
  hash etait illisible.
- `compileall app` ✅ EXIT=0 ; `import app.main` ✅ OK (**1141** chemins OpenAPI,
  derive concurrente +1 inclue).
- Frontend : **aucun changement batch 22** ; `audit_frontend.py --strict-honesty`
  ✅ ; `tsc --noEmit` ✅ **EXIT=0**  l'erreur `ReceiptText` signalee au §23 (cause
  externe) a depuis ete reparee par son auteur.

### Reste (hors perimetre du batch, signale)

- **48 autres routeurs** (inventorieres apres conversion finance) restent proteges par la seule authentification (rh, qhse 38,
  transit_avance 40, acconage_avance 38, magasin_douane 35, integration 28,
  acquisition 27, documents 25, gap_bridges 24, notifications/reporting 23…)  la
  ligne ⏳ du TODO phase 6 n'est pas close ; chaque tranche devra le meme mapping
  explicite + alignement roles + migration additive.
- `visible_user_ids` n'est toujours pas branche sur les listes portant
  `created_by`/`department_id` (2e moitie de la ligne ⏳).
- Les metastadonnees `description` des roles changes dans le catalogue ne sont pas
  reecrites par la migration 034 (additive sur les liens)  cosmetique, declare.
- Convention retenue pour les prochains lots : tout leurre d'identite destinant a
  passer une garde `require_perm` doit porter `is_superuser`/`role_level`/`email`/
  `is_active`, faute de quoi il tombe sur le repli `can_access_module`.

➡️ Zero-Mock applique a la finance : un droit d'approbation comptable ou fiscale
n'est jamais accorde « par defaut » ; la cloture d'exercice, la signature de facture
et l'approval d'ecriture restent des actes distincts, et le depot fiscal  qui
n'existe pas sans GUCE  n'expose aucun bouton « approuve » mensonger.

---

## 25. Batch 23  RBAC granulaire sur `/api/v1/acconage-avance` : 38 endpoints du quai

### Contexte et choix de la cible

Toujours la ligne ⏳ du `TODO.md` (phase 6). Nouveau depart d'audit : **49
routeurs `v1`** encore proteges par la seule authentification. Trois gros
candidates : `transit_avance` (40), `acconage_avance` (38), `qhse` (38). Choix
guide par l'honnetete architecturale et la non-interference : `transit_avance`
est le domaine actif de la session concurrente (elle y commute frontend et
backend depuis trois jours)  **ecarte** pour ne pas ecraser son travail en
cours ; `qhse` n'a **aucun code au catalogue** (il faudrait inventer tout un
domaine dans le meme mouvement  garde pour un lot dedie) ; `acconage_avance`
cumule : fichier intact depuis le 26/09, module `acconage` deja couvert
partiellement au catalogue (escale/manifeste/stevedoring), et 38 endpoints
reels d'acconage portuaire.

### Conversion (38/38, 30 codes, meme discipline)

`scripts/scratch_apply_acconage_perms.py` : table (methode + chemin) → code
explicite, echec si route sans mapping ou mapping sans route, zero reste
`get_current_user`. Parite contre le catalogue : « inconnus : AUCUN ».

| Secteur | Decisions semantiques |
|---|---|
| Navires | nouveau sous-module `acconage.navire` — un navire n'est pas une escale |
| Escales + rapport + **amarage** | `escale.read/create/modify` ; l'amarage est un jalon de l'escale, pas un objet a vie propre → `escale.modify` (pas de sous-module gonfle) |
| Stowage | preparer `stowage.create/modify` ; **valider l'arrimage** `stowage.approve` (engage la securite du chargement) |
| Grues / remorqueurs | registre = `moyen.read/create/modify` ; disponibilite = `moyen.read` |
| Reservation de grue | objet propre → `reservation.create` |
| Connaissements / packing-lists | `connaissement.create/modify`, `packing_list.create`  titres juridiques, hors portee des roles quai |
| Manifestes | sous-module existant ; marchandises dangereuses = `manifeste.modify` |
| Surestaries + THC | nouveau `acconage.frais` (calcul = create, lecture = read, contestation = modify  acte du chef) |
| Dockers temporaires | affecter/lister/modifier/retirer = CRUD `dockers` ; **cloturer** (paie engagee) `dockers.approve` |

### Catalogue + roles : 10 sous-modules neufs, deux roles metier

Sous-modules ajoutes a `acconage` : `navire`, `stowage`, `moyen`,
`reservation`, `conteneur`, `connaissement`, `packing_list`, `frais`,
`nettoyage`, `dockers`. Roles : nouveau **`CHEF_EXPLOITATION`** level 2
(`acconage.*.*` + lecture magasin/transport) et **`OPERATEUR_ACCONAGE`**
level 3 (23 codes d'execution, **huit refus explicites** verifies rouges :
navire.create, stowage.approve, moyen.create/modify, connaissement
create/modify, frais.modify, dockers.approve). `TRANSIT_PRINCIPAL` conserve
son `acconage.*.read` (lecture seule, deja seedee) ; `DECLARANT` ne voit que
le manifeste.

### Migration 035 + tests

- `migrations/versions/035_rbac_acconage_grants.py` : purement additive,
  `downgrade = pass`, garde RuntimeError si tables RBAC absentes ; tete de
  chaine verifiee `035_rbac_acconage_grants`.
- `tests/unit/test_rbac_acconage_perms.py` : ✅ **14 passed des le premier
  run** — parite (30 codes), **matrice 4 roles × 30 codes** avec garde-fou
  interne (les listes operateur doivent epuiser l'ensemble), « chaque code a
  un role porteur », **403 HTTP reels** (operateur refuse sur valider-stowage
  / emettre-connaissement / cloture-dockers  le 403 avant meme le 404 prouve
  que le droit est verifie avant la base ; transitaire principal 200 en
  lecture / 403 a la creation d'escale), test de **porte ouverte** sur la
  reservation de grue (ni 403 ni 500), idempotence 035 et refus sur base
  sans tables.

### Pas de fallout fake-user, et c'est verifie  pas suppose

La convention du batch 22 (les leurres d'identite doivent porter
`is_superuser`/`role_level`) a ete appliquee en amont : grep des tests visant
`/api/v1/acconage-avance` → **aucun trafic de test sur le prefixe converti** ;
la non-regression ciblee (acconage + moteur + rbac 21/22 + chaine migrations +
audit gaps) passe du premier coup : ✅ **54 passed, 0 failed**.

### Verification

- Suite complete (commande CI) : ✅ **705 passed, 2 xfailed, 0 failed**
  (442 s), `PYTEST_EXIT=0`. Delta vs 691 = exactement les 14 tests du lot.
- `DB_CHANGED` : `kamlog_erp.db` toujours date du 9/28 03:35, anterieur a
  tous les runs → base de dev intacte.
- `compileall app` ✅ EXIT=0 ; `import app.main` ✅ (**1142** chemins
  OpenAPI, +1 d'origine concurrente — la conversion n'ajoute aucune route).
- Frontend : **aucun changement batch 23** ; `audit --strict-honesty` ✅ ;
  `tsc --noEmit` ❌ **rouge de cause externe** : erreur de syntaxe
  (`TS1005 '}' expected`) dans `portail-commercial/page.tsx`, fichier **non
  committe** (etat `M`) d'une session concurrente active  signale,
  volontairement non corrige (precedent du §23 : l'auteur avait repare le
  sien).

### Reste (hors perimetre du batch, signale)

- **47 routeurs / 498 endpoints** encore proteges par la seule
  authentification — dont une part legitime (self-service `auth.py`,
  endpoints utilisateur courant) ; les prochains lots naturels :
  `qhse` (38, avec creation d'un domaine catalogue complet),
  `magasin_douane` (35), `integration` (28), `acquisition` (27) ;
  `transit_avance` (40) n'interviendra que quand la session concurrente
  l'aura libere.
- `visible_user_ids` toujours non branche sur les listes `created_by` /
  `department_id` (2e moitie de la ligne ⏳).
- Les descriptions de roles changees dans le catalogue restent cosmetiques
  en base (migrations additives sur les liens uniquement) — declare depuis §23.

➡️ Zero-Mock applique au quai : valider un plan d'arrimage, emettre un
connaissement ou cloturer la liste des dockers sont des actes qui engagent
respectivement la securite du navire, un titre juridique et une paie ; ils ne
peuvent plus etre accomplis par « n'importe qui connecte »  et la preuve du
refus est un HTTP 403 reel, pas une assertion sur un mock.

---

* Aucun acte à valeur légale (validation CNCC, dépôt GUCE/SYDONIA, quittance, bulletin CNPS,
  paiement mobile money) n'est jamais affiché comme "fait" s'il ne l'est pas : soit c'est réel,
  soit l'API répond **501 avec la raison exacte**.
* Aucun écran opérationnel n'affiche de données inventées : valeurs manquantes = "Non renseigné".
* Le endpoint de webhook SaaS ne peut plus être déclenché par un tiers non authentifié.
* Le frontend ne peut plus crasher sur un formatage XAF, et les actions restent accessibles au tactile.
* Le PDF de facture est réellement généré (mentions légales DGI incluses) ou répond 501 avec la
  raison exacte ; le mode hors-ligne champ (outbox + service worker) fonctionne vraiment, avec
  authentification des synchronisations.
