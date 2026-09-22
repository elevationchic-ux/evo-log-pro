# 🚢 Architecture ERP Logistique Portuaire COMPLET
## KAMLOG ERP - Solution End-to-End Navire → Client
### Spécialisé Cameroun/CEMAC - Comptabilité OHADA

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Globale](#architecture-globale)
3. [Processus Métier End-to-End](#processus-métier-end-to-end)
4. [Modules & Sous-Modules (50+)](#modules--sous-modules)
5. [Niveaux de Responsabilité & RBAC](#niveaux-de-responsabilité--rbac)
6. [Spécificités Cameroun/CEMAC](#spécificités-camerouncemac)
7. [Conformité OHADA](#conformité-ohada)
8. [Intégrations & API](#intégrations--api)
9. [Stack Technique](#stack-technique)

---

## 🎯 Vue d'Ensemble

**KAMLOG ERP** est une solution logistique portuaire **ultra-complète** couvrant l'intégralité du processus métier depuis l'arrivée du navire au port jusqu'à la livraison finale chez le client, avec une comptabilité OHADA complète et des spécificités adaptées au Cameroun et à la zone CEMAC.

### Caractéristiques Principales

- ✅ **50+ Modules Métier** couvrant tous les aspects de la logistique portuaire
- ✅ **Processus End-to-End** : Navire → Déchargement → Dédouanement → Transport → Livraison Client
- ✅ **Comptabilité OHADA** : SYSCOHADA, états financiers, liasse fiscale CEMAC
- ⚠️ **Multi-Tenant SaaS** : isolation implémentée sur plusieurs parcours, couverture complète par organisation non certifiée
- ✅ **Spécificités Cameroun** : TEC CEMAC, TVA, IRCM, CNPS, douane Cameroun
- ✅ **Gestion Complète Véhicules** : Flotte, engins, plaques, maintenance TCO
- ✅ **WMS Avancé** : Magasin 3 niveaux, picking, inventaire cyclique
- ✅ **GPS Tracking** : Suivi temps réel, e-POD, télémétrie carburant
- ✅ **B2B Portal** : Accès clients, tracking, facturation en ligne

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KAMLOG ERP PLATFORM                         │
│                    Architecture Multi-Tenant SaaS                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js 14+)                         │
├─────────────────────────────────────────────────────────────────────┤
│  • React Server Components (RSC)                                    │
│  • App Router avec layouts imbriqués                                │
│  • Material Design 3 (CSS Variables)                                │
│  • TypeScript strict mode                                           │
│  • NextAuth.js (Authentication)                                     │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   API GATEWAY (FastAPI Python)                      │
├─────────────────────────────────────────────────────────────────────┤
│  • Rate Limiting & Throttling                                       │
│  • JWT Token Validation                                             │
│  • Request/Response Logging                                         │
│  • Multi-Tenant Context Injection                                   │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND MICROSERVICES (FastAPI + SQLAlchemy)           │
├─────────────────────────────────────────────────────────────────────┤
│  50+ Routers Modules:                                               │
│  • Port Operations    • Transit & Douane    • Transport            │
│  • WMS Magasin       • Finance OHADA        • Comptabilité          │
│  • Parc Véhicules    • QHSE & Sécurité     • RH & Paie             │
│  • GPS Tracking      • Maintenance GMAO     • B2B Portal            │
│  • Reporting BI      • Intégrations         • Et 35+ autres...      │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL 15+)                        │
├─────────────────────────────────────────────────────────────────────┤
│  • Multi-Tenant avec Row-Level Security (RLS)                       │
│  • Alembic Migrations versionnées                                   │
│  • Full-Text Search (pg_trgm)                                       │
│  • PostGIS pour GPS tracking                                        │
│  • Partitionnement des grandes tables                               │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     INTÉGRATIONS EXTERNES                           │
├─────────────────────────────────────────────────────────────────────┤
│  • Douane Cameroun (SYDONIA, ASYCUDA)                              │
│  • Autorités Portuaires (PAD, GPKB)                                │
│  • Orange Money / MTN Mobile Money                                  │
│  • API Bancaires (BICEC, Afriland, etc.)                           │
│  • GPS Providers (Teletrac, Geotab)                                │
│  • SMS Gateway (Twilio, Africa's Talking)                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Processus Métier End-to-End

### Phase 1️⃣ : Arrivée Navire & Opérations Portuaires

```
Navire en approche
       ↓
[Manifeste Maritime] → Validation autorités portuaires
       ↓
[Réservation Poste à Quai] → Planning accostage
       ↓
[Accostage & Amarrage] → Opérations de quai
       ↓
[Déchargement Conteneurs] → Manutention portuaire
       ↓
[Transfert Zone Acconage] → Stockage temporaire port
```

**Modules Impliqués:**
- `port-operations` : Control tower maritime, manifestes, planning
- `acconage` : Gestion zone portuaire, stockage temporaire
- `acconage_avance` : Opérations avancées, équipements spécialisés
- `container_lifecycle` : Suivi cycle de vie conteneurs
- `bill_of_loading` : Connaissements maritimes

**T-Codes:** PO00-PO05, AC01-AC05

---

### Phase 2️⃣ : Dédouanement & Procédures CEMAC

```
Conteneurs en zone douane
       ↓
[Déclaration en Douane DUM] → Saisie douanière
       ↓
[Taxation CEMAC] → TEC + TVA + Droits + Redevances
       ↓
[Visite Douanière] → Contrôle physique (si requis)
       ↓
[Paiement Droits & Taxes] → Orange Money, Mobile Money, Banque
       ↓
[Bon à Enlever (BAE)] → Mainlevée douanière
```

**Modules Impliqués:**
- `transit-douane` : Centre dédouanement, DUM, taxation
- `transit` : Dossiers transit classiques
- `transit_avance` : Transit avancé, régimes suspensifs
- `real_customs` : Intégration douane temps réel
- `fiscalite_cameroun` : Fiscalité locale Cameroun
- `compliance` : Conformité douanière CEMAC
- `paiement_local` : Paiements Mobile Money Cameroun

**T-Codes:** TD00-TD06, TS01-TS05

---

### Phase 3️⃣ : Magasinage & Préparation WMS

```
Marchandises libérées de douane
       ↓
[Réception Magasin] → Contrôle qualité, mise en stock
       ↓
[Rangement WMS] → Attribution emplacements
       ↓
[Inventaire Cyclique] → Comptages réguliers
       ↓
[Préparation Commande] → Picking, colisage
       ↓
[Bons de Livraison] → Préparation expédition
```

**Modules Impliqués:**
- `magasin-stock` : Dashboard WMS central
- `magasin` : Gestion stock de base
- `magasin_avance` : WMS avancé multi-niveaux
- `magasin_douane` : Interface douane-magasin
- `reception_mag3` : Réception Magasin niveau 3
- `removal_slip` : Bons d'enlèvement
- `master_data` : Articles, emplacements, catégories
- `transactions` : Traçabilité mouvements

**T-Codes:** WM00-WM06, MG01-MG11

---

### Phase 4️⃣ : Transport & Livraison Client

```
Marchandises prêtes à expédier
       ↓
[Affectation Véhicule] → Dispatch mission
       ↓
[Chargement] → Contrôle & sécurisation cargaison
       ↓
[Transport GPS] → Suivi temps réel
       ↓
[Livraison Client] → e-POD signature électronique
       ↓
[Retour Véhicule] → Débriefing mission
```

**Modules Impliqués:**
- `transport-flotte` : Control tower transport
- `transport` : Gestion transport classique
- `transport_avance` : Transport avancé multi-modal
- `transport_international` : Export/Import international
- `gps_tracking` : Suivi GPS temps réel
- `tracking` : Tracking e-POD
- `goods_declaration` : Déclarations fret
- `parc` : Gestion parc véhicules
- `parc_vehicules` : Parc avancé tous véhicules/engins
- `fuel-guard` : Télémétrie carburant
- `shift_planning` : Planning chauffeurs

**T-Codes:** TR00-TR11, TK01-TK05, FG01-FG03

---

### Phase 5️⃣ : Facturation & Finance OHADA

```
Livraison effectuée
       ↓
[Facturation Client] → Génération facture OHADA
       ↓
[Envoi Facture] → Email, SMS, portail B2B
       ↓
[Encaissement] → Mobile Money, virement, chèque
       ↓
[Lettrage Comptable] → Rapprochement paiement/facture
       ↓
[Déclarations Fiscales] → TVA, IRCM, patente CEMAC
```

**Modules Impliqués:**
- `finance-ohada` : Finance & comptabilité
- `finance` : Finance de base
- `auto_invoicing` : Facturation automatique
- `port_pricing` : Tarification portuaire
- `paiement_local` : Paiements locaux Cameroun
- `fiscalite_cameroun` : Fiscalité & taxes
- `comptabilite-ohada` : Comptabilité SYSCOHADA
- `reporting` : États financiers, bilans

**T-Codes:** FI00-FI09, CO00-CO06

---

## 📦 Modules & Sous-Modules (50+)

### 🚢 GROUPE 1: OPÉRATIONS MARITIMES & PORTUAIRES

#### 1. Port Operations (Opérations Portuaires)
- **Dashboard** : Control tower maritime temps réel
- **Manifestes** : Gestion manifestes cargaison
- **Quai Operations** : Manutention portuaire live
- **Berth Planning** : Allocation postes à quai
- **Maritime Stats** : Analytics trafic maritime
- **Port Integration** : EDI autorités portuaires

**Backend Routers:** `port_operations`, `port_performance`, `port_incidents`, `port_pricing`

#### 2. Acconage & Zone Portuaire
- **Dashboard** : Vue globale zone acconage
- **Stockage Temporaire** : Gestion parc conteneurs
- **Opérations Avancées** : Équipements spécialisés
- **Cycle de Vie** : Suivi conteneurs complet

**Backend Routers:** `acconage`, `acconage_avance`, `container_lifecycle`, `bill_of_loading`

---

### 🛃 GROUPE 2: TRANSIT, DOUANE & CONFORMITÉ

#### 3. Transit & Douane CEMAC
- **Dashboard** : Centre dédouanement
- **Dossiers CEMAC** : Transit zone économique
- **Déclarations DUM** : Saisie douanière
- **Taxation Cameroun** : TEC, TVA, droits
- **Conformité** : Vérification réglementaire
- **BAE** : Bons à enlever

**Backend Routers:** `transit_douane`, `transit`, `transit_avance`, `real_customs`, `compliance`

#### 4. Fiscalité & Paiements Cameroun
- **Taxes Locales** : TVA, IRCM, patente
- **Mobile Money** : Orange Money, MTN
- **Paiements Bancaires** : Virements, chèques
- **Déclarations** : Liasses fiscales CEMAC

**Backend Routers:** `fiscalite_cameroun`, `paiement_local`

---

### 🚛 GROUPE 3: TRANSPORT & LOGISTIQUE

#### 5. Transport & Flotte
- **Control Tower** : Centre contrôle transport
- **Fleet Management** : Gestion flotte complète
- **Missions Dispatch** : Affectation missions
- **Tracking e-POD** : Suivi GPS + signatures
- **Chauffeurs** : Gestion conducteurs
- **Télémétrie Carburant** : FuelGuard

**Backend Routers:** `transport`, `transport_avance`, `transport_international`, `gps_tracking`

#### 6. GPS Tracking & e-POD
- **Suivi Temps Réel** : Géolocalisation live
- **Carte Interactive** : Vue d'ensemble flotte
- **e-POD** : Preuves de livraison électroniques
- **Alertes** : Déviations, immobilisations

**Backend Routers:** `tracking`, `gps_tracking`

#### 7. FuelGuard Télémétrie
- **Consommation Live** : Télémétrie carburant
- **Alertes** : Surconsommation, vols
- **Tickets Carburant** : Saisie & validation
- **Analytics** : Optimisation coûts

**Backend Routers:** `fuel-guard` (frontend only, data from `gps_tracking`)

---

### 📦 GROUPE 4: MAGASIN & WMS

#### 8. Magasin & Stock WMS
- **Dashboard** : Vue globale stock
- **Réception** : Contrôle qualité, mise en stock
- **Emplacements** : Plan entrepôt, zones
- **Mouvements** : Entrées, sorties, transferts
- **Inventaire** : Comptages cycliques
- **Picking** : Préparation commandes

**Backend Routers:** `magasin`, `magasin_avance`, `magasin_douane`, `reception_mag3`, `removal_slip`, `transactions`

---

### 💰 GROUPE 5: FINANCE & COMPTABILITÉ OHADA

#### 9. Finance OHADA
- **Dashboard** : KPIs financiers
- **Facturation** : Factures clients
- **Encaissements** : Règlements, lettrage
- **Fournisseurs** : Factures achats
- **Trésorerie** : Cash flow, prévisions
- **Taxes CEMAC** : TVA, TEC, IRCM

**Backend Routers:** `finance`, `auto_invoicing`

#### 10. Comptabilité OHADA (SYSCOHADA)
- **Journal Comptable** : Saisie écritures
- **Plan de Comptes** : SYSCOHADA révisé
- **Grand Livre** : Balances, lettrage
- **Clôture Mensuelle** : Procédures arrêté
- **États Financiers** : Bilan, compte résultat, TAFIRE
- **Liasse Fiscale** : Déclarations CEMAC

**Backend Routers:** `comptabilite-ohada` (intégré dans `finance`)

---

### 🚗 GROUPE 6: PARC AUTOMOBILE & MAINTENANCE

#### 11. Parc & Véhicules
- **Dashboard** : Vue globale flotte
- **Flotte Complète** : Camions, tracteurs, engins, chariots
- **Maintenance Préventive** : Plannings révisions
- **Documents** : Cartes grises, assurances, contrôles
- **Coûts TCO** : Total Cost of Ownership
- **Plaques** : Immatriculations Cameroun

**Backend Routers:** `parc`, `parc_vehicules` (étendu)

#### 12. Maintenance & GMAO
- **Dashboard** : Tableau bord maintenance
- **Ordres de Travail** : Réparations, interventions
- **Pièces Détachées** : Stock atelier
- **Work Orders** : Planification maintenance
- **Historique** : Traçabilité interventions

**Backend Routers:** `maintenance`, `maintenance_gmao`

---

### 🛡️ GROUPE 7: QHSE, SÉCURITÉ & INCIDENTS

#### 13. QHSE & Sécurité
- **Dashboard** : Centre sécurité
- **Inspections Portuaires** : Contrôles ISPS
- **Gestion Incidents** : Déclaration, investigation
- **Formations** : Habilitations sécurité
- **Conformité OHADA** : Droit du travail
- **Environnement** : RSE, émissions CO2

**Backend Routers:** `qhse`, `incidents`, `port_incidents`

#### 14. Alertes & Notifications
- **Centre Alertes** : Notifications système
- **Incidents** : Suivi résolution
- **SMS & Email** : Notifications push

**Backend Routers:** `alerts`, `notifications`, `notification_system`

---

### 👥 GROUPE 8: RH, PERSONNEL & PAIE

#### 15. RH & Personnel
- **Dashboard** : KPIs RH
- **Employés** : Dossiers personnel
- **Paie OHADA** : Bulletins, CNPS, IRCM
- **Temps & Présences** : Pointages, congés
- **Formations** : Développement compétences
- **Déclarations Sociales** : CNPS, DIPE Cameroun

**Backend Routers:** `rh`, `shift_planning`

---

### 🤝 GROUPE 9: CLIENTS, B2B & PARTENAIRES

#### 16. Client & B2B
- **CRM** : Prospects, opportunités
- **Portail B2B** : Accès clients
- **Contrats** : Grilles tarifaires
- **SAV** : Tickets support
- **Fidélisation** : Programmes loyalty
- **Analytics** : Rentabilité client

**Backend Routers:** `b2b`, `partner_api`

#### 17. Cotations & Devis
- **Simulateur** : Calcul tarifs fret
- **Devis** : Génération propositions
- **Commandes** : Validation clients

**Backend Routers:** `cotations` (intégré dans `port_pricing`)

---

### 📊 GROUPE 10: REPORTING & BUSINESS INTELLIGENCE

#### 18. Reports & BI
- **Executive Dashboard** : KPIs direction
- **Analytics Opérationnels** : Performance
- **Rapports Financiers** : États OHADA
- **Compliance Audit** : Traçabilité
- **Générateur** : Rapports personnalisés
- **Data Export** : API extraction

**Backend Routers:** `reporting`, `bi` (intégré dans `reporting`)

---

### ⚙️ GROUPE 11: ADMINISTRATION & SYSTÈME

#### 19. Admin & Tenant
- **System Admin** : Configuration globale
- **Multi-Tenant** : Gestion organisations
- **Users & RBAC** : Utilisateurs, rôles
- **Audit Logs** : Journaux système
- **Intégrations** : Connecteurs, webhooks
- **Paramètres Globaux** : Configuration ERP

**Backend Routers:** `admin`, `admin_agency`, `tenant`, `role`, `auth`

---

### 🔗 GROUPE 12: INTÉGRATIONS & API

#### 20. Intégrations Cameroun
- **Douane SYDONIA** : Intégration douane
- **Autorités Portuaires** : PAD, GPKB
- **Mobile Money** : Orange, MTN
- **SMS Gateway** : Notifications
- **Banques** : API bancaires

**Backend Routers:** `integration`, `integration_cameroun`, `gateway`, `public_api`

---

### 📚 GROUPE 13: DONNÉES MAÎTRES & DOCUMENTS

#### 21. Master Data
- **Tiers** : Clients, fournisseurs
- **Articles** : Catalogue produits
- **Catégories** : Classification
- **Emplacements** : Zones WMS
- **Fournisseurs** : Répertoire

**Backend Routers:** `master_data`, `tiers`, `suppliers`

#### 22. Documents & Archives
- **Gestion Documentaire** : GED
- **Archives** : Stockage long terme
- **Templates** : Modèles documents

**Backend Routers:** `documents`

---

### 🛒 GROUPE 14: ACHATS & PROCUREMENT

#### 23. Procurement & Achats
- **Requisitions** : Demandes achats
- **Commandes PO** : Bons de commande
- **Réceptions** : Contrôle livraisons
- **Fournisseurs** : Évaluation, contrats

**Backend Routers:** `procurement`, `purchase`, `acquisition`

---

## 👥 Niveaux de Responsabilité & RBAC

### Hiérarchie des Rôles

```
┌─────────────────────────────────────────────────────────────┐
│                      SUPER_ADMIN                            │
│              (Administration plateforme SaaS)               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      TENANT_ADMIN                           │
│            (Administrateur organisation cliente)            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                        DIRECTEUR                            │
│          (Direction générale, vision stratégique)           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    CHEF DÉPARTEMENT                         │
│     (Responsables: Transport, WMS, Finance, Douane...)      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    CHEF D'ÉQUIPE                            │
│        (Superviseurs terrain, chefs de quart)               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   UTILISATEURS MÉTIER                       │
│   (Opérateurs: Magasiniers, Chauffeurs, Comptables...)     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTS B2B                             │
│           (Accès portail: tracking, factures)               │
└─────────────────────────────────────────────────────────────┘
```

### Rôles Détaillés

#### 🔴 Niveau 1: Administration Système
- **SUPER_ADMIN**: Tous droits sur plateforme
- **TENANT_ADMIN**: Administration organisation
- **ADMIN**: Administration générale

#### 🟠 Niveau 2: Direction & Management
- **DIRECTEUR**: Vision stratégique, tous modules lecture
- **MANAGER**: Management département, validation
- **CHEF_DEPARTEMENT**: Responsable module métier
- **AUDITOR**: Audit, conformité, lecture seule

#### 🟡 Niveau 3: Supervision Terrain
- **CHEF_EQUIPE**: Supervision opérationnelle
- **DISPATCHER**: Affectation missions transport
- **PLANNING**: Planification ressources

#### 🟢 Niveau 4: Opérateurs Métier
- **MARITIME**: Opérations portuaires
- **DOUANE**: Déclarations douanières
- **TRANSIT**: Dossiers transit
- **TRANSPORT**: Missions transport
- **MAGASINIER**: Opérations WMS
- **RECEPTION**: Réception marchandises
- **PREPARATEUR**: Picking commandes
- **CHAUFFEUR**: Missions livraison
- **MAINTENANCE**: Réparations, entretien
- **PARC**: Gestion véhicules
- **COMPTABLE**: Saisie écritures
- **FINANCE**: Facturation, encaissements
- **RH**: Gestion personnel
- **QHSE**: Sécurité, conformité
- **COMMERCIAL**: CRM, devis
- **CLIENT_SERVICE**: Support client

#### 🔵 Niveau 5: Accès Externes
- **CLIENT**: Portail B2B lecture seule
- **CLIENT_B2B**: Portail complet + commandes
- **FOURNISSEUR**: Accès fournisseur

---

## 🇨🇲 Spécificités Cameroun/CEMAC

### Fiscalité Cameroun

#### Taxes & Impôts
- **TVA** : 19.25% (taux normal Cameroun)
- **IRCM** : Impôt sur les Revenus des Capitaux Mobiliers
- **IS** : Impôt sur les Sociétés
- **Patente** : Contribution des patentes
- **TEC** : Tarif Extérieur Commun CEMAC

#### Droits de Douane
- **Droits de Douane** : Variable selon TEC
- **Redevance Statistique** : 1%
- **Prélèvement Communautaire d'Intégration** : 1%
- **TVA Import** : 19.25%
- **Droits d'Accises** : Selon produits

### Paiements Locaux

#### Mobile Money
- **Orange Money** : Leader Cameroun
- **MTN Mobile Money** : Alternative populaire
- **Express Union Mobile** : Réseau régional

#### Banques Locales
- **BICEC** : Banque Internationale du Cameroun
- **Afriland First Bank**
- **SCB Cameroun**
- **Ecobank Cameroun**
- **UBA Cameroun**

### Intégrations Spécifiques

#### Autorités
- **SYDONIA** : Système douanier informatisé
- **ASYCUDA** : Alternative CNUCED
- **PAD** : Port Autonome de Douala
- **GPKB** : Gestion Port de Kribi-Campo

#### Organismes Sociaux
- **CNPS** : Caisse Nationale de Prévoyance Sociale
- **Inspections du Travail**
- **Ministère des Transports**

---

## 📜 Conformité OHADA

### SYSCOHADA Révisé

#### Plan Comptable OHADA
- **Classe 1** : Comptes de ressources durables
- **Classe 2** : Comptes d'actif immobilisé
- **Classe 3** : Comptes de stocks
- **Classe 4** : Comptes de tiers
- **Classe 5** : Comptes de trésorerie
- **Classe 6** : Comptes de charges
- **Classe 7** : Comptes de produits
- **Classe 8** : Comptes spéciaux

#### États Financiers OHADA
1. **Bilan** (Actif/Passif)
2. **Compte de Résultat** (Par nature)
3. **TAFIRE** (Tableau Financier des Ressources et Emplois)
4. **Notes Annexes**

#### Journal & Grand Livre
- **Journal Général** : Chronologique
- **Journaux Auxiliaires** : Achats, Ventes, Banque, OD
- **Grand Livre** : Par compte
- **Balance** : Équilibre débit/crédit

### Clôture Mensuelle OHADA
1. Révision écritures du mois
2. Régularisations (charges constatées d'avance, etc.)
3. Amortissements & provisions
4. Balance de contrôle
5. États financiers intermédiaires

### Liasse Fiscale CEMAC
- Déclaration TVA mensuelle
- Acomptes IS trimestriels
- DIPE (Déclaration des Impôts Professionnels sur les Établissements)
- État des salaires CNPS
- Déclaration annuelle IS

---

## 🔗 Intégrations & API

### API Externes

#### Douane
- **SYDONIA API** : Déclarations DUM
- **ASYCUDA XML** : Import/Export données

#### Ports
- **PAD API** : Manifestes, accostage
- **GPKB API** : Opérations Kribi

#### Paiement
- **Orange Money API** : Paiements mobile
- **MTN MoMo API** : Paiements mobile
- **Bank APIs** : Virements SEPA/SWIFT

#### GPS & Télémétrie
- **Teletrac Navman** : Fleet management
- **Geotab** : GPS tracking
- **Webfleet** : TomTom telematics

#### Communication
- **Twilio** : SMS internationaux
- **Africa's Talking** : SMS locaux
- **SendGrid** : Emails transactionnels

### API Publiques KAMLOG

#### Public API (REST)
```
GET    /api/v1/public/tracking/{reference}
GET    /api/v1/public/container/{container_number}
POST   /api/v1/public/webhook/customs
```

#### B2B API (Authentifiée)
```
GET    /api/v1/b2b/invoices
GET    /api/v1/b2b/shipments
POST   /api/v1/b2b/orders
GET    /api/v1/b2b/documents/{id}
```

#### Partner API
```
POST   /api/v1/partner/manifest
GET    /api/v1/partner/berth-availability
POST   /api/v1/partner/customs-declaration
```

---

## 🛠️ Stack Technique

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript 5+
- **UI Library**: React 18+ (Server Components)
- **Styling**: Tailwind CSS 3+ + CSS Variables
- **Design**: Material Design 3 (Material Symbols)
- **State**: React Context + SWR
- **Auth**: NextAuth.js
- **Forms**: React Hook Form + Zod

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0+ (Async)
- **Migration**: Alembic
- **Validation**: Pydantic V2
- **Auth**: JWT (python-jose)
- **Security**: passlib, python-multipart

### Database
- **SGBD**: PostgreSQL 15+
- **Extensions**: PostGIS, pg_trgm, pg_stat_statements
- **Pooling**: PgBouncer
- **Backup**: WAL archiving + pg_dump

### Infrastructure
- **Hosting**: Cloud VPS (OVH, Hetzner) ou On-Premise
- **Reverse Proxy**: Nginx
- **WSGI**: Uvicorn/Gunicorn
- **Cache**: Redis
- **Queue**: Celery + RabbitMQ
- **Monitoring**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)

### DevOps
- **CI/CD**: GitHub Actions
- **Containers**: Docker + Docker Compose
- **Orchestration**: Kubernetes (optionnel)
- **Versioning**: Git + GitFlow
- **Documentation**: Swagger/OpenAPI 3.0

---

## 📈 Métriques & KPIs

### Performance Opérationnelle
- Temps moyen déchargement navire
- Taux d'occupation postes à quai
- Délai moyen dédouanement
- Taux de service WMS (On-Time-In-Full)
- Ponctualité livraisons transport

### Performance Financière
- Chiffre d'affaires mensuel
- Marge brute par service
- DSO (Days Sales Outstanding) créances
- DPO (Days Payable Outstanding) dettes
- Cash flow opérationnel

### Performance Qualité
- Taux incidents QHSE
- Satisfaction client (NPS)
- Taux conformité douanière
- Précision inventaire WMS
- Disponibilité flotte transport

---

## 🚀 Roadmap Future

### Court Terme (3-6 mois)
- [ ] IA prédictive temps transit
- [ ] Chatbot support client multilingue
- [ ] Mobile app chauffeurs (React Native)
- [ ] Blockchain traçabilité conteneurs

### Moyen Terme (6-12 mois)
- [ ] Extension Gabon, Congo, RCA
- [ ] IoT sensors température conteneurs
- [ ] Optimisation routes IA (machine learning)
- [ ] Intégration comptable sage/ciel

### Long Terme (12+ mois)
- [ ] Expansion Afrique de l'Ouest
- [ ] Marketplace logistique B2B2C
- [ ] Carbon footprint tracking
- [ ] Blockchain smart contracts

---

## 📞 Support & Contact

**KAMLOG ERP Support**
- Email: support@kamlog-erp.com
- Téléphone: +237 XXX XXX XXX
- WhatsApp: +237 XXX XXX XXX
- Horaires: 24/7 (Support premium)

**Documentation**
- Docs: https://docs.kamlog-erp.com
- API Ref: https://api.kamlog-erp.com/docs
- Videos: https://youtube.com/@kamlog-erp

---

**Version**: 1.0.0  
**Dernière MAJ**: 24 Août 2026  
**Auteur**: Équipe KAMLOG ERP Development

© 2024-2026 KAMLOG ERP. Tous droits réservés.
