// src/config/domainLoadingConfig.ts
// Configuration haute fidélité pour les pages de chargement et transitions de grands modules/hubs
// Source de vérité des identités de domaine, palettes, animations signatures et télémétrie métier.

export type DomainAnimationType =
  | 'syscohada-ledger'      // Comptabilité OHADA : Balance bilatérale Débit/Crédit, flux d'écritures
  | 'treasury-flux'         // Finance & Trésorerie : Pulsations bancaires, flux de liquidités
  | 'synergy-constellation' // Collaboratif & Chat : Réseau multipoints, fréquences hertziennes d'équipe
  | 'radar-maritime'        // Port & Acconage : Radar tournant à 360°, détection de navires Douala/Kribi
  | 'customs-laser'         // Transit & Douane : Scan laser de manifestes, sceaux GUCE / SYDONIA
  | 'telematics-satellite'  // Transport & Flotte : Visée satellitaire GPS, axes routiers corridors CEMAC
  | 'wms-lidar'             // Magasin & Stock WMS : Scan 3D de rayonnages, lecture code-barres / RFID
  | 'gmao-gears'            // Parc & Maintenance : Engrenages industriels, diagnostic tachymétrique
  | 'isps-shield'           // QHSE & Sécurité : Bouclier hexagonal de protection, scanner thermique
  | 'biometric-ring'        // RH & Personnel : Anneau biométrique, constellation de capital humain
  | 'b2b-gateway'           // Client & B2B : Passerelle chiffrée partenaires, flux EDI commandes
  | 'bi-prism'              // Reports & BI : Prisme holographique décisionnel, histogrammes 3D
  | 'rbac-matrix'           // Admin & Gouvernance : Cylindre cryptographique de permissions, noyau RBAC
  | 'strategic-compass';    // Dashboard Global : Gyroscope 3 axes et boussole stratégique

