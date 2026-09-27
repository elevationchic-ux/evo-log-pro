# Rapport  Corrections P0 "Honnêteté & Sécurité" (batch exécuté)

> Suite de l'audit à 3 volets (Cameroun/CEMAC 3/10, UX novice 3/10, couverture chaîne ~55-60%).
> Principe appliqué : **le système ne doit jamais simuler un acte juridique, financier ou
> opérationnel qui n'a pas eu lieu.** Convention existante `app/core/not_implemented.py`
> (HTTP 501 explicite) étendue partout où elle était violée.

## Vérifications finales (exécutées)

| Contrôle | Résultat |
|---|---|
| `python -m compileall app tests` | ✅ EXIT=0 |
| `python -m pytest tests` (commande exacte de la CI, suite complete batches 2 a 14) | ✅ **485 passed, 2 xfailed, 0 failed** (305 s). Historique : les 2 « failures » annoncees a tort en batch 12 ne se reproduisaient pas (§15, retraction) ; la vraie cause des fluctuations d'ordre etait un trou d'isolation du harnais pytest qui **ecrivait dans la base de dev `kamlog_erp.db`** — corrige, verrouille par meta-tests et `DB_CHANGED=False` sur le run definitif (§16). |
| `import app.main` (tous routers chargés, plus aucun ImportError avalé) | ✅ OK  endpoint `/api/v1/finance/factures/{id}/pdf` déclaré (1082 routes OpenAPI) |
| `npx tsc --noEmit` (frontend) | ✅ EXIT=0 |

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
- ~~Remplacer les `any` des pages branchées cette semaine par les types existants de `src/types/`.~~ → **PARTIELLEMENT FAIT (batch 10, voir §12)** : `src/types/transport.ts` était un **contrat mort** dont les champs ne correspondaient à aucun schéma backend — réaligné sur le vrai contrat et adopté par `transport/planning` + `transport/control`. Les ~700 `any` restants dans `src/` exigent la même réécriture module par module.
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
4 étapes en `non_liciable_en_base` — **déclaration douanière, magasin sous douane, mission de
livraison, facture** — faute de tout chemin les rattachant au conteneur/B/L de l'ancre. Ces tables
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

**Problème** : `src/types/transport.ts::Mission` était un type **mort** — 0 import
dans tout `src/` (`grep "from '@/types/transport'"` → 0 résultat) — dont les champs
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
Sans typage, le rendu affichait `undefined km` — un faux chiffre. **Correction** :
badge coloré sur `alt.priorite` (rouge CRITIQUE / ambre HAUTE / ardoise MOYENNE)
+ libellé "Echeance : {date fr-FR}" uniquement quand `alt.echeance != null`.
Aucun km n'est inventé ; le champ fantôme disparaît du type.

**Vérification batch 10** : `npx tsc --noEmit` → **EXIT=0** ;
`python scripts/audit_frontend.py` → `broken_links: 0, dead_buttons: 0, fake_data: 0, ghost_routes: 0`.
Les 33 `api_gaps` restants sont des endpoints backend non implémentés (`/api/parc/*`,
`/api/v1/customers`, `/api/v1/telematics/positions`…) : hors périmètre d'un batch de typage.

➡️ Ce n'est qu'une **première brique** : 717 occurrences d'`any` restent dans `src/`.
Le vrai gain structurel est que `src/types/transport.ts` est désormais **adoptable** —
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
| `evo-log-frontend/scripts/audit_frontend.py` | Ajout du flag `--strict-honesty` : exit 1 **uniquement** si l'une des 4 metriques d'honnetete (`broken_links`, `dead_buttons`, `fake_data`, `ghost_routes`) repasse au-dessus de 0. Les `api_gaps` restent affiches et enregistres dans `audit_report.json` mais ne font plus echouer le script. Justification consignee dans le `help` : un appel frontend vers un endpoint backend non implemente est un **trou de couverture** (reponse 501 explicite du backend), pas une regression Zero-Mock — l'inverse d'un faux succes. |
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
corrige 4-5 champs — il a montre que **la page entiere etait structurellement
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
| `src/app/(app)/transport-international/page.tsx` (reecrite) | `useState<OrdreTransportResponse[]>` / `<CarnetTIRResponse[]>` ; tous les acces aux champs corriges (`numero_ot`, `type_transit`, `lieu_chargement`/`lieu_livraison`, `poids_net`) ; objet `STATUTS` centralise avec les valeurs backend sans accent ; compteur "En transit" et "Livres" recalculs sur `STATUTS.EN_TRANSIT` / `STATUTS.LIVRE` qui matchent enfin ; **formulaire de creation remplace par un bouton "N.I."** (Non Implemente) qui ouvre un `toast()` expliquant precisement pourquoi (4 FK + 5 numeriques obligatoires non collectes) — Zero-Mock : un bouton qui affiche une UI mensongere et declenche un 422 avale est **pire** qu'un bouton absent. |

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
En Zero-Mock, on ne peut pas laisser une affirmation fausse trainer dans un rapport —
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

**Cause probable de l'erreur du batch 12** : *[RETRACTEE EN BATCH 14 — voir §16. La
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
  collecte. A traiter sous forme de tâche dedicated "isolation des fixtures pytest" —
  **pas** sous forme de security P0 comme le laissait entendre le batch 12.
- **Aucune action immediate** sur les 2 tests cites.

