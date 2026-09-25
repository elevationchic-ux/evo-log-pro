# Rapport  Corrections P0 "Honnêteté & Sécurité" (batch exécuté)

> Suite de l'audit à 3 volets (Cameroun/CEMAC 3/10, UX novice 3/10, couverture chaîne ~55-60%).
> Principe appliqué : **le système ne doit jamais simuler un acte juridique, financier ou
> opérationnel qui n'a pas eu lieu.** Convention existante `app/core/not_implemented.py`
> (HTTP 501 explicite) étendue partout où elle était violée.

## Vérifications finales (exécutées)

| Contrôle | Résultat |
|---|---|
| `python -m compileall app` | ✅ EXIT=0 |
| `python -m pytest tests` (suite complète, batches 2 à 9 inclus) | ✅ **393 passed, 2 xfailed** (IRGM/CNPS sur service réel + chaîne documentaire close + redevances portuaires réelles + numérotation légale + moteur douanier unifié + import tarif CEMAC) |
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
- Remplacer les `any` des pages branchées cette semaine par les types existants de `src/types/`.
- Ajouter un linteau CI (`tsc --noEmit` + `pytest`) sur les rapports de coverage par module.

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

* Aucun acte à valeur légale (validation CNCC, dépôt GUCE/SYDONIA, quittance, bulletin CNPS,
  paiement mobile money) n'est jamais affiché comme "fait" s'il ne l'est pas : soit c'est réel,
  soit l'API répond **501 avec la raison exacte**.
* Aucun écran opérationnel n'affiche de données inventées : valeurs manquantes = "Non renseigné".
* Le endpoint de webhook SaaS ne peut plus être déclenché par un tiers non authentifié.
* Le frontend ne peut plus crasher sur un formatage XAF, et les actions restent accessibles au tactile.
* Le PDF de facture est réellement généré (mentions légales DGI incluses) ou répond 501 avec la
  raison exacte ; le mode hors-ligne champ (outbox + service worker) fonctionne vraiment, avec
  authentification des synchronisations.
