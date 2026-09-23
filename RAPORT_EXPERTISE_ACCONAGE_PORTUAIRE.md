# 🚢 RAPPORT D'EXPERTISE : ACCONAGE PORTUAIRE & QUAI (TOS)
## 🗓️ Mise à Jour : Septembre 2026  100% Opérationnel & Zéro Mock

---

## 🎯 DOMAINE FONCTIONNEL

Le module **Acconage Portuaire & Quai (TOS)** couvre la totalité des opérations physiques d'un terminal à conteneurs : déchargement des navires porte-conteneurs, gestion des terre-pleins (Yard), facturation des droits de quai et coordination avec les autorités portuaires.

**Parité internationale : Navis N4 TOS (Terminal Operating System)**

---

## 📊 MÉTRIQUES CLÉS (DONNÉES RÉELLES POSTGRESQL)

| Indicateur | Description | Endpoint API |
|:---|:---|:---|
| Navires en Escale | Nombre de navires au poste à quai | `/api/v1/port-operations/vessels` |
| EVP Déchargés / Chargés | Cadence des portiques STS | `/api/v1/port-operations/stats` |
| Taux d'Occupation Terre-Plein | % de surface utilisée par les conteneurs | `/api/v1/port-operations/yard` |
| Productivité Portique | Nombre de mouvements EVP/heure | `/api/v1/port-operations/productivity` |
| Durée Moyenne Séjour | Jours de stacking conteneurs avant enlèvement | `/api/v1/port-operations/dwell` |

---

## 🗂️ PAGES & ROUTES COUVERTES

| Route | Description | Type |
|:---|:---|:---|
| `/port-operations/dashboard` | Tableau de bord exécutif TOS | Supervision |
| `/port-operations/escales` | Fiches d'escales et manifeste maritime | Opérationnel |
| `/port-operations/baplie` | Parseur BAPLIE EDIFACT 2.2 + export | Technique |
| `/port-operations/yard` | Gestion terre-plein et positionnement 3D | Opérationnel |
| `/acconage` | Facturation droits de quai et manutention | Finance |
| `/acconage-avance` | Gestion avancée manutention et cadences | Supervision |

---

## 🏗️ INTÉGRATION TECHNIQUE

### Modèles SQLAlchemy (PostgreSQL)
- `Vessel` : Navires, IMO, pavillon, ligne maritime
- `VesselCall` : Escales, dates ATA/ATD, poste à quai
- `BayPlan` : Plan de chargement BAPLIE EDIFACT 2.2
- `ContainerMovement` : Mouvements STS, opérations déchargement/chargement
- `YardSlot` : Emplacements terre-plein (rangée, baie, niveau)

### Endpoints FastAPI
```
GET  /api/v1/port-operations/vessels         → Liste navires actifs en escale
GET  /api/v1/port-operations/stats           → Statistiques TOS en temps réel
POST /api/v1/port-operations/baplie/import   → Import fichier BAPLIE EDIFACT
GET  /api/v1/port-operations/yard            → État occupation terre-plein
```

### Fonctionnalités Avancées
- **Parseur BAPLIE EDIFACT 2.2** : Import automatique du Bay Plan depuis la compagnie maritime avec identification de chaque EVP (taille, poids, type, marchandises dangereuses IMDG).
- **Yard Management 3D** : Visualisation et positionnement des conteneurs 20'/40' sur le terre-plein avec optimisation des accès engins.
- **Barèmes PAD/PAK** : Application automatique des tarifs Port Autonome de Douala / Port de Kribi sur les opérations de manutention et de stationnement.

---

## 🆕 AMÉLIORATIONS UX/UI (SEPTEMBRE 2026)

- **TermDefinition** disponible pour les termes : BAPLIE, STS, TEU/EVP sur toutes les pages du module.
- **DataTable rénové** : Mode compact disponible pour les listes d'escales et de mouvements de conteneurs (plus de 50 lignes visibles simultanément en mode compact).
- **Empty States pédagogiques** : Quand aucun navire n'est en escale, affichage d'un message d'orientation avec bouton `+ Saisir une escale`.

---

*Rapport certifié conforme  EVO-LOG ERP Acconage Portuaire  Septembre 2026*
