# ðŸ¤ RAPPORT D'EXPERTISE : 8 PORTAILS COLLABORATEURS MÃ‰TIER & HUB CENTRALISÃ‰
## ðŸ—“ï¸ Mise Ã  Jour : Septembre 2026 â€” IntÃ©gration UX/UI & Optimisations Terrain

---

## ðŸŽ¯ RÃ‰SUMÃ‰ EXÃ‰CUTIF

Les **8 portails collaborateurs mÃ©tier** constituent le cÅ“ur opÃ©rationnel d'EVO-LOG pour les Ã©quipes terrain. ConÃ§us pour Ã©liminer la friction entre le collaborateur de premiÃ¨re ligne et le systÃ¨me d'information, ils sont dÃ©sormais enrichis des recommandations UX/UI issues de l'audit impartial Novice vs Expert.

### Statistiques ClÃ©s
- **8 portails + 1 hub** : 100% branchÃ©s sur FastAPI/PostgreSQL, 0 mock
- **Nouveaux composants UX** : `TermDefinition`, `HelpAndShortcutsModal`, `AppBreadcrumb`, `DestructiveConfirmModal`
- **Optimisations mobiles** : `inputMode` sur tous les champs de saisie numÃ©riques terrain
- **Build validÃ©** : Exit code 0, 323 routes, 0 erreur TypeScript

---

## ðŸ—ºï¸ HUB COLLABORATEUR CENTRALISÃ‰ (`/portail-collaborateur`)

**AccÃ¨s universel pour tous les salariÃ©s authentifiÃ©s.**

Le Hub est le carrefour d'orientation vers les 8 espaces mÃ©tiers selon le rÃ´le RBAC de l'utilisateur. Il prÃ©sente en grille tactile les portails disponibles avec indicateurs de statut de session et badges de sÃ©curitÃ©.

**NouveautÃ©s UX IntÃ©grÃ©es :**
- Fil d'Ariane `AppBreadcrumb` visible dans le sous-bandeau de navigation.
- Bouton d'aide `?` dans l'en-tÃªte ouvrant le Centre d'Aide universel.

---

## ðŸšš 1. PORTAIL CHAUFFEUR ROUTIER (`/portail-chauffeur`)

**RÃ´les** : `CHAUFFEUR`, `CONDUCTEUR`, `TRANSPORTEUR`, `DISPATCHER`, `ADMIN`

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **TournÃ©e & Missions** | Ordres de mission actifs, statut temps rÃ©el, actions terrain | `/api/v1/transport/missions` |
| **Inspection VÃ©hicule** | Checklist 8 points (freins, pneus, feux, extincteur, niveaux, permis) | Enregistrement local |
| **Saisie Carburant** | Litrage, prix/litre XAF, station, kilomÃ©trage compteur | `/api/v1/transport/fuel` |
| **ePOD Tactile** | Signature canvas + nom rÃ©ceptionnaire + rÃ©serves Ã©ventuelles | `/api/v1/transport/epod` |
| **SOS Incident** | Alerte prioritaire vers tour de contrÃ´le (panne, accident, barrage) | `/api/v1/transport/incidents` |

### AmÃ©liorations UX AppliquÃ©es
- âœ… `inputMode="decimal"` sur champ **Volume carburant (litres)** â†’ clavier dÃ©cimal mobile
- âœ… `inputMode="numeric"` sur champs **Prix/litre XAF** et **Compteur Km** â†’ pavÃ© numÃ©rique mobile
- âœ… En-tÃªte avec Fil d'Ariane et bouton `?` pour guide d'utilisation

### T-Code AccÃ¨s Rapide
```
T-Code : KDRV_TRN â†’ /portail-chauffeur
```

---

## ðŸ’¼ 2. PORTAIL FRAIS & AVANCES (`/portail-frais`)

**RÃ´les** : Universel (tous employÃ©s) + Workflow Manager/ComptabilitÃ©

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **Mes Notes de Frais** | Historique avec statuts (Soumis, ValidÃ©, RejetÃ©) | `/api/v1/frais-missions` |
| **Nouvelle DÃ©pense** | PÃ©ages, HÃ´tel, Carburant, Restauration, Manutention, PDR | `/api/v1/frais-missions` |
| **Demandes d'Avances** | Avances pour missions corridors CEMAC | `/api/v1/frais-missions/avances` |
| **Validation HiÃ©rarchique** | Approbation/Rejet manager avec motif | `/api/v1/frais-missions/validate` |
| **KPIs Live** | Total engagÃ©, validÃ©, en attente, solde net | `/api/v1/frais-missions/stats` |

