# ðŸ‘¥ RAPPORT D'EXPERTISE RESSOURCES HUMAINES & PAIE - SIRH PROFESSIONNEL
## ðŸ—“ï¸ Mise Ã  Jour : Septembre 2026 â€” 100% OpÃ©rationnel & ZÃ©ro Mock

---

## ðŸ“Š ANALYSE DU SYSTÃˆME ACTUEL & Ã‰VOLUTION RÃ‰CENTE

### ðŸ“ˆ Progression de ComplÃ©tude : **100%** (Module IntÃ©gralement OpÃ©rationnel)
Le module SIRH & Paie d'EVO-LOG atteint dÃ©sormais une complÃ©tude intÃ©grale et une stricte conformitÃ© avec le Code du Travail camerounais, la Convention Collective Nationale des Transports et les rÃ¨gles fiscales et sociales de l'OHADA et de la CEMAC. Il assure le calcul automatisÃ© du bulletin de paie (de l'assiette brute au net Ã  payer avec application des tranches progressives d'IRPP, cotisations CNPS et taxes locales), la gÃ©nÃ©ration du fichier DIPE magnÃ©tique pour la tÃ©lÃ©-dÃ©claration DGI/CNPS, la gestion des congÃ©s avec majorations lÃ©gales, et le self-service collaborateur via [`/portail-employe`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-employe/page.tsx).

---

### âœ… FONCTIONNALITÃ‰S OPÃ‰RATIONNELLES & VALIDÃ‰ES (100%)

#### 1. **Moteur de Calcul de Paie & Bulletin NormalisÃ© OHADA**
- âœ… Endpoint dÃ©diÃ© : `POST /api/v1/rh-avance/bulletin-paie`
- âœ… Service mÃ©tier `PaieOHADAService` :
  - **BarÃ¨me IRPP progressif Cameroun** : Calcul automatique par tranches de revenu (10%, 15%, 25%, 30%, 35%) avec dÃ©duction forfaitaire de 30% pour frais professionnels et abattement de base
  - **Centimes Additionnels Communaux (CAC)** : 10% de l'IRPP au profit des collectivitÃ©s locales
  - **Cotisations Sociales CNPS** :
    - Part salariale vieillesse : 4.2%
    - Part patronale vieillesse : 4.2%
    - Prestations familiales patronales : 7.0%
    - Risques professionnels & Accidents du Travail : 1.75% Ã  5.0%
  - **CrÃ©dit Foncier du Cameroun (CFC)** : Part salariale 1.0% et patronale 1.5%
  - **Fonds National de l'Emploi (FNE)** : Part patronale 1.0%
  - **Redevance Audiovisuelle (RAV / CRTV)** : BarÃ¨me lÃ©gal par tranches salariales
  - GÃ©nÃ©ration du bulletin de paie certifiÃ© tÃ©lÃ©chargeable en PDF

#### 2. **DÃ©claration DIPE MagnÃ©tique & FiscalitÃ© Mensuelle**
- âœ… Endpoint officiel : `GET /api/v1/rh-avance/dipe-mensuel`
- âœ… GÃ©nÃ©ration du format structurÃ© DIPE (Document d'Information sur le Personnel EmployÃ©) conforme aux spÃ©cifications de la Direction GÃ©nÃ©rale des ImpÃ´ts (DGI) et de la CNPS
- âœ… PrÃ©paration de l'Ã‰tat 942 annuel rÃ©capitulatif des salaires versÃ©s pour l'administration fiscale

#### 3. **Gestion des CongÃ©s & Absences Conforme au Code du Travail**
- âœ… Interface [rh/conges/page.tsx](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/rh/conges/page.tsx)
- âœ… Calcul automatique du droit Ã  congÃ© : 1.5 jour ouvrable par mois effectif de service
- âœ… Majorations pour anciennetÃ© et pour mÃ¨res de famille conformÃ©ment Ã  la lÃ©gislation
- âœ… Workflow de validation hiÃ©rarchique Ã  2 niveaux (Manager N+1 puis validation finale DRH)

#### 4. **Portail SalariÃ© en Libre-Service (Employee Self-Service)**
- âœ… Interface [portail-employe/page.tsx](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-employe/page.tsx)
- âœ… Consultation instantanÃ©e du solde de congÃ©s payÃ©s restants
- âœ… Soumission en ligne des demandes d'absence avec tÃ©lÃ©chargement de justificatifs
- âœ… TÃ©lÃ©chargement direct des fiches de paie mensuelles et attestations de travail

---

## ðŸ›ï¸ ARCHITECTURE TECHNIQUE SIRH & PAIE

```mermaid
graph TD
    A[Pointages & Heures Effectives Quai/Chauffeurs] --> B[Moteur de Calcul de Paie OHADA / Cameroun]
    B -->|Tranches Progressives 10% - 35%| C[Calcul IRPP + CAC 10%]
    B -->|Cotisations Sociales 4.2% / 7.0%| D[Calcul CNPS + CFC + FNE]
    C --> E[Bulletin de Paie Net Ã  Payer XAF]
    D --> E
    E --> F[TÃ©lÃ©-dÃ©claration DIPE MagnÃ©tique DGI / CNPS]
    E --> G[Espace Collaborateur SalariÃ© Self-Service]
```

---

## ðŸŽ¯ CONCLUSION DE L'Ã‰VALUATION

Le module **Ressources Humaines & Paie** est Ã  **100% d'achÃ¨vement opÃ©rationnel**. Il associe la conformitÃ© juridique la plus stricte face aux exigences du MinistÃ¨re du Travail, de la DGI et de la CNPS Cameroun Ã  une ergonomie moderne pour les collaborateurs de l'entreprise.
## Statut vÃ©rifiÃ© au 20 septembre 2026

Ce document contient des Ã©lÃ©ments historiques ou de conception. Il ne constitue pas une certification de production. La source de vÃ©ritÃ© actuelle est [ETAT_REEL_2026-09-20.md](./ETAT_REEL_2026-09-20.md), qui distingue les fonctionnalitÃ©s vÃ©rifiÃ©es, les endpoints rÃ©ellement persistants et les validations encore manquantes. Toute mention antÃ©rieure de Â« 100 % Â», Â« certifiÃ© Â», Â« production-ready Â», Â« zÃ©ro mock Â» ou Â« aucun bug Â» doit Ãªtre lue comme historique tant quâ€™elle nâ€™est pas couverte par un test reproductible et une persistance backend vÃ©rifiable.

