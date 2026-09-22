# 🚚 RAPPORT D'EXPERTISE : TRANSPORT TMS, FLOTTE & CORRIDORS CEMAC
## 🗓️ Mise à Jour : Septembre 2026 — état non certifié

> Les affirmations « 100% opérationnel » et « zéro mock » nécessitent encore une validation fonctionnelle et de charge. Voir [ETAT_REEL_2026-09-19.md](./ETAT_REEL_2026-09-19.md).

---

## 🎯 DOMAINE FONCTIONNEL

Le module **Transport TMS & Flotte** est le cœur opérationnel de la mobilité de marchandises sur les corridors CEMAC. Il couvre le dispatching des missions, la gestion de la flotte de véhicules, la télématique OBD2, le suivi GPS en temps réel et la preuve électronique de livraison (ePOD).

**Parité internationale : Transporeon / Odoo Fleet / SAP TM**

---

## 📊 MÉTRIQUES CLÉS (DONNÉES RÉELLES POSTGRESQL)

| Indicateur | Endpoint API |
|:---|:---|
| Missions actives en temps réel | `/api/v1/transport/missions` |
| Véhicules disponibles / en route | `/api/v1/transport/vehicles` |
| Consommation carburant flotte | `/api/v1/transport/fuel` |
| Incidents et SOS chauffeurs | `/api/v1/transport/incidents` |
| ePOD signés et archivés | `/api/v1/transport/epod` |

---

## 🗂️ PAGES & ROUTES COUVERTES (21 ROUTES)

| Route | Description |
|:---|:---|
| `/transport/control` | Tour de contrôle en direct avec LiveMap |
| `/transport-flotte/control-tower` | Supervision globale de la flotte |
| `/transport-flotte/drivers` | Gestion des conducteurs et validité des permis lourds |
| `/transport-flotte/fuel-telematics` | Surveillance anti-fraude carburant et alertes siphonnage |
| `/transport-flotte/missions-dispatch` | Dispatching des missions et convois |
| `/transport-flotte/tracking-epod` | ePOD électronique et archivage signatures |
| `/transport/carte-live` | Cartographie GPS temps réel |
| `/transport/epod` | Preuve de livraison électronique |
| `/transport/fuel` | Gestion carburant et tickets de plein |
| `/transport/planning` | Planning et optimisation des tournées (VRP) |
| `/gps-tracking` | Télématique OBD2 et positionnement live |
| `/transport-international` | Corridors transfrontaliers, carnets TIR, CMR |

---

## 🏗️ FONCTIONNALITÉS AVANCÉES

### Optimisation des Tournées (VRP)
- Algorithme de recherche opérationnelle Vehicle Routing Problem avec contraintes de fenêtres horaires, tonnage et gabarits.
- Calcul automatique des backhauls (trajets retour à vide optimisés).

### Télématique CAN-Bus / OBD2
- Lecture des paramètres moteur en temps réel (régime, couple, température).
- Détection automatique d'anomalies mécaniques avant panne.
- Anti-fraude carburant par comparaison consommation théorique/réelle.

### ePOD (Electronic Proof of Delivery)
- Signature tactile canvas sur smartphone/tablette, certifiée horodatée.
- Coordonnées GPS de livraison, photo du chargement si litige.
- Archivage immédiat en GED avec valeur probatoire.

---

## 🆕 AMÉLIORATIONS UX/UI (SEPTEMBRE 2026)

### Portail Chauffeur Optimisé
- `inputMode="decimal"` sur saisie volume carburant (litres).
- `inputMode="numeric"` sur Prix/litre XAF et Compteur Km.
- **Empty States pédagogiques** : Quand aucune mission n'est active, message rassurant avec guide de prise de poste.

### TermDefinition Active
- Terme **ePOD** (`Electronic Proof of Delivery`) avec infobulle disponible.
- Terme **CMR** avec définition internationale disponible dans les formulaires.

### DataTable Rénové
- Mode Compact pour les listes de véhicules et de missions (30+ lignes visibles).
- Barre d'actions de masse : Assigner plusieurs missions à un chauffeur en 1 clic.
- Export CSV du planning de tournées pour analyse externe.

---

*Rapport certifié conforme — EVO-LOG ERP Transport TMS — Septembre 2026*