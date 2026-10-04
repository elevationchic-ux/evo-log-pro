// src/config/domainLoadingConfig.ts
// SOURCE DE VÉRITÉ OFFICIELLE DES 28 DÉPARTEMENTS ET GRANDS MODULES EVO-LOG ERP
// Chaque département possède son identité visuelle, sa palette chromatique,
// sa localisation institutionnelle, ses messages de diagnostic et son animation parlante.
//
// ATTENTION COULEUR : l'identité chromatique n'est PAS décidée ici. `modulePalette.ts`
// est la source de vérité unique (« une couleur unique par module »). Les 49 écrans de
// chargement ci-dessous sont des vus d'un même module (ex. « acconage », « acconage-avance »
// et « port-incidents » sont trois vues du module port-operations) : ils doivent donc
// hériter de la teinte de leur module parent. La boucle de normalisation en fin de fichier
// écrase primaryColor à partir de modulePalette, ce qui rend toute dérive impossible.

import { getModulePalette } from './modulePalette';

export type DomainAnimationType =
  | 'syscohada-ledger'       // 1. Comptabilité OHADA : Balance bilatérale Débit/Crédit, comptes en orbite
  | 'treasury-flux'          // 2. Finance & Trésorerie : Flux de liquidités, coffre-fort et devises
  | 'radar-maritime'         // 3. Port Operations : Radar rotatif à 360°, détection de navires Douala/Kribi
  | 'crane-sts'              // 4. Acconage & Manutention : Portique STS, levage de conteneurs de quai
  | 'customs-laser'          // 5. Transit & Guichet GUCE : Scan laser de manifestes, certification Sydonia++
  | 'dum-customs-stamp'      // 6. Déclarations Douanières : Sceau douanier officiel, liquidation et DUM
  | 'telematics-satellite'   // 7. Transport & Flotte : Réticule GPS satellitaire, corridors CEMAC
  | 'truck-dashboard'        // 8. Portail Chauffeur : Tableau de bord de camion routier, tachygraphe
  | 'wms-lidar'              // 9. Magasin & Stock WMS : Racks 3D isométriques, scan laser vertical
  | 'rf-scan-gun'            // 10. Portail Magasinier : Douchette RF code-barres et contrôle scellés
  | 'container-3d-lifecycle' // 11. Cycle de Vie Conteneurs : Conteneur ISO 3D avec tracker IoT
  | 'gmao-gears'             // 12. Parc Véhicules : Double engrenages industriels, diagnostic moteur
  | 'workshop-wrench'        // 13. Maintenance Atelier : Clé dynamométrique, analyse vibratoire banc d'essai
  | 'fuel-gauge'             // 14. Fuel Guard & Énergie : Cuve de carburant volumétrique, débitmètre anti-vol
  | 'isps-shield'            // 15. QHSE & Sécurité : Bouclier hexagonal de protection, normes ISPS
  | 'incident-beacon'        // 16. Portail QHSE & Incidents : Gyrophare d'alerte active, radar de zone
  | 'biometric-ring'         // 17. RH & Capital Humain : Anneau d'empreinte biométrique, organigramme
  | 'employee-badge'         // 18. Portail Employé : Badge d'accréditation RFID individuel
  | 'shift-clock'            // 19. Chef Personnel & Quarts : Horloge de relève 3x8 et plannings dockers
  | 'expense-voucher'        // 20. Portail Frais : Justificatif dématérialisé scellé et virement indemnités
  | 'synergy-constellation'  // 21. Hub Collaboratif & Chat : Constellation multipoints, flux hertzien d'équipe
  | 'collaborator-hub'       // 22. Portail Collaborateur : Carrefour central d'aiguillage des missions
  | 'b2b-gateway'            // 23. Espace Client B2B : Passerelle cryptographique EDI partenaires
  | 'pricing-scale'          // 24. Cotations & Commercial : Balance de cotation fret, simulateur marge
  | 'procurement-cart'       // 25. Achats & Fournisseurs : Chariot d'approvisionnement, bons certifiés
  | 'tax-dgi'                // 26. Fiscalité Cameroun : Sceau officiel DGI, TVA 19.25% et télédéclaration
  | 'bi-prism'               // 27. Décisionnel & BI : Prisme holographique 3D, matrice décisionnelle
  | 'rbac-matrix'            // 28. Admin & Gouvernance : Cylindre de clés cryptographiques RBAC
  | 'port-blueprint'         // 29. Aménagement Portuaire : plan de schéma directeur, tracés de périmètre & levés bathymétriques
  | 'strategic-compass';     // Cockpit Global : Boussole gyroscopique 3 axes Navire → Client

export interface DomainLoadingConfig {
  key: string;
  departmentNumber: number;
  domainName: string;
  subTitle: string;
  badgeCode: string;
  locationTag: string;
  primaryColor: string;
  accentColor: string;
  gradientBg: string;
  glowClass: string;
  animationType: DomainAnimationType;
  steps: [string, string, string, string];
}

