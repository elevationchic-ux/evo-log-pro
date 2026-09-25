<!-- ARCHIVE-HISTORIQUE -->
> **Rapport d'expertise historique**  instantané au 2026-09-23. Ce document témoigne d'un état passé et **ne reflète pas l'état courant** du projet. Pour la référence à jour, voir [docs/README.md](../README.md).

---

# EVO-LOG - Analyse UX/UI & Architecture SAAS Multi-Tenant

## 📊 Diagnostic Architecture SAAS Actuelle

### ❌ GAPS CRITIQUES IDENTIFIÉS

#### 1. Absence de Véritable Multi-Tenancy SAAS

**État Actuel:**
- Modèle `Agency` = Branches/Agences d'une seule entreprise
- Pas de modèle `Company` ou `Tenant` pour isoler les entreprises clientes
- Tous les utilisateurs partagent la même base de données sans isolation par entreprise

**Requis SAAS:**
```sql
-- MANQUEANT: Modèle Company/Tenant
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(200) NOT NULL,
    legal_form VARCHAR(50),
    tax_id VARCHAR(50),
    adresse TEXT,
    ville VARCHAR(100),
    pays VARCHAR(50) DEFAULT 'Cameroun',
    logo_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    subscription_plan_id INTEGER,
    subscription_start DATE,
    subscription_end DATE,
    max_users INTEGER DEFAULT 10,
    max_storage_mb INTEGER DEFAULT 1024,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- RELATION MANQUANTE: User → Company
ALTER TABLE users ADD COLUMN company_id INTEGER REFERENCES companies(id);
```

#### 2. RBAC Non Hiérarchique Multi-Tenant

**État Actuel:**
- Rôles plats: ADMIN, MAGASINIER, DISPATCHER, QHSE, FINANCIER, DOUANE, PARC, AUDITOR
- Pas de distinction entre Super Admin (plateforme) et Admin Entreprise
- Pas de Chef Département avec permissions spécifiques
- `modules_allowed` = JSON string (pas optimisé)

**Requis SAAS:**
```sql
-- MANQUEANT: Hiérarchie de rôles multi-tenant
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 0, -- 0=SuperAdmin, 1=AdminEntreprise, 2=ChefDept, 3=User
    company_id INTEGER NULL, -- NULL pour SuperAdmin
    modules_allowed JSONB, -- Changé de TEXT à JSONB
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Rôles prédéfinis
-- SUPER_ADMIN (level 0, company_id NULL) - Gère toute la plateforme
-- ADMIN_ENTREPRISE (level 1, company_id=X) - Gère son entreprise
-- CHEF_DEPT (level 2, company_id=X) - Gère son département
-- USER (level 3, company_id=X) - Utilisateur standard
```

#### 3. Gestion des Profils Incomplète

**Fonctionnalités Manquantes:**
- ❌ Interface pour créer des entreprises par le Super Admin
- ❌ Interface pour créer des profils utilisateurs par l'Admin Entreprise
- ❌ Workflow d'onboarding (création compte → validation → attribution rôle)
- ❌ Gestion des quotas (utilisateurs, stockage, modules)
- ❌ Portail de gestion des abonnements

**UX/UI Manquante:**
```
/src/app/(app)/admin/companies/      - Gestion des entreprises (Super Admin)
/src/app/(app)/admin/users/          - Gestion globale des utilisateurs
/src/app/(app)/admin/subscriptions/ - Gestion des abonnements
/src/app/(app)/company/users/        - Gestion utilisateurs entreprise
/src/app/(app)/company/departments/  - Gestion départements
/src/app/(app)/company/roles/        - Gestion rôles personnalisés
```

#### 4. Portail B2B Partiel

**État Actuel:**
- Dossier `client-portal/` existe avec sous-dossiers (invoices, litiges, orders, profile, reports, shipments)
- MAIS: Pas de backend dédié pour isoler les données par entreprise
- MAIS: Pas d'authentification B2B spécifique
- MAIS: Pas de personnalisation par entreprise (logo, couleurs, domaine)

