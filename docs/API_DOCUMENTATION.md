# API Documentation  EVO-LOG SaaS

## Source de Vérité

Pour les schémas OpenAPI interactifs, la validation des contrats Pydantic et l'essai des endpoints en direct :

- **Swagger UI** : `http://localhost:8000/api/docs` (ou `https://your-backend.up.railway.app/api/docs` en production)
- **ReDoc** : `http://localhost:8000/api/redoc`

---

## 🌐 Endpoints d'Observabilité & Health Check

- `GET /api/health` : Statut général du service (utilisé par Railway).
- `GET /api/health/detailed` : État détaillé des connexions BDD PostgreSQL, Redis et MinIO.

---

## 🗺️ Cartographie des Routeurs FastAPI

| Préfixe Routeur | Domaine Métier | Description & Entités associées |
| --- | --- | --- |
| `/api/auth` | Authentification & Sécurité | Connexion JWT, rafraîchissement de token, `/me`, déconnexion, MFA, politique mot de passe |
| `/api/admin` | Administration RBAC | Gestion des utilisateurs, attribution des profils et des autorisations `modules_allowed`, audit |
| `/api/admin/agencies` | Agences & Multi-Agences | RLS multi-tenant, agences portuaires (Douala, Kribi, Yaoundé) |
| `/api/tiers` | Tiers & Partenaires | Fiches clients, armateurs, transporteurs, transitaires |
| `/api/suppliers` | Fournisseurs | Homologation, suivi des fournisseurs de services et pièces |
| `/api/master-data` | Données de Référence | Référentiels d'articles, devises, unités, ports |
| `/api/transport` | Transport & Livraisons | Flotte camions, chauffeurs, ordonnancement des missions, carburant |
| `/api/transport/goods-declarations` | Déclarations de Marchandises | Connaissements (BL), manifestes portuaires, déclarations cargaison |
| `/api/parc` | Yard & Emplacements | Zones de stockage, mouvements de conteneurs, pesage et porte (Gate) |
| `/api/magasin` | Stock & WMS | Entrepôts, catalogue d'articles, inventaires, transferts |
| `/api/magasin/receptions-mag3` | Réceptions Mag3 | Réceptions d'articles Mag3 et contrôle d'entrée |
| `/api/magasin/removal-slips` | Bons d'Enlèvement Mag3 | Bons d'enlèvement et sorties de stock |
| `/api/finance` | Finance & Rapprochement | Facturation, factures d'acconage/transit, encaissements, dépenses |
| `/api/purchase` | Procurement & Achats | Demandes d'achat, bons de commande, workflows de validation |
| `/api/documents` | Impression & PDF | Génération de documents PDF WeasyPrint (factures, bons de livraison, BL) |
| `/api/alerts` | Alertes Applicatives | Notifications d'anomalies de stock, retards de livraison, carburant |
| `/api/notifications` | Notifications Web | Notifications temps réel pour les utilisateurs |
| `/api/transactions` | Journal Comptable | Audit des mouvements transactionnels et journaux de stock |
| `/api/gateway` | Inter-Modules | Passerelles et échanges de données entre modules métiers |
| `/api/v1/rbac` | RBAC granulaire | Catalogue de permissions, rôles & grants, permissions d'un rôle (GET/PUT), `/permissions/check` |
| `/api/v1/accreditations` | Accréditations | Habilitations nominatives datées (`permission` / `scope`), gestion admin + `mes-accreditations` |
| `/api/v1/shared-access` | Espaces communs | Modules communs par entreprise (`GET`, `POST`, `DELETE`, `/initialiser`) |
| `/api/v1/saas/console` | Console SuperAdmin CADC (niv. 0) | CRUD entreprises + upload logo, plans d'abonnement (`max_modules`), allocation de modules, accréditations entreprises, demandes d'accréditation (approuver/refuser), annuaire prestataires. Garde `require_superadmin`. |
| `/api/v1/company-admin` | Administration Entreprise (niv. 1) | Profil société, CRUD collaborateurs scopés, responsabilités/statuts, modules alloués/verrouillés + demandes d'accréditation vers le CADC. Garde `require_company_admin` + scope `company_id`. |
| `/api/v1/departement` | Espace Département (niv. 2) | Vue d'ensemble, roster membres/candidats, affectation, **planning** (publication « au mercredi » de la semaine précédente), **présence/pointage** + validation. Épinglé au `department_id` de l'agent. |
| `/api/v1/amenagement-portuaire` | Aménagement Portuaire & Domaine Public (département autonome) | 60 endpoints, `amenagement.<sous_module>.<action>` : `places` (référentiel national des ports), `schemas-directeurs`, `projets`, `programmation` (PIP/CDMT + visa de maturité), `marches` (PPP loi n°2023/008), `titres-domaniaux` (AOT, conventions d'occupation, attributions), `concessions`, `infrastructures`, `dragage`, `autorisations` (EIES), plus `nomenclatures` et `synthese`. Détail : § ci-dessous. |

---

## 🔐 Matrice des Rôles & Accès API

| Rôle RBAC | Module d'Entrée | Préfixes Accès API Autorisé |
| --- | --- | --- |
| `ADMIN` | `/admin` | Tous les préfixes API (`/api/*`) |
| `MAGASINIER` | `/magasin` | `/api/magasin`, `/api/master-data`, `/api/documents` |
| `DISPATCHER` | `/transport` | `/api/transport`, `/api/parc`, `/api/tiers`, `/api/documents` |
| `QHSE` | `/qhse` | `/api/alerts`, `/api/notifications`, `/api/documents` |
| `FINANCIER` | `/finance` | `/api/finance`, `/api/purchase`, `/api/suppliers`, `/api/documents` |
| `DOUANE` | `/douane` | `/api/transport/goods-declarations`, `/api/tiers`, `/api/documents` |
| `PARC` | `/parc` | `/api/parc`, `/api/transport`, `/api/documents` |
| `AUDITOR` | `/reports` | `/api/transactions`, `/api/alerts`, `/api/admin` (Lecture seule) |

> **Au-delà des préfixes.** Depuis la migration `020_rbac_granulaire_accreditations`,
> l'accès est affiné par **permissions granulaires** `module.sous_module.action`
> (`require_perm`) et par **visibilité hiérarchique** (`visible_user_ids`). La matrice
> ci-dessus reste le niveau grossier `modules_allowed` (fallback). Détail complet :
> [`RBAC_ACCREDITATIONS.md`](./RBAC_ACCREDITATIONS.md).

---

## 🧭 Gouvernance SaaS multi-niveaux & Présence (Phases 1-4)

Le modèle d'accès s'articule autour de `User.role_level` :

| Niveau | Profil | Surface dédiée |
| --- | --- | --- |
| `0` | Super-Admin **CADC** | `/api/v1/saas/console` + UI `admin/super-admin/*` |
| `1` | **Admin Entreprise** | `/api/v1/company-admin` + UI `admin/*` |
| `2` | **Chef de département** | `/api/v1/departement` + UI `departement/*` |
| `3` | **Collaborateur** | Hub par défaut `/portail-collaborateur` |

### Présence / pointage automatique (`/api/v1/auth`)

- **Arrivée** : à chaque ouverture de session effective (`POST /auth/login` et
  `POST /auth/2fa/verify`), une pointe d'arrivée est **auto-enregistrée** pour un
  collaborateur de niveau 3 rattaché à un département (idempotente par jour, meilleure
  effort : ne bloque **jamais** la connexion). L'écart à l'heure de début du
  `PlanningGarde` du jour est calculé (retard au-delà d'une tolérance de 5 min) et
  renvoyé dans `pointage_info`, affiché en toast au login.
- **Départ** : `POST /api/v1/auth/pointer-depart` (authentifié) clôture la journée et
  calcule `heures_effectives` (gère le passage de minuit pour les quarts de nuit).
  Côté UI, le départ est tenté en best-effort à la déconnexion.

### Planning du département (`/api/v1/departement/planning`)

Publication des gardes **confirmées** contrainte « **au mercredi de la semaine
préalable** » : au-delà de cette date, la confirmation renvoie `400 Publication
fermée`. Les écritures restent scopées au département de l'agent.

### Utilisateur ≠ Rôle (beaucoup-à-beaucoup)

Un `User` porte son **identité employé** (`matricule`, `job_title`) séparée de ses
**casquettes** (`roles`). Le rôle détermine l'accès ; un utilisateur peut cumuler
plusieurs rôles.

- `GET/POST/PUT /api/v1/admin/users` : lit/écrit l'identité (`matricule`, `job_title`).
- `PUT /api/v1/admin/users/{user_id}/roles` : remplace l'ensemble des casquettes
  (liste de noms de rôles). `role_level` est **re-dérivé** du rôle le plus privilégié ;
  les rôles standard absents de la base sont matérialisés (get-or-create).
  **Anti-escalade** : un non-Super-Admin ne peut ni accorder `SUPER_ADMIN` ni un rôle
  plus privilégié que le sien (`403`).

### UX adaptative (front)

- **Hub par défaut** : `landingRouteFor(roles, roleLevel)` redirige un collaborateur
  sans rôle métier vers `/portail-collaborateur` (et non le dashboard exécutif).
- **Rendu adaptatif** : `AdaptiveModuleGrid` affiche une grille au-delà de 6 modules
  accessibles, sinon un **anneau orbital** (les modules gravitent autour du noyau),
  **sans jamais modifier les `href`**.

---

## 🏗️ Département Aménagement Portuaire & Domaine Public

`/api/v1/amenagement-portuaire`  60 endpoints, dont **54 branchés en base** et
**6 téléprocédures institutionnelles honnêtement annoncées `501`**.

**Ce que le département gère réellement** (données saisies par les agents, aucune
ligne seedée) : places portuaires du référentiel national `ports_cameroun`,
schémas directeurs et périmètres, projets d'aménagement, programmation et maturité
(PIP/CDMT, visa de maturité décret n°2018/0492), marchés publics et PPP
(loi n°2023/008), titres domaniaux et permissions d'occuper, concessions et
contrats d'exploitation, inventaire des infrastructures, dragage et profondeurs
disponibles, autorisations administratives (EIES loi n°96/012).

**Ce qui reste `501`** : les échanges avec les administrations elles-mêmes. Une
transmission au MINMIVT ou au MINFI, un passage en COLIFE, une demande d'exutoire
de rejet, un dépôt d'étude d'impact ou une réversion de concession supposent un
guichet tiers que le projet n'a pas branché.
L'API enregistre la **preuve** de la démarche (date, destinataire, référence du
document) côté agent  les colonnes existent sur l'entité (`date_depot`,
`numero_arrete`, `date_colife`, `date_notification_minfi`,
`autorisation_rejet_reference`, `reference_approbatrice` …)  et refuse d'inventer
la réponse de l'administration :

