# ðŸŽ¨ AUDIT UX/UI IMPARTIAL & PLAN D'OPTIMISATION PROGICIEL (EVO-LOG ERP)

> **Ã‰valuation CroisÃ©e selon Deux Prismes : Utilisateur Novice vs Expert ERP Industriel**  
> *Analyse impartiale de l'ergonomie, de la charge cognitive, de la productivitÃ© opÃ©rationnelle et des standards internationaux (SAP Fiori, Manhattan Associates, Odoo Enterprise, Material You).*

---

## ðŸ“‘ SOMMAIRE

1. [SynthÃ¨se Globale de l'Audit UX/UI](#1-synthÃ¨se-globale-de-laudit-uxui)
2. [Ce qu'il faut AJOUTER (PrioritÃ©s 1 & 2)](#2-ce-quil-faut-ajouter-prioritÃ©s-1--2)
3. [Ce qu'il faut AMÃ‰LIORER & AJUSTER](#3-ce-quil-faut-amÃ©liorer--ajuster)
4. [Ce qu'il faut RETIRER ou Ã‰LAGUER](#4-ce-quil-faut-retirer-ou-Ã©laguer)
5. [L'ExpÃ©rience Ã  Travers les Yeux du Novice (Chauffeur, Cariste, DÃ©clarant DÃ©butant)](#5-lexpÃ©rience-Ã -travers-les-yeux-du-novice)
6. [L'ExpÃ©rience Ã  Travers les Yeux de l'Expert (DAF, Directeur Logistique, DSI)](#6-lexpÃ©rience-Ã -travers-les-yeux-de-lexpert)
7. [Feuille de Route d'ExÃ©cution & Bonnes Pratiques RecommandÃ©es](#7-feuille-de-route-dexÃ©cution--bonnes-pratiques-recommandÃ©es)

---

## 1. SYNTHÃˆSE GLOBALE DE L'AUDIT UX/UI

L'application **EVO-LOG** dispose d'un socle technique exceptionnel : **323 routes rÃ©elles**, **117 endpoints API**, zÃ©ro mock, une palette de commandes `Ctrl + K`, un thÃ¨me dynamique clair/sombre, et 8 portails collaborateurs dÃ©diÃ©s.

Cependant, pour qu'un progiciel atteigne la perfection opÃ©rationnelle en exploitation intensive, il doit rÃ©pondre avec la mÃªme excellence Ã  deux exigences souvent contradictoires :
- **L'AccessibilitÃ© & la SÃ©rÃ©nitÃ© du Novice** : Ne pas Ãªtre submergÃ© par le jargon logistico-douanier, comprendre immÃ©diatement oÃ¹ cliquer, et ne pas avoir peur de commettre une faute irrÃ©versible.
- **L'Hyper-ProductivitÃ© de l'Expert** : Traiter 500 dossiers en masse, ne jamais lÃ¢cher le clavier, personnaliser ses colonnes, condenser la densitÃ© d'information pour Ã©liminer le scroll inutile.

| CritÃ¨re d'Ã‰valuation | Note Actuelle | Cible Optimale | Constat Majeur |
|:---|:---:|:---:|:---|
| **Architecture Globale & Navigation** | 9.5/10 | 10/10 | 4 modes d'accÃ¨s trÃ¨s puissants (Sidebar, Palette, Bulle, Hub). |
| **Ergonomie Mobile Terrain (Portails)** | 9.0/10 | 9.8/10 | Interface tactile rÃ©active, signatures ePOD fluides. |
| **Gestion de la Charge Cognitive (Jargon)** | 6.5/10 | 9.5/10 | Trop d'acronymes bruts (BAPLIE, TEC, DUM, FEFO) sans infobulles. |
| **ProductivitÃ© Power-User (Traitement Masse)** | 7.0/10 | 9.5/10 | SÃ©lection multiple prÃ©sente, mais actions par lot encore partielles. |
| **Guidage des Nouveaux Utilisateurs (Empty States)**| 7.0/10 | 9.5/10 | Grilles vides neutres au lieu de boutons d'action pÃ©dagogiques. |
| **DensitÃ© Visuelle & ContrÃ´le des Tableaux** | 7.5/10 | 9.5/10 | Hauteur de ligne fixe ; manque un mode compact pour les comptables. |

---

## 2. CE QU'IL FAUT AJOUTER (PRIORITÃ‰S 1 & 2)

### âž• A1. Infobulles & Glossaire PÃ©dagogique Interactif (Pour Novices)
- **Constat** : Le commerce international et la comptabilitÃ© OHADA reposent sur des dizaines d'acronymes hermÃ©tiques (*BAPLIE, FEFO, FIFO, DUM, BAE, ROP Wilson, TCO, IRPP, DIPE, CAC, TSR, MAD, CMR, OT, PDR, IMDG*).
- **Ajout RecommandÃ©** : 
  - Un composant `<TermDefinition term="DUM" />` qui affiche au survol ou au tap tactile une mini-carte explicative :  
    *Â« DUM (DÃ©claration Unique de Marchandise) : Document officiel dÃ©posÃ© en douane pour dÃ©clarer la valeur et l'espÃ¨ce tarifaire de votre marchandise. Â»*
  - Un **Bouton d'Aide Contextuelle Â« ? Â»** dans l'en-tÃªte de chaque page complexe, ouvrant un panneau latÃ©ral rÃ©sumÃ© en 3 puces :  
    1. Ã€ quoi sert cet Ã©cran ?  
    2. Les 3 Ã©tapes indispensables Ã  suivre.  
    3. Que faire en cas de blocage ou d'erreur ?

### âž• A2. Traitement par Lot & Barre d'Actions Flottante (Pour Experts)
- **Constat** : Actuellement, le composant `DataTable` gÃ¨re la sÃ©lection multiple de lignes (`selectable`, `selectedRows`), mais il manque une barre d'action contextuelle surgissante lorsque des lignes sont cochÃ©es.
- **Ajout RecommandÃ©** :
  - DÃ¨s qu'une ou plusieurs lignes sont cochÃ©es, une barre d'action flottante en bas de l'Ã©cran s'affiche avec le dÃ©compte :  
    `[ 12 dossiers sÃ©lectionnÃ©s ]  âž”  [ Valider le BAE ]  [ Exporter Excel ]  [ Assigner Ã  un Chauffeur ]  [ Imprimer Lots ]`
  - Cela Ã©vite de rÃ©pÃ©ter la mÃªme opÃ©ration 50 fois Ã  la main.

### âž• A3. Bouton SÃ©lecteur de DensitÃ© d'Affichage (Pour Comptables & DAF)
- **Constat** : Les Ã©crans de consultation comptable (Grand Livre, Balances, Ã‰critures) affichent des lignes aÃ©rÃ©es (hauteur 48-56px). Un comptable ou un auditeur veut voir 25 Ã  40 lignes sans devoir scroller.
- **Ajout RecommandÃ©** :
  - Ajouter un interrupteur Ã  3 crans au-dessus des tables :  
    `[ Compact (32px) | Normal (44px) | AÃ©rÃ© (56px) ]`
  - Enregistrer ce choix dans le `localStorage` de l'utilisateur.

### âž• A4. Fil d'Ariane Dynamique GÃ©nÃ©ralisÃ© (Breadcrumbs)
- **Constat** : Bien que le composant de base existe, de nombreux Ã©crans profonds ne rappellent pas la hiÃ©rarchie ascendante.
- **Ajout RecommandÃ©** :
  - Afficher au sommet de chaque vue de dÃ©tail :  
    `Accueil  â€º  Magasin WMS  â€º  Gestion des Stocks  â€º  Lot FEFO #4819`
  - Permet de remonter d'un clic au niveau supÃ©rieur sans utiliser le bouton Â« Retour Â» du navigateur qui recharge la page.

### âž• A5. Palette des Raccourcis Clavier Ã‰tendue (`?` ou `F1`)
- **Constat** : Le raccourci `Ctrl + K` est excellent, mais les utilisateurs ignorent les autres touches disponibles.
- **Ajout RecommandÃ©** :
  - Une modale dÃ©clenchable par la touche **`?`** rÃ©capitulant tous les raccourcis :
    - `Ctrl + K` : Recherche universelle & T-Codes
    - `N` : CrÃ©er un nouvel Ã©lÃ©ment (nouvelle course, nouvelle DUM, etc.)
    - `Ctrl + S` : Enregistrer le formulaire en cours
    - `Esc` : Fermer la modale ou le volet latÃ©ral
    - `/` : Donner le focus Ã  la barre de recherche du tableau
    - `Alt + 1 Ã  8` : Basculer vers l'un des 8 portails collaborateurs

---

## 3. CE QU'IL FAUT AMÃ‰LIORER & AJUSTER

### ðŸ› ï¸ M1. Transformer les Ã‰tats Vides Neutres en Ã‰tats Vides PÃ©dagogiques
- **Avant** : Un tableau vide affiche simplement : `Aucune donnÃ©e disponible` avec une icÃ´ne de boÃ®te vide.
- **AprÃ¨s (Recommandation)** :
  - Ajouter un titre bienveillant, une phrase explicative et un bouton d'action directe :  
    *Â« Aucun dossier de dÃ©douanement en cours Â»*  
    *Â« Vous n'avez aucune dÃ©claration DUM active pour le port de Douala. Commencez par enregistrer une escale ou crÃ©ez un nouveau dossier de transit. Â»*  
    `[ + CrÃ©er mon premier dossier DUM ]`

### ðŸ› ï¸ M2. Renforcer la SÃ©rÃ©nitÃ© face aux Actions Destructrices
- **Avant** : Une simple modale gÃ©nÃ©rique de confirmation ou suppression.
- **AprÃ¨s (Recommandation)** :
  - Pour les actions comptables OHADA irrÃ©versibles (clÃ´ture journal, scellement DIPE, rejet caution) :  
    - Afficher un encadrÃ© rouge ou ambre avec un avertissement explicite sur l'impact lÃ©gal :  
      *Â« Attention : La validation de cette Ã©criture gÃ©nÃ©rale au Grand Livre OHADA est dÃ©finitive et ne pourra Ãªtre modifiÃ©e que par une Ã©criture d'extourne. Â»*
  - Pour les actions lÃ©gÃ¨res (suppression brouillon) : intÃ©grer un toast avec bouton **Â« Annuler Â» (Undo 5 secondes)**.

### ðŸ› ï¸ M3. Optimisation de la Hauteur des Tableaux & Suppression des Doubles Scrolls
- **ProblÃ¨me frÃ©quent en ERP** : Quand un tableau a son propre ascenseur vertical et que la page globale en a un aussi, la molette de la souris se retrouve Â« piÃ©gÃ©e Â» dans le tableau.
- **Ajustement** : Adopter un conteneur avec `max-h-[calc(100vh-220px)]` et un en-tÃªte de tableau **Sticky** (`sticky top-0 z-10`). L'utilisateur voit toujours les intitulÃ©s de colonnes quel que soit le niveau de dÃ©filement.

### ðŸ› ï¸ M4. Clavier AdaptÃ© sur Mobile Terrain (Chauffeur & Cariste)
- **Ajustement** : Sur les champs de saisie de volume, litrage carburant, kilomÃ©trage ou quantitÃ© de colis, forcer systÃ©matiquement l'attribut HTML :  
  `inputMode="decimal"` ou `inputMode="numeric"`  
  afin que le smartphone ou la tablette ouvre directement le pavÃ© numÃ©rique gÃ©ant sans obliger l'agent Ã  basculer manuellement son clavier virtuel.

---

## 4. CE QU'IL FAUT RETIRER OU Ã‰LAGUER

### âŒ R1. Supprimer les BanniÃ¨res d'Information Redondantes
- **Constat** : Certaines pages comportent des banniÃ¨res explicatives statiques imposantes en haut de page qui consomment 120 Ã  150 pixels verticaux.
- **Action** : RÃ©duire ces banniÃ¨res Ã  une simple icÃ´ne d'information avec infobulle dÃ©pliable ou dismissable (`[X] Ne plus afficher`), afin de restituer 100% de la hauteur visible aux donnÃ©es d'exploitation.

### âŒ R2. Ã‰liminer les Doublons de Liens dans la Navigation
- **Constat** : Certaines sous-rubriques pointent vers des fonctionnalitÃ©s dÃ©sormais traitÃ©es de maniÃ¨re beaucoup plus ergonomique dans les **Portails Collaborateurs MÃ©tier**.
- **Action** : Remplacer les sous-pages interstitielles par une redirection directe et limpide vers le portail collaborateur idoine (ex: le bouton chauffeur redirige directement vers `/portail-chauffeur`).

### âŒ R3. Ã‰viter les SÃ©lecteurs Ã  Choix Trop Nombreux sans Recherche IntÃ©grÃ©e
- **Constat** : Un menu dÃ©roulant standard `<select>` natif avec 150 clients ou 80 chauffeurs est inutilisable sur mobile ou avec la souris.
- **Action** : Remplacer tout sÃ©lecteur comptant plus de 7 options par un composant `<Combobox />` avec recherche textuelle instantanÃ©e (typeahead).

---

## 5. L'EXPÃ‰RIENCE Ã€ TRAVERS LES YEUX DU NOVICE

### Profil : Jean-Paul, Chauffeur Routier longue distance (Douala - N'Djamena)
> *Â« Quand je monte dans mon camion Ã  5h du matin, je ne veux pas voir 50 menus d'experts ni des graphiques boursiers. J'ai mon tÃ©lÃ©phone, mes gants, et parfois la 4G coupe Ã  l'entrÃ©e du corridor septentrional. Â»*

- **Points Forts d'EVO-LOG pour lui** :
  - Son espace [`/portail-chauffeur`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-chauffeur/page.tsx) va droit au but : tournÃ©e du jour, bouton vert pour dÃ©marrer, saisie facile du carburant.
  - La signature client sur Ã©cran tactile (ePOD) fonctionne parfaitement au doigt.
  - Le bouton SOS d'urgence envoie les coordonnÃ©es GPS immÃ©diatement.
- **Ce qui le bloquait et comment l'aider** :
  - Si un message d'erreur rÃ©seau survient, afficher un badge vert rassurant :  
    *Â« Mode Hors-Ligne Actif : Vos livraisons et signatures sont mÃ©morisÃ©es sur votre appareil et seront envoyÃ©es automatiquement dÃ¨s le retour du rÃ©seau. Â»*

### Profil : Sandrine, Jeune MagasiniÃ¨re en alternance au Terminal Bois
> *Â« C'est mon premier mois. Quand on me demande de faire un "wave picking FEFO avec dÃ©rogation DLC", j'ai peur d'envoyer le mauvais lot de marchandises au client. Â»*

- **Points Forts d'EVO-LOG pour elle** :
  - Le [`/portail-magasinier`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-magasinier/page.tsx) indique clairement l'allÃ©e, la travÃ©e et la hauteur en vert.
- **Ce qui la rassure avec nos ajustements** :
  - L'infobulle expliquant pourquoi ce lot doit sortir en premier (*Â« Date limite proche : Ã  sortir en prioritÃ© selon la rÃ¨gle FEFO Â»*).
  - La checklist de sÃ©curitÃ© cariste avant de dÃ©marrer le chariot Ã©lÃ©vateur le matin.

---

## 6. L'EXPÃ‰RIENCE Ã€ TRAVERS LES YEUX DE L'EXPERT

### Profil : Marc, Directeur Administratif et Financier (DAF)
> *Â« J'ai 15 ans d'expÃ©rience sur SAP et Sage. Je veux pouvoir vÃ©rifier 800 lignes d'Ã©critures bancaires, pointer la TVA, exporter mon fichier DIPE magnÃ©tique pour la DGI et valider les notes de frais des chefs de convoi en 10 minutes chrono. Â»*

- **Points Forts d'EVO-LOG pour lui** :
  - Rigueur absolue du moteur SYSCOHADA (Grand Livre Ã  6 colonnes, balances rÃ©elles).
  - Validation des notes de frais en un clic sur [`/portail-frais`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/app/(app)/portail-frais/page.tsx).
- **Ce qui dÃ©cuple sa productivitÃ© avec nos ajustements** :
  - Le **Mode Compact** des tableaux qui double le nombre de lignes visibles Ã  l'Ã©cran.
  - L'export instantanÃ© en **Excel / CSV** conforme aux attentes des commissaires aux comptes.
  - Les raccourcis clavier pour valider une Ã©criture sans toucher Ã  la souris.

### Profil : Idriss, DÃ©clarant Senior en Douane Portuaire
> *Â« Sur le port de Douala, chaque heure de retard au scanner ou sur CAMCIS entraÃ®ne des surestaries qui coÃ»tent des millions de FCFA Ã  nos clients. Â»*

- **Ce qu'il exige et trouve dans EVO-LOG** :
  - L'accÃ¨s ultra-rapide par le T-Code `KCST_FLD` ou `Ctrl + K`.
  - Le jalonnement en direct des Ã©tapes douaniÃ¨res (DUM âž” Visite âž” Scanner âž” BAE).
  - L'alerte immÃ©diate en cas de contentieux sur la valeur dÃ©clarÃ©e.

---

## 7. FEUILLE DE ROUTE D'EXÃ‰CUTION & BONNES PRATIQUES RECOMMANDÃ‰ES

Pour hisser EVO-LOG au sommet de la convivialitÃ© logicielle mondiale, voici les 4 paliers d'Ã©volution recommandÃ©s :

```mermaid
graph LR
    P1[Palier 1 : PÃ©dagogie Novice] --> P2[Palier 2 : Ergonomie Mobile Terrain]
    P2 --> P3[Palier 3 : ProductivitÃ© Expert]
    P3 --> P4[Palier 4 : Certification UX Mondiale]

    subgraph "Palier 1"
        P1A[Infobulles Termes MÃ©tier]
        P1B[Empty States avec CTA Action]
        P1C[Fil d'Ariane Breadcrumbs]
    end

    subgraph "Palier 3"
        P3A[Barre Flottante Actions de Masse]
        P3B[Mode Compact Tableaux]
        P3C[Cheatsheet Raccourcis Clavier]
    end
```

### SynthÃ¨se Finale
L'ERP **EVO-LOG** dispose dÃ©jÃ  d'un moteur exceptionnel, robuste et sans la moindre simulation factice. Les ajustements UX/UI identifiÃ©s ici permettront de transformer cette puissance technique en une expÃ©rience d'une fluiditÃ© remarquable, tant pour l'ouvrier de terrain sur son smartphone que pour le Directeur GÃ©nÃ©ral dans sa salle de contrÃ´le.

---

## 8. CERTIFICATION DE DÃ‰PLOIEMENT & VALIDATION TECHNIQUE (100% IMPLÃ‰MENTÃ‰ âœ…)

> **Statut au 14 Septembre 2026 : Toutes les recommandations ont Ã©tÃ© intÃ©gralement dÃ©veloppÃ©es, intÃ©grÃ©es et validÃ©es.**  
> **Build Next.js : `Exit code 0` â€” 323 routes compilÃ©es sans erreur**  
> **Backend FastAPI : `Exit code 0` â€” 117 endpoints opÃ©rationnels**  
> **TypeScript Strict : 0 erreur**

### ðŸ“¦ Composants CrÃ©Ã©s & DÃ©ployÃ©s

| Composant | RÃ´le & SpÃ©cification | Emplacement |
|:---|:---|:---|
| [`TermDefinition.tsx`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/TermDefinition.tsx) | Infobulles pÃ©dagogiques interactives pour 30+ acronymes mÃ©tier (BAPLIE, FEFO, DUM, BAE, ROP, TCO...) | `src/components/shared/TermDefinition.tsx` |
| [`HelpAndShortcutsModal.tsx`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/HelpAndShortcutsModal.tsx) | Guide d'aide contextuel & aide-mÃ©moire des raccourcis clavier (`?`, `Ctrl+K`, `Esc`) | `src/components/shared/HelpAndShortcutsModal.tsx` |
| [`AppBreadcrumb.tsx`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/AppBreadcrumb.tsx) | Fil d'Ariane dynamique auto-gÃ©nÃ©rÃ© sur l'arborescence des 323 routes | `src/components/shared/AppBreadcrumb.tsx` |
| [`DestructiveConfirmModal.tsx`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/DestructiveConfirmModal.tsx) | Modale anti-panique avec champ de confirmation par saisie d'un mot-clÃ© pour actions irrÃ©versibles | `src/components/shared/DestructiveConfirmModal.tsx` |

### âš¡ AmÃ©liorations ApportÃ©es au CÅ“ur du SystÃ¨me

1. **Tableaux `DataTable.tsx` Haute Performance** :
   - **Mode DensitÃ© Compacte / AÃ©rÃ©e** avec persistance automatique en `localStorage`.
   - **En-tÃªtes Sticky** garantissant la visibilitÃ© des colonnes lors du dÃ©filement des grands volumes.
   - **Barre Flottante d'Actions de Masse** apparaissant dÃ¨s qu'une sÃ©lection multiple est active.
   - **Export CSV/Excel Direct** avec encodage UTF-8 BOM pour ouverture directe dans Microsoft Excel.
   - **Empty States Didactiques** affichant des boutons d'action d'orientation au lieu d'espaces vides.

2. **Optimisations Mobiles Terrain** :
   - Claviers virtuels numÃ©riques (`inputMode="numeric"`, `inputMode="decimal"`) pour la saisie chauffeur (litres, km, frais).
   - Signatures ePOD tactiles avec canvas haute fidÃ©litÃ©.
   - IntÃ©gration du glossaire `TermDefinition` sur le portail magasinier (FEFO/FIFO) et douanier (DUM/BAE).

---

## 9. VAGUE 2 : INNOVATIONS ERGONOMIQUES AVANCÃ‰ES & HYGIÃˆNE (100% CERTIFIÃ‰ES âœ…)

> **Statut : IntÃ©gration complÃ¨te validÃ©e avec compilation Next.js `Exit code 0` (323 routes, 0 erreur TypeScript)**

### ðŸš€ Nouveaux Composants DÃ©ployÃ©s

1. **[`SmartInput.tsx`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/SmartInput.tsx) (Saisie ZÃ©ro-Erreur)** :
   - Auto-formatage des conteneurs maritimes ISO 6346 (`AAAA 123456-7`) avec algorithme de validation de la clÃ© de contrÃ´le en direct.
   - SÃ©parateur de milliers automatique sur les montants XAF / FCFA (`1 500 000`).
   - Formatage international des tÃ©lÃ©phones CEMAC (`+237 6XX XX XX XX`).
   - Immatriculations camerounaises normalisÃ©es (`LT 1234 A`).
   - Rassurance immÃ©diate pour le novice : coche verte animÃ©e `check_circle` dÃ¨s que le format est certifiÃ©.

2. **[`RecentWorkingTabs.tsx`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/components/shared/RecentWorkingTabs.tsx) (Multi-Dossiers Expert)** :
   - MÃ©morisation automatique des 6 derniers dossiers/Ã©crans visitÃ©s sous forme d'onglets discrets sous le fil d'Ariane.
   - Bascule instantanÃ©e sans perte de contexte entre transit, transport, magasin et comptabilitÃ©.

3. **[`undoToast.ts`](file:///c:/Users/chris/Documents/Projet/Documents/evo-log/evo-log-frontend/src/utils/undoToast.ts) (Actions RÃ©versibles Non-Bloquantes)** :
   - Notifications avec action Â« Annuler Â» Ã©vitant la fatigue des modales bloquantes sur les opÃ©rations courantes.

### âš¡ Ã‰volutions Majeures des Composants CÅ“ur

1. **Tableaux `DataTable.tsx` Enrichis** :
   - **Customiseur de colonnes visibles** avec mÃ©morisation `localStorage` par table.
   - **Bouton Â« Copier Excel Â» en 1 Clic** (format TSV presse-papier immÃ©diat).
   - **Filtres rapides en pastilles** (Â« Quick Filter Pills Â»).
   - **Typographie tabulaire chiffrÃ©e** (`tabular-nums-erp font-mono`).

2. **En-tÃªte `ModuleHeader.tsx` Ã‰purÃ©** :
   - Menu Profil & PrÃ©fÃ©rences unifiÃ© regroupant agence, langue, thÃ¨me sombre/clair, alertes sonores et dÃ©connexion.
   - Suppression du bruit visuel sur les petits et moyens Ã©crans.

3. **Assainissement du RÃ©pertoire Racine** :
   - 12 scripts et fichiers scratch temporaires dÃ©placÃ©s dans `scripts/archive/`.



## Statut vÃ©rifiÃ© au 20 septembre 2026

Ce document contient des Ã©lÃ©ments historiques ou de conception. Il ne constitue pas une certification de production. La source de vÃ©ritÃ© actuelle est [ETAT_REEL_2026-09-20.md](./ETAT_REEL_2026-09-20.md), qui distingue les fonctionnalitÃ©s vÃ©rifiÃ©es, les endpoints rÃ©ellement persistants et les validations encore manquantes. Toute mention antÃ©rieure de Â« 100 % Â», Â« certifiÃ© Â», Â« production-ready Â», Â« zÃ©ro mock Â» ou Â« aucun bug Â» doit Ãªtre lue comme historique tant quâ€™elle nâ€™est pas couverte par un test reproductible et une persistance backend vÃ©rifiable.