**Requis Portail B2B:**
```sql
-- MANQUEANT: Portail B2B configuration
CREATE TABLE b2b_portals (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    subdomain VARCHAR(100) UNIQUE, -- ex: client1.evolog.cm
    custom_domain VARCHAR(100), -- ex: client1.logistics.cm
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    logo_url VARCHAR(255),
    banner_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- MANQUEANT: B2B User isolation
ALTER TABLE users ADD COLUMN is_b2b BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN b2b_portal_id INTEGER REFERENCES b2b_portals(id);
```

### 📋 Cartographie des Rôles Requis

#### Niveau 0: Super Admin (Plateforme)
- Créer/Supprimer des entreprises
- Gérer les abonnements (plans, facturation)
- Superviser toutes les entreprises
- Accès aux statistiques globales
- Gérer les rôles système

#### Niveau 1: Admin Entreprise
- Gérer les utilisateurs de son entreprise
- Créer des départements
- Attribuer des rôles (Chef Département, User)
- Configurer les modules autorisés
- Gérer les quotas
- Personnaliser le portail B2B

#### Niveau 2: Chef Département
- Gérer les utilisateurs de son département
- Voir les KPIs de son département
- Valider les demandes de son équipe
- Accès limité aux modules de son département

#### Niveau 3: User Standard
- Accès aux modules autorisés par son rôle
- Effectuer les opérations de son métier
- Voir ses propres données
- Pas d'accès admin

### 🎨 UX/UI Requis pour Gestion des Profils

#### 1. Super Admin Dashboard
```
Super Admin →
  ├── Dashboard Global
  │   ├── Statistiques (nombre entreprises, revenus, utilisateurs)
  │   ├── Alertes (entreprises en retard, surcharge)
  │   └── Rapports consolidés
  ├── Entreprises
  │   ├── Liste des entreprises
  │   ├── Créer nouvelle entreprise
  │   ├── Détails entreprise (users, modules, quota)
  │   └── Suspendre/Réactiver entreprise
  ├── Abonnements
  │   ├── Plans (Starter, Pro, Enterprise)
  │   ├── Facturation
  │   ├── Paiements
  │   └── Rapports revenus
  └── Système
      ├── Rôles globaux
      ├── Permissions
      ├── Logs d'audit
      └── Configuration
```

#### 2. Admin Entreprise Dashboard
```
Admin Entreprise →
  ├── Dashboard Entreprise
  │   ├── KPIs entreprise
  │   ├── Utilisation quota
  │   └── Activité récente
  ├── Utilisateurs
  │   ├── Liste utilisateurs
  │   ├── Inviter utilisateur
  │   ├── Gérer rôles
  │   └── Départements
  ├── Configuration
  │   ├── Modules autorisés
  │   ├── Personnalisation portail
  │   ├── Intégrations
  │   └── Paramètres
  └── Facturation
      ├── Abonnement actuel
      ├── Factures
      └── Paiements
```

#### 3. Portail B2B
```
Client B2B →
  ├── Accès personnalisé (subdomain: client1.evolog.cm)
  ├── Branding personnalisé (logo, couleurs)
  ├── Modules autorisés uniquement
  ├── Voir uniquement ses données
  ├── Gérer ses commandes
  ├── Voir ses factures
  ├── Suivre ses expéditions
  ├── Litiges
  └── Rapports personnalisés
```

### 🔧 Implémentation Technique Requise

#### 1. Middleware d'Isolation Multi-Tenant
```python
# app/middleware/tenant.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extraire tenant du subdomain ou header
        subdomain = request.headers.get("X-Tenant-ID")
        if not subdomain:
            # Déduire du subdomain
            host = request.headers.get("host", "")
            subdomain = host.split(".")[0]
        
        # Charger tenant
        tenant = get_tenant_by_subdomain(subdomain)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Injecter tenant dans le state
        request.state.tenant = tenant
        request.state.company_id = tenant.company_id
        
        response = await call_next(request)
        return response
```

#### 2. Query Filtering Automatique
```python
# app/core/database.py
from sqlalchemy.orm import Query

class TenantQuery(Query):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_id = None
    
    def with_tenant(self, tenant_id):
        self._tenant_id = tenant_id
        return self
    
    def __iter__(self):
        # Ajouter automatiquement WHERE company_id = tenant_id
        if self._tenant_id:
            self = self.filter_by(company_id=self._tenant_id)
        return super().__iter__()
```

