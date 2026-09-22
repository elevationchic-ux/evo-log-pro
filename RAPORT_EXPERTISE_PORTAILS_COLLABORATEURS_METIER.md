# 🤝 RAPPORT D'EXPERTISE : 8 PORTAILS COLLABORATEURS MÉTIER & HUB CENTRALISÉ
## 🗓️ Mise à Jour : Septembre 2026 — Intégration UX/UI & Optimisations Terrain

> Les chiffres et formulations de raccordement total sont historiques. Les portails nécessitent une validation API, tenant, accessibilité et charge avant toute certification. Voir [ETAT_REEL_2026-09-19.md](./ETAT_REEL_2026-09-19.md).

---

## 🎯 RÉSUMÉ EXÉCUTIF

Les **8 portails collaborateurs métier** constituent le cœur opérationnel d'EVO-LOG pour les équipes terrain. Conçus pour éliminer la friction entre le collaborateur de première ligne et le système d'information, ils sont désormais enrichis des recommandations UX/UI issues de l'audit impartial Novice vs Expert.

### Statistiques Clés
- **8 portails + 1 hub** : raccordement présent sur les parcours vérifiés, couverture globale non certifiée
- **Nouveaux composants UX** : `TermDefinition`, `HelpAndShortcutsModal`, `AppBreadcrumb`, `DestructiveConfirmModal`
- **Optimisations mobiles** : `inputMode` sur tous les champs de saisie numériques terrain
- **Build validé** : Exit code 0, 323 routes, 0 erreur TypeScript

---

## 🗺️ HUB COLLABORATEUR CENTRALISÉ (`/portail-collaborateur`)

**Accès universel pour tous les salariés authentifiés.**

Le Hub est le carrefour d'orientation vers les 8 espaces métiers selon le rôle RBAC de l'utilisateur. Il présente en grille tactile les portails disponibles avec indicateurs de statut de session et badges de sécurité.

**Nouveautés UX Intégrées :**
- Fil d'Ariane `AppBreadcrumb` visible dans le sous-bandeau de navigation.
- Bouton d'aide `?` dans l'en-tête ouvrant le Centre d'Aide universel.

---

## 🚚 1. PORTAIL CHAUFFEUR ROUTIER (`/portail-chauffeur`)

**Rôles** : `CHAUFFEUR`, `CONDUCTEUR`, `TRANSPORTEUR`, `DISPATCHER`, `ADMIN`

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Tournée & Missions** | Ordres de mission actifs, statut temps réel, actions terrain | `/api/v1/transport/missions` |
| **Inspection Véhicule** | Checklist 8 points (freins, pneus, feux, extincteur, niveaux, permis) | Enregistrement local |
| **Saisie Carburant** | Litrage, prix/litre XAF, station, kilométrage compteur | `/api/v1/transport/fuel` |
| **ePOD Tactile** | Signature canvas + nom réceptionnaire + réserves éventuelles | `/api/v1/transport/epod` |
| **SOS Incident** | Alerte prioritaire vers tour de contrôle (panne, accident, barrage) | `/api/v1/transport/incidents` |

### Améliorations UX Appliquées
- ✅ `inputMode="decimal"` sur champ **Volume carburant (litres)** → clavier décimal mobile
- ✅ `inputMode="numeric"` sur champs **Prix/litre XAF** et **Compteur Km** → pavé numérique mobile
- ✅ En-tête avec Fil d'Ariane et bouton `?` pour guide d'utilisation

### T-Code Accès Rapide
```
T-Code : KDRV_TRN → /portail-chauffeur
```

---

## 💼 2. PORTAIL FRAIS & AVANCES (`/portail-frais`)

**Rôles** : Universel (tous employés) + Workflow Manager/Comptabilité

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Mes Notes de Frais** | Historique avec statuts (Soumis, Validé, Rejeté) | `/api/v1/frais-missions` |
| **Nouvelle Dépense** | Péages, Hôtel, Carburant, Restauration, Manutention, PDR | `/api/v1/frais-missions` |
| **Demandes d'Avances** | Avances pour missions corridors CEMAC | `/api/v1/frais-missions/avances` |
| **Validation Hiérarchique** | Approbation/Rejet manager avec motif | `/api/v1/frais-missions/validate` |
| **KPIs Live** | Total engagé, validé, en attente, solde net | `/api/v1/frais-missions/stats` |

### Améliorations UX Appliquées
- ✅ `inputMode="numeric"` sur champ **Montant (XAF)** → pavé numérique mobile
- ✅ `inputMode="numeric"` sur champ **Montant Avance demandée (XAF)**

### T-Code Accès Rapide
```
T-Code : KEXP_FEE → /portail-frais
```

---

## 📦 3. PORTAIL MAGASINIER & QUAI (`/portail-magasinier`)

**Rôles** : `MAGASINIER`, `MANUTENTIONNAIRE`, `LOGISTICIEN`, `CHEF_MAGASIN`, `ADMIN`

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Picking FEFO/FIFO** | Ordres de sortie avec emplacement 3D, pointage ligne par ligne | `/api/v1/magasin/picking` |
| **Réceptions Quai** | Dépotage conteneurs, contrôle colis, intégrité scellés | `/api/v1/reception-mag3` |
| **Inventaire Tournant** | Comptage aveugle sur emplacements assignés | `/api/v1/magasin/inventaire` |
| **Checklist Engin** | Auto-contrôle sécurité chariot élévateur/gerbeur | Local + enregistrement |

