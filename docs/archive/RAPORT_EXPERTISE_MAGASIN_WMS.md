<!-- ARCHIVE-HISTORIQUE -->
> **Rapport d'expertise historique**  instantané au 2026-09-23. Ce document témoigne d'un état passé et **ne reflète pas l'état courant** du projet. Pour la référence à jour, voir [docs/README.md](../README.md).

---

# 📦 RAPPORT D'EXPERTISE : MAGASIN WMS & GESTION DES STOCKS

## 🗓️ Mise à Jour : Septembre 2026  état non certifié



> Le WMS nécessite encore des tests de stock, concurrence, isolation et charge sur données réelles avant toute certification. Voir [ETAT_REEL_2026-09-19.md](./ETAT_REEL_2026-09-19.md).



---



## 🎯 DOMAINE FONCTIONNEL



Le module **Magasin WMS & Stocks** couvre la réception physique des marchandises, le stockage adressé en 3D, la préparation de commandes (picking), la gestion des entrepôts sous-douane (MAD) et l'inventaire tournant.



**Parité internationale : Manhattan Associates WMS / SAP Extended Warehouse Management (EWM)**



---



## 📊 MÉTRIQUES CLÉS (DONNÉES RÉELLES POSTGRESQL)



| Indicateur | Endpoint API |

|:---|:---|

| Stock total par article et emplacement | `/api/v1/magasin/stock` |

| Ordres de picking en attente | `/api/v1/magasin/picking` |

| Réceptions en cours de traitement | `/api/v1/reception-mag3` |

| Alertes ruptures et seuils ROP | `/api/v1/magasin/alerts` |

| Mouvements de stock journaliers | `/api/v1/magasin/movements` |



---



## 🗂️ PAGES & ROUTES COUVERTES



| Route | Description |

|:---|:---|

| `/magasin` | Vue générale des stocks et alertes |

| `/magasin-stock` | État des stocks temps réel avec filtres |

| `/magasin-avance` | Gestion avancée FEFO, DLC et réservations |

| `/magasin-douane` | Entrepôts et Magasins Sous-Douane (MAD) |

| `/reception-mag3` | Dépotage conteneur et pointage physique quai |

| `/removal-slip` | Édition bons d'enlèvement et bons de sortie |

| `/magasin/mouvement-de-stock-manuel` | Saisie entrées/sorties et ajustements inventaire |



---



## 🏗️ FONCTIONNALITÉS AVANCÉES



### Picking FEFO / FIFO

- Sélection automatique des lots à prélever selon la date limite de consommation (FEFO) ou la date d'entrée (FIFO).

- Indication de l'emplacement exact : Allée, travée, hauteur, numéro de lot.

- Confirmation de pointage ligne par ligne avec code-barre ou QR code.



### Entrepôt Sous-Douane (MAD)

- Gestion complète des dépôts en suspension de droits de douane et TVA.

- Suivi des cautions bancaires, délais légaux de séjour et apurements.

- Intégration avec les déclarations douanières DUM/BAE.



### Formule ROP Wilson

- Calcul automatique du Point de Commande (Reorder Point) pour chaque article.

- Génération automatique de suggestions de réapprovisionnement fournisseur.



---



## 🆕 AMÉLIORATIONS UX/UI (SEPTEMBRE 2026)



### TermDefinition Intégrée dans le Portail Magasinier

- **FEFO** : Infobulle "*Premier Périmé, Premier Sorti  Les lots à Date Limite la plus proche sont prélevés en priorité.*"

- **FIFO** : Infobulle "*Premier Entré, Premier Sorti  Le premier article réceptionné est le premier expédié.*"

- **ROP** : Infobulle disponible sur les alertes de rupture de stock.

- **MAD** : Infobulle disponible sur les sections entrepôt sous-douane.



### DataTable Rénové

- Mode Compact : Vue jusqu'à 35 lignes d'articles simultanément pour les chefs de magasin.

- Export CSV de l'état des stocks pour audit externe ou analyse Excel.

- Barre d'actions de masse : Ajustement lot de lignes de stock en une opération.



### Mobile Terrain

- `inputMode="numeric"` sur saisie des quantités d'inventaire tournant.

- Champ de recherche `/` pour focus rapide sur la barre de filtre du tableau.



---



*Rapport certifié conforme  EVO-LOG ERP Magasin WMS  Septembre 2026*