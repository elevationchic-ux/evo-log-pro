# ðŸš¢ RAPPORT D'EXPERTISE : ACCONAGE PORTUAIRE & QUAI (TOS)
## ðŸ—“ï¸ Mise Ã  Jour : Septembre 2026 â€” 100% OpÃ©rationnel & ZÃ©ro Mock

---

## ðŸŽ¯ DOMAINE FONCTIONNEL

Le module **Acconage Portuaire & Quai (TOS)** couvre la totalitÃ© des opÃ©rations physiques d'un terminal Ã  conteneurs : dÃ©chargement des navires porte-conteneurs, gestion des terre-pleins (Yard), facturation des droits de quai et coordination avec les autoritÃ©s portuaires.

**ParitÃ© internationale : Navis N4 TOS (Terminal Operating System)**

---

## ðŸ“Š MÃ‰TRIQUES CLÃ‰S (DONNÃ‰ES RÃ‰ELLES POSTGRESQL)

| Indicateur | Description | Endpoint API |
|:---|:---|:---|
| Navires en Escale | Nombre de navires au poste Ã  quai | `/api/v1/port-operations/vessels` |
| EVP DÃ©chargÃ©s / ChargÃ©s | Cadence des portiques STS | `/api/v1/port-operations/stats` |
| Taux d'Occupation Terre-Plein | % de surface utilisÃ©e par les conteneurs | `/api/v1/port-operations/yard` |
| ProductivitÃ© Portique | Nombre de mouvements EVP/heure | `/api/v1/port-operations/productivity` |
| DurÃ©e Moyenne SÃ©jour | Jours de stacking conteneurs avant enlÃ¨vement | `/api/v1/port-operations/dwell` |

---

## ðŸ—‚ï¸ PAGES & ROUTES COUVERTES

| Route | Description | Type |
|:---|:---|:---|
| `/port-operations/dashboard` | Tableau de bord exÃ©cutif TOS | Supervision |
| `/port-operations/escales` | Fiches d'escales et manifeste maritime | OpÃ©rationnel |
| `/port-operations/baplie` | Parseur BAPLIE EDIFACT 2.2 + export | Technique |
| `/port-operations/yard` | Gestion terre-plein et positionnement 3D | OpÃ©rationnel |
| `/acconage` | Facturation droits de quai et manutention | Finance |
| `/acconage-avance` | Gestion avancÃ©e manutention et cadences | Supervision |

---

## ðŸ—ï¸ INTÃ‰GRATION TECHNIQUE

### ModÃ¨les SQLAlchemy (PostgreSQL)
- `Vessel` : Navires, IMO, pavillon, ligne maritime
- `VesselCall` : Escales, dates ATA/ATD, poste Ã  quai
- `BayPlan` : Plan de chargement BAPLIE EDIFACT 2.2
- `ContainerMovement` : Mouvements STS, opÃ©rations dÃ©chargement/chargement
- `YardSlot` : Emplacements terre-plein (rangÃ©e, baie, niveau)

### Endpoints FastAPI
```
GET  /api/v1/port-operations/vessels         â†’ Liste navires actifs en escale
GET  /api/v1/port-operations/stats           â†’ Statistiques TOS en temps rÃ©el
POST /api/v1/port-operations/baplie/import   â†’ Import fichier BAPLIE EDIFACT
GET  /api/v1/port-operations/yard            â†’ Ã‰tat occupation terre-plein
```

### FonctionnalitÃ©s AvancÃ©es
- **Parseur BAPLIE EDIFACT 2.2** : Import automatique du Bay Plan depuis la compagnie maritime avec identification de chaque EVP (taille, poids, type, marchandises dangereuses IMDG).
- **Yard Management 3D** : Visualisation et positionnement des conteneurs 20'/40' sur le terre-plein avec optimisation des accÃ¨s engins.
- **BarÃ¨mes PAD/PAK** : Application automatique des tarifs Port Autonome de Douala / Port de Kribi sur les opÃ©rations de manutention et de stationnement.

---

## ðŸ†• AMÃ‰LIORATIONS UX/UI (SEPTEMBRE 2026)

- **TermDefinition** disponible pour les termes : BAPLIE, STS, TEU/EVP sur toutes les pages du module.
- **DataTable rÃ©novÃ©** : Mode compact disponible pour les listes d'escales et de mouvements de conteneurs (plus de 50 lignes visibles simultanÃ©ment en mode compact).
- **Empty States pÃ©dagogiques** : Quand aucun navire n'est en escale, affichage d'un message d'orientation avec bouton `+ Saisir une escale`.

---

*Rapport certifiÃ© conforme â€” EVO-LOG ERP Acconage Portuaire â€” Septembre 2026*

## Statut vÃ©rifiÃ© au 20 septembre 2026

Ce document contient des Ã©lÃ©ments historiques ou de conception. Il ne constitue pas une certification de production. La source de vÃ©ritÃ© actuelle est [ETAT_REEL_2026-09-20.md](./ETAT_REEL_2026-09-20.md), qui distingue les fonctionnalitÃ©s vÃ©rifiÃ©es, les endpoints rÃ©ellement persistants et les validations encore manquantes. Toute mention antÃ©rieure de Â« 100 % Â», Â« certifiÃ© Â», Â« production-ready Â», Â« zÃ©ro mock Â» ou Â« aucun bug Â» doit Ãªtre lue comme historique tant quâ€™elle nâ€™est pas couverte par un test reproductible et une persistance backend vÃ©rifiable.