### Améliorations UX Appliquées
- ✅ **TermDefinition** actif sur labels **FEFO** et **FIFO** dans l'interface de picking (définitions accessibles au survol)
- ✅ `inputMode="numeric"` sur saisie **Quantité comptée** lors des inventaires
- ✅ Intégration `import { TermDefinition } from '@/components/shared/TermDefinition'`

### T-Code Accès Rapide
```
T-Code : KWMS_OP → /portail-magasinier
```

---

## 🔧 4. PORTAIL TECHNICIEN GMAO (`/portail-technicien`)

**Rôles** : `TECHNICIEN`, `MECANICIEN`, `CHEF_ATELIER`, `MAINTENANCE`, `ADMIN`

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Ordres de Travaux (OT)** | Interventions curatives et préventives, temps passé | `/api/v1/maintenance/work-orders` |
| **Compte-Rendu Atelier** | Rapport d'intervention avec pièces remplacées | `/api/v1/maintenance/reports` |
| **Demande PDR** | Réquisition pièces détachées depuis le stock WMS | `/api/v1/maintenance/spare-parts` |
| **Parc & État Véhicules** | Fiches techniques VIN, kilométrage, disponibilité | `/api/v1/maintenance/vehicles` |

### T-Code Accès Rapide
```
T-Code : KTEC_OT → /portail-technicien
```

---

## 🏛️ 5. PORTAIL DÉCLARANT DOUANE (`/portail-declarant`)

**Rôles** : `DECLARANT`, `TRANSITAIRE`, `CHEF_TRANSIT`, `ADMIN`

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Dossiers DUM** | Liste des déclarations actives avec jalonnement | `/api/v1/transit/declarations` |
| **Jalonnement Physique** | Milestones quai : Dépôt DUM → Scanner → Visite → BAE | `/api/v1/transit/milestones` |
| **Upload Documents** | Dépôt DUM, factures, certificats d'origine | `/api/v1/documents` |
| **Alertes Litige** | Contentieux sur valeur, régimes suspensifs | `/api/v1/transit/alerts` |

### T-Code Accès Rapide
```
T-Code : KCST_FLD → /portail-declarant
```

---

## 🦺 6. PORTAIL QHSE & SÉCURITÉ (`/portail-qhse`)

**Rôles** : Universel — Tous les collaborateurs peuvent signaler un danger

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Signalement Flash** | Déclaration danger/Near-Miss en 30 secondes | `/api/v1/qhse/incidents` |
| **Checklist PPE** | Vérification des Équipements de Protection Individuelle | Local |
| **Fiches IMDG** | Consultation SDS matières dangereuses | `/api/v1/qhse/imdg` |
| **Work Permits** | Permis de travail électroniques (feu, hauteur, cuve) | `/api/v1/qhse/permits` |

### T-Code Accès Rapide
```
T-Code : KQHS_ALR → /portail-qhse
```

---

## 📈 7. PORTAIL COMMERCIAL CEMAC (`/portail-commercial`)

**Rôles** : `COMMERCIAL`, `RESPONSABLE_COMMERCIAL`, `ADMIN`

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Simulateur Cotation** | Devis fret corridor Douala-Bangui / Douala-N'Djamena | `/api/v1/cotations` |
| **Pipeline CRM** | Opportunités par stade, taux de transformation | `/api/v1/clients` |
| **Commissions** | Calcul des primes commerciales sur CA réalisé | `/api/v1/finance` |

### T-Code Accès Rapide
```
T-Code : KSAL_CRM → /portail-commercial
```

---

## 👤 8. PORTAIL SALARIÉ RH (`/portail-employe`)

**Rôles** : Universel — Tous les salariés

### Fonctionnalités
| Module | Description | API Backend |
|:---|:---|:---|
| **Bulletins de Paie PDF** | Téléchargement des fiches de paie mensuelle OHADA | `/api/v1/rh/payslips` |
| **Solde de Congés** | Jours acquis, pris, reliquat annuel | `/api/v1/rh/leaves` |
| **Attestations RH** | Attestation de travail, de salaire, d'emploi | `/api/v1/documents` |
| **Mon Dossier** | Contrat, grade, ancienneté, coordonnées | `/api/v1/rh/employees` |

### T-Code Accès Rapide
```
T-Code : KEMP_PAY → /portail-employe
```

---

## 🆕 NOUVEAUX COMPOSANTS UX SHARED (SEPTEMBRE 2026)

Quatre composants ont été développés et intégrés suite à l'audit ergonomique :

### Pour les Novices
- **`TermDefinition`** : Infobulles interactives sur 22 sigles métier. Premier déploiement actif sur FEFO/FIFO dans `/portail-magasinier`.
- **`HelpAndShortcutsModal`** : Centre d'aide 3 onglets (raccourcis clavier, glossaire, guide 3 règles d'or). Activable via `?`, `F1`, ou bouton en-tête.
- **`AppBreadcrumb`** : Fil d'Ariane dynamique avec labels français dans tous les écrans.

### Pour les Experts
- **`DestructiveConfirmModal`** : Dialogue de confirmation légale pour les scellements OHADA.
- **`DataTable` Rénové** : Mode compact (32px), sticky headers, barre d'actions de masse, export CSV en 1 clic.

---

*Rapport historique — Septembre 2026 — validation globale encore requise*