➡️ Le principe Zero-Mock s'applique aussi aux **rapports** : une fausse accusation de
trou de securite coutera plus cher a corriger plus tard qu'une retractation immediate.

**Bonus : 2 vraies regressions front capturees par le verrou CI batch 11**

En re-activant `python scripts/audit_frontend.py --strict-honesty` et `npx tsc --noEmit`
en toute fin de batch 13, deux bugs reels sont tombes — preuve que le gate CI place en
batch 11 n'etait pas decoratif :

| Fichier | Bug | Correction |
|---|---|---|
| `src/config/navigationRegistry.ts` (l.1156) | Le lien "Profil Entreprise (SaaS)" pointait vers `/admin-entreprise/profil` ; **aucun `page.tsx` n'existait** a ce chemin. Le clic dans la sidebar partait en 404. | Repointe vers `/company` (page existante qui rend deja `GET/PUT /api/v1/tenant/company-profile` avec bouton "Enregistrer le Profil Entreprise"). Commentaire Zero-Mock dans le registre. |
| `src/app/(app)/admin-entreprise/modules/page.tsx` (l.149) | (a) chaine `'Votre demande est en cours d'examen.'` **cassait la syntaxe JS** (apostrophe non escapee a l'interieur d'un single-quote) — `tsc` sortait en TS1005/TS1381 ; (b) comparaison `m.etat === 'alloué' \|\| m.etat === 'alloue'` : la premiere branche etait **morte** (le backend `company_admin.py:421` renvoie systematiquement `alloue` sans accent), TS2367 le signale. | (a) remplacee par double-quote `"Votre demande est en cours d'examen."` ; (b) branche accentuee supprimee + commentaire Zero-Mock. |

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
symptome visible d'un bien pire — **les runs de tests mutaient `kamlog_erp.db`, la
base SQLite reelle de developpement**.

**Preuve materielle** : `LastWriteTime` du fichier = **28/09 02:37:47**, soit EN PLEIN
run pytest (avant ce batch, le fichier ne devait plus bouger que par l'app en local).

**Chaine causale complete** :

1. La fixture `client` du conftest surcharge `get_db` (base memoire) ET
   `get_current_user` (faux super-utilisateur) — contrat en vigueur depuis le
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
   de faux-vert que le Zero-Mock interdit — appliquee ici a l'infra de test.
6. Les 13 fluctuations de `test_magasin_stock_analytics.py` (batch 13) et la
   fausse « contention arriere-plan » (retractee en §15) partagent cette cause.

**Corrections** :

| Fichier | Probleme | Correction |
|---|---|---|
| `tests/conftest.py` | Aucun garde-fou : tout override `get_db` perdu partait sur le fichier de dev | **Guard Zero-Pollution** : `os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")` AVANT l'import de l'app (une requete perdue echoue bruyamment « no such table » au lieu d'ecrire dans la base de dev) ; docstring CONTRAT ; nouvelle fixture `unauthenticated` (ne pop QUE `get_current_user`, la restaure en finally) |
| `test_rbac_permissions_engine.py` | 3 `dependency_overrides.clear()` en milieu de test — source material de la mutation du fichier | Helper local `_anonyme()` qui ne pop que `get_current_user` |
| `test_cadc_arbitrage_phase3.py`, `test_company_admin_phase2.py`, `test_saas_console_cadc.py`, `test_tenant_console_rbac.py` | Helper `_clear()` = `.clear()` (mine endormie : aucun test ne requetait apres, mais suffisait d'un futur ajout) | Corps de `_clear()` → `pop(get_current_user, None)` + commentaire |
| `test_transport_international.py` | `test_endpoint_exige_auth` creait un `TestClient(app)` **nu** apres clear : aucun override `get_db` du tout | Fixture `unauthenticated` |
| `test_parc_purchase_store.py`, `test_pdf_generator.py` | Patterns manuels de pop pour les tests 401 | Migres vers `unauthenticated` |
| `tests/unit/test_isolation_guards.py` (**nouveau**) | Le contrat n'etait verrouille par rien | 3 meta-tests : `client` porte les 2 overrides ; `unauthenticated` CONSERVE `get_db` (verifie avant ET apres une requete 401) ; l'engine/`settings` applicatifs ne pointent JAMAIS sur `kamlog_erp.db` |
| `test_real_backend.py`, `test_simple_real.py` | `test_database_tables_exist` inspectait l'engine global : vert uniquement parce qu'il lisait le fichier de dev (et dependant de l'ordre apres le garde-fou) | Fixture `client` : le startup du TestClient (lifespan → `create_all`) rend l'assertion hermetique et reellement executee. Variante `skipif` (test toujour saute en local/CI) ecartee : **un test saute n'est pas un test** |

**Verification** :
- Subset 8 fichiers (les plus touches) : **112 passed**, `DB_CHANGED=False`
  (mtime 02:37:47 identique avant/apres le run).
- `test_isolation_guards.py` : 3 passed.
- Premier run complet posterieur aux correctifs : 3 failed / 479 passed — les 3
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

➡️ Zero-Mock applique a l'infra : un test vert qui lit/ecrit la base de prod-dev
reelle est un faux-vert avec effet de bord reel. Le contrat des fixtures est
desormais (1) force par l'environnement (`DATABASE_URL` memoire), (2) documente
(docstring du conftest), et (3) verrouille par des meta-tests qui rougissent des
qu'un maillon saute.

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