export const DOMAIN_LOADING_CONFIGS: Record<string, DomainLoadingConfig> = {
  // ═══════════════════════════════════════════════════════════════════════════
  // 1. COMPTABILITÉ OHADA
  // ═══════════════════════════════════════════════════════════════════════════
  'comptabilite-ohada': {
    key: 'comptabilite-ohada',
    departmentNumber: 1,
    domainName: 'DÉPARTEMENT COMPTABILITÉ OHADA',
    subTitle: 'GRAND LIVRE GÉNÉRAL, BALANCE BILATÉRALE & ÉTATS SYSCOHADA',
    badgeCode: 'SYSCOHADA-2017 • CEMAC OHADA',
    locationTag: 'DIRECTION FINANCIÈRE & COMPTABLE (BUREAU 401)',
    primaryColor: '#8B5CF6',
    accentColor: '#F59E0B',
    gradientBg: 'from-violet-950 via-[#130728] to-[#04010b]',
    glowClass: 'shadow-violet-500/50 border-violet-500/60 text-violet-400',
    animationType: 'syscohada-ledger',
    steps: [
      '▶ Vérification de l\'équilibre bilatéral Débit / Crédit SYSCOHADA...',
      '▶ Synchronisation des journaux auxiliaires (Achats, Ventes, Banque, OD)...',
      '▶ Contrôle des comptes de tiers et calcul de la balance avant inventaire...',
      '✓ Grand Livre SYSCOHADA ouvert. Prêt pour les écritures comptables.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 2. FINANCE & TRÉSORERIE OHADA
  // ═══════════════════════════════════════════════════════════════════════════
  'finance-ohada': {
    key: 'finance-ohada',
    departmentNumber: 2,
    domainName: 'DÉPARTEMENT FINANCE & TRÉSORERIE',
    subTitle: 'GESTION DES LIQUIDITÉS, FACTURATION & RÈGLEMENTS BANCAIRES',
    badgeCode: 'SWIFT / BEAC PROTOCOL • OHADA SECURE',
    locationTag: 'SALLE DES MARCHÉS & TRÉSORERIE CENTRALE',
    primaryColor: '#10B981',
    accentColor: '#34D399',
    gradientBg: 'from-emerald-950 via-[#031d14] to-[#010905]',
    glowClass: 'shadow-emerald-500/50 border-emerald-500/60 text-emerald-400',
    animationType: 'treasury-flux',
    steps: [
      '▶ Interconnexion avec les passerelles bancaires (XAF, EUR, USD)...',
      '▶ Synchronisation des échéanciers clients et avis d\'encaissement...',
      '▶ Calcul en direct de la position nette de trésorerie consolidée...',
      '✓ Trésorerie synchronisée. Flux de capitaux validés.',
    ],
  },
  finance: {
    key: 'finance',
    departmentNumber: 2,
    domainName: 'DÉPARTEMENT FINANCE & FACTURATION',
    subTitle: 'ÉMISSION DES FACTURES PORTUAIRES & SUIVI RECOUVREMENT',
    badgeCode: 'FINANCE-CORE • FACTURATION CLIENTS',
    locationTag: 'DIRECTION FINANCIÈRE DOUALA',
    primaryColor: '#10B981',
    accentColor: '#F59E0B',
    gradientBg: 'from-emerald-950 via-[#031d14] to-[#010905]',
    glowClass: 'shadow-emerald-500/50 border-emerald-500/60 text-emerald-400',
    animationType: 'treasury-flux',
    steps: [
      '▶ Récupération des décomptes d\'acconage et transit...',
      '▶ Génération des factures pro-forma et bordereaux fiscaux...',
      '▶ Vérification des garanties de paiement et cautionnements...',
      '✓ Facturation prête. Échéanciers actualisés.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 3. PORT OPERATIONS & ARRIVÉE NAVIRES
  // ═══════════════════════════════════════════════════════════════════════════
  'port-operations': {
    key: 'port-operations',
    departmentNumber: 3,
    domainName: 'DÉPARTEMENT OPÉRATIONS PORTUAIRES',
    subTitle: 'ARRIVÉE NAVIRES, RADAR DES BASSINS & GESTION DES ESCALES',
    badgeCode: 'DOUALA PORT AUTHORITY • CAPITAINERIE',
    locationTag: 'TOUR RADAR CAPITAINERIE (04°03\'04"N 009°42\'54"E)',
    primaryColor: '#0EA5E9',
    accentColor: '#38BDF8',
    gradientBg: 'from-sky-950 via-[#041a2e] to-[#01080f]',
    glowClass: 'shadow-sky-500/50 border-sky-500/60 text-sky-400',
    animationType: 'radar-maritime',
    steps: [
      '▶ Activation du faisceau radar maritime Port de Douala & Kribi...',
      '▶ Synchronisation des plans d\'armement et avis d\'arrivée navire...',
      '▶ Allocation dynamique des postes à quai et remorqueurs...',
      '✓ Radar opérationnel. Navires en approche identifiés.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 4. ACCONAGE & MANUTENTION DE QUAI
  // ═══════════════════════════════════════════════════════════════════════════
  acconage: {
    key: 'acconage',
    departmentNumber: 4,
    domainName: 'DÉPARTEMENT ACCONAGE & MANUTENTION',
    subTitle: 'PORTIQUES STS, DÉBARQUEMENT CONTENEURS & ÉQUIPES DE QUAI',
    badgeCode: 'TERMINAL QUAI STS 1-4 • ACCONAGE LOURD',
    locationTag: 'TERMINAL À CONTENEURS • POSTE SUD',
    primaryColor: '#2563EB',
    accentColor: '#F59E0B',
    gradientBg: 'from-blue-950 via-[#0b1c3d] to-[#02050f]',
    glowClass: 'shadow-blue-500/50 border-blue-500/60 text-blue-400',
    animationType: 'crane-sts',
    steps: [
      '▶ Calibrage des grues portiques STS et cavaliers cavaliers...',
      '▶ Synchronisation des cadences de manutention au poste à quai...',
      '▶ Affectation des équipes d\'acconiers et pointeurs certifiés...',
      '✓ Régie d\'acconage opérationnelle. Déchargement autorisé.',
    ],
  },
  'acconage-avance': {
    key: 'acconage-avance',
    departmentNumber: 4,
    domainName: 'ACCONAGE AVANCÉ & OPTIMISATION NAVIRES',
    subTitle: 'PLANS D\'ARRIMAGE BAY-PLAN & CADENCES TERMINAL',
    badgeCode: 'BAPLIE PROTOCOL • STS OPTIMIZER',
    locationTag: 'CENTRE D\'INGÉNIERIE D\'ARRIMAGE',
    primaryColor: '#1D4ED8',
    accentColor: '#60A5FA',
    gradientBg: 'from-blue-950 via-[#0b1c3d] to-[#02050f]',
    glowClass: 'shadow-blue-500/50 border-blue-500/60 text-blue-400',
    animationType: 'crane-sts',
    steps: [
      '▶ Chargement du fichier Baplie / EDIFACT du porte-conteneurs...',
      '▶ Calcul des centres de gravité et stabilité navire...',
      '▶ Optimisation des séquences de levage des grues...',
      '✓ Plans d\'arrimage validés.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 5. TRANSIT & GUICHET UNIQUE GUCE
  // ═══════════════════════════════════════════════════════════════════════════
  'transit-douane': {
    key: 'transit-douane',
    departmentNumber: 5,
    domainName: 'DÉPARTEMENT TRANSIT & GUICHET UNIQUE',
    subTitle: 'GUCE CAMEROUN, SYDONIA++ & CONNAISSEMENTS MARITIMES (BL)',
    badgeCode: 'GUCE CAMEROUN • DOUANES CEMAC',
    locationTag: 'GUICHET UNIQUE DU COMMERCE EXTÉRIEUR (GUCE)',
    primaryColor: '#3B82F6',
    accentColor: '#93C5FD',
    gradientBg: 'from-blue-950 via-[#061430] to-[#020510]',
    glowClass: 'shadow-blue-500/50 border-blue-500/60 text-blue-400',
    animationType: 'customs-laser',
    steps: [
      '▶ Interconnexion avec le système SydoniaWorld & Guichet GUCE...',
      '▶ Scan et validation automatisée des Déclarations Sommaires (DS)...',
      '▶ Calcul des droits de douane, taxes communautaires & cautionnements...',
      '✓ Guichet douanier prêt. Dossiers de transit prêts à liquider.',
    ],
  },
  transit: {
    key: 'transit',
    departmentNumber: 5,
    domainName: 'TRANSIT & EXPÉDITIONS MARITIMES',
    subTitle: 'CONNAISSEMENTS B/L, TITRES DE TRANSPORT & BESC',
    badgeCode: 'TRANSIT-MARITIME • FORMALITÉS CEMAC',
    locationTag: 'BUREAU DE TRANSIT INTERNATIONAL',
    primaryColor: '#3B82F6',
    accentColor: '#60A5FA',
    gradientBg: 'from-blue-950 via-[#061430] to-[#020510]',
    glowClass: 'shadow-blue-500/50 border-blue-500/60 text-blue-400',
    animationType: 'customs-laser',
    steps: [
      '▶ Contrôle des manifestes maritimes et titres BESC...',
      '▶ Rapprochement des bons de délivrance (BAD)...',
      '▶ Émission des autorisations de sortie sous douane...',
      '✓ Formalités de transit validées.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 6. DÉCLARATIONS DOUANIÈRES & DUM
  // ═══════════════════════════════════════════════════════════════════════════
  'real-customs': {
    key: 'real-customs',
    departmentNumber: 6,
    domainName: 'DÉPARTEMENT DÉDOUANEMENT RÉEL (DUM)',
    subTitle: 'DÉCLARATION UNIQUE DE MARCHANDISES & LIQUIDATION FISCALE',
    badgeCode: 'DUM OFFICIELLE • BORDEREAU DE TAXATION',
    locationTag: 'INSPECTION DOUANIÈRE PORT DE DOUALA',
    primaryColor: '#0284C7',
    accentColor: '#F59E0B',
    gradientBg: 'from-sky-950 via-[#051a2d] to-[#01080e]',
    glowClass: 'shadow-sky-500/50 border-sky-500/60 text-sky-400',
    animationType: 'dum-customs-stamp',
    steps: [
      '▶ Récupération de la Déclaration Unique de Marchandises (DUM)...',
      '▶ Contrôle des positions tarifaires du Système Harmonisé (SH)...',
      '▶ Application du tampon officiel de liquidation douanière...',
      '✓ Dédouanement certifié. Droits acquittés.',
    ],
  },
  'portail-declarant': {
    key: 'portail-declarant',
    departmentNumber: 6,
    domainName: 'PORTAIL DÉCLARANT AGRÉÉ EN DOUANE',
    subTitle: 'ESPACE DE DÉCLARATION, SUIVI DES DOSSIERS ET BAE',
    badgeCode: 'AGRÉMENT DÉCLARANT CEMAC • SYDONIA++',
    locationTag: 'ESPACE RÉSERVÉ DES TRANSITAIRES DÉCLARANTS',
    primaryColor: '#0284C7',
    accentColor: '#38BDF8',
    gradientBg: 'from-sky-950 via-[#051a2d] to-[#01080e]',
    glowClass: 'shadow-sky-500/50 border-sky-500/60 text-sky-400',
    animationType: 'dum-customs-stamp',
    steps: [
      '▶ Vérification de l\'agrément déclarant et certificats cryptographiques...',
      '▶ Téléchargement des déclarations en attente de BAE...',
      '▶ Contrôle des quittances de paiement des droits...',
      '✓ Portail Déclarant déverrouillé.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 7. TRANSPORT & CONVOIS FLOTTE
  // ═══════════════════════════════════════════════════════════════════════════
  'transport-flotte': {
    key: 'transport-flotte',
    departmentNumber: 7,
    domainName: 'DÉPARTEMENT TRANSPORT & FLOTTE',
    subTitle: 'TÉLÉMATIQUE SATELLITAIRE GPS & CONVOIS SÉCURISÉS CEMAC',
    badgeCode: 'CORRIDORS CEMAC • DOUALA-N\'DJAMENA-BANGUI',
    locationTag: 'TOUR DE DISPATCHING ROUTIER CENTRAL',
    primaryColor: '#06B6D4',
    accentColor: '#22D3EE',
    gradientBg: 'from-cyan-950 via-[#041d24] to-[#01090c]',
    glowClass: 'shadow-cyan-500/50 border-cyan-500/60 text-cyan-400',
    animationType: 'telematics-satellite',
    steps: [
      '▶ Accrochage aux balises GPS et boîtiers télématiques OBD...',
      '▶ Tracé des convois fret sur les corridors Douala-Yaoundé-N\'Djamena...',
      '▶ Surveillance en temps réel des jauges, vitesses et arrêts...',
      '✓ Tour de contrôle transport active. Flotte connectée.',
    ],
  },
  transport: {
    key: 'transport',
    departmentNumber: 7,
    domainName: 'DISPATCHING ROUTIER & LOGISTIQUE TERRESTRE',
    subTitle: 'AFFECTATION DES TRACTEURS, REMORQUES & LETTRES DE VOITURE',
    badgeCode: 'DISPATCH FRET • GESTION MISSIONS',
    locationTag: 'RÉGIE ROUTIÈRE DE LA ZONE PORTUAIRE',
    primaryColor: '#06B6D4',
    accentColor: '#67E8F9',
    gradientBg: 'from-cyan-950 via-[#041d24] to-[#01090c]',
    glowClass: 'shadow-cyan-500/50 border-cyan-500/60 text-cyan-400',
    animationType: 'telematics-satellite',
    steps: [
      '▶ Calcul des plannings de chargement et ordres de mission...',
      '▶ Affectation des remorques porte-conteneurs 20\'/40\'...',
      '▶ Validation des fiches de tournée chauffeurs...',
      '✓ Dispatching route opérationnel.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 8. PORTAIL CHAUFFEUR & MISSION ROUTE
  // ═══════════════════════════════════════════════════════════════════════════
  chauffeur: {
    key: 'chauffeur',
    departmentNumber: 8,
    domainName: 'PORTAIL CHAUFFEUR & FEUILLE DE ROUTE',
    subTitle: 'TABLEAU DE BORD CONDUCTEUR, LETTRE DE VOITURE & CONVOI',
    badgeCode: 'APPLICATION CHAUFFEUR • CORRIDORS FREIGHT',
    locationTag: 'POSTE DE CONDUITE EMBARQUÉ DU VÉHICULE',
    primaryColor: '#F43F5E',
    accentColor: '#06B6D4',
    gradientBg: 'from-rose-950 via-[#220710] to-[#0b0104]',
    glowClass: 'shadow-rose-500/50 border-rose-500/60 text-rose-400',
    animationType: 'truck-dashboard',
    steps: [
      '▶ Connexion au terminal de bord du tracteur routier...',
      '▶ Téléchargement de la lettre de voiture numérique...',
      '▶ Vérification du tachygraphe, pression pneus et carburant...',
      '✓ Ordre de mission prêt. Bonne route en sécurité.',
    ],
  },
  'portail-chauffeur': {
    key: 'portail-chauffeur',
    departmentNumber: 8,
    domainName: 'ESPACE CONDUCTEUR ROUTIER',
    subTitle: 'SUIVI DES PESÉES AU PONT-BASCULE & FRAIS DE ROUTE',
    badgeCode: 'TERMINAL MOBILE CONDUCTEUR',
    locationTag: 'POSTE CONDUCTEUR EN TRANSIT',
    primaryColor: '#F43F5E',
    accentColor: '#38BDF8',
    gradientBg: 'from-rose-950 via-[#220710] to-[#0b0104]',
    glowClass: 'shadow-rose-500/50 border-rose-500/60 text-rose-400',
    animationType: 'truck-dashboard',
    steps: [
      '▶ Synchronisation de l\'itinéraire officiel du corridor...',
      '▶ Contrôle des certificats de pesée au pont-bascule...',
      '▶ Préparation des déclarations d\'étape...',
      '✓ Espace Conducteur paré.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 9. MAGASIN & STOCK WMS
  // ═══════════════════════════════════════════════════════════════════════════
  'magasin-stock': {
    key: 'magasin-stock',
    departmentNumber: 9,
    domainName: 'DÉPARTEMENT MAGASIN & STOCK WMS',
    subTitle: 'RACKS ISOMÉTRIQUES, SCAN CODES-BARRES & GESTION DES ALVÉOLES',
    badgeCode: 'WMS PROTOCOL • CODE-BARRES GS1 & RFID',
    locationTag: 'ENTREPÔT LOGISTIQUE CENTRAL (ZONE CALE & PARC)',
    primaryColor: '#F59E0B',
    accentColor: '#FBBF24',
    gradientBg: 'from-amber-950 via-[#221303] to-[#0c0601]',
    glowClass: 'shadow-amber-500/50 border-amber-500/60 text-amber-400',
    animationType: 'wms-lidar',
    steps: [
      '▶ Cartographie 3D des allées, travées et racks d\'entrepôt...',
      '▶ Scan laser vertical des alvéoles de stockage...',
      '▶ Rapprochement des inventaires physiques et informatiques...',
      '✓ Système WMS prêt. Emplacements de stockage assignés.',
    ],
  },
  magasin: {
    key: 'magasin',
    departmentNumber: 9,
    domainName: 'MAGASINAGE & ENTREPOSAGE FRET',
    subTitle: 'RÉCEPTION MARCHANDISES, EMPOTAGE & DÉPOTAGE',
    badgeCode: 'WMS OPÉRATIONS • GESTION STOCKS',
    locationTag: 'PLATEFORME LOGISTIQUE PORTUAIRE',
    primaryColor: '#F59E0B',
    accentColor: '#FBBF24',
    gradientBg: 'from-amber-950 via-[#221303] to-[#0c0601]',
    glowClass: 'shadow-amber-500/50 border-amber-500/60 text-amber-400',
    animationType: 'wms-lidar',
    steps: [
      '▶ Contrôle des manifestes d\'empotage et dépotage...',
      '▶ Vérification de l\'intégrité des emballages et réserves...',
      '▶ Édition des bons d\'entrée en magasin...',
      '✓ Espace Magasin connecté.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 10. PORTAIL MAGASINIER & TERMINAL RF
  // ═══════════════════════════════════════════════════════════════════════════
  'portail-magasinier': {
    key: 'portail-magasinier',
    departmentNumber: 10,
    domainName: 'PORTAIL MAGASINIER & DOUCHETTE RF',
    subTitle: 'SCANNER DURCI DE QUAI, CODE 128/DATAMATRIX & INVENTAIRES',
    badgeCode: 'TERMINAL PORTATIF SCAN-GUN • RADIO-FRÉQUENCE',
    locationTag: 'TERMINAL PORTABLE SUR QUAI D\'ENTREPOSAGE',
    primaryColor: '#71717A',
    accentColor: '#F59E0B',
    gradientBg: 'from-zinc-950 via-[#131316] to-[#060608]',
    glowClass: 'shadow-zinc-500/50 border-zinc-500/60 text-zinc-400',
    animationType: 'rf-scan-gun',
    steps: [
      '▶ Synchronisation de la douchette RF avec la base WMS...',
      '▶ Chargement de la liste des colis à scanner en priorité...',
      '▶ Contrôle des numéros de plombs et codes scellés...',
      '✓ Douchette RF calibrée. Prêt pour le scan de quai.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 11. CYCLE DE VIE DES CONTENEURS (CONTAINER LIFECYCLE)
  // ═══════════════════════════════════════════════════════════════════════════
  'container-lifecycle': {
    key: 'container-lifecycle',
    departmentNumber: 11,
    domainName: 'DÉPARTEMENT CYCLE DE VIE CONTENEURS',
    subTitle: 'SUIVI BOUT-EN-BOUT DU CONTENEUR : PLEIN, DÉTENTION & RESTITUTION',
    badgeCode: 'ISO 6346 CONTAINER • BIC / CSC CERTIFIED',
    locationTag: 'PARC À CONTENEURS & ZONES DE RESTITUTION',
    primaryColor: '#8B5CF6',
    accentColor: '#06B6D4',
    gradientBg: 'from-purple-950 via-[#130728] to-[#04010b]',
    glowClass: 'shadow-purple-500/50 border-purple-500/60 text-purple-400',
    animationType: 'container-3d-lifecycle',
    steps: [
      '▶ Détection du numéro de série ISO du conteneur (ex: MSKU, CMAU)...',
      '▶ Suivi du statut : Navire → Quai → Magasin → Route → Dépotage...',
      '▶ Calcul des détentions (demurrage) et alertes surestaries...',
      '✓ Cycle conteneur synchronisé. Traçabilité totale assurée.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 12. PARC VÉHICULES & ENGINS LOURDS
  // ═══════════════════════════════════════════════════════════════════════════
  'parc-vehicules': {
    key: 'parc-vehicules',
    departmentNumber: 12,
    domainName: 'DÉPARTEMENT PARC & ENGINS LOURDS',
    subTitle: 'TRACTEURS, GRUES, REMORQUES & DIAGNOSTIC TÉLÉMÉTRIQUE',
    badgeCode: 'GMAO INDUSTRIELLE • ISO 55000',
    locationTag: 'CENTRE TECHNIQUE DU PARC ROULANT',
    primaryColor: '#F97316',
    accentColor: '#FB923C',
    gradientBg: 'from-orange-950 via-[#230d03] to-[#0c0401]',
    glowClass: 'shadow-orange-500/50 border-orange-500/60 text-orange-400',
    animationType: 'gmao-gears',
    steps: [
      '▶ Enclenchement de la télémétrie des tracteurs, élévateurs et grues...',
      '▶ Analyse des compteurs d\'heures et pressions hydrauliques...',
      '▶ Contrôle des visites techniques et assurances obligatoires...',
      '✓ Parc matériel opérationnel. Engins parés au service.',
    ],
  },
  parc: {
    key: 'parc',
    departmentNumber: 12,
    domainName: 'GESTION DU PARC MATÉRIEL',
    subTitle: 'DISPONIBILITÉ TECHNIQUE & AFFECTATION DES VÉHICULES',
    badgeCode: 'FLOTTE MATÉRIEL • SUIVI ENGINTÈQUE',
    locationTag: 'DIRECTION TECHNIQUE DU PARC',
    primaryColor: '#F97316',
    accentColor: '#FB923C',
    gradientBg: 'from-orange-950 via-[#230d03] to-[#0c0401]',
    glowClass: 'shadow-orange-500/50 border-orange-500/60 text-orange-400',
    animationType: 'gmao-gears',
    steps: [
      '▶ Examen de l\'état de marche de chaque équipement...',
      '▶ Évaluation du taux de disponibilité opérationnelle...',
      '▶ Planification des rotations d\'engins sur le quai...',
      '✓ Parc matériel prêt.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 13. MAINTENANCE GMAO & ATELIER
  // ═══════════════════════════════════════════════════════════════════════════
  maintenance: {
    key: 'maintenance',
    departmentNumber: 13,
    domainName: 'DÉPARTEMENT MAINTENANCE & ATELIER GMAO',
    subTitle: 'RÉVISIONS PRÉVENTIVES, INTERVENTIONS CURATIVES & PIÈCES DÉTACHÉES',
    badgeCode: 'ATELIER MÉCANIQUE • GMAO EXPERT',
    locationTag: 'ATELIER CENTRAL DE RÉPARATION LOURDE',
    primaryColor: '#EA580C',
    accentColor: '#F97316',
    gradientBg: 'from-orange-950 via-[#230d03] to-[#0c0401]',
    glowClass: 'shadow-orange-500/50 border-orange-500/60 text-orange-400',
    animationType: 'workshop-wrench',
    steps: [
      '▶ Synchronisation des Ordres de Travail (OT) prioritaires...',
      '▶ Vérification du stock de pièces de rechange au magasin technique...',
      '▶ Relevé des diagnostics et analyse vibratoire des moteurs...',
      '✓ Atelier GMAO opérationnel. Bancs d\'essai validés.',
    ],
  },
  'portail-technicien': {
    key: 'portail-technicien',
    departmentNumber: 13,
    domainName: 'PORTAIL TECHNICIEN GMAO ATELIER',
    subTitle: 'FEUILLE D\'INTERVENTION, SAISIE DU TEMPS & PIÈCES CONSOMMÉES',
    badgeCode: 'TECHNICIEN AGRÉÉ • GMAO ATELIER',
    locationTag: 'POSTE D\'INTERVENTION MÉCANIQUE',
    primaryColor: '#78716C',
    accentColor: '#F97316',
    gradientBg: 'from-stone-950 via-[#181615] to-[#080706]',
    glowClass: 'shadow-stone-500/50 border-stone-500/60 text-stone-400',
    animationType: 'workshop-wrench',
    steps: [
      '▶ Récupération de la fiche d\'intervention mécanique...',
      '▶ Contrôle de la disponibilité des filtres, courroies et pièces...',
      '▶ Enregistrement des heures atelier et validation des tests...',
      '✓ Espace Technicien prêt.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 14. FUEL GUARD & GESTION CARBURANT
  // ═══════════════════════════════════════════════════════════════════════════
  'fuel-guard': {
    key: 'fuel-guard',
    departmentNumber: 14,
    domainName: 'DÉPARTEMENT FUEL GUARD & CARBURANT',
    subTitle: 'JAUGEAGE ÉLECTRONIQUE, DÉBITMÈTRES & CONTRÔLE ANTI-SIPHONNAGE',
    badgeCode: 'FUEL GUARD • ANTI-SIPHON TELEMETRY',
    locationTag: 'STATION PRIVATIVE & CUVES DE CARBURANT PORT',
    primaryColor: '#F59E0B',
    accentColor: '#EF4444',
    gradientBg: 'from-amber-950 via-[#1e0f03] to-[#0a0501]',
    glowClass: 'shadow-amber-500/50 border-amber-500/60 text-amber-400',
    animationType: 'fuel-gauge',
    steps: [
      '▶ Sondage ultrasonique des cuves de gazole et réservoirs camions...',
      '▶ Rapprochement des consommations au km vs dotations prévues...',
      '▶ Analyse des alertes de baisse anormale et suspicion siphonnage...',
      '✓ Télémétrie carburant armée. Gestion énergétique active.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 15. QHSE & SÉCURITÉ PORTUAIRE
  // ═══════════════════════════════════════════════════════════════════════════
  'qhse-securite': {
    key: 'qhse-securite',
    departmentNumber: 15,
    domainName: 'DÉPARTEMENT QHSE & SÉCURITÉ ISPS',
    subTitle: 'CONFORMITÉ CODE ISPS, MARCHANDISES DANGEREUSES IMDG & ZONES',
    badgeCode: 'ISPS CODE • ISO 45001 & ISO 14001',
    locationTag: 'POSTE CENTRAL DE CONTRÔLE & SÛRETÉ (PC SÉCURITÉ)',
    primaryColor: '#EF4444',
    accentColor: '#F87171',
    gradientBg: 'from-red-950 via-[#210606] to-[#0c0101]',
    glowClass: 'shadow-red-500/50 border-red-500/60 text-red-400',
    animationType: 'isps-shield',
    steps: [
      '▶ Déploiement du bouclier de sûreté portuaire Code ISPS...',
      '▶ Détection thermique et contrôle des marchandises dangereuses IMDG...',
      '▶ Contrôle des protocoles de port des EPI et autorisations d\'accès...',
      '✓ Bouclier QHSE actif. Intégrité des zones portuaires certifiée.',
    ],
  },
  qhse: {
    key: 'qhse',
    departmentNumber: 15,
    domainName: 'QUALITÉ, HYGIÈNE, SÉCURITÉ & ENVIRONNEMENT',
    subTitle: 'AUDITS DE CONFORMITÉ & PLANS DE PRÉVENTION',
    badgeCode: 'QHSE AUDIT • VEILLE RÈGLEMENTAIRE',
    locationTag: 'BUREAU DE PRÉVENTION DES RISQUES',
    primaryColor: '#EF4444',
    accentColor: '#F87171',
    gradientBg: 'from-red-950 via-[#210606] to-[#0c0101]',
    glowClass: 'shadow-red-500/50 border-red-500/60 text-red-400',
    animationType: 'isps-shield',
    steps: [
      '▶ Revue des fiches d\'accidents et presqu\'accidents...',
      '▶ Contrôle des registres de vérification périodique des extincteurs...',
      '▶ Évaluation de la conformité environnementale sur les quais...',
      '✓ Registre QHSE à jour.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 16. PORTAIL QHSE TERRAIN & INCIDENTS
  // ═══════════════════════════════════════════════════════════════════════════
  'portail-qhse': {
    key: 'portail-qhse',
    departmentNumber: 16,
    domainName: 'PORTAIL QHSE TERRAIN & ALERTE LIVE',
    subTitle: 'SIGNALEMENT IMMÉDIAT DES DANGERS SUR LE QUAI ET MAIN COURANTE',
    badgeCode: 'SIGNALEMENT RAPIDE • SÉCURITÉ ACTIVE',
    locationTag: 'PATROUILLE DE SÛRETÉ SUR LE QUAI',
    primaryColor: '#E11D48',
    accentColor: '#EF4444',
    gradientBg: 'from-rose-950 via-[#23050c] to-[#0c0103]',
    glowClass: 'shadow-rose-600/50 border-rose-600/60 text-rose-400',
    animationType: 'incident-beacon',
    steps: [
      '▶ Connexion au canal prioritaire des urgences de quai...',
      '▶ Géolocalisation des équipes de sûreté et patrouilles...',
      '▶ Ouverture de la main courante électronique de sécurité...',
      '✓ Espace QHSE Terrain paré.',
    ],
  },
  'port-incidents': {
    key: 'port-incidents',
    departmentNumber: 16,
    domainName: 'GESTION DES INCIDENTS PORTUAIRES',
    subTitle: 'DÉCLARATION, ANALYSE DES CAUSES RACINES & ACTIONS CORRECTIVES',
    badgeCode: 'INCIDENTS TRACKER • AUDIT QUAI',
    locationTag: 'CELLULE D\'ANALYSE DES INCIDENTS',
    primaryColor: '#E11D48',
    accentColor: '#F59E0B',
    gradientBg: 'from-rose-950 via-[#23050c] to-[#0c0103]',
    glowClass: 'shadow-rose-600/50 border-rose-600/60 text-rose-400',
    animationType: 'incident-beacon',
    steps: [
      '▶ Réception des signalements d\'avaries matérielles...',
      '▶ Déclenchement de l\'arbre des causes et expertise assurances...',
      '▶ Enregistrement des mesures conservatoires...',
      '✓ Registre des incidents connecté.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 17. RH & CAPITAL HUMAIN
  // ═══════════════════════════════════════════════════════════════════════════
  'rh-personnel': {
    key: 'rh-personnel',
    departmentNumber: 17,
    domainName: 'DÉPARTEMENT RESSOURCES HUMAINES',
    subTitle: 'GESTION DU PERSONNEL, POINTAGES BIOMÉTRIQUES & BULLETIN PAIE',
    badgeCode: 'OHADA SOCIAL • CONVENTION COLLECTIVE',
    locationTag: 'DIRECTION DES RESSOURCES HUMAINES (RH)',
    primaryColor: '#EC4899',
    accentColor: '#F472B6',
    gradientBg: 'from-pink-950 via-[#220716] to-[#0c0107]',
    glowClass: 'shadow-pink-500/50 border-pink-500/60 text-pink-400',
    animationType: 'biometric-ring',
    steps: [
      '▶ Synchronisation des terminaux biométriques de pointage aux portes...',
      '▶ Contrôle des plannings de présence, retards et heures supplémentaires...',
      '▶ Calcul des variables de rémunération et cotisations sociales CNPS...',
      '✓ Espace RH ouvert. Données du personnel synchronisées.',
    ],
  },
  rh: {
    key: 'rh',
    departmentNumber: 17,
    domainName: 'ADMINISTRATION DU PERSONNEL & CONTRATS',
    subTitle: 'DOSSIERS INDIVIDUELS, MÉDECINE DU TRAVAIL & CONTRATS',
    badgeCode: 'RH PERSONNEL • GESTION TALENTS',
    locationTag: 'SERVICE DE L\'ADMINISTRATION RH',
    primaryColor: '#EC4899',
    accentColor: '#F472B6',
    gradientBg: 'from-pink-950 via-[#220716] to-[#0c0107]',
    glowClass: 'shadow-pink-500/50 border-pink-500/60 text-pink-400',
    animationType: 'biometric-ring',
    steps: [
      '▶ Vérification des dates de renouvellement des contrats...',
      '▶ Contrôle des visites médicales d\'aptitude des dockers...',
      '▶ Préparation des états de déclaration annuelle...',
      '✓ Dossiers agents à jour.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 18. PORTAIL EMPLOYÉ & MON ESPACE
  // ═══════════════════════════════════════════════════════════════════════════
  'portail-employe': {
    key: 'portail-employe',
    departmentNumber: 18,
    domainName: 'MON ESPACE EMPLOYÉ & AGENT',
    subTitle: 'CONSULTATION BULLETINS, DEMANDES DE CONGÉS & ATTESTATIONS',
    badgeCode: 'BADGE RFID AGENT • ESPACE PRIVÉ',
    locationTag: 'PORTAIL INDIVIDUEL DE L\'AGENT',
    primaryColor: '#84CC16',
    accentColor: '#10B981',
    gradientBg: 'from-lime-950 via-[#101c03] to-[#040801]',
    glowClass: 'shadow-lime-500/50 border-lime-500/60 text-lime-400',
    animationType: 'employee-badge',
    steps: [
      '▶ Reconnaissance du badge RFID de l\'employé...',
      '▶ Chargement du solde de congés payés et compteurs d\'heures...',
      '▶ Mise à disposition des derniers bulletins de paie numérisés...',
      '✓ Votre espace personnel est prêt. Bienvenue.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 19. CHEF DE PERSONNEL & RELÈVES DES QUARTS
  // ═══════════════════════════════════════════════════════════════════════════
  'chef-personnel': {
    key: 'chef-personnel',
    departmentNumber: 19,
    domainName: 'DÉPARTEMENT CHEF DU PERSONNEL',
    subTitle: 'PLANIFICATION DES RELÈVES 3X8 & AFFECTATION DES DOCKERS',
    badgeCode: 'SHIFTS 3X8 • COMMANDEMENT QUAIS',
    locationTag: 'BUREAU DE COMMANDEMENT DES ÉQUIPES DE QUAI',
    primaryColor: '#F43F5E',
    accentColor: '#8B5CF6',
    gradientBg: 'from-rose-950 via-[#1a0520] to-[#08020d]',
    glowClass: 'shadow-rose-500/50 border-rose-500/60 text-rose-400',
    animationType: 'shift-clock',
    steps: [
      '▶ Vérification des présences à la relève de quart (Matin, Soir, Nuit)...',
      '▶ Affectation des dockers aux navires en cours de déchargement...',
      '▶ Contrôle des heures de vacation et primes d\'intempéries...',
      '✓ Planification des relèves validée. Équipes sur le quai.',
    ],
  },
  'shift-planning': {
    key: 'shift-planning',
    departmentNumber: 19,
    domainName: 'PLANIFICATION DES HORAIRES ET QUARTS',
    subTitle: 'TABLEAU DE SERVICE MENSUEL & ROTATION DES ÉQUIPES',
    badgeCode: 'ROSTER ENGINE • PLANNING 24/7',
    locationTag: 'SERVICE DE PLANIFICATION DES HORAIRES',
    primaryColor: '#F43F5E',
    accentColor: '#F59E0B',
    gradientBg: 'from-rose-950 via-[#1a0520] to-[#08020d]',
    glowClass: 'shadow-rose-500/50 border-rose-500/60 text-rose-400',
    animationType: 'shift-clock',
    steps: [
      '▶ Calcul des grilles de roulement 24h/24 et 7j/7...',
      '▶ Respect des temps de repos légaux et conventions collectives...',
      '▶ Édition des plannings prévisionnels par équipe...',
      '✓ Grille des quarts prête.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 20. PORTAIL FRAIS & INDEMNITÉS
  // ═══════════════════════════════════════════════════════════════════════════
  'portail-frais': {
    key: 'portail-frais',
    departmentNumber: 20,
    domainName: 'PORTAIL FRAIS DE MISSION & AVANCES',
    subTitle: 'TÉLÉCHARGEMENT REÇUS, INDEMNITÉS ROUTE & BORDEREAUX SCELLÉS',
    badgeCode: 'JUSTIFICATIFS SÉCURISÉS • REMBOURSEMENT RAPIDE',
    locationTag: 'BUREAU DE LIQUIDATION DES FRAIS DE MISSION',
    primaryColor: '#0D9488',
    accentColor: '#10B981',
    gradientBg: 'from-teal-950 via-[#031c19] to-[#010908]',
    glowClass: 'shadow-teal-500/50 border-teal-500/60 text-teal-400',
    animationType: 'expense-voucher',
    steps: [
      '▶ Numérisation et extraction OCR des reçus de péage et hôtel...',
      '▶ Calcul des forfaits d\'indemnités kilométriques et repas...',
      '▶ Transmission du bordereau scellé au service comptabilité...',
      '✓ Note de frais prête pour le virement.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 21. HUB COLLABORATIF & MESSAGERIE D'ÉQUIPE
  // ═══════════════════════════════════════════════════════════════════════════
  chat: {
    key: 'chat',
    departmentNumber: 21,
    domainName: 'HUB COLLABORATIF & COMMUNICATIONS',
    subTitle: 'SALONS DE QUAI, CANAUX FLOTTE & DISCUSSIONS MULTI-ÉQUIPES',
    badgeCode: 'WEBSOCKET TEMPS RÉEL • RADIO INTERNE',
    locationTag: 'CENTRE DE COMMUNICATION NUMÉRIQUE CADC',
    primaryColor: '#22C55E',
    accentColor: '#EAB308',
    gradientBg: 'from-green-950 via-[#051c0e] to-[#010803]',
    glowClass: 'shadow-green-500/50 border-green-500/60 text-green-400',
    animationType: 'synergy-constellation',
    steps: [
      '▶ Établissement du canal WebSocket temps réel chiffré...',
      '▶ Synchronisation des salons d\'équipe (Quai, Flotte, Compta, Direction)...',
      '▶ Détection de la présence des agents et conducteurs en ligne...',
      '✓ Canaux collaboratifs opérationnels. Équipes en direct.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 22. PORTAIL COLLABORATEUR CENTRAL
  // ═══════════════════════════════════════════════════════════════════════════
  'portail-collaborateur': {
    key: 'portail-collaborateur',
    departmentNumber: 22,
    domainName: 'HUB CENTRAL COLLABORATEUR',
    subTitle: 'CARREFOUR DES MISSIONS, DOSSIERS PARTAGÉS & AGENDAS ÉQUIPE',
    badgeCode: 'HUB CENTRAL • RÔLE COLLABORATEUR',
    locationTag: 'ESPACE DE TRAVAIL UNIFIÉ MULTI-DÉPARTEMENTS',
    primaryColor: '#EAB308',
    accentColor: '#22C55E',
    gradientBg: 'from-yellow-950 via-[#1e1503] to-[#0a0701]',
    glowClass: 'shadow-yellow-500/50 border-yellow-500/60 text-yellow-400',
    animationType: 'collaborator-hub',
    steps: [
      '▶ Initialisation de votre bureau virtuel personnalisé...',
      '▶ Rapprochement des dossiers partagés entre services...',
      '▶ Vérification des notifications prioritaires et jalons du jour...',
      '✓ Hub Collaborateur activé. Bienvenue.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 23. ESPACE CLIENT & PARTENAIRES B2B
  // ═══════════════════════════════════════════════════════════════════════════
  'client-b2b': {
    key: 'client-b2b',
    departmentNumber: 23,
    domainName: 'DÉPARTEMENT RELATIONS CLIENTS & B2B',
    subTitle: 'PORTAIL CLIENT PRIVILÈGE, SUIVI EXPÉDITIONS & COMMANDES',
    badgeCode: 'B2B SECURE GATEWAY • SSL 256-BIT',
    locationTag: 'PASSERELLE PARTENAIRES & IMPORT/EXPORT',
    primaryColor: '#14B8A6',
    accentColor: '#2DD4BF',
    gradientBg: 'from-teal-950 via-[#031d1b] to-[#010908]',
    glowClass: 'shadow-teal-500/50 border-teal-500/60 text-teal-400',
    animationType: 'b2b-gateway',
    steps: [
      '▶ Authentification du compte partenaire et vérification des mandats...',
      '▶ Chargement du suivi satellite en temps réel des cargaisons...',
      '▶ Synchronisation des cotations en cours et factures électroniques...',
      '✓ Passerelle B2B déverrouillée. Vos flux logistiques sont à portée.',
    ],
  },
  'client-portal': {
    key: 'client-portal',
    departmentNumber: 23,
    domainName: 'PORTAIL CLIENT IMPORT-EXPORT',
    subTitle: 'VISIBILITÉ BOUT-EN-BOUT DU CHARGEMENT JUSQU\'AU DÉPOTAGE',
    badgeCode: 'PORTAIL CLIENTS PRIVILÈGE',
    locationTag: 'ESPACE SELF-SERVICE LOGISTIQUE',
    primaryColor: '#14B8A6',
    accentColor: '#2DD4BF',
    gradientBg: 'from-teal-950 via-[#031d1b] to-[#010908]',
    glowClass: 'shadow-teal-500/50 border-teal-500/60 text-teal-400',
    animationType: 'b2b-gateway',
    steps: [
      '▶ Récupération des numéros de booking et références BESC...',
      '▶ Actualisation des heures estimées d\'arrivée (ETA / ETD)...',
      '▶ Téléchargement des justificatifs d\'empotage...',
      '✓ Espace Client prêt.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 24. COTATIONS & DIRECTION COMMERCIALE
  // ═══════════════════════════════════════════════════════════════════════════
  cotations: {
    key: 'cotations',
    departmentNumber: 24,
    domainName: 'DÉPARTEMENT COMMERCIAL & COTATIONS',
    subTitle: 'TARIFICATION FRET, BAREMES D\'ACCONAGE & SIMULATEUR DE MARGE',
    badgeCode: 'GRILLE TARIFAIRE • CRM COMMERCIAL',
    locationTag: 'DIRECTION COMMERCIALE & DÉVELOPPEMENT',
    primaryColor: '#EAB308',
    accentColor: '#F59E0B',
    gradientBg: 'from-yellow-950 via-[#1e1302] to-[#090601]',
    glowClass: 'shadow-yellow-500/50 border-yellow-500/60 text-yellow-400',
    animationType: 'pricing-scale',
    steps: [
      '▶ Chargement des grilles de prix au conteneur et à la tonne...',
      '▶ Simulation des frais de transit, douane et magasinage...',
      '▶ Génération de l\'offre commerciale personnalisée en FCFA...',
      '✓ Devis commercial prêt à émettre.',
    ],
  },
  'portail-commercial': {
    key: 'portail-commercial',
    departmentNumber: 24,
    domainName: 'ESPACE COMMERCIAL & NÉGOCIATION',
    subTitle: 'PIPELINE AFFAIRES, COMPTES CLÉS & COMMISSIONS',
    badgeCode: 'COMMERCIAL TERRAIN • PORT CADC',
    locationTag: 'BUREAU DES VENTES MARITIMES',
    primaryColor: '#EAB308',
    accentColor: '#10B981',
    gradientBg: 'from-yellow-950 via-[#1e1302] to-[#090601]',
    glowClass: 'shadow-yellow-500/50 border-yellow-500/60 text-yellow-400',
    animationType: 'pricing-scale',
    steps: [
      '▶ Actualisation des opportunités de trafic maritime...',
      '▶ Vérification des encours clients et limites de crédit...',
      '▶ Suivi des relances et des propositions contractuelles...',
      '✓ Espace Commercial paré.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 25. ACHATS & FOURNISSEURS (PROCUREMENT)
  // ═══════════════════════════════════════════════════════════════════════════
  procurement: {
    key: 'procurement',
    departmentNumber: 25,
    domainName: 'DÉPARTEMENT ACHATS & APPROVISIONNEMENTS',
    subTitle: 'BONS DE COMMANDE, ÉVALUATION DES FOURNISSEURS & RÉCEPTIONS',
    badgeCode: 'PROCUREMENT ENGINE • HOMOLOGATION PRESTATAIRES',
    locationTag: 'DIRECTION DES ACHATS & MOYENS GÉNÉRAUX',
    primaryColor: '#10B981',
    accentColor: '#34D399',
    gradientBg: 'from-emerald-950 via-[#031d14] to-[#010905]',
    glowClass: 'shadow-emerald-500/50 border-emerald-500/60 text-emerald-400',
    animationType: 'procurement-cart',
    steps: [
      '▶ Contrôle des demandes d\'achat (DA) validées par la direction...',
      '▶ Comparaison des offres fournisseurs et délais de livraison...',
      '▶ Émission des bons de commande officiels avec visa budgétaire...',
      '✓ Centrale d\'achats connectée. Commandes prêtes à valider.',
    ],
  },
  purchase: {
    key: 'purchase',
    departmentNumber: 25,
    domainName: 'APPROVISIONNEMENTS & MOYENS GÉNÉRAUX',
    subTitle: 'GESTION DES PRESTATAIRES ET STOCKS DE FONCTIONNEMENT',
    badgeCode: 'ACHATS MATÉRIEL • FOURNISSEURS',
    locationTag: 'SERVICE DES ACHATS',
    primaryColor: '#10B981',
    accentColor: '#34D399',
    gradientBg: 'from-emerald-950 via-[#031d14] to-[#010905]',
    glowClass: 'shadow-emerald-500/50 border-emerald-500/60 text-emerald-400',
    animationType: 'procurement-cart',
    steps: [
      '▶ Examen des devis fournisseurs en attente...',
      '▶ Suivi des livraisons et réceptions magasins...',
      '▶ Rapprochement factures / bons de livraison...',
      '✓ Module Approvisionnements prêt.',
    ],
  },
  fournisseurs: {
    key: 'fournisseurs',
    departmentNumber: 25,
    domainName: 'ANNUAIRE FOURNISSEURS & PRESTATAIRES',
    subTitle: 'CONTRATS CADRES, AUDITS QUALITÉ & CONDITIONS DE PAIEMENT',
    badgeCode: 'BASE FOURNISSEURS AGRÉÉS',
    locationTag: 'BUREAU DE CONTRÔLE DES TIERS',
    primaryColor: '#10B981',
    accentColor: '#F59E0B',
    gradientBg: 'from-emerald-950 via-[#031d14] to-[#010905]',
    glowClass: 'shadow-emerald-500/50 border-emerald-500/60 text-emerald-400',
    animationType: 'procurement-cart',
    steps: [
      '▶ Vérification des attestations fiscales et bancaires des prestataires...',
      '▶ Notation de la conformité et des délais constatés...',
      '▶ Suivi des contrats cadres actifs...',
      '✓ Annuaire Fournisseurs disponible.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 26. FISCALITÉ CAMEROUN & DGI
  // ═══════════════════════════════════════════════════════════════════════════
  'fiscalite-cameroun': {
    key: 'fiscalite-cameroun',
    departmentNumber: 26,
    domainName: 'DÉPARTEMENT FISCALITÉ CAMEROUN & DGI',
    subTitle: 'DÉCLARATIONS FISCALES CGI, TVA 19.25% & RETENUES À LA SOURCE',
    badgeCode: 'DGI CAMEROUN • CGI CEMAC',
    locationTag: 'DIRECTION DES AFFAIRES FISCALES & JURIDIQUES',
    primaryColor: '#8B5CF6',
    accentColor: '#10B981',
    gradientBg: 'from-violet-950 via-[#130728] to-[#04010b]',
    glowClass: 'shadow-violet-500/50 border-violet-500/60 text-violet-400',
    animationType: 'tax-dgi',
    steps: [
      '▶ Interconnexion avec le portail officiel de la DGI Cameroun...',
      '▶ Calcul automatique de la TVA (19,25%), acomptes IS et TSR...',
      '▶ Rapprochement avec les écritures du Grand Livre SYSCOHADA...',
      '✓ Télédéclarations fiscales prêtes. Conformité DGI certifiée.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 27. DÉCISIONNEL & REPORTING BI
  // ═══════════════════════════════════════════════════════════════════════════
  'reports-bi': {
    key: 'reports-bi',
    departmentNumber: 27,
    domainName: 'DÉPARTEMENT DÉCISIONNEL & REPORTING BI',
    subTitle: 'PRISME HOLOGRAPHIQUE 3D, CUBES OLAP & PRÉVISIONS LOGISTIQUES',
    badgeCode: 'BUSINESS INTELLIGENCE • DATA WAREHOUSE',
    locationTag: 'CENTRE DÉCISIONNEL STRATÉGIQUE (DATA LAB)',
    primaryColor: '#A855F7',
    accentColor: '#C084FC',
    gradientBg: 'from-purple-950 via-[#1e072a] to-[#0a0110]',
    glowClass: 'shadow-purple-500/50 border-purple-500/60 text-purple-400',
    animationType: 'bi-prism',
    steps: [
      '▶ Compilation des flux multidimensionnels Navires, Flotte et Douane...',
      '▶ Calcul des métriques de temps de séjour (dwell time) et ratios OHADA...',
      '▶ Déploiement des graphiques décisionnels et courbes prédictives...',
      '✓ Matrice BI opérationnelle. Données exécutives prêtes.',
    ],
  },
  bi: {
    key: 'bi',
    departmentNumber: 27,
    domainName: 'TABLEAU DE BORD STRATÉGIQUE EXÉCUTIF',
    subTitle: 'INDICATEURS CLÉS DE PERFORMANCE & VUE CONSOLIDÉE DIRECTION',
    badgeCode: 'KPI SUITE • DIRECTOIRE CADC',
    locationTag: 'SALLE DU DIRECTOIRE GÉNÉRAL',
    primaryColor: '#A855F7',
    accentColor: '#F59E0B',
    gradientBg: 'from-purple-950 via-[#1e072a] to-[#0a0110]',
    glowClass: 'shadow-purple-500/50 border-purple-500/60 text-purple-400',
    animationType: 'bi-prism',
    steps: [
      '▶ Rapprochement des volumes conteneurs EVP traités...',
      '▶ Mesure de la rentabilité opérationnelle par axe de fret...',
      '▶ Synthèse du chiffre d\'affaires consolidé...',
      '✓ Tableau de bord stratégique prêt.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 28. GOUVERNANCE & ADMINISTRATION SAAS CADC
  // ═══════════════════════════════════════════════════════════════════════════
  'admin-tenant': {
    key: 'admin-tenant',
    departmentNumber: 28,
    domainName: 'DÉPARTEMENT GOUVERNANCE & TENANT',
    subTitle: 'MATRICE RBAC, ACCRÉDITATIONS, AGENCES & PISTE D\'AUDIT',
    badgeCode: 'RBAC MULTI-TENANT • CONFORMITÉ SYSTÈME',
    locationTag: 'CENTRE DE CONTRÔLE GOUVERNANCE & SÉCURITÉ SYSTÈME',
    primaryColor: '#64748B',
    accentColor: '#D946EF',
    gradientBg: 'from-slate-950 via-[#111622] to-[#05070a]',
    glowClass: 'shadow-slate-500/50 border-slate-500/60 text-slate-400',
    animationType: 'rbac-matrix',
    steps: [
      '▶ Chargement de la matrice granulaire des rôles et habilitations...',
      '▶ Contrôle de l\'étanchéité multi-tenant et des politiques d\'isolation...',
      '▶ Inspection des journaux d\'audit et certificats de signature...',
      '✓ Console de gouvernance déverrouillée. Administration opérationnelle.',
    ],
  },
  'admin-saas': {
    key: 'admin-saas',
    departmentNumber: 28,
    domainName: 'CONSOLE ADMINISTRATION CADC HQ',
    subTitle: 'SUPERVISION MULTI-LOCATAIRES, LICENCES & CLUSTERS CLOUD',
    badgeCode: 'CORE SYSTEM • NIVEAU SUPERADMIN CADC',
    locationTag: 'CODE AXIS DIGITAL CAMEROUN (SIÈGE)',
    primaryColor: '#D946EF',
    accentColor: '#F59E0B',
    gradientBg: 'from-fuchsia-950 via-[#260424] to-[#0d010c]',
    glowClass: 'shadow-fuchsia-500/50 border-fuchsia-500/60 text-fuchsia-400',
    animationType: 'rbac-matrix',
    steps: [
      '▶ Vérification de l\'intégrité des bases PostgreSQL et brokers...',
      '▶ Contrôle de charge des API FastAPI et nœuds de calcul...',
      '▶ Supervision de l\'ensemble des entreprises hébergées...',
      '✓ Console SaaS CADC active.',
    ],
  },
  admin: {
    key: 'admin',
    departmentNumber: 28,
    domainName: 'ADMINISTRATION & SÉCURITÉ SYSTÈME',
    subTitle: 'PARAMÈTRES GÉNÉRAUX, SESSIONS & CONTRÔLE D\'ACCÈS',
    badgeCode: 'ADMIN SYSTÈME • HABILITATIONS',
    locationTag: 'CENTRE D\'ADMINISTRATION GÉNÉRALE',
    primaryColor: '#64748B',
    accentColor: '#94A3B8',
    gradientBg: 'from-slate-950 via-[#111622] to-[#05070a]',
    glowClass: 'shadow-slate-500/50 border-slate-500/60 text-slate-400',
    animationType: 'rbac-matrix',
    steps: [
      '▶ Vérification des accréditations administrateur...',
      '▶ Chargement des référentiels système d\'entreprise...',
      '▶ Contrôle des jetons de session actifs...',
      '✓ Administration système prête.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 29. AMÉNAGEMENT PORTUAIRE & DOMAINE PUBLIC (département autonome)
  //     Registre des actes (schéma directeur, titre domanial, concession, PIP),
  //     pas d'exécution de travaux : les étapes décrivent une lecture du
  //     registre, jamais un chantier fictif.
  // ═══════════════════════════════════════════════════════════════════════════
  'amenagement-portuaire': {
    key: 'amenagement-portuaire',
    departmentNumber: 29,
    domainName: 'DÉPARTEMENT AMÉNAGEMENT PORTUAIRE & DOMAINE PUBLIC',
    subTitle: 'SCHÉMAS DIRECTEURS, DOMAINE PUBLIC, GROS ŒUVRE & CONCESSIONS — DOUALA, KRIBI, LIMBÉ',
    badgeCode: 'REGISTRE DES ACTES D\'AMÉNAGEMENT • AUTORITÉ PORTUAIRE',
    locationTag: 'PLAN DE MASSE DU PORT • ARRÊTÉ D\'AFFECTATION',
    primaryColor: '#0E7490',
    accentColor: '#67E8F9',
    gradientBg: 'from-cyan-950 via-[#04222c] to-[#01090c]',
    glowClass: 'shadow-cyan-600/50 border-cyan-600/60 text-cyan-300',
    animationType: 'port-blueprint',
    steps: [
      '▶ Ouverture du registre des actes d\'aménagement (Douala, Kribi, Limbé)...',
      '▶ Raccordement aux nomenclatures du domaine public et des ouvrages...',
      '▶ Lecture des schémas directeurs, titres domaniaux & concessions saisies...',
      '✓ Département aménagement prêt. Seules les données saisies sont affichées.',
    ],
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // TRANSVERSAL : DASHBOARD GLOBAL & COCKPIT NAVIRE → CLIENT
  // ═══════════════════════════════════════════════════════════════════════════
  dashboard: {
    key: 'dashboard',
    departmentNumber: 0,
    domainName: 'COCKPIT GLOBAL EVO-LOG',
    subTitle: 'SYNTHÈSE INTÉGRÉE NAVIRE → CLIENT & SUPERVISION OPÉRATIONNELLE',
    badgeCode: 'CADC ERP • 28 DÉPARTEMENTS INTÉGRÉS',
    locationTag: 'DIRECTION GÉNÉRALE & SALLE DES OPÉRATIONS',
    primaryColor: '#6366F1',
    accentColor: '#F59E0B',
    gradientBg: 'from-indigo-950 via-[#0a0e28] to-[#02040c]',
    glowClass: 'shadow-indigo-500/50 border-indigo-500/60 text-indigo-400',
    animationType: 'strategic-compass',
    steps: [
      '▶ Agrégation des flux opérationnels des 28 départements métiers...',
      '▶ Synchronisation des alertes en direct et indicateurs clés de performance...',
      '▶ Déploiement de la vue transversale consolidée de l\'entreprise...',
      '✓ Cockpit Global déployé. Bienvenue sur EVO-LOG SaaS.',
    ],
  },
};

/**
 * Résolution intelligente de n'importe quelle route ou clé de module vers son département
 */
export function resolveDomainLoadingConfig(routeOrKey: string): DomainLoadingConfig {
  const clean = routeOrKey.replace(/^\/+/, '').split('/')[0] || 'dashboard';

  // 1. Correspondance directe
  if (DOMAIN_LOADING_CONFIGS[clean]) {
    return DOMAIN_LOADING_CONFIGS[clean];
  }

  // 2. Mappages fins vers les 29 départements
  // Dpt 29 : Aménagement Portuaire & Domaine Public. La clé canonique
  // « amenagement-portuaire » tombe déjà dans la correspondance directe ci
  // dessus ; cette règle rattrape la variante « amenagement » (nom du module
  // dans le catalogue de permissions backend et alias legacy de modulePalette),
  // qu'aucune règle mot-clé plus bas ne reconnaîtrait.
  if (clean.includes('amenagement')) {
    return DOMAIN_LOADING_CONFIGS['amenagement-portuaire'];
  }
  // Dpt 1 : Comptabilité OHADA
  if (clean.includes('compta') || clean.includes('syscohada') || clean.includes('journal') || clean.includes('grand-livre') || clean.includes('cloture')) {
    return DOMAIN_LOADING_CONFIGS['comptabilite-ohada'];
  }
  // Dpt 2 : Finance OHADA
  if (clean.includes('finance') || clean.includes('tresorerie') || clean.includes('banque') || clean.includes('encaissement') || clean.includes('facture')) {
    return DOMAIN_LOADING_CONFIGS['finance-ohada'];
  }
  // Dpt 3 : Port Operations
  if (clean.includes('port-operations') || clean.includes('navire') || clean.includes('escale') || clean.includes('control-tower')) {
    return DOMAIN_LOADING_CONFIGS['port-operations'];
  }
  // Dpt 4 : Acconage
  if (clean.includes('acconage') || clean.includes('quai') || clean.includes('manutention') || clean.includes('weighbridge')) {
    return DOMAIN_LOADING_CONFIGS['acconage'];
  }
  // Dpt 5 : Transit & GUCE
  if (clean.includes('transit') || clean.includes('guce') || clean.includes('bill-of-loading') || clean.includes('connaissement')) {
    return DOMAIN_LOADING_CONFIGS['transit-douane'];
  }
  // Dpt 6 : Douane réelle & Déclarant
  if (clean.includes('customs') || clean.includes('declarant') || clean.includes('douane') || clean.includes('dum') || clean.includes('bae')) {
    return DOMAIN_LOADING_CONFIGS['real-customs'];
  }
  // Dpt 7 : Transport & Flotte
  if (clean.includes('transport') || clean.includes('flotte') || clean.includes('tracking') || clean.includes('gps') || clean.includes('convoi')) {
    return DOMAIN_LOADING_CONFIGS['transport-flotte'];
  }
  // Dpt 8 : Chauffeur
  if (clean.includes('chauffeur') || clean.includes('conducteur') || clean.includes('mobile-chauffeur')) {
    return DOMAIN_LOADING_CONFIGS['chauffeur'];
  }
  // Dpt 9 : Magasin & Stock
  if (clean.includes('magasin-stock') || clean.includes('magasin') || clean.includes('stock') || clean.includes('wms') || clean.includes('entrepot') || clean.includes('reception')) {
    return DOMAIN_LOADING_CONFIGS['magasin-stock'];
  }
  // Dpt 10 : Portail Magasinier
  if (clean.includes('magasinier') || clean.includes('scan-gun') || clean.includes('douchette')) {
    return DOMAIN_LOADING_CONFIGS['portail-magasinier'];
  }
  // Dpt 11 : Cycle conteneurs
  if (clean.includes('container') || clean.includes('conteneur') || clean.includes('demurrage')) {
    return DOMAIN_LOADING_CONFIGS['container-lifecycle'];
  }
  // Dpt 12 : Parc Véhicules
  if (clean.includes('parc') || clean.includes('vehicule') || clean.includes('engin')) {
    return DOMAIN_LOADING_CONFIGS['parc-vehicules'];
  }
  // Dpt 13 : Maintenance GMAO
  if (clean.includes('maintenance') || clean.includes('gmao') || clean.includes('technicien') || clean.includes('atelier')) {
    return DOMAIN_LOADING_CONFIGS['maintenance'];
  }
  // Dpt 14 : Carburant
  if (clean.includes('fuel') || clean.includes('carburant') || clean.includes('gazole')) {
    return DOMAIN_LOADING_CONFIGS['fuel-guard'];
  }
  // Dpt 15 : QHSE Sécurité
  if (clean.includes('qhse-securite') || clean.includes('qhse') || clean.includes('securite') || clean.includes('compliance') || clean.includes('isps')) {
    return DOMAIN_LOADING_CONFIGS['qhse-securite'];
  }
  // Dpt 16 : Incidents portuaires
  if (clean.includes('incident') || clean.includes('alert') || clean.includes('danger')) {
    return DOMAIN_LOADING_CONFIGS['portail-qhse'];
  }
  // Dpt 17 : RH & Personnel
  if (clean.includes('rh') || clean.includes('personnel') || clean.includes('paie') || clean.includes('social')) {
    return DOMAIN_LOADING_CONFIGS['rh-personnel'];
  }
  // Dpt 18 : Portail Employé
  if (clean.includes('employe') || clean.includes('agent') || clean.includes('mon-espace')) {
    return DOMAIN_LOADING_CONFIGS['portail-employe'];
  }
  // Dpt 19 : Chef Personnel & Quarts
  if (clean.includes('chef-personnel') || clean.includes('shift') || clean.includes('releve') || clean.includes('quart')) {
    return DOMAIN_LOADING_CONFIGS['chef-personnel'];
  }
  // Dpt 20 : Frais & Indemnités
  if (clean.includes('frais') || clean.includes('indemnite') || clean.includes('per-diem')) {
    return DOMAIN_LOADING_CONFIGS['portail-frais'];
  }
  // Dpt 21 : Hub Collaboratif & Chat
  if (clean.includes('chat') || clean.includes('message') || clean.includes('discussion') || clean.includes('canal')) {
    return DOMAIN_LOADING_CONFIGS['chat'];
  }
  // Dpt 22 : Portail Collaborateur
  if (clean.includes('collaborat') || clean.includes('hub')) {
    return DOMAIN_LOADING_CONFIGS['portail-collaborateur'];
  }
  // Dpt 23 : Client B2B
  if (clean.includes('client') || clean.includes('b2b') || clean.includes('portal')) {
    return DOMAIN_LOADING_CONFIGS['client-b2b'];
  }
  // Dpt 24 : Commercial & Cotations
  if (clean.includes('cotation') || clean.includes('commercial') || clean.includes('tarif') || clean.includes('pricing') || clean.includes('devis')) {
    return DOMAIN_LOADING_CONFIGS['cotations'];
  }
  // Dpt 25 : Achats & Fournisseurs
  if (clean.includes('purchase') || clean.includes('procurement') || clean.includes('fournisseur') || clean.includes('achat') || clean.includes('supplier')) {
    return DOMAIN_LOADING_CONFIGS['procurement'];
  }
  // Dpt 26 : Fiscalité DGI
  if (clean.includes('fiscal') || clean.includes('dgi') || clean.includes('impot') || clean.includes('tax')) {
    return DOMAIN_LOADING_CONFIGS['fiscalite-cameroun'];
  }
  // Dpt 27 : BI & Décisionnel
  if (clean.includes('bi') || clean.includes('report') || clean.includes('analytics') || clean.includes('stat')) {
    return DOMAIN_LOADING_CONFIGS['reports-bi'];
  }
  // Dpt 28 : Gouvernance & Admin
  if (clean.includes('admin') || clean.includes('tenant') || clean.includes('saas') || clean.includes('setting') || clean.includes('role')) {
    return DOMAIN_LOADING_CONFIGS['admin-tenant'];
  }

  return DOMAIN_LOADING_CONFIGS.dashboard;
}

/**
 * Écrans de chargement dont la clé n'est NI une entrée de MODULE_PALETTE NI un
 * LEGACY_ALIAS : sans ce pont, getModulePalette() retomberait sur le dashboard
 * (indigo) et le module afficherait une teinte différente de celle de sa page,
 * de sa sidebar et de sa bulle orbitale  violation de « une couleur unique par
 * module ». Ces vues sont rattachées à leur module majeur réel.
 *
 * NB : toutes les AUTRES clés (acconage, transit, transport, finance, magasin,
 * parc, qhse, rh, bi, admin, cotations, procurement, fuel-guard, maintenance,
 * fiscalite-cameroun, client-portal…) sont laissées telles quelles : getModulePalette
 * résout déjà leur parent via LEGACY_ALIAS, ce qui garantit l'identité chromatique
 * avec le reste de l'application (une seule et même fonction de référence).
 */
export const LOADING_TO_MODULE: Record<string, string> = {
  'acconage-avance': 'port-operations',
  'real-customs': 'port-operations',
  'container-lifecycle': 'port-operations',
  'port-incidents': 'port-operations',
  'shift-planning': 'port-operations',
  chauffeur: 'portail-chauffeur',
  purchase: 'finance-ohada',
};

/**
 * Applique la palette officielle aux écrans de chargement.
 * Exécutée à l'import : plus aucun écran ne peut afficher une teinte que
 * modulePalette n'a pas accordée à son module. L'accent reste une nuance
 * claire dérivée du hex du module (lisibilité preserve sur fond sombre).
 */
function teinteClaire(hex: string): string {
  const melange = (c: number) => Math.round(c + (255 - c) * 0.34);
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (
    '#' +
    [melange(r), melange(g), melange(b)]
      .map((v) => v.toString(16).padStart(2, '0'))
      .join('')
      .toUpperCase()
  );
}

for (const [cle, cfg] of Object.entries(DOMAIN_LOADING_CONFIGS)) {
  const moduleKey = LOADING_TO_MODULE[cle] ?? cle;
  const hex = getModulePalette(moduleKey).hex;
  cfg.primaryColor = hex;
  cfg.accentColor = teinteClaire(hex);
}
