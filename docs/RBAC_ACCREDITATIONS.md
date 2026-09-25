# RBAC granulaire, accréditations & espaces communs

**Dernière mise à jour :** 25 septembre 2026  *aligné code au 25/09/2026*.

Ce document décrit le modèle d'autorisation effectif du backend EVO-LOG : le
moteur de permissions granulaires, la visibilité hiérarchique, les accréditations
nominatives datées, les espaces communs par entreprise, le catalogue de permissions
et les rôles semés par la migration.

> **Principe directeur  additif / non-régression.** Tout est cumulatif. Les niveaux
> 0 (SuperAdmin) et 1 (Admin entreprise) **bypassent** la granularité. Si un rôle
> n'a **aucune** permission granulaire semée, le moteur retombe exactement sur le
> comportement historique `modules_allowed` (`can_access_module`). Un tenant non seedé
> se comporte donc comme avant cette évolution.

---

## 1. Pièces du dispositif

| Brique | Fichier | Rôle |
| --- | --- | --- |
| Moteur d'autorisation | `app/core/permissions.py` | Résout les permissions effectives, `require_perm`, `visible_user_ids`. |
| Catalogue | `app/core/permission_catalog.py` | Source de vérité domaines > modules > sous-modules > actions + rôles semés. |
| Modèle `Permission` | `app/models/user.py` | Permission atomique `module.sous_module.action`. |
| Accréditations / espaces communs | `app/models/accreditation.py` | `Accreditation`, `SharedAccess`, `DEFAULT_SHARED_MODULES`. |
| Routers | `app/routers/v1/accreditations.py`, `app/routers/v1/rbac_avance.py` | API REST. |
| Migration de seed | `migrations/versions/020_rbac_granulaire_accreditations.py` | Crée les tables, sème permissions/rôles/partages. |

---

## 2. Format des codes de permission

Un code est `module.sous_module.action`, segments séparés par des points, chacun
pouvant valoir le joker `*`.

Exemples :
- `comptabilite.journal.read`  lecture du sous-module *journal* du module *comptabilite*.
- `comptabilite.*.read`  lecture de tous les sous-modules de *comptabilite*.
- `comptabilite.*.*`  tout sur le module *comptabilite*.
- `*`  wildcard total (réservé SuperAdmin, non semé).

La fonction `_match(granted, wanted)` de `app/core/permissions.py` compare segment
par segment ; un code accordé plus court que le code voulu est complété par `*`.
Le frontend (`src/lib/permissions.ts :: matchPermission`) reproduit la même logique
pour que le rendu de l'UI concorde avec le contrôle serveur.

### Résolution des permissions effectives

`load_effective_permissions(db, user)` = union des codes portés par :
1. les rôles de l'utilisateur (via la table `role_permissions`) ;
2. les **accréditations actives** (voir §5) qui ajoutent un `permission_code`.

Une permission granulaire n'est comptée que si l'accréditation correspondante est
encore valide (non expirée, statut `actif`).

---

## 3. Comportement du moteur (`can` / `require_perm`)

`can(user, code)` :
1. **Bypass** si `role_level` ∈ {0, 1} ou `is_superuser` → `True`.
2. **Espace commun** : si le module du code est un module commun actif pour
   l'entreprise (§6) → `True`.
3. **Granulaire** : si le rôle possède au moins une permission granulaire, on
   évalue `code` dans l'ensemble effectif.
4. **Fallback** : sinon, on retombe sur `can_access_module(user, module)`
   (`modules_allowed`)  comportement historique.

`require_perm("module.sous.action")` est une fabrique de dépendance FastAPI ; elle
renvoie **403** en cas de refus. Elle est appliquée sur les **domaines cœur**
(comptabilité avancée `comptabilite_avance.py`, magasin `magasin.py`).

> **Périmètre d'application.** Conformément au plan, `require_perm` est câblé sur les
> domaines cœur ; le reste des routes reste sur `modules_allowed` et bénéficiera du
> seed **sans changement de comportement**.

---

## 4. Visibilité hiérarchique (`visible_user_ids`)

Utilisé pour filtrer les listes là où le modèle porte `created_by` / `user_id` /
`department_id`.

| Profil | Périmètre visible |
| --- | --- |
| SuperAdmin / Admin entreprise (niveau 0/1) | toute l'entreprise (`None` = pas de filtre) |
| Chef de département (niveau 2) | les utilisateurs de son département, **restreignable** à une liste nominative via une accréditation de périmètre (§5) |
| Utilisateur (niveau ≥ 3) | soi-même |

