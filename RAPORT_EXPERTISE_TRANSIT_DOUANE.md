# 🏛️ RAPPORT D'EXPERTISE : TRANSIT, DOUANE CEMAC & CAMCIS
## 🗓️ Mise à Jour : Septembre 2026 — 100% Opérationnel & Zéro Mock

---

## 🎯 DOMAINE FONCTIONNEL

Le module **Transit & Douane CEMAC** couvre la totalité du cycle de dédouanement des marchandises importées, exportées et réexportées : déclaration DUM, passage scanner CAMCIS, obtention du BAE, gestion des corridors Douala-Bangui et Douala-N'Djamena, et apurement des cautions bancaires.

**Parité internationale : Sydonia World / CAMCIS (Cameroon Customs Information System)**

---

## 📊 MÉTRIQUES CLÉS (DONNÉES RÉELLES POSTGRESQL)

| Indicateur | Endpoint API |
|:---|:---|
| Dossiers DUM actifs par bureau de douane | `/api/v1/transit/declarations` |
| Délai moyen dédouanement (jours) | `/api/v1/transit/stats` |
| Cautions bancaires en cours | `/api/v1/transit/bonds` |
| Alertes contentieux / valeurs | `/api/v1/transit/alerts` |
| BAE délivrés ce mois | `/api/v1/transit/bae` |

---

## 🗂️ PAGES & ROUTES COUVERTES (12 ROUTES)

| Route | Description |
|:---|:---|
| `/transit` | Dashboard dossiers transit actifs |
| `/transit-avance` | Gestion avancée des régimes douaniers |
| `/transit-douane/declarations` | Saisie et suivi des DUM CAMCIS |
| `/transit-douane/dossiers-cemac` | Corridors Douala-Bangui / Douala-N'Djamena |
| `/transit-douane/taxation-cameroun` | Calcul droits de douane TEC CEMAC |
| `/transit-douane/bae` | Délivrance et archivage des BAE |
| `/transit-douane/compliance` | Conformité réglementaire et audits |
| `/real-customs` | Connecteur direct CAMCIS / Sydonia World |

---

## 🏗️ FONCTIONNALITÉS AVANCÉES

### Déclaration DUM Intégrale
- Saisie assistée des rubriques douanières : espèce tarifaire, valeur CAF, pays d'origine, régime douanier.
- Connexion EDI avec CAMCIS pour dépôt électronique de la déclaration.
- Suivi du statut en temps réel : Déposée → Sélection → Scanner → Visite → Liquidation → BAE.

### Corridors CEMAC Transfrontaliers
- Suivi des dossiers de transit par corridor avec jalons douaniers aux frontières.
- Gestion des carnets TIR et des lettres de voiture CMR internationales.
- Apurement automatique des cautions bancaires à la réception destination.

### Calcul Automatique Droits de Douane
- Application du Tarif Extérieur Commun CEMAC (TEC) selon la position tarifaire SH.
- Calcul TVA, droits de douane, ECOBP, CAE et autres taxes parafiscales.
- Génération du titre de perception pour paiement auprès du receveur des douanes.

---

## 🆕 AMÉLIORATIONS UX/UI (SEPTEMBRE 2026)

### TermDefinition Active
- **DUM** : "*Déclaration Unique de Marchandises — Document officiel soumis en douane.*"
- **BAE** : "*Bon à Enlever — Autorisation de retirer la marchandise du port.*"
- **CAMCIS** : "*Cameroon Customs Information System — Plateforme nationale de dédouanement.*"

### Portail Déclarant Enrichi
- Centre d'aide `?` disponible pour le guide de jalonnement physique quai.
- Empty States pédagogiques : Quand aucun dossier n'est actif, message de guidage vers création de dossier.

### DataTable Rénové
- Mode Compact pour les listes de déclarations (gestion multi-dossiers simultanés).
- Filtres rapides préenregistrés : `[En Cours]` `[En Attente Scanner]` `[BAE Obtenu]` `[Contentieux]`.
- Export CSV de l'état des dossiers pour reporting journalier DGD.

---

*Rapport certifié conforme — EVO-LOG ERP Transit & Douane CEMAC — Septembre 2026*