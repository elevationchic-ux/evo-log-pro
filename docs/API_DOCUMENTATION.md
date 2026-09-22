# API Documentation — EVO-LOG SaaS

## Source de Vérité

Pour les schémas OpenAPI interactifs, la validation des contrats Pydantic et l'essai des endpoints en direct :

- **Swagger UI** : `http://localhost:8000/api/docs` (ou `https://your-backend.up.railway.app/api/docs` en production)
- **ReDoc** : `http://localhost:8000/api/redoc`

---

## 🌐 Endpoints d'Observabilité & Health Check

- `GET /api/health` : Statut général du service (utilisé par Railway).
- `GET /api/health/detailed` : État détaillé des connexions BDD PostgreSQL, Redis et MinIO.

---

## 🗺️ Cartographie Complète des 19 Routeurs FastAPI

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