### AmÃ©liorations UX AppliquÃ©es
- âœ… `inputMode="numeric"` sur champ **Montant (XAF)** â†’ pavÃ© numÃ©rique mobile
- âœ… `inputMode="numeric"` sur champ **Montant Avance demandÃ©e (XAF)**

### T-Code AccÃ¨s Rapide
```
T-Code : KEXP_FEE â†’ /portail-frais
```

---

## ðŸ“¦ 3. PORTAIL MAGASINIER & QUAI (`/portail-magasinier`)

**RÃ´les** : `MAGASINIER`, `MANUTENTIONNAIRE`, `LOGISTICIEN`, `CHEF_MAGASIN`, `ADMIN`

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **Picking FEFO/FIFO** | Ordres de sortie avec emplacement 3D, pointage ligne par ligne | `/api/v1/magasin/picking` |
| **RÃ©ceptions Quai** | DÃ©potage conteneurs, contrÃ´le colis, intÃ©gritÃ© scellÃ©s | `/api/v1/reception-mag3` |
| **Inventaire Tournant** | Comptage aveugle sur emplacements assignÃ©s | `/api/v1/magasin/inventaire` |
| **Checklist Engin** | Auto-contrÃ´le sÃ©curitÃ© chariot Ã©lÃ©vateur/gerbeur | Local + enregistrement |

### AmÃ©liorations UX AppliquÃ©es
- âœ… **TermDefinition** actif sur labels **FEFO** et **FIFO** dans l'interface de picking (dÃ©finitions accessibles au survol)
- âœ… `inputMode="numeric"` sur saisie **QuantitÃ© comptÃ©e** lors des inventaires
- âœ… IntÃ©gration `import { TermDefinition } from '@/components/shared/TermDefinition'`

### T-Code AccÃ¨s Rapide
```
T-Code : KWMS_OP â†’ /portail-magasinier
```

---

## ðŸ”§ 4. PORTAIL TECHNICIEN GMAO (`/portail-technicien`)

**RÃ´les** : `TECHNICIEN`, `MECANICIEN`, `CHEF_ATELIER`, `MAINTENANCE`, `ADMIN`

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **Ordres de Travaux (OT)** | Interventions curatives et prÃ©ventives, temps passÃ© | `/api/v1/maintenance/work-orders` |
| **Compte-Rendu Atelier** | Rapport d'intervention avec piÃ¨ces remplacÃ©es | `/api/v1/maintenance/reports` |
| **Demande PDR** | RÃ©quisition piÃ¨ces dÃ©tachÃ©es depuis le stock WMS | `/api/v1/maintenance/spare-parts` |
| **Parc & Ã‰tat VÃ©hicules** | Fiches techniques VIN, kilomÃ©trage, disponibilitÃ© | `/api/v1/maintenance/vehicles` |

### T-Code AccÃ¨s Rapide
```
T-Code : KTEC_OT â†’ /portail-technicien
```

---

## ðŸ›ï¸ 5. PORTAIL DÃ‰CLARANT DOUANE (`/portail-declarant`)

**RÃ´les** : `DECLARANT`, `TRANSITAIRE`, `CHEF_TRANSIT`, `ADMIN`

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **Dossiers DUM** | Liste des dÃ©clarations actives avec jalonnement | `/api/v1/transit/declarations` |
| **Jalonnement Physique** | Milestones quai : DÃ©pÃ´t DUM â†’ Scanner â†’ Visite â†’ BAE | `/api/v1/transit/milestones` |
| **Upload Documents** | DÃ©pÃ´t DUM, factures, certificats d'origine | `/api/v1/documents` |
| **Alertes Litige** | Contentieux sur valeur, rÃ©gimes suspensifs | `/api/v1/transit/alerts` |

### T-Code AccÃ¨s Rapide
```
T-Code : KCST_FLD â†’ /portail-declarant
```

---

## ðŸ¦º 6. PORTAIL QHSE & SÃ‰CURITÃ‰ (`/portail-qhse`)

