# EVO-LOG SaaS - KAMLOG EM-ERP

**Version:** 2.0  
**Statut:** Développement avancé  staging requis avant production  
**Dernière mise à jour:** 19 septembre 2026  
**État vérifié:** [ETAT_REEL_2026-09-19.md](./ETAT_REEL_2026-09-19.md)

---

## 🎯 Vision du Projet

EVO-LOG SaaS est une solution ERP logistique professionnelle adaptée au contexte camerounais et CEMAC, offrant une gestion complète des opérations portuaires, du transport, de la maintenance et de la gestion des ressources.

### Architecture SaaS à 4 Niveaux

1. **Super Admin (Plateforme)** - Administration de la plateforme, création des entreprises
2. **Admin Entreprise (Tenant)** - Gestion des utilisateurs, configuration des modules
3. **Chefs de Départements/Sections** - Supervision des équipes, validation des opérations
4. **Utilisateur Final** - Exécution des tâches opérationnelles

---

## 📦 Modules Principaux

### Opérations Portuaires
- **Bill of Lading** - Gestion des connaissements maritimes
- **Port Operations & Stevedoring** - Acconage et déchargement navires
- **Reception MAG3** - Réception et stockage en entrepôt
- **Vessel Call Management** - Gestion des escales navires

### Transport & Logistique
- **Transport** - Gestion de la flotte et des missions
- **Fleet Management** - Maintenance et suivi véhicules
- **Route Optimization** - Optimisation des itinéraires
- **GPS Tracking** - Tracking temps réel de la flotte

### Gestion Magasin
- **EVO-Magasin** - Gestion des stocks et entrepôts
- **Stock Movement** - Mouvements de stock
- **Inventory Management** - Gestion des inventaires

### Finance & Facturation
- **Finance** - Gestion financière
- **Auto Invoicing** - Facturation automatique OHADA
- **Port Pricing** - Tarification des services portuaires
- **Comptabilité SYSCOHADA** - Comptabilité conforme OHADA

### Gestion des Ressources
- **RH** - Gestion des ressources humaines
- **Accreditation Management** - Système d'accréditation à 3 niveaux
- **Shift Planning** - Planification des shifts et ressources
- **Performance Management** - Dashboard de performance

### Douane & Réglementation
- **Real Customs Integration** - Intégration SYDONIA+ et GUICHET UNIQUE
- **Goods Declaration** - Déclarations douanières
- **Risk Assessment** - Évaluation des risques douaniers

### QHSE & Sécurité
- **QHSE** - Qualité, Hygiène, Sécurité et Environnement
- **Port Incidents** - Gestion des incidents portuaires
- **Safety Management** - Gestion de la sécurité

### Communication & Intégration
- **Notifications** - Système de notifications multi-canal
- **Partner API** - API pour intégration B2B
- **Webhooks** - Webhooks pour partenaires
- **Collaboration** - Outils de collaboration

---

## 🏗️ Architecture Technique

### Monolithe Modulaire Découplé

### Backend (FastAPI)
- **Framework**: FastAPI 0.115
- **Base de données**: PostgreSQL (production) / SQLite (développement)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentification**: NextAuth v4 synchronisée
- **Tâches asynchrones**: Celery + Redis
- **PDF Generation**: WeasyPrint
- **Rate Limiting**: SlowAPI
- **Monitoring**: Prometheus

### Frontend (Next.js)
- **Framework**: Next.js 14 (App Router)
- **Styling**: Vanilla CSS Design System
- **État**: Zustand
- **UI**: Radix UI
- **PWA**: 3D Metallic Icons (512x512, 192x192, apple-touch-icon.png, favicon.ico)
- **Build Production**: 153/153 pages statiques

### Rôles & RBAC
- **Rôles**: ADMIN, MAGASINIER, DISPATCHER, QHSE, FINANCIER, DOUANE, PARC, AUDITOR
- **Contrôle dynamique**: `modules_allowed` par rôle
- **Contrôle d'accès**: Validation stricte des permissions

### Infrastructure
- **Multi-tenancy**: Organisation isolation
- **RBAC**: Rôles et permissions dynamiques
- **Offline-first**: Sync pour zones non-connectées
- **Docker Railway**: Auto-aplatissement pour déploiement flexible

---

## 🚀 Installation

### Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Installation
```bash
cd EVO-LOG-backend
pip install -r requirements.tx