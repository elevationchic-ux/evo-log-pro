# ðŸ“˜ LE GRAND LIVRE D'ARCHITECTURE, DE NAVIGATION & CARTOGRAPHIE DES 323 ROUTES (EVO-LOG ERP)

> **Document de RÃ©fÃ©rence Technique & Guide OpÃ©rationnel Universel**  
> *DestinÃ© Ã  l'ensemble des parties prenantes : Novices, EmployÃ©s de Terrain, Directeurs d'Exploitation, Comptables OHADA, DSI et Experts Logiciels.*  
> **Statut vÃ©rifiÃ© au 20 septembre 2026 : dÃ©veloppement avancÃ©, non certifiÃ© production.**  
> Les nombres de routes et endpoints sont des inventaires historiques ; la couverture rÃ©elle des contrats frontend/backend, la persistance mÃ©tier et les validations PostgreSQL/Redis doivent Ãªtre vÃ©rifiÃ©es dans [`ETAT_REEL_2026-09-20.md`](./ETAT_REEL_2026-09-20.md).

---

## ðŸ“‘ TABLE DES MATIÃˆRES

1. [Vue d'Ensemble & Mission du Progiciel EVO-LOG](#1-vue-densemble--mission-du-progiciel-evo-log)
2. [Comprendre l'Architecture en 5 Minutes (Pour Novices & Experts)](#2-comprendre-larchitecture-en-5-minutes-pour-novices--experts)
3. [Comment Naviguer Facilement dans l'Application ? (Les 4 MÃ©canismes ClÃ©s)](#3-comment-naviguer-facilement-dans-lapplication-les-4-mÃ©canismes-clÃ©s)
4. [Le SystÃ¨me des T-Codes (SAP-Like) pour les Experts](#4-le-systÃ¨me-des-t-codes-sap-like-pour-les-experts)
5. [Le Pipeline MÃ©tier de Bout en Bout : Navire âž” Quai âž” Douane âž” EntrepÃ´t âž” Route âž” Client](#5-le-pipeline-mÃ©tier-de-bout-en-bout-navire--quai--douane--entrepÃ´t--route--client)
6. [Guide d'Aiguillage des 8 Portails Collaborateurs MÃ©tier](#6-guide-daiguillage-des-8-portails-collaborateurs-mÃ©tier)
7. [Matrice des RÃ´les RBAC : Â« Qui accÃ¨de Ã  quoi ? Â»](#7-matrice-des-rÃ´les-rbac--qui-accÃ¨de-Ã -quoi-)
8. [Cartographie Exhaustive des 18 Modules & RÃ©pertoire des Routes](#8-cartographie-exhaustive-des-18-modules--rÃ©pertoire-des-routes)
9. [Foire Aux Questions & RÃ©solution des DifficultÃ©s Courantes](#9-foire-aux-questions--rÃ©solution-des-difficultÃ©s-courantes)

---

## 1. VUE D'ENSEMBLE & MISSION DU PROGICIEL EVO-LOG

**EVO-LOG** est un progiciel de gestion intÃ©grÃ© (ERP) et une plateforme SaaS de nouvelle gÃ©nÃ©ration dÃ©diÃ©e Ã  la logistique portuaire, au transit douanier maritime, au transport routier lourd et au commerce international dans la zone **CEMAC** (Cameroun, Tchad, Centrafrique, Gabon, Congo, GuinÃ©e Ã‰quatoriale).

### Les 3 Principes Fondamentaux de la Plateforme
1. **Architecture orientÃ©e donnÃ©es rÃ©elles** :
   Les Ã©crans auditÃ©s n'affichent plus leurs jeux de dÃ©monstration les plus dangereux. Des modules restent incomplets ou dÃ©pendent d'endpoints absents ; ils doivent afficher une indisponibilitÃ© explicite plutÃ´t qu'une donnÃ©e inventÃ©e.
2. **ConformitÃ© RÃ©glementaire OHADA & CEMAC** :
   - IntÃ©gration native du rÃ©fÃ©rentiel comptable **SYSCOHADA rÃ©visÃ©** (Grand Livre Ã  6 colonnes, liasse fiscale, bilans, DIPE magnÃ©tique DGI).
   - Prise en charge des procÃ©dures douaniÃ¨res camerounaises (**CAMCIS / Sydonia World**), des rÃ©gimes de transit corridors et des cautions bancaires.
3. **Couverture MÃ©tier Totale (End-to-End)** :
   Depuis l'accostage du navire au port (Douala/Kribi) jusqu'Ã  la livraison finale par lettre de voiture au destinataire Ã  Bangui ou N'Djamena, avec signature Ã©lectronique de livraison (ePOD).

---

## 2. COMPRENDRE L'ARCHITECTURE EN 5 MINUTES (POUR NOVICES & EXPERTS)

Le systÃ¨me repose sur une architecture duale moderne et dÃ©couplÃ©e :

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   FRONTEND NEXT.JS 14 (App Router)                       â”‚
â”‚     323 Routes d'Exploitation â€¢ Tailwind CSS â€¢ TypeScript Strict         â”‚
â”‚  Composants d'Exploitation, Tableaux de Bord, Portails Collaborateurs   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                     â”‚  RequÃªtes REST JSON sÃ©curisÃ©es (JWT)
                                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     BACKEND FASTAPI (Python 3.11)                        â”‚
â”‚         117 Routes API Actives â€¢ Pydantic v2 â€¢ SÃ©curitÃ© OAuth2           â”‚
â”‚        Moteur de Paie IRPP â€¢ Moteur Comptable OHADA â€¢ TraÃ§abilitÃ©        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                     â”‚  ORM SQLAlchemy 2.0 / Alembic
                                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     BASE DE DONNÃ‰ES POSTGRESQL                           â”‚
â”‚  SchÃ©mas Relationnels Multi-Tenants (par company_id) â€¢ IntÃ©gritÃ© Totale  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Pour le Novice
ConsidÃ©rez **EVO-LOG** comme un grand bureau numÃ©rique :
- Le **Frontend (Next.js)** est ce que vous voyez Ã  l'Ã©cran : les boutons, les formulaires, les cartes et les tableaux.
- Le **Backend (FastAPI)** est le moteur invisible qui calcule vos salaires, vÃ©rifie vos stocks et enregistre vos commandes.
- La **Base de DonnÃ©es (PostgreSQL)** est l'armoire forte oÃ¹ tous les documents, factures et historiques sont conservÃ©s en sÃ©curitÃ© pendant 10 ans.

### Pour l'Expert / DSI
- **Isolation Multi-Tenant** : Cloisonnement strict au niveau de la couche donnÃ©es par filtre automatique `company_id`.
- **Typage Stricte** : 100% du frontend est compilÃ© sous TypeScript avec validation SWC (`exit code 0`).
- **WebRTC & WebSocket** : Canaux bidirectionnels en temps rÃ©el pour le Push-to-Talk vocal et la visioconfÃ©rence P2P.
- **Piste d'Audit Immuable** : Journalisation horodatÃ©e des Ã©critures financiÃ¨res et des actions de sÃ©curitÃ©.

---

## 3. COMMENT NAVIGUER FACILEMENT DANS L'APPLICATION ? (LES 4 MÃ‰CANISMES CLÃ‰S)

Avec **323 pages**, un utilisateur pourrait craindre de se perdre. EVO-LOG intÃ¨gre **4 mÃ©canismes d'orientation ergonomiques** utilisables aussi bien sur ordinateur de bureau que sur tablette ou mobile :

### 1. La Barre LatÃ©rale Principale (`ModuleSidebar`)
- SituÃ©e Ã  gauche de l'Ã©cran, elle affiche les grands modules autorisÃ©s pour votre profil.
- Elle se rÃ©tracte d'un clic sur la flÃ¨che pour libÃ©rer tout l'espace d'affichage pour les tableaux de donnÃ©es.
- Sur mobile, elle s'ouvre comme un tiroir latÃ©ral tactile fluide.

### 2. La Palette de Commandes Universelle (`CommandPalette` via `Ctrl + K`)
- Appuyez simplement sur **`Ctrl + K`** (ou **`Cmd + K`** sur Mac) n'importe oÃ¹ dans l'application.
- Une barre de recherche centrale s'ouvre : tapez 3 lettres de ce que vous cherchez (ex: *"paie"*, *"carburant"*, *"douane"*, *"conteneur"*).
- Appuyez sur **EntrÃ©e** : vous Ãªtes immÃ©diatement redirigÃ© vers la page voulue en 0,2 seconde !

### 3. La Bulle Orbitale de Navigation (`SubModuleOrbitalBubble`)
- PrÃ©sente en bas Ã  droite de votre Ã©cran sous forme de bouton flottant discret.
- En cliquant dessus, elle dÃ©ploie les sous-modules immÃ©diats du domaine dans lequel vous vous trouvez, sans avoir Ã  remonter au menu principal.

### 4. Le Hub Collaborateur CentralisÃ© (`/portail-collaborateur`)
- **L'adresse universelle par excellence** : [`/portail-collaborateur`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-collaborateur/page.tsx).
- PrÃ©sente sur un seul Ã©cran les 8 espaces de travail terrain sous forme de grandes cartes interactives adaptÃ©es aux Ã©crans tactiles.

### 5. Le Fil d'Ariane Dynamique (`AppBreadcrumb`)
- PositionnÃ© au sommet de chaque vue d'exploitation, il retrace l'arborescence exacte de votre parcours (ex: *Accueil > ComptabilitÃ© OHADA > Grand Livre*).
- Permet de remonter d'un clic au niveau supÃ©rieur sans jamais perdre son contexte.

### 6. Le Centre d'Aide Contextuelle & Raccourcis Clavier (Touche `?`)
- Appuyez simplement sur la touche **`?`** sur votre clavier ou cliquez sur l'icÃ´ne d'aide en haut de page.
- Ouvre instantanÃ©ment [`HelpAndShortcutsModal`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/HelpAndShortcutsModal.tsx) prÃ©sentant :
  - La mission exacte de l'Ã©cran courant.
  - Les 3 Ã©tapes indispensables pour accomplir votre tÃ¢che sans blocage.
  - L'aide-mÃ©moire complet des touches rapides (`Ctrl+K`, `?`, `Esc`, `Tab`).

### 7. Les Infobulles PÃ©dagogiques du Glossaire MÃ©tier (`TermDefinition`)
- Au survol ou au tap tactile d'un acronyme technique (*DUM, BAE, BAPLIE, FEFO, FIFO, ROP, TCO, IRPP, DIPE...*), une carte explicative dÃ©taillÃ©e s'affiche.
- Garantit qu'un utilisateur novice comprend immÃ©diatement la signification sans devoir consulter un manuel papier.

### 8. Le SÃ©lecteur de DensitÃ© des Tableaux (Mode Compact / AÃ©rÃ©)
- Un bouton sÃ©lecteur situÃ© sur chaque tableau [`DataTable`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/DataTable.tsx) permet d'alterner entre :
  - **Mode AÃ©rÃ©** : IdÃ©al pour les Ã©crans tactiles et tablettes de quai.
  - **Mode Compact** : RÃ©duit la hauteur des lignes Ã  32px pour afficher 30 Ã  50 Ã©critures sans scroller (plÃ©biscitÃ© par les comptables et DAF).
  - Le choix de l'utilisateur est automatiquement mÃ©morisÃ© dans son navigateur (`localStorage`).

### 9. La Protection Anti-Erreur & Modal de Confirmation RenforcÃ©e (`DestructiveConfirmModal`)
- EmpÃªche toute suppression ou annulation accidentelle sur des dossiers critiques (annulation de mission, purge de stock).
- Exige la saisie explicite d'un mot-clÃ© de validation (ex : taper `SUPPRIMER`) pour dÃ©verrouiller l'action.

---

## 4. LE SYSTÃˆME DES T-CODES (SAP-LIKE) POUR LES EXPERTS

Pour les utilisateurs habituÃ©s aux systÃ¨mes industriels de type SAP, **EVO-LOG** intÃ¨gre des **codes de transaction rapides (T-Codes)** qui permettent d'accÃ©der instantanÃ©ment Ã  un Ã©cran prÃ©cis via la palette de commandes (`Ctrl + K`) :

| T-Code | Ã‰cran AssociÃ© | Module | Utilisation Principale |
|:---|:---|:---|:---|
| **`KM24`** | `/dashboard/global` | Supervision | Tableau de bord exÃ©cutif de synthÃ¨se |
| **`KPRC_FLW`** | `/dashboard/process-flow` | Supervision | Pipeline temps rÃ©el du flux Navire âž” Client |
| **`KDRV_TRN`** | `/portail-chauffeur` | Transport | Espace mobilitÃ©, tournÃ©e conducteur et ePOD |
| **`KEXP_FEE`** | `/portail-frais` | Finance | Saisie et validation des notes de frais |
| **`KWMS_OP`** | `/portail-magasinier` | EntrepÃ´t | PrÃ©paration de commandes (Picking) et quai |
| **`KTEC_OT`** | `/portail-technicien` | Maintenance | Ordres de travail GMAO et compte-rendu atelier |
| **`KCST_FLD`** | `/portail-declarant` | Douane | Jalonnement physique quai et suivi DUM |
| **`KQHS_ALR`** | `/portail-qhse` | SÃ©curitÃ© | Signalement flash de danger Near-Miss |
| **`KSAL_CRM`** | `/portail-commercial` | Ventes | Simulateur de cotation fret corridor CEMAC |
| **`KEMP_PAY`** | `/portail-employe` | RH | Consultation et tÃ©lÃ©chargement bulletins de paie |
| **`KOHA_GL`** | `/comptabilite-ohada` | Finance | Grand Livre gÃ©nÃ©ral OHADA et balance |
| **`KTOS_ESC`** | `/portail-b2b/dashboard` | Quai | Gestion des escales navires et BAPLIE |

---

## 5. LE PIPELINE MÃ‰TIER DE BOUT EN BOUT : NAVIRE âž” QUAI âž” DOUANE âž” ENTREPÃ”T âž” ROUTE âž” CLIENT

Pour comprendre comment s'enchaÃ®nent les donnÃ©es dans EVO-LOG, voici le cycle de vie complet d'une marchandise importÃ©e :

```mermaid
sequenceDiagram
    autonumber
    actor Navire as ðŸš¢ Navire / Ligne Maritime
    actor Quai as ðŸ—ï¸ Acconier / Quai (TOS)
    actor Douane as ðŸ›ï¸ DÃ©clarant & Douane (CAMCIS)
    actor Entrepot as ðŸ“¦ Magasinier (WMS)
    actor Transport as ðŸšš Chauffeur (TMS)
    actor Client as ðŸ¤ Client Destinataire
    actor Compta as ðŸ“Š ComptabilitÃ© OHADA

    Navire->>Quai: 1. Annonce escale & Import fichier EDI BAPLIE
    Quai->>Quai: 2. DÃ©chargement portique STS & Pointage conteneur terre-plein
    Quai->>Douane: 3. Mise Ã  disposition conteneur pour formalitÃ©s
    Douane->>Douane: 4. DÃ©claration DUM, Scanner, Visite conjointe & Obtention BAE
    Douane->>Entrepot: 5. Transfert sous-douane ou magasin avancÃ© (EntrÃ©e WMS)
    Entrepot->>Entrepot: 6. Stockage adressÃ© 3D & PrÃ©paration Picking (FEFO/FIFO)
    Entrepot->>Transport: 7. Ã‰dition Bon de Sortie & Chargement Camion
    Transport->>Transport: 8. Inspection vÃ©hicule, saisie carburant & trajet corridor
    Transport->>Client: 9. Livraison physique & Signature tactile ePOD
    Client->>Compta: 10. Facture Ã©mise, encaissement & Ã©criture Grand Livre OHADA
```

---

## 6. GUIDE D'AIGUILLAGE DES 8 PORTAILS COLLABORATEURS MÃ‰TIER

Ces portails sont conÃ§us spÃ©cifiquement pour les collaborateurs qui ont besoin d'aller droit au but, sans naviguer dans des menus complexes :

```
                                  [ HUB COLLABORATEUR ]
                                /portail-collaborateur
                                          â”‚
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚               â”‚                  â”‚                  â”‚               â”‚
       â–¼               â–¼                  â–¼                  â–¼               â–¼
[ ðŸšš CHAUFFEUR ] [ ðŸ’¼ FRAIS ]     [ ðŸ“¦ MAGASINIER ]  [ ðŸ”§ TECHNICIEN ] [ ðŸ›ï¸ DÃ‰CLARANT ]
 /portail-        /portail-frais   /portail-          /portail-         /portail-
 chauffeur                         magasinier         technicien        declarant
       â”‚                                  â”‚                  â”‚               â”‚
       â”œâ”€ TournÃ©e du jour                 â”œâ”€ Picking FEFO    â”œâ”€ Mes OTs      â”œâ”€ Dossiers DUM
       â”œâ”€ Checklist dÃ©part                â”œâ”€ RÃ©ceptions quai â”œâ”€ Rapports     â”œâ”€ Jalonnement
       â”œâ”€ Plein carburant                 â”œâ”€ Inventaire      â”œâ”€ PiÃ¨ces PDR   â”œâ”€ Upload BAE
       â””â”€ Signature ePOD                  â””â”€ SÃ©curitÃ© engin  â””â”€ Parc matÃ©rielâ””â”€ Litiges
```

### AccÃ¨s Rapides Directs :
- **Conducteur de camion** âž” Allez sur [`/portail-chauffeur`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-chauffeur/page.tsx)
- **SalariÃ© dÃ©clarant des frais** âž” Allez sur [`/portail-frais`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-frais/page.tsx)
- **Agent de magasin ou cariste** âž” Allez sur [`/portail-magasinier`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-magasinier/page.tsx)
- **MÃ©canicien de l'atelier** âž” Allez sur [`/portail-technicien`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-technicien/page.tsx)
- **Transitaire sur le port** âž” Allez sur [`/portail-declarant`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-declarant/page.tsx)
- **Signalement d'un danger / sÃ©curitÃ©** âž” Allez sur [`/portail-qhse`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-qhse/page.tsx)
- **Commercial en clientÃ¨le** âž” Allez sur [`/portail-commercial`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-commercial/page.tsx)
- **Consultation de bulletin de paie** âž” Allez sur [`/portail-employe`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-employe/page.tsx)

---

## 7. MATRICE DES RÃ”LES RBAC : Â« QUI ACCÃˆDE Ã€ QUOI ? Â»

Pour assurer la sÃ©curitÃ© industrielle et la confidentialitÃ© des donnÃ©es, l'accÃ¨s aux 323 pages est strictement filtrÃ© selon le rÃ´le de l'utilisateur :

| RÃ´le Utilisateur | Modules Prioritaires Visibles | Portails Collaborateurs Directs | Restrictions de SÃ©curitÃ© |
|:---|:---|:---|:---|
| **CHAUFFEUR / CONDUCTEUR** | TMS Transport, e-POD, Carburant | `/portail-chauffeur`, `/portail-frais`, `/portail-qhse`, `/portail-employe` | Aucun accÃ¨s aux finances, clients ou paramÃ©trages |
| **MAGASINIER / CARISTE** | WMS Magasin, EntrepÃ´t Sous-Douane | `/portail-magasinier`, `/portail-frais`, `/portail-qhse`, `/portail-employe` | AccÃ¨s limitÃ© aux mouvements de stocks et ordres de sortie |
| **MÃ‰CANICIEN / TECHNICIEN** | GMAO Parc & Maintenance | `/portail-technicien`, `/portail-frais`, `/portail-qhse`, `/portail-employe` | AccÃ¨s rÃ©servÃ© aux ordres de travaux et piÃ¨ces dÃ©tachÃ©es |
| **DÃ‰CLARANT / TRANSITAIRE** | Transit Douane, DUM, BAE, Scanner | `/portail-declarant`, `/portail-frais`, `/portail-qhse`, `/portail-employe` | AccÃ¨s aux dossiers import/export et bureaux de douane |
| **COMMERCIAL** | CRM, Cotations CEMAC, Facturation | `/portail-commercial`, `/portail-frais`, `/portail-employe` | AccÃ¨s Ã  ses devis et clients assignÃ©s uniquement |
| **COMPTABLE / DAF** | Finance OHADA, Rapprochement, TrÃ©sorerie | `/portail-frais` (Validation), `/portail-employe` | AccÃ¨s complet aux Ã©critures, TVA, bilans et banques |
| **RESPONSABLE RH** | RH Personnel, Paie IRPP/CNPS, Chef Personnel | Tous portails salariÃ©s | Gestion globale des dossiers salariÃ©s et contrats |
| **DIRECTEUR TRANSPORT** | Tour de ContrÃ´le, LiveMap, TCO Flotte | Tous portails transport | Supervision globale de la flotte et dispatching |
| **SUPER ADMIN / ADMIN** | **AccÃ¨s Total aux 323 Routes & 117 APIs** | L'ensemble des 8 portails + Admin SaaS | Gouvernance globale, gestion des licences et audits |

---

## 8. CARTOGRAPHIE EXHAUSTIVE DES 18 MODULES & RÃ‰PERTOIRE DES ROUTES

Voici l'inventaire structurÃ© des 18 grands domaines applicatifs composant les **323 routes Next.js** de l'application :

### 1. ðŸŽ¯ Supervision & Dashboards Globaux
- `/dashboard/global` : Tableau de bord exÃ©cutif de synthÃ¨se avec mÃ©triques clÃ©s live.
- `/dashboard/process-flow` : Vue interactive du pipeline end-to-end (Navire âž” Client).
- `/dashboard/performance` : Indicateurs de rentabilitÃ©, dÃ©lais de rotation et taux de service.

### 2. ðŸš¢ OpÃ©rations Portuaires, Quai & Acconage (TOS)
- `/port-operations/dashboard` : Suivi des arrivÃ©es navires, occupation des postes Ã  quai.
- `/port-operations/escales` : Fiches d'escales, cargaisons annoncÃ©es et manifeste maritime.
- `/port-operations/baplie` : Parseur et exportateur officiel BAPLIE EDIFACT 2.2.
- `/port-operations/yard` : Gestion des terre-pleins et placement des conteneurs 20'/40'.
- `/acconage` & `/acconage-avance` : Facturation des droits de quai et cadences portiques STS.

### 3. ðŸ›ï¸ Transit, Douane CEMAC & CAMCIS
- `/transit` & `/transit-avance` : Gestion des dossiers de transit import/export/rÃ©exportation.
- `/transit-douane/declarations` : Saisie et suivi des dÃ©clarations douaniÃ¨res DUM.
- `/transit-douane/dossiers-cemac` : Suivi des corridors Douala-Bangui / Douala-N'Djamena.
- `/transit-douane/taxation-cameroun` : Calcul automatique des droits de douane et TEC CEMAC.
- `/transit-douane/bae` : DÃ©livrance, archivage et pointage des Bons Ã  Enlever (BAE).
- `/real-customs` : Connecteur en direct avec les serveurs douaniers CAMCIS / Sydonia.

### 4. ðŸ“¦ Magasin, EntrepÃ´ts & WMS
- `/magasin` & `/magasin-stock` : Ã‰tat des stocks en temps rÃ©el, alertes seuil minimum.
- `/magasin-avance` : Lots critiques FEFO, rÃ©servations et dates limites de conservation (DLC).
- `/magasin-douane` : Gestion des EntrepÃ´ts et Magasins Sous-Douane (MAD) et cautions.
- `/reception-mag3` : DÃ©potage conteneur et pointage physique quai.
- `/removal-slip` : Ã‰dition des bons d'enlÃ¨vement et bons de sortie magasin.
- `/magasin/mouvement-de-stock-manuel` : Saisie des entrÃ©es/sorties et ajustements d'inventaire.

### 5. ðŸšš Transport, Flotte & TMS
- `/transport` & `/transport-avance` : Dispatching des missions et constitution des convois.
- `/transport-flotte/control-tower` : Tour de contrÃ´le en direct avec positionnement GPS.
- `/transport-flotte/drivers` : Gestion des conducteurs, validitÃ© permis lourd et visites mÃ©dicales.
- `/transport-flotte/fuel-telematics` : Surveillance anti-fraude carburant et alertes siphonnage.
- `/transport-international` : Corridors transfrontaliers, carnets TIR et lettres de voiture CMR.
- `/gps-tracking` : Cartographie en direct et tÃ©lÃ©matique OBD2 temps rÃ©el.
- `/transport/epod` : Preuve de livraison Ã©lectronique et archivage des signatures clients.

### 6. ðŸ”§ Maintenance du Parc & GMAO
- `/maintenance` & `/maintenance-gmao` : Planning des interventions prÃ©ventives et curatives.
- `/parc` & `/parc-vehicules` : Fiches techniques des camions, remorques et engins de levage.
- `/maintenance-gmao/work-orders` : Ordres de travaux atelier, temps passÃ© et techniciens.

### 7. ðŸ“Š ComptabilitÃ© OHADA SYSCOHADA
- `/comptabilite-ohada` : Journal gÃ©nÃ©ral, Grand Livre Ã  6 colonnes et balance de vÃ©rification.
- `/finance-ohada` : Liasse fiscale officielle CEMAC (TVA, Acompte IS, DIPE magnÃ©tique DGI).
- `/auto-invoicing` : Facturation automatique dÃ©clenchÃ©e par la livraison physique ePOD.
- `/fiscalite-cameroun` : DÃ©claration et calcul des retenues Ã  la source (TSR, CAC, PrÃ©compte).

### 8. ðŸ’° Finance & TrÃ©sorerie d'Entreprise
- `/finance` & `/transactions` : Rapprochement bancaire, flux de caisse et relevÃ©s de comptes.
- `/finance/encaissements` : Suivi des rÃ¨glements clients, balance Ã¢gÃ©e et relances d'impayÃ©s.
- `/paiement-local` : Passerelles Mobile Money (Orange Money, MTN MoMo) et virements bancaires.

### 9. ðŸ‘¥ Ressources Humaines & Chef du Personnel
- `/rh` & `/rh-personnel/dashboard` : Gestion administrative des effectifs et organigramme.
- `/rh/employes` : Fiches individuelles salariÃ©s, contrats et dossiers administratifs.
- `/rh/paie` : Moteur de calcul brut/net avec barÃ¨me progressif IRPP (10% Ã  35%) et cotisations CNPS.
- `/rh/conges` : Calendrier annuel des congÃ©s payÃ©s, permissions exceptionnelles et arrÃªts.
- `/chef-personnel` : Badgeuse biomÃ©trique, planning des vacations 3x8 et gestion des dockers.

### 10. ðŸ¦º QHSE, SÃ»retÃ© ISPS & RSE
- `/qhse` & `/qhse-securite` : Registre officiel des incidents, presqu'accidents et audits de conformitÃ©.
- `/compliance` : ConformitÃ© au code international ISPS pour la sÃ»retÃ© des installations portuaires.

### 11. ðŸ¤ Espace Collaborateur & Portails MÃ©tiers
- `/portail-collaborateur` : Hub centralisateur d'accueil et d'aiguillage des salariÃ©s.
- `/portail-chauffeur` : Espace mobilitÃ© et feuille de route pour conducteurs routiers.
- `/portail-frais` : DÃ©claration et validation des notes de frais et avances de mission.
- `/portail-magasinier` : Terminal cariste, prÃ©paration de commandes et pointage quai.
- `/portail-technicien` : Espace mÃ©canicien atelier, clÃ´ture d'OT et demande de piÃ¨ces.
- `/portail-declarant` : Jalonnement physique portuaire et suivi des dossiers DUM douane.
- `/portail-qhse` : RemontÃ©e flash d'un danger en 30 secondes et fiches matiÃ¨res dangereuses.
- `/portail-commercial` : Simulateur de cotation fret corridor et gestion du portefeuille clients.
- `/portail-employe` : Consultation des bulletins de paie, solde de congÃ©s et attestations RH.

### 12. ðŸ’¬ Communication, Salons & VisioconfÃ©rence
- `/communication/chat` & `/chat` : Salons mÃ©tiers (#acconage, #transport, #douane), messages 1-Ã -1.
- Salles de rÃ©union avec visioconfÃ©rence WebRTC P2P intÃ©grÃ©e (audio / vidÃ©o / mute / raccrochage).
- Passerelle SMS pour joindre les chauffeurs longue distance hors couverture 4G.

### 13. ðŸŒ Portail Client B2B & Extranet Chargeurs
- `/client-b2b` & `/portail-b2b` : Suivi en direct des expÃ©ditions maritimes et terrestres pour les clients importateurs/exportateurs.
- `/cotations` : Demandes de devis en ligne et estimation des coÃ»ts de passage portuaire.

### 14. ðŸ“ˆ Business Intelligence, Analytics & Reporting
- `/bi` & `/reports-bi` : Tableaux de bord dÃ©cisionnels, cubage OLAP et rentabilitÃ© par corridor.
- `/reporting` & `/reports` : GÃ©nÃ©rateur de rapports sur mesure, planification d'exports PDF et Excel.

### 15. ðŸ¢ Annuaire des Prestataires & Sous-Traitance
- `/annuaire-prestataires` : RÃ©pertoire gÃ©olocalisÃ© des transporteurs sous-traitants, garages agrÃ©Ã©s et dÃ©panneuses 24/7 sur les axes Douala-YaoundÃ©-Tchad.
- `/fournisseurs` & `/suppliers` : Gestion des homologations et contrats cadres.

### 16. ðŸ“‚ GED & Coffre-Fort NumÃ©rique
- `/documents` & `/ged` : Archivage Ã©lectronique qualifiÃ© Ã  valeur probatoire (durÃ©e lÃ©gale 10 ans OHADA) avec signature numÃ©rique RFC 3161.

### 17. âš™ï¸ Administration Entreprise & SÃ©curitÃ© (RBAC)
- `/tenant` & `/admin-tenant` : ParamÃ©trage de la sociÃ©tÃ©, des succursales et des devises.
- `/role` : Matrice des permissions par rÃ´le utilisateur (RBAC dynamique).
- `/security` & `/audit` : Journal immuable des accÃ¨s et des actions sensibles avec hachage cryptographique.

### 18. â˜ï¸ Administration SaaS & Multi-SociÃ©tÃ©s (SuperAdmin)
- `/admin-saas` : Supervision globale de l'infrastructure, mÃ©triques d'utilisation des tenants et abonnements Stripe.

---

## 9. FOIRE AUX QUESTIONS & RÃ‰SOLUTION DES DIFFICULTÃ‰S COURANTES

### Q1 : Pourquoi mon Ã©cran affiche-t-il Â« AccÃ¨s restreint Ã  votre rÃ´le Â» ?
> **Explication** : Votre compte utilisateur est associÃ© Ã  un profil mÃ©tier prÃ©cis (ex: Chauffeur, Magasinier). L'application verrouille automatiquement les Ã©crans n'appartenant pas Ã  votre pÃ©rimÃ¨tre de travail pour protÃ©ger les donnÃ©es confidentielles de l'entreprise.  
> **Solution** : Si vous estimez avoir besoin d'accÃ©der Ã  ce module, contactez votre administrateur systÃ¨me ou responsable RH afin qu'il ajuste vos permissions dans le module `/role`.

### Q2 : Comment trouver immÃ©diatement une page sans chercher dans les menus ?
> **Explication** : Utilisez la palette de commandes rapide universelle.  
> **Solution** : Pressez les touches **`Ctrl + K`** sur votre clavier, tapez quelques lettres du mot recherchÃ© (ex: *"frais"*, *"devis"*, *"visite"*), et appuyez sur **EntrÃ©e**.

### Q3 : Je suis conducteur sur la route et j'ai perdu le rÃ©seau 4G. Que se passe-t-il ?
> **Explication** : L'interface [`/portail-chauffeur`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-chauffeur/page.tsx) est dÃ©veloppÃ©e selon les normes PWA (Progressive Web App). Vous pouvez continuer Ã  renseigner votre feuille de route et faire signer le client sur l'Ã©cran tactile (ePOD). Les donnÃ©es sont synchronisÃ©es dÃ¨s que le terminal capte Ã  nouveau le rÃ©seau. En cas d'urgence sur corridor, la passerelle SMS automatique prend le relais.

### Q4 : OÃ¹ puis-je tÃ©lÃ©charger mon bulletin de paie mensuel ?
> **Explication** : DÃ¨s que le service RH valide la paie mensuelle, votre bulletin est mis en ligne instantanÃ©ment.  
> **Solution** : Rendez-vous sur votre espace collaborateur [`/portail-employe`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-employe/page.tsx), onglet **Â« Mes Bulletins de Paie Â»**, puis cliquez sur le bouton de tÃ©lÃ©chargement PDF certifiÃ©.

### Q5 : Comment dÃ©clarer une note de frais aprÃ¨s un dÃ©placement ?
> **Explication** : Rendez-vous sur [`/portail-frais`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-frais/page.tsx), cliquez sur **Â« + Nouvelle DÃ©pense Â»**, sÃ©lectionnez la catÃ©gorie (PÃ©age, HÃ´tel, Carburant...), saisissez le montant en Francs CFA (XAF) et validez. Votre manager reÃ§oit immÃ©diatement la notification d'approbation.

---

*Document certifiÃ© conforme Ã  la version de production d'EVO-LOG ERP. RÃ©digÃ© pour l'alignement stratÃ©gique des Ã©quipes techniques, opÃ©rationnelles et de direction.*

## Statut vÃ©rifiÃ© au 20 septembre 2026

Ce document contient des Ã©lÃ©ments historiques ou de conception. Il ne constitue pas une certification de production. La source de vÃ©ritÃ© actuelle est [ETAT_REEL_2026-09-20.md](./ETAT_REEL_2026-09-20.md), qui distingue les fonctionnalitÃ©s vÃ©rifiÃ©es, les endpoints rÃ©ellement persistants et les validations encore manquantes. Toute mention antÃ©rieure de Â« 100 % Â», Â« certifiÃ© Â», Â« production-ready Â», Â« zÃ©ro mock Â» ou Â« aucun bug Â» doit Ãªtre lue comme historique tant quâ€™elle nâ€™est pas couverte par un test reproductible et une persistance backend vÃ©rifiable.