---

## 5. Accréditations (`/api/v1/accreditations`)

Une **accréditation** est une habilitation nominative, datée et comptable portée par
un utilisateur. Deux types :

- **`permission`**  accorde un `permission_code` supplémentaire
  (ex. `comptabilite.bilan.approve`).
- **`scope`**  restreint la visibilité hiérarchique d'un chef de département à une
  liste explicite de collaborateurs (`perimetre_utilisateurs`, JSON d'ids).

Champs : `user_id`, `code` (référence métier auto-générée `ACC-…`), `libelle`, `type`,
`permission_code` ou `perimetre_utilisateurs`, `module`, `date_debut`, `date_fin`,
`statut` (`actif` | `suspendu` | `revoque`), `motif`, `octroye_par`.

**Expiration** : `Accreditation.is_active()` renvoie `False` si le statut n'est pas
`actif`, si `date_debut` est future ou si `date_fin` est dépassée. Une accréditation
non active est **ignorée** par `load_effective_permissions`.

Endpoints : l'administrateur entreprise gère les accréditations de sa société
(`GET /`, `POST /`, `PUT /{id}`, `DELETE /{id}`) ; chaque utilisateur consulte les
siennes via `GET /mes-accreditations`.

UI : `admin/accreditations` (liste, octroi, révocation).

---

## 6. Espaces communs par entreprise (`SharedAccess`)

Un **espace commun** est un module accessible à **tout utilisateur authentifié** d'une
entreprise, quel que soit son rôle. Bascule par entreprise :
`(company_id, module_key, autorise_tous_utilisateurs)`.

Modules communs par défaut (`DEFAULT_SHARED_MODULES`) :

| Clé | Libellé |
| --- | --- |
| `rh-mon-espace` | Portail RH self-service (mes infos, mes congés) |
| `chat` | Messagerie / chat interne |
| `notifications` | Centre de notifications |
| `documents-partages` | Documents communs de l'entreprise |
| `annuaire` | Annuaire interne des collaborateurs |

**Comportement out-of-the-box** : `_shared_module_keys()` retourne l'union des défauts
moins les lignes d'entreprise explicitement **désactivées**. Ouvrir un module commun
supplémentaire crée une ligne `autorise_tous_utilisateurs=True` ; le désactiver crée
une exception explicite qui s'impose au moteur.

Endpoints : `GET /api/v1/shared-access`, `POST /api/v1/shared-access` (upsert),
`DELETE /api/v1/shared-access/{id}`, `POST /api/v1/shared-access/initialiser` (seed).

UI : `admin/espaces-communs` (bascules par module + initialisation des communs).

---

## 7. Catalogue des permissions

Source : `app/core/permission_catalog.py`. Actions de référence :
`read`, `create`, `modify`, `delete`, `approve`, `export`.

### Domaines > modules > sous-modules

| Domaine | Modules (sous-modules) |
| --- | --- |
| **Gouvernance & Administration** | `users` (comptes, statuts) · `roles` (matrice, accreditations) · `departments` (organisation) · `audit` (journal) · `settings` (generaux, communs) |
| **Finance & Comptabilité** | `comptabilite` (journal, grand_livre, balance, bilan, lettrage) · `tresorerie` (mouvement, rapprochement) · `facturation` (facture, devis, avoir) · `fiscalite` (tva, declarations) · `immobilisations` (actif, amortissement) |
| **Opérations portuaires & logistiques** | `acconage` (escale, manifeste, stevedoring) · `transit` (dossier, declaration, tarification) · `magasin` (stock, mouvement, inventaire, picking) · `port` (quai, pesee, zone) |
| **Transport & Flotte** | `transport` (mission, dispatch, epod, carburant) · `parc` (flotte, maintenance, documents) · `gps` (tracking, alertes) |
| **Ressources Humaines** | `rh` (employes, contrat, monitoring) · `paie` (bulletin, declarations_sociales) · `conges` (demande, pointage) |
| **Achats & Commerce** | `achats` (commande, reception) · `fournisseurs` (referentiel) · `cotations` (cotation) |

Endpoint UI : `GET /api/v1/permissions/catalog` (arborescence domains > modules >
subModules > actions).

---

## 8. Rôles métier semés

Semés par `020_rbac_granulaire_accreditations` (rôles système, `company_id=NULL`).
Niveau **2** = chef de département, **3** = opérateur.

| Rôle | Niv. | Permissions clés (jokers inclus) |
| --- | --- | --- |
| `DIRECTEUR_FINANCIER` | 2 | `comptabilite.*.*`, `tresorerie.*.*`, `facturation.*.*`, `fiscalite.*.*`, `immobilisations.*.*`, `achats.commande.approve` |
| `CHEF_COMPTABLE` | 2 | `comptabilite.*.*`, `tresorerie.*.read`, `tresorerie.mouvement.approve`, `facturation.*.read`, `facturation.facture.approve`, `facturation.*.export`, `fiscalite.*.read`, `fiscalite.declarations.approve`, `immobilisations.*.read` |
| `COMPTABLE` | 3 | `comptabilite.journal.*` (read/create/modify), `grand_livre.read`, `balance.read`, `lettrage.read/modify`, `tresorerie.mouvement.read/create`, `facturation.facture.read/create`, `fiscalite.tva.read` |
| `AUDITEUR` | 3 | lecture transversale : `comptabilite.*.read`, `tresorerie.*.read`, `facturation.*.read`, `transport.*.read`, `magasin.*.read`, `transit.*.read`, `audit.journal.read` |
| `TRANSIT_PRINCIPAL` | 2 | `transit.*.*`, `acconage.*.read`, `magasin.stock.read`, `fiscalite.declarations.read` |
| `DECLARANT` | 3 | `transit.dossier.*` (read/create/modify), `transit.declaration.*` (read/create/modify), `acconage.manifeste.read` |
| `MAGASINIER` | 3 | `magasin.stock.read/modify`, `magasin.mouvement.create`, `magasin.picking.read/create`, `magasin.inventaire.read` |
| `CHEF_PARC` | 2 | `parc.*.*`, `transport.*.read`, `gps.tracking.read`, `gps.alertes.modify` |
| `DISPATCHER` | 3 | `transport.mission.read/create`, `transport.dispatch.read/create/modify`, `parc.flotte.read` |
| `ADMIN_RH` | 2 | `rh.*.*`, `paie.*.read`, `paie.bulletin.create`, `conges.*.*` |
| `QHSE` | 3 | `gouvernance.*.read`, `transport.*.read`, `parc.documents.read` |

Les rôles de niveau 0/1 (SuperAdmin, Admin entreprise) ne reçoivent **aucune**
permission granulaire semée : ils bypassent la granularité dans le moteur.

> Volume (base vierge vérifiée) : **256 permissions**, **11 rôles**, **68 grants** de
> rôle à permission.

---

## 9. Frontend

- **Session NextAuth** (`src/lib/auth.ts`) propage `permissions`, `shared_modules`,
  `role_level`, `department_id`, `is_superuser` (authorize → jwt → session).
- **Résolution** (`src/lib/permissions.ts`) : `matchPermission`, `hasPermission`
  (bypass niveaux 0/1, espaces communs, granulaire, fallback `modules_allowed`),
  `hasGranularPermissions`.
- **Garde** : `PermissionGuard` accepte un mode `code="module.sous.action"` (repli sur
  `requiredRoles` si session sans permissions) ; hook `useCan(code)`.
- **Navigation** (`src/config/navigationRegistry.ts`) : filtrage additif par
  permissions effectives ; les `requiredRoles` en dur restent le défaut quand non seedé.
- **Pages admin** (`Administration Entreprise`) : `configuration-des-roles-rbac`
  (arbre à cocher modules > sous-modules > actions par rôle, via
  `GET/PUT /api/v1/rbac/roles/{id}/permissions`), `accreditations`, `espaces-communs`.

---

## 10. Sécurité

- Le router `rbac_avance` (liste des tenants, rôles par tenant) est réservé : tenants
  = **SuperAdmin uniquement** (`require_superadmin`), lecture des rôles & catalogue =
  **admin** (`require_min_role_level(2)` / `require_company_admin`).
- Édition des permissions d'un rôle (`PUT /roles/{id}/permissions`) : un admin
  entreprise ne peut modifier que les rôles de **son** entreprise (`company_id ∈
  {NULL, sienne}`) et **pas** les rôles d'administration (niveau ≤ 1), afin d'éviter
  toute auto-escalade.

---

## 11. Réinitialisation / migration

```bash
cd evo-log-backend
alembic upgrade head   # rejouable sur base vierge SQLite et sur base de dev existante
```

Migrations chaînées de façon linéaire : `020_rbac_granulaire_accreditations` suit
`020_add_gap_bridge_tables` (tête unique vérifiée). Gardes idempotents par
introspection (`sa.inspect`) + `batch_alter_table` (SQLite) ; seed en try/except pour
ne jamais bloquer un déploiement.
