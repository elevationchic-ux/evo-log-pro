# Guide Complet d'Utilisation KAMLOG ERP

## 📖 Table des Matières

1. [Introduction](#introduction)
2. [Architecture du Système](#architecture-du-système)
3. [Guide par Niveau d'Accès](#guide-par-niveau-daccès)
4. [Processus Métier Détaillé](#processus-métier-détaillé)
5. [Modules et Fonctionnalités](#modules-et-fonctionnalités)
6. [Guide Pas à Pas](#guide-pas-à-pas)
7. [Règles de Gouvernance](#règles-de-gouvernance)
8. [Spécificités Cameroun/CEMAC](#spécificités-camerouncemac)
9. [Support et Assistance](#support-et-assistance)

---

## 1. Introduction

### 1.1 Qu'est-ce que KAMLOG ERP ?

**KAMLOG ERP** (Knowledge and Advanced Management for Logistics) est une solution logicielle de gestion d'entreprise complète, adaptée aux opérations logistiques portuaires et de transport au Cameroun et dans la zone CEMAC.

### 1.2 Objectifs du Système

- **Digitalisation complète** des processus logistiques portuaires
- **Traçabilité** de bout en bout (navire → client)
- **Conformité OHADA** pour la comptabilité et la gestion financière
- **Adaptation réglementaire** aux spécificités Cameroun/CEMAC
- **Réduction des délais** de transmission d'information
- **Amélioration de la productivité** de l'entreprise

### 1.3 Processus End-to-End

Le système gère l'intégralité du cycle logistique :

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   NAVIRE    │───▶│  DÉDOUANEMENT│───▶│   MAGASIN   │───▶│  TRANSPORT  │───▶│   CLIENT    │
│  ARRIVÉE    │    │   & TRANSIT  │    │  & WMS      │    │ & LIVRAISON │    │  FINAL      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │                   │                   │
     ▼                   ▼                   ▼                   ▼                   ▼
  Manifestes         DUM/B AE           Réceptions          Missions           Facturation
  Escales            Taxation           Stockage             e-POD              Paiements
  Quai               Douane              Picking              GPS                Comptabilité
```

---

## 2. Architecture du Système

### 2.1 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION WEB                             │
│                    (Next.js 14 + TypeScript)                    │
├─────────────────────────────────────────────────────────────────┤
│  Pages: Dashboard, Transport, Magasin, Finance, RH, etc.       │
│  Composants: KPICard, DataTable, StatusBadge, etc.             │
│  Services API: transportApi, magasinApi, financeApi            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API REST                                  │
│                  (FastAPI - Python 3.11)                        │
├─────────────────────────────────────────────────────────────────┤
│  Authentification JWT                                           │
│  50+ Endpoints (transit, transport, magasin, finance, etc.)   │
│  Validation Pydantic                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BASE DE DONNÉES                              │
│                   (PostgreSQL 15 + PostGIS)                     │
├─────────────────────────────────────────────────────────────────┤
│  Tables: missions, vehicles, drivers, invoices, etc.           │
│  Multi-tenant (Row Level Security)                             │
│  Migrations Alembic                                            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Base de Données - Schéma Simplifié

#### Entités Principales

| Entité | Description | Modules Liés |
|--------|-------------|--------------|
| `tenants` | Organisations/clients | Tous |
| `users` | Utilisateurs avec rôles | Auth, Admin |
| `vehicles` | Parc automobile | Transport, Parc |
| `drivers` | Chauffeurs | Transport |
| `missions` | Livraisons/transport | Transport |
| `articles` | Catalogue produits | Magasin |
| `receptions` | Réceptions marchandise | Magasin |
| `invoices` | Factures clients | Finance |
| `payments` | Encaissements | Finance |
| `journal_entries` | Écritures comptables | Finance |

### 2.3 Technologies Utilisées

| Niveau | Technologie | Version |
|--------|-------------|---------|
| Frontend | Next.js | 14+ |
| Langage | TypeScript | 5+ |
| UI | Tailwind CSS | 3+ |
| Backend | FastAPI | 0.109+ |
| BDD | PostgreSQL | 15+ |
| Auth | NextAuth.js | 4.x |
| Tests | Playwright | 1.41+ |

---

## 3. Guide par Niveau d'Accès

### 3.1 Hiérarchie des Rôles

```
┌─────────────────────────────────────────────────────────────────────┐
│                    1. SUPER_ADMIN (Plateforme)                      │
│         Administration technique de la plateforme SaaS              │
│         → Gestion multi-tenant, configuration système               │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    2. TENANT_ADMIN (Organisation)                   │
│              Adminstrateur de l'entreprise cliente                  │
│              → Utilisateurs, modules, configuration                 │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    3. DIRECTION (Management)                        │
│                    Vue globale, reporting, validation               │
│              → Accès tous modules en lecture/écriture               │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│               4. CHEF DÉPARTEMENT / MANAGER                         │
│              Responsable d'un module métier                         │
│    → Transport, Magasin, Finance, Douane, RH, QHSE, etc.           │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    5. CHEF D'ÉQUIPE / SUPERVISEUR                   │
│                   Gestion opérationnelle terrain                    │
│        → Planning, dispatch, coordination équipes jour              │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    6. OPERATEURS MÉTIER                             │
│      Exécution des tâches quotidiennes                             │
│   → Magasiniers, Chauffeurs, Comptables, Agents douane, etc.       │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    7. CLIENTS B2B                                   │
│                   Accès limité portail client                       │
│           → Suivi expéditions, factures, commandes                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Détail des Rôles et Permissions

#### 🔴 SUPER_ADMIN
**Profil** : Équipe technique KAMLOG

| Permission | Accès |
|------------|-------|
| Création tenant | ✓ |
| Configuration plateforme | ✓ |
| Accès logs système | ✓ |
| Gestion API publiques | ✓ |
| Support niveau 3 | ✓ |

#### 🟠 TENANT_ADMIN
**Profil** : Directeur informatique ou responsable IT du client

| Permission | Accès |
|------------|-------|
| Gestion utilisateurs | ✓ |
| Configuration modules | ✓ |
| Import/export données | ✓ |
| Accès audit logs | ✓ |
| Souscriptions & facturation | ✓ |

#### 🟡 DIRECTION
**Profil** : Directeur général, Directeur des opérations

| Module | Lecture | Écriture | Validation |
|--------|---------|----------|------------|
| Dashboard global | ✓ | - | - |
| Transport | ✓ | ✓ | ✓ |
| Magasin | ✓ | ✓ | ✓ |
| Finance | ✓ | ✓ | ✓ |
| RH | ✓ | ✓ | - |
| Reporting BI | ✓ | - | - |

#### 🟢 CHEF DÉPARTEMENT
**Profil** : Responsable transport, Responsable magasin, Responsable finance

| Module | Permissions |
|--------|-------------|
| Son département | Accès complet |
| Autres départements | Lecture seule |
| Validation | ✓ |
| Reporting | ✓ |

#### 🔵 OPERATEURS

| Métier | Modules Accessibles |
|--------|---------------------|
| **Chauffeur** | Transport (ses missions), POD |
| **Magasinier** | Magasin (réception, picking) |
| **Comptable** | Finance, Comptabilité |
| **Agent Douane** | Transit, Douane |
| **Dispatcheur** | Transport (planning) |
| **RH** | RH (gestion employés) |

#### 🟣 CLIENT B2B
**Profil** : Client externe de l'entreprise

| Permission | Accès |
|------------|-------|
| Portail client | ✓ |
| Suivi expéditions | ✓ |
| Factures | ✓ |
| Commandes | ✓ |
| Support | Ticket |

---

## 4. Processus Métier Détaillé

### 4.1 Flux Principal: Navire → Client

#### Phase 1: Opérations Portuaires

**Acteurs** : Agent maritime, Opérateur quai
**Modules** : Port Operations, Acconage

| Étape | Action | Détail |
|-------|--------|--------|
| 1.1 | Réception manifeste | Navire annonce cargaison |
| 1.2 | Validation manifeste | Vérification conformité |
| 1.3 | Planning accostage | Réservation poste à quai |
| 1.4 | Opérations quai | Déchargement/manutention |
| 1.5 | Transfert zone acconage | Stockage temporaire |

#### Phase 2: Transit & Douane

**Acteurs** : Agent transit, Agent douane, Déclarant
**Modules** : Transit, Douane, Fiscalité

| Étape | Action | Détail |
|-------|--------|--------|
| 2.1 | Création DUM | Déclaration Unique de Marchandises |
| 2.2 | Taxation | Calcul TEC, TVA, droits |
| 2.3 | Visite douanière | Contrôle physique (si besoin) |
| 2.4 | Paiement taxes | Mobile Money ou virement |
| 2.5 | Émission BAE | Bon à Enlever - mainlevée |

#### Phase 3: Magasin & WMS

**Acteurs** : Magasinier, Préparateur
**Modules** : Magasin, Stock, WMS

| Étape | Action | Détail |
|-------|--------|--------|
| 3.1 | Réception physique | Contrôle qualité, колич |
| 3.2 | Mise en stock | Affectation emplacement |
| 3.3 | Inventaire | Vérification niveaux |
| 3.4 | Préparation | Picking, colisage |
| 3.5 | Expédition | Sortie entrepôt |

#### Phase 4: Transport & Livraison

**Acteurs** : Dispatcheur, Chauffeur, Client
**Modules** : Transport, Tracking, GPS

| Étape | Action | Détail |
|-------|--------|--------|
| 4.1 | Attribution mission | Affectation véhicule/chauffeur |
| 4.2 | Chargement | Contrôle cargaison |
| 4.3 | Transport | Suivi GPS temps réel |
| 4.4 | Livraison | Remise client |
| 4.5 | e-POD | Signature électronique |

#### Phase 5: Facturation & Comptabilité

**Acteurs** : Comptable, Directeur finance
**Modules** : Finance, Comptabilité OHADA

| Étape | Action | Détail |
|-------|--------|--------|
| 5.1 | Émission facture | Selon prestation |
| 5.2 | Envoi client | Email + portail B2B |
| 5.3 | Encaissement | Paiement client |
| 5.4 | Saisie comptable | Écritures journal |
| 5.5 | Clôture mensuelle | États financiers |

---

## 5. Modules et Fonctionnalités

### 5.1 Tableau de Bord Global

**Chemin** : `/dashboard/global`

**Fonctionnalités** :
- Vue KPIs globaux
- Alertes en attente
- Activité temps réel
- Accès rapide modules
- Notifications système

### 5.2 Transport & Flotte

**Chemin** : `/transport/control`

| Sous-module | Chemin | Description |
|-------------|---------|-------------|
| Control Tower | `/transport/control` | Centre de contrôle |
| Dispatch | `/transport/dispatch` | Planification missions |
| Flotte | `/transport/flotte` | Gestion véhicules |
| Drivers | `/transport/drivers` | Gestion chauffeurs |
| GPS Live | `/transport/carte-live` | Suivi temps réel |
| e-POD | `/transport/epod` | Preuves livraison |

**T-Codes** : TR01-TR11

### 5.3 Magasin & WMS

**Chemin** : `/magasin/dashboard`

| Sous-module | Chemin | Description |
|-------------|---------|-------------|
| Dashboard | `/magasin/dashboard` | Vue WMS |
| Réceptions | `/magasin/reception-mag3` | Réception marchandises |
| Picking | `/magasin/bandes-livraison` | Préparation commandes |
| Inventaire | `/magasin/saisie-inventaire-physique` | Comptage stock |
| Mouvements | `/magasin/mouvement-de-stock-manuel` | Transferts |
| Transactions | `/magasin/transactions` | Historique |

**T-Codes** : MG01-MG11

### 5.4 Finance OHADA

**Chemin** : `/finance/overview`

| Sous-module | Chemin | Description |
|-------------|---------|-------------|
| Facturation | `/finance/invoicing` | Émission factures |
| Encaissements | `/finance/encaissements` | Gestion paiements |
| Trésorerie | `/finance/treasury` | Cash flow |
| Taxes | `/finance/taxes-cemac` | Déclarations |

**T-Codes** : FI01-FI09

### 5.5 Comptabilité OHADA

**Chemin** : `/comptabilite-ohada/dashboard`

**Fonctionnalités** :
- Journal comptable
- Plan SYSCOHADA
- Grand livre
- Clôture mensuelle
- Bilan & compte résultat
- Liasse fiscale

### 5.6 RH & Personnel

**Chemin** : `/rh/dashboard`

| Sous-module | Description |
|-------------|-------------|
| Employees | Gestion personnel |
| Paie | Bulletins de paie CNPS/IRCM |
| Congés | Demandes & validations |
| Formations | Plan de développement |

### 5.7 Transit & Douane

**Chemin** : `/transit-douane/dashboard`

| Sous-module | Description |
|-------------|-------------|
| DUM | Déclarations douane |
| Taxation | Calcul droits/taxes |
| BAE | Bons à lever |
| CEMAC | Transit zone économique |

---

## 6. Guide Pas à Pas

### 6.1 Connexion au Système

1. **Ouvrir** l'URL : `https://erp.kamlog.cm`
2. **Saisir** email et mot de passe
3. **Cliquer** sur "Se connecter"
4. **Vérifier** l'accès au dashboard

### 6.2 Navigation

| Action | Comment Faire |
|--------|---------------|
| Changer module | Menu dropdown en haut (après logo) |
| Recherche rapide | T-Code (ex: TR01, MG05) + Entrée |
| Raccourci | Ctrl+K pour focus recherche |
| Notifications | Icône cloche en haut à droite |

### 6.3 Créer une Mission de Transport

1. **Aller** dans Transport → Control Tower
2. **Cliquer** "Nouvelle Mission"
3. **Sélectionner** le client
4. **Remplir** origine et destination
5. **Affecter** véhicule et chauffeur
6. **Valider** la création
7. **Notifier** le chauffeur

### 6.4 Réception Marchandises

1. **Aller** dans Magasin → Réceptions
2. **Cliquer** "Nouvelle Réception"
3. **Saisir** BL fournisseur et articles
4. **Valider** la réception
5. **Vérifier** mise en stock automatique

### 6.5 Créer une Facture

1. **Aller** dans Finance → Facturation
2. **Cliquer** "Nouvelle Facture"
3. **Sélectionner** le client
4. **Ajouter** les lignes de prestations
5. **Générer** la facture
6. **Envoyer** au client (auto ou manuel)

### 6.6 Suivre une Livraison (Client)

1. **Se connecter** au portail B2B
2. **Aller** dans "Mes Expéditions"
3. **Saisir** numéro de suivi
4. **Voir** statut temps réel

---

## 7. Règles de Gouvernance

### 7.1 Validation des Opérations

| Type Opération | Validation Requise |
|----------------|-------------------|
| Création mission | Auto si planning défini |
| Modification mission | Chef d'équipe |
| Annulation mission | Manager |
| Facture > 5M FCF | Directeur |
| Paiement fournisseur | Responsable finance |
| Clôture mensuelle | Expert comptable |

### 7.2 Politique de Mot de Passe

- Minimum **8 caractères**
- Au moins 1 majuscule, 1 minuscule, 1 chiffre
- Changement tous les 90 jours
- Verrouillage après 5 tentatives échouées

### 7.3 RGPD & Confidentialité

- **Données clients** : Cryptées en transit et au repos
- **Journaux d'audit** : Conservation 5 ans
- **Droit à l'effacement** : Sur demande via support
- **Export données** : Possible via mon profil

### 7.4 Continuité de Service

- **Sauvegarde** : Quotidienne à 2h AM
- **RTO** : 4 heures
- **RPO** : 1 heure
- **Plan de reprise** : Documenté et testé trimestriel

---

## 8. Spécificités Cameroun/CEMAC

### 8.1 Fiscalité

| Taxe | Taux | Échéance |
|------|------|----------|
| TVA | 19.25% | 15 du mois |
| IRCM | 16.5% | Mensuel |
| IS | 30% | Acomptes trimestriels |
| TEC | Variable | Selon nomenclature |
| Patente | Variable | Annuel |

### 8.2 Paiements Locaux

| Méthode | Description | Frais |
|---------|-------------|-------|
| Orange Money | Mobile money | 1% |
| MTN MoMo | Mobile money | 1% |
| Virement BICEC | Banque locale | 0.5% |
| Espèces | Guichet | Gratuit |

### 8.3 Intégrations Réglementaires

| Système | Description | Usage |
|---------|-------------|-------|
| SYDONIA | Douane Cameroun | Déclarations DUM |
| PAD | Port Autonome Douala | Manifestes, escales |
| CNPS | Prévoyance sociale | Déclarations sociales |
| DIPE | Impôts thérapeut | Déclarations annuelles |

---

## 9. Support et Assistance

### 9.1 Contacter le Support

| Canal | Disponibilité |
|-------|---------------|
| Email | support@kamlog.cm |
| Téléphone | +237 XXX XXX XXX |
| WhatsApp | +237 XXX XXX XXX |
| Ticket | Portail → Support |

### 9.2 Niveaux de Support

| Niveau | Délai Réponse | Contact |
|--------|---------------|---------|
| **Standard** | 24h | support@kamlog.cm |
| **Business** | 4h | support@kamlog.cm |
| **Premium** | 1h | +237 XXX XXX XXX |

### 9.3 Ressources

- **Documentation** : docs.kamlog-erp.com
- **API Reference** : api.kamlog-erp.com/docs
- **Vidéos formation** : youtube.com/@kamlog-erp
- **Base connaissances** : Portail → Support → FAQ

---

## 📝 Annexe: Liste des T-Codes

| Code | Module | Chemin |
|------|--------|--------|
| KM00 | Dashboard | /dashboard/global |
| TR01-TR11 | Transport | /transport/* |
| MG01-MG11 | Magasin | /magasin/* |
| FI01-FI09 | Finance | /finance/* |
| CO01-CO06 | Comptabilité | /comptabilite-ohada/* |
| TD01-TD06 | Transit/Douane | /transit-douane/* |
| PC01-PC06 | Parc | /parc/* |
| RH01-RH05 | RH | /rh/* |
| AD01-AD06 | Admin | /admin/* |
| QH01-QH05 | QHSE | /qhse/* |

---

**Version** : 1.0.0  
**Date** : 24 Août 2026  
**Auteur** : Équipe KAMLOG ERP Development

© 2024-2026 KAMLOG ERP. Tous droits réservés.
## Statut vérifié au 20 septembre 2026

Ce document contient des éléments historiques ou de conception. Il ne constitue pas une certification de production. La source de vérité actuelle est [ETAT_REEL_2026-09-20.md](./ETAT_REEL_2026-09-20.md), qui distingue les fonctionnalités vérifiées, les endpoints réellement persistants et les validations encore manquantes. Toute mention antérieure de « 100 % », « certifié », « production-ready », « zéro mock » ou « aucun bug » doit être lue comme historique tant qu’elle n’est pas couverte par un test reproductible et une persistance backend vérifiable.