| Endpoint `501` | Démarche réellement concernée |
| --- | --- |
| `POST /schemas-directeurs/{id}/demande-visa-minmivt` | Visa ministériel du schéma |
| `POST /programmation/{id}/notification-minfi` | Notification de la programmation au MINFI |
| `POST /marches/{id}/soumission-colife` | Passage en COLIFE / CIP |
| `POST /concessions/{id}/reversaison` | Réversion des biens et remise du site |
| `POST /dragage/{id}/autorisation-rejet` | Autorisation d'exutoire de rejet en mer |
| `POST /autorisations/{id}/depot` | Dépôt du dossier auprès de l'administration |

**Permissions** : `amenagement.<sous_module>.<action>` (`require_perm`), cataloguées
et grantées par les migrations `038`/`039`/`042`. Rôles propres au département :
`CHEF_AMENAGEMENT_PORTUAIRE`, `INGENIEUR_AMENAGEMENT`. Voir
[`RBAC_ACCREDITATIONS.md`](./RBAC_ACCREDITATIONS.md).

**Re-mesurer ces chiffres** (au lieu de recopier ce tableau) :

```bash
cd evo-log-backend
python scripts/cartographie_routeur.py amenagement_portuaire   # endpoints, permissions, 501
python scripts/cartographie_routeur.py --total                 # bilan de tous les routeurs v1
python scripts/audit_rbac_volume.py                            # permissions / rôles / grants sur base vierge
```