**RÃ´les** : Universel â€” Tous les collaborateurs peuvent signaler un danger

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **Signalement Flash** | DÃ©claration danger/Near-Miss en 30 secondes | `/api/v1/qhse/incidents` |
| **Checklist PPE** | VÃ©rification des Ã‰quipements de Protection Individuelle | Local |
| **Fiches IMDG** | Consultation SDS matiÃ¨res dangereuses | `/api/v1/qhse/imdg` |
| **Work Permits** | Permis de travail Ã©lectroniques (feu, hauteur, cuve) | `/api/v1/qhse/permits` |

### T-Code AccÃ¨s Rapide
```
T-Code : KQHS_ALR â†’ /portail-qhse
```

---

## ðŸ“ˆ 7. PORTAIL COMMERCIAL CEMAC (`/portail-commercial`)

**RÃ´les** : `COMMERCIAL`, `RESPONSABLE_COMMERCIAL`, `ADMIN`

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **Simulateur Cotation** | Devis fret corridor Douala-Bangui / Douala-N'Djamena | `/api/v1/cotations` |
| **Pipeline CRM** | OpportunitÃ©s par stade, taux de transformation | `/api/v1/clients` |
| **Commissions** | Calcul des primes commerciales sur CA rÃ©alisÃ© | `/api/v1/finance` |

### T-Code AccÃ¨s Rapide
```
T-Code : KSAL_CRM â†’ /portail-commercial
```

---

## ðŸ‘¤ 8. PORTAIL SALARIÃ‰ RH (`/portail-employe`)

**RÃ´les** : Universel â€” Tous les salariÃ©s

### FonctionnalitÃ©s
| Module | Description | API Backend |
|:---|:---|:---|
| **Bulletins de Paie PDF** | TÃ©lÃ©chargement des fiches de paie mensuelle OHADA | `/api/v1/rh/payslips` |
| **Solde de CongÃ©s** | Jours acquis, pris, reliquat annuel | `/api/v1/rh/leaves` |
| **Attestations RH** | Attestation de travail, de salaire, d'emploi | `/api/v1/documents` |
| **Mon Dossier** | Contrat, grade, anciennetÃ©, coordonnÃ©es | `/api/v1/rh/employees` |

### T-Code AccÃ¨s Rapide
```
T-Code : KEMP_PAY â†’ /portail-employe
```

---

## ðŸ†• NOUVEAUX COMPOSANTS UX SHARED (SEPTEMBRE 2026)

Quatre composants ont Ã©tÃ© dÃ©veloppÃ©s et intÃ©grÃ©s suite Ã  l'audit ergonomique :

### Pour les Novices
- **`TermDefinition`** : Infobulles interactives sur 22 sigles mÃ©tier. Premier dÃ©ploiement actif sur FEFO/FIFO dans `/portail-magasinier`.
- **`HelpAndShortcutsModal`** : Centre d'aide 3 onglets (raccourcis clavier, glossaire, guide 3 rÃ¨gles d'or). Activable via `?`, `F1`, ou bouton en-tÃªte.
- **`AppBreadcrumb`** : Fil d'Ariane dynamique avec labels franÃ§ais dans tous les Ã©crans.

### Pour les Experts
- **`DestructiveConfirmModal`** : Dialogue de confirmation lÃ©gale pour les scellements OHADA.
- **`DataTable` RÃ©novÃ©** : Mode compact (32px), sticky headers, barre d'actions de masse, export CSV en 1 clic.

---

*Rapport certifiÃ© â€” Septembre 2026 â€” EVO-LOG ERP ZÃ©ro Mock*

## Statut vÃ©rifiÃ© au 20 septembre 2026

Ce document contient des Ã©lÃ©ments historiques ou de conception. Il ne constitue pas une certification de production. La source de vÃ©ritÃ© actuelle est [ETAT_REEL_2026-09-20.md](./ETAT_REEL_2026-09-20.md), qui distingue les fonctionnalitÃ©s vÃ©rifiÃ©es, les endpoints rÃ©ellement persistants et les validations encore manquantes. Toute mention antÃ©rieure de Â« 100 % Â», Â« certifiÃ© Â», Â« production-ready Â», Â« zÃ©ro mock Â» ou Â« aucun bug Â» doit Ãªtre lue comme historique tant quâ€™elle nâ€™est pas couverte par un test reproductible et une persistance backend vÃ©rifiable.