#### 3. Sécurité au Niveau Ligne (Row-Level Security)
```sql
-- PostgreSQL Row-Level Security
ALTER TABLE missions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON missions
    FOR ALL
    USING (company_id = current_setting('app.company_id')::INTEGER);
```

### 📊 Portail B2B - État & Gaps

#### ✅ Existe (Frontend)
- Dossier structure: `client-portal/`
- Sous-dossiers: invoices, litiges, orders, profile, reports, shipments
- Layout de base

#### ❌ Manque (Backend & Fonctionnel)
1. **Isolation des données par entreprise**
   - Filtrage automatique des requêtes par company_id
   - Sécurité au niveau ligne
   - Sandbox de données

2. **Authentification B2B spécifique**
   - Token avec scope B2B
   - Refresh token B2B
   - Rate limiting par entreprise

3. **Personnalisation par entreprise**
   - Logo dynamique
   - Couleurs personnalisées
   - Domaine personnalisé (subdomain)
   - Emailing personnalisé

4. **Fonctionnalités B2B manquantes**
   - Catalogue de services
   - Devis en ligne
   - Signature électronique B2B
   - Chat support intégré
   - API B2B dédiée

5. **Reporting B2B**
   - Rapports personnalisés par entreprise
   - Export avec branding
   - Historique des transactions
   - Analytics client

### 🎯 Roadmap Implémentation SAAS

#### Phase 1: Infrastructure Multi-Tenant (2-3 semaines)
1. Créer modèle `Company` avec migration
2. Créer modèle `Subscription` et `SubscriptionPlan`
3. Créer modèle `B2BPortal`
4. Modifier `User` pour inclure `company_id`
5. Créer middleware `TenantMiddleware`
6. Implémenter row-level security

#### Phase 2: RBAC Hiérarchique (1-2 semaines)
1. Refactor `Role` avec `level` et `company_id`
2. Créer rôles prédéfinis (SuperAdmin, AdminEntreprise, ChefDept, User)
3. Créer modèle `Department`
4. Implémenter middleware de vérification de rôle
5. Créer endpoints de gestion des rôles

#### Phase 3: Frontend Gestion Profils (2-3 semaines)
1. Créer `admin/companies/` pour Super Admin
2. Créer `admin/subscriptions/` pour gestion abonnements
3. Créer `company/users/` pour Admin Entreprise
4. Créer `company/departments/` pour gestion départements
5. Créer `company/roles/` pour rôles personnalisés
6. Implémenter workflow d'onboarding

#### Phase 4: Portail B2B Complet (3-4 semaines)
1. Implémenter isolation des données
2. Créer système de subdomain personnalisé
3. Implémenter branding dynamique
4. Créer endpoints B2B dédiés
5. Ajouter fonctionnalités manquantes (devis, chat, API)
6. Créer reporting B2B personnalisé

### 📈 Métriques de Succès SAAS

- **Onboarding time**: < 15 minutes pour créer une entreprise
- **User setup time**: < 5 minutes pour créer un utilisateur
- **Tenant isolation**: non certifiée à 100% ; absence de fuite à démontrer par des tests inter-tenant
- **B2B availability**: 99.9% uptime
- **Customization time**: < 1 heure pour personnaliser portail

### 🚨 Conclusions

#### ❌ Le projet N'EST PAS optimal pour SAAS actuellement

**Gaps Critiques:**
1. Pas de véritable multi-tenancy (modèle Company manquant)
2. RBAC non hiérarchique (pas de distinction Super Admin / Admin Entreprise)
3. Pas d'interface de gestion des profils multi-tenant
4. Portail B2B partiel sans isolation des données
5. Pas de système d'abonnements

#### ✅ Fondations Solides

**Points Positifs:**
1. Modèle RBAC existe (Role/Permission)
2. Modèle Agency pour branches
3. Structure frontend complète
4. Portail B2B existe (structure)
5. 12 modules métiers robustes

#### 🎯 Recommandation Prioritaire

**Avant de lancer en SAAS:**
1. Implémenter l'infrastructure multi-tenant (Company, Subscription)
2. Créer la hiérarchie de rôles (Super Admin, Admin Entreprise, Chef Dept)
3. Développer les interfaces de gestion des profils
4. Compléter le portail B2B avec isolation des données
5. Ajouter le système d'abonnements et facturation

**Estimation temps complet:** 8-12 semaines pour un SAAS production-ready