export interface DomainLoadingConfig {
  key: string;
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
  // ─────────────────────────────────────────────────────────────────────────────
  // 1. COMPTABILITÉ OHADA
  // ─────────────────────────────────────────────────────────────────────────────
  'comptabilite-ohada': {
    key: 'comptabilite-ohada',
    domainName: 'COMPTABILITÉ OHADA',
    subTitle: 'GRAND LIVRE GÉNÉRAL & PLAN COMPTABLE SYSCOHADA',
    badgeCode: 'SYSCOHADA-2017 • CEMAC OHADA',
    locationTag: 'ESPACE FINANCIER & COMPTABLE RÉGIONAL',
    primaryColor: '#8B5CF6', // Violet Royal
    accentColor: '#F59E0B',  // Or SYSCOHADA
    gradientBg: 'from-violet-950 via-[#130728] to-[#04010b]',
    glowClass: 'shadow-violet-500/50 border-violet-500/60 text-violet-400',
    animationType: 'syscohada-ledger',
    steps: [
      '▶ Vérification de l\'équilibre bilatéral Débit / Crédit SYSCOHADA...',
      '▶ Synchronisation des journaux auxiliaires (Achats, Ventes, Banque, OD)...',
      '▶ Contrôle des comptes de tiers et calcul de la balance avant inventaire...',
      '✓ Grand Livre SYSCOHADA ouvert. Bienvenue dans l\'Espace Comptable.',
    ],
  },
  'fiscalite-cameroun': {
    key: 'fiscalite-cameroun',
    domainName: 'FISCALITÉ CAMEROUN & DGI',
    subTitle: 'DÉCLARATIONS FISCALES, TVA & PRÉLÈVEMENTS SPÉCIFIQUES',
    badgeCode: 'DGI CAMEROUN • CGI OHADA',
    locationTag: 'ADMINISTRATION FISCALE CEMAC',
    primaryColor: '#8B5CF6',
    accentColor: '#10B981',
    gradientBg: 'from-violet-950 via-[#130728] to-[#04010b]',
    glowClass: 'shadow-violet-500/50 border-violet-500/60 text-violet-400',
    animationType: 'syscohada-ledger',
    steps: [
      '▶ Interconnexion télédéclarations DGI Cameroun...',
      '▶ Calcul des acomptes IS, TVA collectée & retenues à la source...',
      '▶ Rapprochement avec le Grand Livre SYSCOHADA...',
      '✓ Espace Fiscal prêt. Conformité légale certifiée.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 2. FINANCE OHADA & TRÉSORERIE
  // ─────────────────────────────────────────────────────────────────────────────
  'finance-ohada': {
    key: 'finance-ohada',
    domainName: 'FINANCE OHADA & TRÉSORERIE',
    subTitle: 'GESTION DE TRÉSORERIE, FACTURATION & RÈGLEMENTS BANCAIRES',
    badgeCode: 'SWIFT / BEAC PROTOCOL • OHADA SECURE',
    locationTag: 'SALLE DES MARCHÉS & TRÉSORERIE DOUALA',
    primaryColor: '#10B981', // Vert Émeraude
    accentColor: '#F59E0B',
    gradientBg: 'from-emerald-950 via-[#031d14] to-[#010905]',
    glowClass: 'shadow-emerald-500/50 border-emerald-500/60 text-emerald-400',
    animationType: 'treasury-flux',
    steps: [
      '▶ Connexion aux passerelles bancaires & soldes en devises (XAF / EUR)...',
      '▶ Contrôle des factures émises, échéanciers & rapprochements...',
      '▶ Calcul en direct de la position nette de trésorerie...',
      '✓ Espace Trésorerie synchronisé. Flux de capitaux validés.',
    ],
  },
  finance: {
    key: 'finance',
    domainName: 'FINANCE & FACTURATION CLIENTS',
    subTitle: 'ÉMISSION DES FACTURES PORTUAIRES & SUIVI DES PAIEMENTS',
    badgeCode: 'FINANCE-CORE • FACTURATION PRO',
    locationTag: 'DIRECTION FINANCIÈRE & RECOUVREMENT',
    primaryColor: '#10B981',
    accentColor: '#34D399',
    gradientBg: 'from-emerald-950 via-[#031d14] to-[#010905]',
    glowClass: 'shadow-emerald-500/50 border-emerald-500/60 text-emerald-400',
    animationType: 'treasury-flux',
    steps: [
      '▶ Récupération des décomptes d\'acconage et transit...',
      '▶ Génération des factures pro-forma et bordereaux fiscaux...',
      '▶ Vérification des garanties de paiement et cautionnements...',
      '✓ Module Facturation prêt.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 3. MODULES COLLABORATIFS & CHAT D'ÉQUIPE (Demandé expressément)
  // ─────────────────────────────────────────────────────────────────────────────
  chat: {
    key: 'chat',
    domainName: 'HUB COLLABORATIF & MESSAGERIE',
    subTitle: 'SALONS DE QUAI, CANAUX FLOTTE & DISCUSSIONS SÉCURISÉES',
    badgeCode: 'TEMPS RÉEL WEBSOCKET • ÉQUIPES TERRAIN',
    locationTag: 'RÉSEAU RADIO & HERTZIEN INTERNE CADC',
    primaryColor: '#22C55E', // Vert Synergie
    accentColor: '#EAB308', // Jaune Collaboration
    gradientBg: 'from-green-950 via-[#051c0e] to-[#010803]',
    glowClass: 'shadow-green-500/50 border-green-500/60 text-green-400',
    animationType: 'synergy-constellation',
    steps: [
      '▶ Établissement du canal WebSocket temps réel sécurisé...',
      '▶ Synchronisation des salons d\'équipe (Quai, Dispatch, Comptabilité)...',
      '▶ Détection de la présence des agents et chauffeurs en ligne...',
      '✓ Canaux collaboratifs opérationnels. Vos équipes sont connectées.',
    ],
  },
  'portail-collaborateur': {
    key: 'portail-collaborateur',
    domainName: 'HUB COLLABORATIF ADAPTATIF',
    subTitle: 'ESPACE CENTRAL DE TRAVAIL, AGENDAS & ACTIONS PARTAGÉES',
    badgeCode: 'HUB CENTRAL • RÔLE COLLABORATEUR',
    locationTag: 'PLATEFORME DE PRODUCTIVITÉ MULTI-SERVICES',
    primaryColor: '#EAB308', // Jaune Or
    accentColor: '#22C55E',
    gradientBg: 'from-yellow-950 via-[#1e1503] to-[#0a0701]',
    glowClass: 'shadow-yellow-500/50 border-yellow-500/60 text-yellow-400',
    animationType: 'synergy-constellation',
    steps: [
      '▶ Chargement de votre environnement personnalisé d\'équipe...',
      '▶ Synchronisation des dossiers partagés et tâches en attente...',
      '▶ Connexion aux passerelles de coordination inter-services...',
      '✓ Espace Collaboratif activé. Bienvenue au Hub.',
    ],
  },
  'portail-employe': {
    key: 'portail-employe',
    domainName: 'MON ESPACE COLLABORATEUR',
    subTitle: 'GESTION PERSONNELLE, DEMANDES DE CONGÉS & NOTES DE FRAIS',
    badgeCode: 'ESPACE PERSONNEL • RH & CONFORMITÉ',
    locationTag: 'PORTAIL AGENT INDIVIDUEL',
    primaryColor: '#84CC16', // Lime
    accentColor: '#10B981',
    gradientBg: 'from-lime-950 via-[#101c03] to-[#040801]',
    glowClass: 'shadow-lime-500/50 border-lime-500/60 text-lime-400',
    animationType: 'synergy-constellation',
    steps: [
      '▶ Authentification biométrique de l\'agent en cours...',
      '▶ Chargement de votre solde de congés et relevé de pointage...',
      '▶ Préparation de vos formulaires de mission...',
      '✓ Votre espace personnel est prêt.',
    ],
  },
  documents: {
    key: 'documents',
    domainName: 'GED & ARCHIVES COLLABORATIVES',
    subTitle: 'GESTION ÉLECTRONIQUE DES DOCUMENTS & PIÈCES DOUANIÈRES',
    badgeCode: 'GED SÉCURISÉE • ARCHIVES NUMÉRIQUES',
    locationTag: 'SERVEUR CENTRAL D\'ARCHIVES NUMÉRISÉES',
    primaryColor: '#22C55E',
    accentColor: '#0EA5E9',
    gradientBg: 'from-green-950 via-[#051c0e] to-[#010803]',
    glowClass: 'shadow-green-500/50 border-green-500/60 text-green-400',
    animationType: 'synergy-constellation',
    steps: [
      '▶ Indexation des connaissements, manifestes et factures scannées...',
      '▶ Vérification de l\'intégrité des signatures électroniques...',
      '▶ Contrôle des autorisations d\'accès documentaires...',
      '✓ Coffre-fort documentaire ouvert.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 4. PORT OPERATIONS & ACCONAGE
  // ─────────────────────────────────────────────────────────────────────────────
  'port-operations': {
    key: 'port-operations',
    domainName: 'PORT OPERATIONS & ACCONAGE',
    subTitle: 'ARRIVÉE NAVIRES, RADAR DES QUAIS & GESTION DES ESCALES',
    badgeCode: 'DOUALA PORT AUTHORITY • GUCE READY',
    locationTag: 'TERMINAL À CONTENEURS • BASSIN SUD (04°03\'04"N 009°42\'54"E)',
    primaryColor: '#0EA5E9', // Sky Blue
    accentColor: '#38BDF8',
    gradientBg: 'from-sky-950 via-[#041a2e] to-[#01080f]',
    glowClass: 'shadow-sky-500/50 border-sky-500/60 text-sky-400',
    animationType: 'radar-maritime',
    steps: [
      '▶ Activation du faisceau radar maritime Port de Douala & Kribi...',
      '▶ Synchronisation des plans d\'armement et d\'arrimage navires...',
      '▶ Allocation dynamique des cavaliers et grues portiques de quai...',
      '✓ Opérations maritimes connectées. Système paré à l\'accostage.',
    ],
  },
  acconage: {
    key: 'acconage',
    domainName: 'ACCONAGE & MANUTENTION PORTUAIRE',
    subTitle: 'DÉBARQUEMENT, EMBARQUEMENT & POINTEURS DE QUAI',
    badgeCode: 'TERMINAL QUAI 1-4 • OPÉRATIONS MARITIMES',
    locationTag: 'PORT AUTONOME DE DOUALA (PAD)',
    primaryColor: '#0EA5E9',
    accentColor: '#38BDF8',
    gradientBg: 'from-sky-950 via-[#041a2e] to-[#01080f]',
    glowClass: 'shadow-sky-500/50 border-sky-500/60 text-sky-400',
    animationType: 'radar-maritime',
    steps: [
      '▶ Réception des avis d\'arrivée navire et pré-manifestes...',
      '▶ Affectation des équipes d\'acconiers et pointeurs...',
      '▶ Vérification des cadences de manutention au poste à quai...',
      '✓ Régie d\'acconage opérationnelle.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 5. TRANSIT & DOUANE
  // ─────────────────────────────────────────────────────────────────────────────
  'transit-douane': {
    key: 'transit-douane',
    domainName: 'TRANSIT & DÉDOUANEMENT GUCE',
    subTitle: 'GUICHET UNIQUE, SYDONIA++ & CONNAISSEMENTS MARITIMES',
    badgeCode: 'GUCE CAMEROUN • DOUANES CEMAC',
    locationTag: 'GUICHET UNIQUE DU COMMERCE EXTÉRIEUR',
    primaryColor: '#3B82F6', // Blue Cobalt
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
    domainName: 'TRANSIT & FORMALITÉS MARITIMES',
    subTitle: 'CONNAISSEMENTS BL, BONS DE LIVRAISON & BESC',
    badgeCode: 'TRANSIT-MARITIME • DÉCLARATIONS CEMAC',
    locationTag: 'CENTRE DE TRANSIT INTERNATIONAL',
    primaryColor: '#3B82F6',
    accentColor: '#60A5FA',
    gradientBg: 'from-blue-950 via-[#061430] to-[#020510]',
    glowClass: 'shadow-blue-500/50 border-blue-500/60 text-blue-400',
    animationType: 'customs-laser',
    steps: [
      '▶ Vérification des numéros BESC & titres de transport...',
      '▶ Rapprochement avec les manifestes maritimes certifiés...',
      '▶ Émission des bons à délivrer (BAD) et autorisations de sortie...',
      '✓ Régie transit opérationnelle.',
    ],
  },
  'portail-declarant': {
    key: 'portail-declarant',
    domainName: 'PORTAIL DÉCLARANT EN DOUANE',
    subTitle: 'SAISIE DES DÉCLARATIONS, DOCUMENTS GUCE & SUIVI LIQUIDATION',
    badgeCode: 'AGRÉMENT DÉCLARANT CEMAC • SYDONIA++',
    locationTag: 'BUREAU CENTRAL DES DÉCLARANTS AGRÉÉS',
    primaryColor: '#3B82F6',
    accentColor: '#F59E0B',
    gradientBg: 'from-blue-950 via-[#061430] to-[#020510]',
    glowClass: 'shadow-blue-500/50 border-blue-500/60 text-blue-400',
    animationType: 'customs-laser',
    steps: [
      '▶ Vérification de l\'agrément déclarant et des certificats cryptographiques...',
      '▶ Importation des positions tarifaires du Système Harmonisé (SH)...',
      '▶ Synchronisation de vos dossiers en cours de liquidation...',
      '✓ Espace Déclarant déverrouillé.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 6. TRANSPORT & FLOTTE
  // ─────────────────────────────────────────────────────────────────────────────
  'transport-flotte': {
    key: 'transport-flotte',
    domainName: 'TRANSPORT & CONVOIS FLOTTE',
    subTitle: 'TÉLÉMATIQUE SATELLITAIRE GPS & DISPATCHING ROUTIER CEMAC',
    badgeCode: 'CORRIDORS CEMAC • DOUALA-N\'DJAMENA-BANGUI',
    locationTag: 'CENTRE DE CONTRÔLE FLOTTE & DISPATCH ROUTIER',
    primaryColor: '#06B6D4', // Cyan Électrique
    accentColor: '#22D3EE',
    gradientBg: 'from-cyan-950 via-[#041d24] to-[#01090c]',
    glowClass: 'shadow-cyan-500/50 border-cyan-500/60 text-cyan-400',
    animationType: 'telematics-satellite',
    steps: [
      '▶ Accrochage aux constellations GPS et balises télématiques OBD...',
      '▶ Cartographie des convois sur les corridors Douala - N\'Djamena - Bangui...',
      '▶ Contrôle des feuilles de route, lettres de voiture et jauges de carburant...',
      '✓ Tour de contrôle transport active. Flotte en liaison continue.',
    ],
  },
  transport: {
    key: 'transport',
    domainName: 'DISPATCHING ROUTIER & EXPÉDITIONS',
    subTitle: 'AFFECTATION DES TRACTEURS, REMORQUES & LETTRES DE VOITURE',
    badgeCode: 'DISPATCH OPÉRATIONNEL • GESTION MISSIONS',
    locationTag: 'RÉGIE ROUTIÈRE DU PORT',
    primaryColor: '#06B6D4',
    accentColor: '#67E8F9',
    gradientBg: 'from-cyan-950 via-[#041d24] to-[#01090c]',
    glowClass: 'shadow-cyan-500/50 border-cyan-500/60 text-cyan-400',
    animationType: 'telematics-satellite',
    steps: [
      '▶ Calcul des ordres de transport et plannings de chargement...',
      '▶ Affectation des remorques porte-conteneurs...',
      '▶ Validation des ordres de mission des chauffeurs...',
      '✓ Module Dispatching prêt.',
    ],
  },
  chauffeur: {
    key: 'chauffeur',
    domainName: 'PORTAIL CHAUFFEUR & MISSION ROUTE',
    subTitle: 'FEUILLE DE ROUTE NUMÉRIQUE, LETTRES DE VOITURE & CONTRÔLES',
    badgeCode: 'APPLICATION CHAUFFEUR • CONVOIS SÉCURISÉS',
    locationTag: 'TERMINAL MOBILE EMBARQUÉ',
    primaryColor: '#F43F5E', // Rose Flotte
    accentColor: '#06B6D4',
    gradientBg: 'from-rose-950 via-[#220710] to-[#0b0104]',
    glowClass: 'shadow-rose-500/50 border-rose-500/60 text-rose-400',
    animationType: 'telematics-satellite',
    steps: [
      '▶ Connexion au terminal télématique du camion...',
      '▶ Téléchargement de la lettre de voiture et des consignes de sécurité...',
      '▶ Vérification du contrôle technique et du niveau de carburant...',
      '✓ Mission validée. Bonne route.',
    ],
  },
  'portail-chauffeur': {
    key: 'portail-chauffeur',
    domainName: 'PORTAIL CHAUFFEUR & MISSION ROUTE',
    subTitle: 'FEUILLE DE ROUTE NUMÉRIQUE, LETTRES DE VOITURE & CONTRÔLES',
    badgeCode: 'APPLICATION CHAUFFEUR • CONVOIS SÉCURISÉS',
    locationTag: 'TERMINAL MOBILE EMBARQUÉ',
    primaryColor: '#F43F5E',
    accentColor: '#06B6D4',
    gradientBg: 'from-rose-950 via-[#220710] to-[#0b0104]',
    glowClass: 'shadow-rose-500/50 border-rose-500/60 text-rose-400',
    animationType: 'telematics-satellite',
    steps: [
      '▶ Synchronisation de la feuille de route du convoi...',
      '▶ Contrôle des points d\'étape et des pesées aux ponts-bascules...',
      '▶ Déclaration de démarrage de convoi...',
      '✓ Espace Chauffeur prêt.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 7. MAGASIN & STOCK WMS
  // ─────────────────────────────────────────────────────────────────────────────
  'magasin-stock': {
    key: 'magasin-stock',
    domainName: 'MAGASIN & STOCK WMS',
    subTitle: 'GESTION DES RAYONNAGES, SCAN CODES-BARRES & PRÉPARATION DE COLIS',
    badgeCode: 'WMS PROTOCOL • CODE-BARRES GS1 & RFID',
    locationTag: 'ENTREPÔT LOGISTIQUE ZONE PORTUAIRE',
    primaryColor: '#F59E0B', // Ambre Industriel
    accentColor: '#FBBF24',
    gradientBg: 'from-amber-950 via-[#221303] to-[#0c0601]',
    glowClass: 'shadow-amber-500/50 border-amber-500/60 text-amber-400',
    animationType: 'wms-lidar',
    steps: [
      '▶ Calibrage du scanner Lidar des travées & alvéoles de stockage...',
      '▶ Cartographie 3D des magasins sous douane et parcs à conteneurs...',
      '▶ Synchronisation des inventaires permanents et avis de réception...',
      '✓ Système WMS initialisé. Alvéoles prêtes pour la préparation.',
    ],
  },
  magasin: {
    key: 'magasin',
    domainName: 'MAGASINAGE & ENTREPOSAGE',
    subTitle: 'GESTION DES MARCHANDISES ENTRANTES ET SORTANTES',
    badgeCode: 'WMS MAGASINIER • GESTION PARC & CALE',
    locationTag: 'ENTREPÔT LOGISTIQUE CENTRAL',
    primaryColor: '#F59E0B',
    accentColor: '#FBBF24',
    gradientBg: 'from-amber-950 via-[#221303] to-[#0c0601]',
    glowClass: 'shadow-amber-500/50 border-amber-500/60 text-amber-400',
    animationType: 'wms-lidar',
    steps: [
      '▶ Chargement du registre d\'empotage et dépotage...',
      '▶ Vérification des plombs et de l\'intégrité des scellés conteneurs...',
      '▶ Contrôle des stocks disponibles et emplacements...',
      '✓ Régie Magasin connectée.',
    ],
  },
  'portail-magasinier': {
    key: 'portail-magasinier',
    domainName: 'PORTAIL MAGASINIER & TERMINAL QUAI',
    subTitle: 'SCANNER PORTABLE, RÉCEPTIONS & PRÉPARATIONS PALETTES',
    badgeCode: 'TERMINAL EMBARQUÉ MAGASINIER • SCANNER SCAN-GUN',
    locationTag: 'PLATEFORME LOGISTIQUE DE CROSS-DOCKING',
    primaryColor: '#71717A', // Zinc
    accentColor: '#F59E0B',
    gradientBg: 'from-zinc-950 via-[#131316] to-[#060608]',
    glowClass: 'shadow-zinc-500/50 border-zinc-500/60 text-zinc-400',
    animationType: 'wms-lidar',
    steps: [
      '▶ Synchronisation du terminal durci / scan-gun de quai...',
      '▶ Récupération de la liste des colis à réceptionner...',
      '▶ Validation de l\'état des marchandises et réserves éventuelles...',
      '✓ Terminal Magasinier prêt.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 8. PARC & VÉHICULES / GMAO
  // ─────────────────────────────────────────────────────────────────────────────
  'parc-vehicules': {
    key: 'parc-vehicules',
    domainName: 'PARC ENGINS & GMAO TECHNIQUE',
    subTitle: 'MAINTENANCE PRÉVENTIVE, DIAGNOSTIC MOTEUR & ÉQUIPEMENTS LOURDS',
    badgeCode: 'GMAO INDUSTRIELLE • NORME ISO 55000',
    locationTag: 'ATELIER MÉCANIQUE CENTRAL & ATELIER QUAIS',
    primaryColor: '#F97316', // Orange Mécanique
    accentColor: '#FB923C',
    gradientBg: 'from-orange-950 via-[#230d03] to-[#0c0401]',
    glowClass: 'shadow-orange-500/50 border-orange-500/60 text-orange-400',
    animationType: 'gmao-gears',
    steps: [
      '▶ Enclenchement des capteurs télémétriques des tracteurs et grues...',
      '▶ Analyse vibratoire, pression hydraulique & compteurs d\'heures...',
      '▶ Synchronisation des Ordres de Réparation (OR) et pièces de rechange...',
      '✓ Système GMAO armé. Parc mécanique sous supervision préventive.',
    ],
  },
  parc: {
    key: 'parc',
    domainName: 'GESTION DU PARC MATÉRIEL',
    subTitle: 'SUIVI DES VISITES TECHNIQUES, ASSURANCES & CONSOMMATION CARBURANT',
    badgeCode: 'PARC ROULANT • FLEET MANAGEMENT',
    locationTag: 'DIRECTION DU PARC & LOGISTIQUE MATÉRIEL',
    primaryColor: '#F97316',
    accentColor: '#FB923C',
    gradientBg: 'from-orange-950 via-[#230d03] to-[#0c0401]',
    glowClass: 'shadow-orange-500/50 border-orange-500/60 text-orange-400',
    animationType: 'gmao-gears',
    steps: [
      '▶ Examen des dates d\'échéance des vignettes et assurances...',
      '▶ Rapprochement des cartes carburant et cubitainers...',
      '▶ Évaluation de la disponibilité opérationnelle de la flotte...',
      '✓ Registre du parc à jour.',
    ],
  },
  'portail-technicien': {
    key: 'portail-technicien',
    domainName: 'PORTAIL TECHNICIEN GMAO',
    subTitle: 'DIAGNOSTICS ATELIER, PIÈCES DÉTACHÉES & ORDRES DE TRAVAIL',
    badgeCode: 'ATELIER GMAO • TECHNICIEN AGRÉÉ',
    locationTag: 'POSTE D\'INTERVENTION ATELIER',
    primaryColor: '#78716C', // Stone
    accentColor: '#F97316',
    gradientBg: 'from-stone-950 via-[#181615] to-[#080706]',
    glowClass: 'shadow-stone-500/50 border-stone-500/60 text-stone-400',
    animationType: 'gmao-gears',
    steps: [
      '▶ Récupération des fiches d\'intervention mécanique prioritaires...',
      '▶ Disponibilité des pièces au magasin technique...',
      '▶ Enregistrement des temps d\'intervention et tests de charge...',
      '✓ Espace Technicien prêt.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 9. QHSE & SÉCURITÉ PORTUAIRE
  // ─────────────────────────────────────────────────────────────────────────────
  'qhse-securite': {
    key: 'qhse-securite',
    domainName: 'QHSE & SÉCURITÉ PORTUAIRE',
    subTitle: 'CODE ISPS, SURVEILLANCE DES RISQUES & CONFORMITÉ ENVIRONNEMENTALE',
    badgeCode: 'ISPS CODE • ISO 45001 / 14001',
    locationTag: 'CENTRE DE GESTION DES RISQUES & SÛRETÉ',
    primaryColor: '#EF4444', // Rouge Écarlate
    accentColor: '#F87171',
    gradientBg: 'from-red-950 via-[#210606] to-[#0c0101]',
    glowClass: 'shadow-red-500/50 border-red-500/60 text-red-400',
    animationType: 'isps-shield',
    steps: [
      '▶ Activation du bouclier de conformité ISPS & contrôles d\'accès de zone...',
      '▶ Analyse thermique et détection des marchandises dangereuses (IMDG)...',
      '▶ Vérification des protocoles EPI et registres de presqu\'accidents...',
      '✓ Système de sûreté déployé. Intégrité opérationnelle à 100%.',
    ],
  },
  qhse: {
    key: 'qhse',
    domainName: 'QUALITÉ, HYGIÈNE, SÉCURITÉ & ENVIRONNEMENT',
    subTitle: 'AUDITS DE CONFORMITÉ, PLANS DE PRÉVENTION & GESTION INCIDENTS',
    badgeCode: 'QHSE AUDIT • CONFORMITÉ RÈGLEMENTAIRE',
    locationTag: 'DÉPARTEMENT QHSE & PRÉVENTION DES RISQUES',
    primaryColor: '#EF4444',
    accentColor: '#F87171',
    gradientBg: 'from-red-950 via-[#210606] to-[#0c0101]',
    glowClass: 'shadow-red-500/50 border-red-500/60 text-red-400',
    animationType: 'isps-shield',
    steps: [
      '▶ Examen des rapports d\'incidents en cours...',
      '▶ Suivi des formations sécurité et habilitations caristes...',
      '▶ Contrôle des fiches de données de sécurité (FDS)...',
      '✓ Régie QHSE en veille active.',
    ],
  },
  'portail-qhse': {
    key: 'portail-qhse',
    domainName: 'PORTAIL QHSE TERRAIN',
    subTitle: 'SIGNALEMENT LIVE DES RISQUES, AUDITS SUR LE QUAI & ACTIONS IMMÉDIATES',
    badgeCode: 'SIGNALEMENT RAPIDE • SÉCURITÉ ACTIVE',
    locationTag: 'PATROUILLE DE SÛRETÉ PORTUAIRE',
    primaryColor: '#E11D48',
    accentColor: '#EF4444',
    gradientBg: 'from-rose-950 via-[#23050c] to-[#0c0103]',
    glowClass: 'shadow-rose-600/50 border-rose-600/60 text-rose-400',
    animationType: 'isps-shield',
    steps: [
      '▶ Connexion au canal d\'alerte prioritaire sécurité...',
      '▶ Géolocalisation des patrouilles et rondes de surveillance...',
      '▶ Préparation des formulaires d\'audit inopiné...',
      '✓ Espace QHSE Terrain opérationnel.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 10. RH & CAPITAL HUMAIN
  // ─────────────────────────────────────────────────────────────────────────────
  'rh-personnel': {
    key: 'rh-personnel',
    domainName: 'RH & CAPITAL HUMAIN',
    subTitle: 'GESTION DU PERSONNEL, POINTAGES BIOMÉTRIQUES & FICHES DE PAIE',
    badgeCode: 'OHADA SOCIAL • CONVENTION PORTUAIRE',
    locationTag: 'DIRECTION DES RESSOURCES HUMAINES & SOCIALES',
    primaryColor: '#EC4899', // Rose Vibrant
    accentColor: '#F472B6',
    gradientBg: 'from-pink-950 via-[#220716] to-[#0c0107]',
    glowClass: 'shadow-pink-500/50 border-pink-500/60 text-pink-400',
    animationType: 'biometric-ring',
    steps: [
      '▶ Synchronisation des pointages biométriques d\'arrivée aux portes...',
      '▶ Contrôle des plannings de relève des dockers et agents de quart...',
      '▶ Calcul des variables de paie, heures sup & primes de rendement...',
      '✓ Registre du personnel ouvert. Gestion du capital humain active.',
    ],
  },
  rh: {
    key: 'rh',
    domainName: 'RESSOURCES HUMAINES & ADMINISTRATION DU PERSONNEL',
    subTitle: 'CONTRATS DE TRAVAIL, CNPS & HABILITATIONS OPÉRATIONNELLES',
    badgeCode: 'RH DIRECTOIRE • CONFORMITÉ LÉGALE',
    locationTag: 'BUREAU DU PERSONNEL',
    primaryColor: '#EC4899',
    accentColor: '#F472B6',
    gradientBg: 'from-pink-950 via-[#220716] to-[#0c0107]',
    glowClass: 'shadow-pink-500/50 border-pink-500/60 text-pink-400',
    animationType: 'biometric-ring',
    steps: [
      '▶ Contrôle des cotisations CNPS et déclarations sociales...',
      '▶ Mise à jour des dossiers agents et fiches de poste...',
      '▶ Validation des demandes de congés et autorisations d\'absence...',
      '✓ Espace RH synchronisé.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 11. CLIENT & B2B
  // ─────────────────────────────────────────────────────────────────────────────
  'client-b2b': {
    key: 'client-b2b',
    domainName: 'ESPACE CLIENT & PARTENAIRES B2B',
    subTitle: 'PORTAIL EXTÉRIEUR, TRACKING CONTENEURS & COTATIONS INSTANTANÉES',
    badgeCode: 'B2B SECURE GATEWAY • SSL 256-BIT',
    locationTag: 'PASSERELLE PARTENAIRES & IMPORT/EXPORT',
    primaryColor: '#14B8A6', // Teal
    accentColor: '#2DD4BF',
    gradientBg: 'from-teal-950 via-[#031d1b] to-[#010908]',
    glowClass: 'shadow-teal-500/50 border-teal-500/60 text-teal-400',
    animationType: 'b2b-gateway',
    steps: [
      '▶ Authentification du compte partenaire et vérification des mandats...',
      '▶ Chargement du suivi satellite en temps réel des expéditions maritimes...',
      '▶ Synchronisation des cotations en cours et factures électroniques...',
      '✓ Passerelle B2B déverrouillée. Vos flux logistiques sont à portée.',
    ],
  },
  'client-portal': {
    key: 'client-portal',
    domainName: 'PORTAIL CLIENT IMPORT-EXPORT',
    subTitle: 'VISIBILITÉ BOUT-EN-BOUT DU CHARGEMENT NAVIRE JUSQU\'À DESTINATION',
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

  // ─────────────────────────────────────────────────────────────────────────────
  // 12. REPORTS & DÉCISIONNEL BI
  // ─────────────────────────────────────────────────────────────────────────────
  'reports-bi': {
    key: 'reports-bi',
    domainName: 'DÉCISIONNEL & REPORTING BI',
    subTitle: 'ANALYTICS AVANCÉS, KPI PORTUAIRES & PRÉVISIONS LOGISTIQUES',
    badgeCode: 'BUSINESS INTELLIGENCE • DATA WAREHOUSE',
    locationTag: 'SALLE STRATÉGIQUE & ANALYSE DÉCISIONNELLE',
    primaryColor: '#A855F7', // Purple
    accentColor: '#C084FC',
    gradientBg: 'from-purple-950 via-[#1e072a] to-[#0a0110]',
    glowClass: 'shadow-purple-500/50 border-purple-500/60 text-purple-400',
    animationType: 'bi-prism',
    steps: [
      '▶ Agrégation des cubes OLAP financiers, douaniers et maritimes...',
      '▶ Calcul des métriques de temps de rotation (dwell time) et rentabilité...',
      '▶ Génération des graphiques prédictifs et synthèses exécutives...',
      '✓ Matrice BI opérationnelle. Données d\'aide à la décision prêtes.',
    ],
  },
  bi: {
    key: 'bi',
    domainName: 'TABLEAUX DE BORD STRATÉGIQUES',
    subTitle: 'TABLEAU DE BORD EXÉCUTIF ET PERFORMANCES MULTI-AGENCES',
    badgeCode: 'KPI SUITE • DIRECTOIRE CADC',
    locationTag: 'CENTRE DÉCISIONNEL CONSOLIDÉ',
    primaryColor: '#A855F7',
    accentColor: '#C084FC',
    gradientBg: 'from-purple-950 via-[#1e072a] to-[#0a0110]',
    glowClass: 'shadow-purple-500/50 border-purple-500/60 text-purple-400',
    animationType: 'bi-prism',
    steps: [
      '▶ Compilation des chiffres d\'affaires par module...',
      '▶ Évaluation des cadences de manutention et du taux de fret...',
      '▶ Consolidation des rapports périodiques OHADA...',
      '✓ Tableaux de bord stratégiques actualisés.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 13. ADMIN SAAS & GOUVERNANCE MULTI-TENANT
  // ─────────────────────────────────────────────────────────────────────────────
  'admin-tenant': {
    key: 'admin-tenant',
    domainName: 'GOUVERNANCE & TENANT ENTREPRISE',
    subTitle: 'GESTION DES ACCRÉDITATIONS, AGENCES, RÔLES RBAC & AUDIT PISTE',
    badgeCode: 'RBAC MULTI-TENANT • CONFORMITÉ SYSTÈME',
    locationTag: 'CENTRE DE CONTRÔLE GOUVERNANCE & ACCRÉDITATIONS',
    primaryColor: '#64748B', // Slate
    accentColor: '#D946EF', // Fuchsia
    gradientBg: 'from-slate-950 via-[#111622] to-[#05070a]',
    glowClass: 'shadow-slate-500/50 border-slate-500/60 text-slate-400',
    animationType: 'rbac-matrix',
    steps: [
      '▶ Chargement de la matrice granulaire des rôles et habilitations...',
      '▶ Contrôle de l\'étanchéité multi-tenant et politique de sécurité...',
      '▶ Inspection des journaux d\'audit et des signatures d\'accès...',
      '✓ Console de gouvernance déverrouillée. Administration prête.',
    ],
  },
  'admin-saas': {
    key: 'admin-saas',
    domainName: 'ADMINISTRATION CADC SAAS',
    subTitle: 'SUPERVISION MULTI-TENANT, GESTION DES ENTREPRISES & LICENCES',
    badgeCode: 'CORE SYSTEM • NIVEAU SUPERADMIN CADC',
    locationTag: 'CODE AXIS DIGITAL CAMEROUN (HQ)',
    primaryColor: '#D946EF', // Fuchsia
    accentColor: '#F59E0B',
    gradientBg: 'from-fuchsia-950 via-[#260424] to-[#0d010c]',
    glowClass: 'shadow-fuchsia-500/50 border-fuchsia-500/60 text-fuchsia-400',
    animationType: 'rbac-matrix',
    steps: [
      '▶ Vérification du cluster PostgreSQL et des métriques d\'isolation...',
      '▶ Contrôle de l\'état de santé des API FastAPI et du broker de messages...',
      '▶ Supervision de l\'ensemble des tenants déployés...',
      '✓ Console SaaS CADC active.',
    ],
  },
  admin: {
    key: 'admin',
    domainName: 'PARAMÈTRES & GOUVERNANCE',
    subTitle: 'CONFIGURATIONS SYSTÈME, UTILISATEURS & ACCÈS',
    badgeCode: 'GOUVERNANCE SYSTÈME',
    locationTag: 'CENTRE D\'ADMINISTRATION',
    primaryColor: '#64748B',
    accentColor: '#94A3B8',
    gradientBg: 'from-slate-950 via-[#111622] to-[#05070a]',
    glowClass: 'shadow-slate-500/50 border-slate-500/60 text-slate-400',
    animationType: 'rbac-matrix',
    steps: [
      '▶ Vérification des droits administrateur...',
      '▶ Chargement des référentiels système...',
      '▶ Contrôle des certificats de connexion...',
      '✓ Espace Administration prêt.',
    ],
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // 14. DASHBOARD GLOBAL (COCKPIT CENTRAL)
  // ─────────────────────────────────────────────────────────────────────────────
  dashboard: {
    key: 'dashboard',
    domainName: 'COCKPIT GLOBAL EVO-LOG',
    subTitle: 'SYNTHÈSE INTÉGRÉE NAVIRE → CLIENT & SUPERVISION OPÉRATIONNELLE',
    badgeCode: 'CADC ERP • SUITE LOGISTIQUE INTÉGRÉE',
    locationTag: 'DIRECTION GÉNÉRALE & SALLE DES OPÉRATIONS',
    primaryColor: '#6366F1', // Indigo Stratégique
    accentColor: '#F59E0B', // Or
    gradientBg: 'from-indigo-950 via-[#0a0e28] to-[#02040c]',
    glowClass: 'shadow-indigo-500/50 border-indigo-500/60 text-indigo-400',
    animationType: 'strategic-compass',
    steps: [
      '▶ Agrégation des flux opérationnels Navire → Douane → Route → Entrepôt...',
      '▶ Synchronisation des alertes en direct et indicateurs clés de performance...',
      '▶ Déploiement de la vue transversale consolidée de l\'entreprise...',
      '✓ Cockpit Global déployé. Bienvenue sur EVO-LOG SaaS.',
    ],
  },
};

/**
 * Résout la configuration visuelle pour n'importe quelle route ou clé de module.
 */
export function resolveDomainLoadingConfig(routeOrKey: string): DomainLoadingConfig {
  const clean = routeOrKey.replace(/^\/+/, '').split('/')[0] || 'dashboard';

  // Correspondance directe
  if (DOMAIN_LOADING_CONFIGS[clean]) {
    return DOMAIN_LOADING_CONFIGS[clean];
  }

  // Correspondances partielles ou alias
  if (clean.includes('comptabilite') || clean.includes('cloture') || clean.includes('journal')) {
    return DOMAIN_LOADING_CONFIGS['comptabilite-ohada'];
  }
  if (clean.includes('finance') || clean.includes('invoicing') || clean.includes('tresorerie') || clean.includes('frais')) {
    return DOMAIN_LOADING_CONFIGS['finance-ohada'];
  }
  if (clean.includes('chat') || clean.includes('collaborat') || clean.includes('notif')) {
    return DOMAIN_LOADING_CONFIGS['chat'];
  }
  if (clean.includes('port') || clean.includes('acconage') || clean.includes('navire')) {
    return DOMAIN_LOADING_CONFIGS['port-operations'];
  }
  if (clean.includes('transit') || clean.includes('douane') || clean.includes('declarant') || clean.includes('sydonia')) {
    return DOMAIN_LOADING_CONFIGS['transit-douane'];
  }
  if (clean.includes('transport') || clean.includes('flotte') || clean.includes('chauffeur') || clean.includes('tracking')) {
    return DOMAIN_LOADING_CONFIGS['transport-flotte'];
  }
  if (clean.includes('magasin') || clean.includes('stock') || clean.includes('wms') || clean.includes('entrepot')) {
    return DOMAIN_LOADING_CONFIGS['magasin-stock'];
  }
  if (clean.includes('parc') || clean.includes('gmao') || clean.includes('maintenance') || clean.includes('vehicule')) {
    return DOMAIN_LOADING_CONFIGS['parc-vehicules'];
  }
  if (clean.includes('qhse') || clean.includes('securite') || clean.includes('compliance') || clean.includes('isps')) {
    return DOMAIN_LOADING_CONFIGS['qhse-securite'];
  }
  if (clean.includes('rh') || clean.includes('personnel') || clean.includes('employe') || clean.includes('shift')) {
    return DOMAIN_LOADING_CONFIGS['rh-personnel'];
  }
  if (clean.includes('client') || clean.includes('b2b') || clean.includes('portal')) {
    return DOMAIN_LOADING_CONFIGS['client-b2b'];
  }
  if (clean.includes('report') || clean.includes('bi')) {
    return DOMAIN_LOADING_CONFIGS['reports-bi'];
  }
  if (clean.includes('admin') || clean.includes('tenant') || clean.includes('setting')) {
    return DOMAIN_LOADING_CONFIGS['admin-tenant'];
  }

  return DOMAIN_LOADING_CONFIGS.dashboard;
}
