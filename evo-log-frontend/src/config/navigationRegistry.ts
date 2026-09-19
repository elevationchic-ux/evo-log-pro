// src/config/navigationRegistry.ts
// ERP Logistique Portuaire COMPLET - Architecture End-to-End Navire → Client
// Spécialisé Cameroun/CEMAC avec Comptabilité OHADA & Système T-Code SAP-like
// 12 Modules Majeurs + Dashboard Global

import {
  Anchor, Ship, Compass, Navigation, MapPin, Globe,
  Truck, Fuel, Package, Boxes, Warehouse, ArrowUpDown,
  DollarSign, CreditCard, Receipt, Calculator, TrendingUp, Banknote,
  ShieldAlert, Shield, Users, UserCheck, Crown, Tag, Building, Landmark,
  Settings, Wrench, Activity, Zap, Clock, Calendar, ClipboardList,
  BarChart3, PieChart, LineChart, FileText, BookOpen,
  Radio, Wifi, MessageSquare, Bell,
  LayoutDashboard, Layers, Grid, FileCheck, ShoppingCart, RotateCcw,
  ArrowRightLeft, Bot, CheckCircle2
} from 'lucide-react';

export interface SubModuleItem {
  label: string;
  path: string;
  icon: any;
  badge?: string;
  description?: string;
  tcode?: string;
  businessProcess?: string;
  requiredRoles?: string[];
  isOhadaCompliant?: boolean;
  isCemacSpecific?: boolean;
}

export interface ModuleNavConfig {
  key: string;
  title: string;
  path: string;
  icon: any;
  color: string;
  glow: string;
  bgGradient: string;
  businessArea: string;
  processPhase: string;
  requiredRoles?: string[];
  subModules: SubModuleItem[];
}

export const NAVIGATION_REGISTRY: Record<string, ModuleNavConfig> = {
  // ============================================================================
  // 🎯 DASHBOARD: VUE GLOBALE ERP
  // ============================================================================
  dashboard: {
    key: 'dashboard',
    title: 'Vue Globale ERP',
    path: '/dashboard/global',
    icon: Compass,
    color: '#6366f1',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-blue-600',
    businessArea: 'Supervision Générale',
    processPhase: 'Vue Transversale Processus Complete',
    subModules: [
      {
        label: "Vue d'Ensemble Executive",
        path: '/dashboard/global',
        icon: LayoutDashboard,
        badge: 'Main',
        tcode: 'KM24',
        description: 'Tableau de bord de synthèse stratégique et opérationnel',
        businessProcess: 'Pilotage global'
      },
      {
        label: 'Processus Navire → Client',
        path: '/dashboard/process-flow',
        icon: Ship,
        badge: 'Process',
        tcode: 'KPRC_FLW',
        description: 'Suivi temps réel du pipeline end-to-end de bout en bout',
        businessProcess: 'Supervision processus'
      },
      {
        label: 'Alertes & Incidents Live',
        path: '/security/notifications',
        icon: Zap,
        badge: 'Live',
        tcode: 'KAUD_ALT',
        description: 'Centre d alertes opérationnelles et de sécurité en direct',
        businessProcess: 'Monitoring'
      },
      {
        label: 'Indicateurs Clés BI',
        path: '/bi',
        icon: BarChart3,
        badge: 'KPIs',
        tcode: 'KBI_DSH',
        description: 'Métriques clés de performance financière et logistique',
        businessProcess: 'Performance globale'
      },
      {
        label: 'Control Tower Transport',
        path: '/transport/control',
        icon: Truck,
        badge: 'Tower',
        tcode: 'KTRN_RTE',
        description: 'Poste de contrôle en temps réel de la flotte et des tournées',
        businessProcess: 'Activité live'
      }
    ]
  },

  // ============================================================================
  // 🚢 MODULE 1: OPÉRATIONS PORTUAIRES & ACCONAGE
  // ============================================================================
  'port-operations': {
    key: 'port-operations',
    title: '🚢 Opérations Portuaires & Quai',
    path: '/port-operations/dashboard',
    icon: Ship,
    color: '#0ea5e9',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-blue-600',
    businessArea: 'Port Maritime',
    processPhase: 'Phase 1: Arrivée & Déchargement Navire',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS', 'MARITIME', 'MANAGER', 'ACCONAGE'],
    subModules: [
      {
        label: 'Control Tower Maritime',
        path: '/port-operations/dashboard',
        icon: LayoutDashboard,
        badge: 'Live',
        tcode: 'KACC_DSH',
        description: 'Centre de contrôle temps réel des opérations portuaires',
        businessProcess: 'Supervision portuaire',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS', 'MANAGER']
      },
      {
        label: 'Manifestes & Escales Navires',
        path: '/port-operations/manifests',
        icon: FileText,
        badge: 'Manifestes',
        tcode: 'KACC_MNF',
        description: 'Gestion des manifestes de cargaison et programmation des escales',
        businessProcess: 'Documentation navire',
        requiredRoles: ['PORT_OPERATIONS', 'MARITIME', 'DOUANE']
      },
      {
        label: 'Opérations de Quai & Acconage',
        path: '/port-operations/quai-operations',
        icon: Anchor,
        badge: 'Quai',
        tcode: 'KACC_OPS',
        description: 'Coordination déchargement conteneurs et manutention quai',
        businessProcess: 'Manutention portuaire',
        requiredRoles: ['PORT_OPERATIONS', 'QUAI', 'MARITIME', 'ACCONAGE']
      },
      {
        label: 'Planning Accostage & Postes',
        path: '/port-operations/berth-planning',
        icon: Anchor,
        badge: 'Planning',
        tcode: 'KACC_PLN',
        description: 'Allocation des postes à quai et calendrier d accostage',
        businessProcess: 'Planification maritime',
        requiredRoles: ['PORT_OPERATIONS', 'PLANNING']
      },
      {
        label: 'Statistiques Trafic Maritime',
        path: '/port-operations/maritime-stats',
        icon: BarChart3,
        badge: 'Analytics',
        tcode: 'KACC_STS',
        description: 'Analyses de cadence de manutention et KPIs maritimes',
        businessProcess: 'Reporting portuaire',
        requiredRoles: ['PORT_OPERATIONS', 'MANAGER', 'AUDITOR']
      },
      {
        label: 'Intégration Portuaire Douala/Kribi',
        path: '/port-operations/port-integration',
        icon: Wifi,
        badge: 'EDI',
        tcode: 'KACC_EDI',
        description: 'Passerelle EDI avec les autorités portuaires camerounaises',
        businessProcess: 'Intégration systèmes',
        isCemacSpecific: true,
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'INTEGRATION']
      }
    ]
  },

  // ============================================================================
  // 🛃 MODULE 2: TRANSIT & DOUANE CEMAC
  // ============================================================================
  'transit-douane': {
    key: 'transit-douane',
    title: '🛃 Transit & Douane CEMAC',
    path: '/transit-douane/dashboard',
    icon: Landmark,
    color: '#0284c7',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-blue-600',
    businessArea: 'Dédouanement & Transit',
    processPhase: 'Phase 2: Procédures Douanières & Transit',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'DOUANE', 'TRANSIT', 'MANAGER'],
    subModules: [
      {
        label: 'Centre Dédouanement & Statuts',
        path: '/transit-douane/dashboard',
        icon: LayoutDashboard,
        badge: 'Douane',
        tcode: 'KDOU_DSH',
        description: 'Supervision globale des dossiers de dédouanement import/export',
        businessProcess: 'Dédouanement',
        requiredRoles: ['DOUANE', 'TRANSIT', 'MANAGER']
      },
      {
        label: 'Déclarations DUM & Sydonia',
        path: '/transit-douane/declarations',
        icon: FileCheck,
        badge: 'DUM',
        tcode: 'KDOU_DUM',
        description: 'Saisie Déclaration Unique Marchandises conforme CEMAC',
        businessProcess: 'Déclarations douanières',
        isCemacSpecific: true,
        requiredRoles: ['DOUANE', 'DECLARANT', 'TRANSIT']
      },
      {
        label: 'Taxation & Droits Cameroun',
        path: '/transit-douane/taxation-cameroun',
        icon: Calculator,
        badge: '🇨🇲 TEC',
        tcode: 'KDOU_TAX',
        description: 'Calculateur automatique DD, TVA (19.25%), centimes additionnels',
        businessProcess: 'Taxation douanière',
        isCemacSpecific: true,
        isOhadaCompliant: true,
        requiredRoles: ['DOUANE', 'FINANCE']
      },
      {
        label: 'Dossiers Transit CEMAC (Corridor)',
        path: '/transit-douane/dossiers-cemac',
        icon: Globe,
        badge: 'Corridor',
        tcode: 'KDOU_COR',
        description: 'Suivi corridors Douala-N\'Djamena & Douala-Bangui',
        businessProcess: 'Transit régional CEMAC',
        isCemacSpecific: true,
        requiredRoles: ['DOUANE', 'TRANSIT']
      },
      {
        label: 'Bon à Enlever (BAE) & Mainlevée',
        path: '/transit-douane/bae',
        icon: FileText,
        badge: 'BAE',
        tcode: 'KDOU_BAE',
        description: 'Émission BAE, levée de caution et autorisation de sortie',
        businessProcess: 'Sortie douanière',
        requiredRoles: ['DOUANE', 'MAGASIN']
      },
      {
        label: 'Conformité & Licences Import/Export',
        path: '/transit-douane/compliance',
        icon: Shield,
        badge: 'Normes',
        tcode: 'KDOU_CMP',
        description: 'Contrôles SGS, certificats d origine, conformité CEMAC',
        businessProcess: 'Conformité douanière',
        isCemacSpecific: true,
        requiredRoles: ['DOUANE', 'COMPLIANCE']
      }
    ]
  },

  // ============================================================================
  // 🚛 MODULE 3: TRANSPORT TMS & DISPATCH INTELLIGENT
  // ============================================================================
  'transport-flotte': {
    key: 'transport-flotte',
    title: '🚛 K-Transport & Flotte TMS',
    path: '/transport-flotte/control-tower',
    icon: Truck,
    color: '#06b6d4',
    glow: 'shadow-cyan-500/50 border-cyan-500/60',
    bgGradient: 'from-cyan-600 to-blue-500',
    businessArea: 'Transport & Logistique',
    processPhase: 'Phase 3: Transport Marchandises vers Client',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT', 'DISPATCHER', 'MANAGER', 'CHAUFFEUR'],
    subModules: [
      {
        label: 'Control Tower & Live Map',
        path: '/transport-flotte/control-tower',
        icon: LayoutDashboard,
        badge: 'Live',
        tcode: 'KTRN_RTE',
        description: 'Supervision de la flotte en direct, tracking GPS temps réel',
        businessProcess: 'Tour de contrôle transport',
        requiredRoles: ['TRANSPORT', 'DISPATCHER', 'MANAGER']
      },
      {
        label: 'Missions & Dispatch Intelligent',
        path: '/transport-flotte/missions-dispatch',
        icon: Navigation,
        badge: 'Dispatch',
        tcode: 'KTRN_DSP',
        description: 'Optimisation des tournées, affectation automatique, drag-and-drop',
        businessProcess: 'Planification dispatch',
        requiredRoles: ['DISPATCHER', 'TRANSPORT']
      },
      {
        label: 'Tracking GPS & e-POD Signatures',
        path: '/transport-flotte/tracking-epod',
        icon: Radio,
        badge: 'e-POD',
        tcode: 'KTRN_POD',
        description: 'Preuve de livraison dématérialisée, signature client et photos',
        businessProcess: 'Validation livraison',
        requiredRoles: ['TRANSPORT', 'CHAUFFEUR', 'CLIENT']
      },
      {
        label: 'Flotte Camions & Tracteurs',
        path: '/transport-flotte/fleet-management',
        icon: Truck,
        badge: 'Flotte',
        tcode: 'KTRN_FLT',
        description: 'Inventaire des véhicules, TCO, alertes entretiens kilométriques',
        businessProcess: 'Gestion parc matériel',
        requiredRoles: ['TRANSPORT', 'PARC']
      },
      {
        label: 'Gestion des Chauffeurs',
        path: '/transport-flotte/drivers',
        icon: Users,
        badge: 'Chauffeurs',
        tcode: 'KTRN_DRV',
        description: 'Dossiers conducteurs, validité permis, heures de conduite et repos',
        businessProcess: 'Gestion conducteurs',
        requiredRoles: ['TRANSPORT', 'RH']
      },
      {
        label: 'Carburant & FuelGuard Télémétrie',
        path: '/transport-flotte/fuel-telematics',
        icon: Fuel,
        badge: 'Fuel',
        tcode: 'KTRN_FUEL',
        description: 'Tickets carburant, contrôle des consommations, alertes anomalies',
        businessProcess: 'Maîtrise carburant',
        requiredRoles: ['TRANSPORT', 'FINANCE']
      }
    ]
  },

  // ============================================================================
  // 📦 MODULE 4: MAGASIN & STOCK WMS
  // ============================================================================
  'magasin-stock': {
    key: 'magasin-stock',
    title: '📦 K-Magasin WMS & Stock',
    path: '/magasin-stock/dashboard',
    icon: Package,
    color: '#f59e0b',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-500',
    businessArea: 'Entreposage & Stock',
    processPhase: 'Phase 4: Gestion Stock & Préparation',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAGASIN', 'MAGASINIER', 'STOCK', 'MANAGER'],
    subModules: [
      {
        label: 'Dashboard WMS Central',
        path: '/magasin-stock/dashboard',
        icon: LayoutDashboard,
        badge: 'WMS',
        tcode: 'KMAG_DSH',
        description: 'Taux d occupation, flux d entrées/sorties et alertes ruptures',
        businessProcess: 'Supervision entrepôt',
        requiredRoles: ['MAGASIN', 'STOCK', 'MANAGER']
      },
      {
        label: 'Réception & Entrées MAG3',
        path: '/magasin-stock/reception',
        icon: Boxes,
        badge: 'MAG3',
        tcode: 'KMAG_RCP',
        description: 'Réception physique sous douane MAG3, contrôle conformité',
        businessProcess: 'Entrée en stock',
        requiredRoles: ['MAGASIN', 'MAGASINIER']
      },
      {
        label: 'Préparation Commandes & Picking',
        path: '/magasin-stock/picking',
        icon: ShoppingCart,
        badge: 'Picking',
        tcode: 'KMAG_PIK',
        description: 'Algorithmes de picking optimisés FIFO/FEFO, mode mobile',
        businessProcess: 'Préparation colisage',
        requiredRoles: ['MAGASIN', 'MAGASINIER']
      },
      {
        label: 'Emplacements & Slots WMS',
        path: '/magasin-stock/locations',
        icon: MapPin,
        badge: 'Slots',
        tcode: 'KMAG_SLT',
        description: 'Cartographie zones, allées, travées, niveaux et capacité',
        businessProcess: 'Agencement stock',
        requiredRoles: ['MAGASIN', 'STOCK']
      },
      {
        label: 'Inventaires Physiques & Écarts',
        path: '/magasin-stock/inventory',
        icon: ClipboardList,
        badge: 'Inventaire',
        tcode: 'KMAG_INV',
        description: 'Inventaires tournants, comptage physique et valorisation',
        businessProcess: 'Contrôle stocks',
        isOhadaCompliant: true,
        requiredRoles: ['MAGASIN', 'AUDITOR', 'FINANCE']
      },
      {
        label: 'Mouvements & Transferts de Stock',
        path: '/magasin-stock/movements',
        icon: ArrowUpDown,
        badge: 'Transferts',
        tcode: 'KMAG_MVM',
        description: 'Transferts inter-magasins, ajustements et bons d enlèvement',
        businessProcess: 'Mouvements stock',
        isOhadaCompliant: true,
        requiredRoles: ['MAGASIN', 'STOCK']
      }
    ]
  },

  // ============================================================================
  // 📚 MODULE 5: COMPTABILITÉ OHADA (TYPE SAGE)
  // ============================================================================
  'comptabilite-ohada': {
    key: 'comptabilite-ohada',
    title: '📚 Comptabilité OHADA (Sage)',
    path: '/comptabilite-ohada/dashboard',
    icon: BookOpen,
    color: '#8b5cf6',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    businessArea: 'Comptabilité Générale',
    processPhase: 'Phase 5: Comptabilité & États Financiers',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'COMPTABLE', 'EXPERT_COMPTABLE', 'FINANCE', 'MANAGER'],
    subModules: [
      {
        label: 'Dashboard Comptable OHADA',
        path: '/comptabilite-ohada/dashboard',
        icon: LayoutDashboard,
        badge: 'OHADA',
        tcode: 'KOHA_DSH',
        description: 'Synthèse des journaux, écritures à valider, soldes de trésorerie',
        businessProcess: 'Pilotage comptable',
        isOhadaCompliant: true,
        requiredRoles: ['COMPTABLE', 'EXPERT_COMPTABLE', 'MANAGER']
      },
      {
        label: 'Journaux Auxiliaires & Saisie',
        path: '/comptabilite-ohada/journal',
        icon: BookOpen,
        badge: 'Journaux',
        tcode: 'KOHA_JRN',
        description: 'Achats, Ventes, Banque, Caisse, OD, Salaires, Amortissements, Lettrage',
        businessProcess: 'Saisie écritures',
        isOhadaCompliant: true,
        requiredRoles: ['COMPTABLE', 'EXPERT_COMPTABLE']
      },
      {
        label: 'Grand Livre & Balances',
        path: '/comptabilite-ohada/general-ledger',
        icon: Layers,
        badge: 'Grand Livre',
        tcode: 'KOHA_GL',
        description: 'Grand livre général et auxiliaires (411, 401, 512, 531), balance 6 colonnes',
        businessProcess: 'Livres légaux',
        isOhadaCompliant: true,
        requiredRoles: ['COMPTABLE', 'AUDITOR', 'EXPERT_COMPTABLE']
      },
      {
        label: 'Plan Comptable SYSCOHADA',
        path: '/comptabilite-ohada/chart-accounts',
        icon: Grid,
        badge: 'SYSCOHADA',
        tcode: 'KOHA_COA',
        description: 'Nomenclature officielle classes 1 à 8, comptes tiers, paramétrage',
        businessProcess: 'Référentiel comptable',
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'COMPTABLE']
      },
      {
        label: 'États Financiers (Bilan, CR, TAFIRE)',
        path: '/comptabilite-ohada/financial-statements',
        icon: BarChart3,
        badge: 'Bilan',
        tcode: 'KOHA_BIL',
        description: 'Bilan actif/passif, Compte de résultat, TAFIRE et Annexes certifiées',
        businessProcess: 'États financiers légaux',
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'FINANCE', 'MANAGER']
      },
      {
        label: 'Clôtures Mensuelle & Annuelle',
        path: '/comptabilite-ohada/monthly-closing',
        icon: Calendar,
        badge: 'Clôture',
        tcode: 'KOHA_CLO',
        description: 'Verrouillage périodes, dotations amortissements, reports à nouveau',
        businessProcess: 'Arrêté des comptes',
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE']
      },
      {
        label: 'Liasse Fiscale & Déclarations CEMAC',
        path: '/comptabilite-ohada/tax-package-cemac',
        icon: FileText,
        badge: 'Liasse',
        tcode: 'KOHA_TAX',
        description: 'Déclarations fiscales CEMAC, TVA 19.25%, IS, acomptes et DIPE',
        businessProcess: 'Fiscalité d entreprise',
        isCemacSpecific: true,
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'FINANCE']
      }
    ]
  },

  // ============================================================================
  // 💰 MODULE 6: FINANCE, TRÉSORERIE & FACTURATION
  // ============================================================================
  'finance-ohada': {
    key: 'finance-ohada',
    title: '💰 K-Finance & Trésorerie',
    path: '/finance-ohada/dashboard',
    icon: DollarSign,
    color: '#10b981',
    glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-teal-500',
    businessArea: 'Finance & Facturation',
    processPhase: 'Phase 6: Facturation & Trésorerie',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE', 'COMPTABLE', 'MANAGER'],
    subModules: [
      {
        label: 'Tableau de Bord Trésorerie',
        path: '/finance-ohada/dashboard',
        icon: LayoutDashboard,
        badge: 'Finance',
        tcode: 'KFIN_DSH',
        description: 'Cash flow en direct, prévisions liquidités, BFR et ratios',
        businessProcess: 'Pilotage financier',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'MANAGER']
      },
      {
        label: 'Trésorerie, Banques & Caisses',
        path: '/finance-ohada/treasury',
        icon: Banknote,
        badge: 'Cash Flow',
        tcode: 'KFIN_TRZ',
        description: 'Rapprochements bancaires, caisses principales/secondaires, virements',
        businessProcess: 'Gestion liquidités',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'COMPTABLE']
      },
      {
        label: 'Facturation & Émission Client',
        path: '/finance-ohada/invoicing',
        icon: Receipt,
        badge: 'Factures',
        tcode: 'KFIN_FAC',
        description: 'Génération automatique factures fret, transit et magasinage',
        businessProcess: 'Facturation client',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'COMPTABLE']
      },
      {
        label: 'Recouvrement & Créances Clients',
        path: '/finance-ohada/collections',
        icon: CreditCard,
        badge: 'Créances',
        tcode: 'KFIN_REC',
        description: 'Balance âgée clients, calcul DSO, relances et provisions',
        businessProcess: 'Gestion créances',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE']
      },
      {
        label: 'Dettes Fournisseurs & Achats',
        path: '/finance-ohada/suppliers',
        icon: FileText,
        badge: 'Dettes',
        tcode: 'KFIN_DET',
        description: 'Balance âgée fournisseurs, calcul DPO, calendrier d échéances',
        businessProcess: 'Gestion dettes',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE']
      },
      {
        label: 'Fiscalité Cameroun & Règlements Locaux',
        path: '/finance-ohada/taxes-cemac',
        icon: Calculator,
        badge: '🇨🇲 Fiscal',
        tcode: 'KFIN_TAX',
        description: 'TVA collectée/déductible, Mobile Money, prélèvements et retenues',
        businessProcess: 'Paiements & taxes',
        isCemacSpecific: true,
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE']
      }
    ]
  },

  // ============================================================================
  // 🚗 MODULE 7: PARC VÉHICULES & GMAO ATELIER
  // ============================================================================
  'parc-vehicules': {
    key: 'parc-vehicules',
    title: '🚗 K-Parc Véhicules & GMAO',
    path: '/parc-vehicules/dashboard',
    icon: Wrench,
    color: '#f97316',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-600 to-amber-500',
    businessArea: 'Maintenance & Parc',
    processPhase: 'Support: Maintenance & Disponibilité Matériel',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PARC', 'MAINTENANCE', 'MANAGER'],
    subModules: [
      {
        label: 'Tableau de Bord Parc & Atelier',
        path: '/parc-vehicules/dashboard',
        icon: LayoutDashboard,
        badge: 'Atelier',
        tcode: 'KMNT_DSH',
        description: 'Disponibilité du parc, véhicules immobilisés, coûts GMAO',
        businessProcess: 'Supervision matériel',
        requiredRoles: ['PARC', 'MAINTENANCE', 'MANAGER']
      },
      {
        label: 'Ordres de Travail & Réparations',
        path: '/parc-vehicules/preventive-maintenance',
        icon: Wrench,
        badge: 'GMAO',
        tcode: 'KMNT_WO',
        description: 'Création et clôture des ordres de réparation, bons de travail',
        businessProcess: 'Interventions atelier',
        requiredRoles: ['MAINTENANCE', 'PARC']
      },
      {
        label: 'Maintenance Préventive & Échéances',
        path: '/parc-vehicules/fleet-complete',
        icon: Clock,
        badge: 'Préventif',
        tcode: 'KMNT_PRV',
        description: 'Plannings vidanges, pneumatiques, visites techniques obligatoires',
        businessProcess: 'Plan préventif',
        requiredRoles: ['MAINTENANCE', 'PARC']
      },
      {
        label: 'Cartes Grises, Assurances & Conformité',
        path: '/parc-vehicules/documents',
        icon: FileCheck,
        badge: 'Papiers',
        tcode: 'KMNT_DOC',
        description: 'Suivi des polices d assurance, vignettes CEMAC et contrôles',
        businessProcess: 'Légalité véhicules',
        isCemacSpecific: true,
        requiredRoles: ['PARC', 'ADMINISTRATIF']
      },
      {
        label: 'Consommations, Coûts & TCO',
        path: '/parc-vehicules/costs-consumption',
        icon: TrendingUp,
        badge: 'TCO',
        tcode: 'KMNT_TCO',
        description: 'Calcul du coût total de possession au km par véhicule',
        businessProcess: 'Rentabilité parc',
        isOhadaCompliant: true,
        requiredRoles: ['PARC', 'FINANCE']
      }
    ]
  },

  // ============================================================================
  // 👥 MODULE 8: RH, PAIE OHADA & PERSONNEL
  // ============================================================================
  'rh-personnel': {
    key: 'rh-personnel',
    title: '👥 Ressources Humaines & Paie',
    path: '/rh-personnel/dashboard',
    icon: Users,
    color: '#ec4899',
    glow: 'shadow-pink-500/50 border-pink-500/60',
    bgGradient: 'from-pink-600 to-rose-500',
    businessArea: 'Ressources Humaines',
    processPhase: 'Support: Gestion Capital Humain',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'RH', 'PAIE', 'MANAGER'],
    subModules: [
      {
        label: 'Dashboard Ressources Humaines',
        path: '/rh-personnel/dashboard',
        icon: LayoutDashboard,
        badge: 'RH',
        tcode: 'KRH_DSH',
        description: 'Effectifs actifs, masse salariale, congés et indicateurs RH',
        businessProcess: 'Pilotage RH',
        requiredRoles: ['RH', 'MANAGER']
      },
      {
        label: 'Bulletins de Paie OHADA Cameroun',
        path: '/rh-personnel/payroll-ohada',
        icon: CreditCard,
        badge: 'Paie OHADA',
        tcode: 'KRH_PAY',
        description: 'Calcul net à payer, retenues fiscales IRGM, primes de transport',
        businessProcess: 'Émission paie',
        isOhadaCompliant: true,
        isCemacSpecific: true,
        requiredRoles: ['RH', 'PAIE']
      },
      {
        label: 'Annuaire & Dossiers Employés',
        path: '/rh-personnel/employees',
        icon: UserCheck,
        badge: 'Personnel',
        tcode: 'KRH_EMP',
        description: 'Contrats, fiches de poste, dossiers individuels et habilitations',
        businessProcess: 'Gestion personnel',
        requiredRoles: ['RH', 'MANAGER']
      },
      {
        label: 'Congés, Absences & Temps de Travail',
        path: '/rh-personnel/time-attendance',
        icon: Clock,
        badge: 'Congés',
        tcode: 'KRH_LEV',
        description: 'Demandes de congés conformes droit camerounais, pointages',
        businessProcess: 'Gestion des temps',
        isCemacSpecific: true,
        requiredRoles: ['RH', 'ALL_USERS']
      },
      {
        label: 'Déclarations Sociales (CNPS & DIPE)',
        path: '/rh-personnel/social-declarations',
        icon: FileText,
        badge: 'CNPS/DIPE',
        tcode: 'KRH_DIP',
        description: 'Télé-déclarations CNPS, télé-déclaration DIPE mensuelle/annuelle',
        businessProcess: 'Déclarations sociales',
        isCemacSpecific: true,
        requiredRoles: ['RH', 'PAIE']
      }
    ]
  },

  // ============================================================================
  // 🛡️ MODULE 9: QHSE, SÉCURITÉ & AUDIT ISPS
  // ============================================================================
  'qhse-securite': {
    key: 'qhse-securite',
    title: '🛡️ K-QHSE & Sécurité Portuaire',
    path: '/qhse-securite/dashboard',
    icon: ShieldAlert,
    color: '#ef4444',
    glow: 'shadow-red-500/50 border-red-500/60',
    bgGradient: 'from-red-600 to-rose-500',
    businessArea: 'Qualité & Sécurité',
    processPhase: 'Support: Conformité & Sécurité',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'QHSE', 'SECURITE', 'MANAGER', 'AUDITOR'],
    subModules: [
      {
        label: 'Centre de Sécurité & Alertes',
        path: '/qhse-securite/dashboard',
        icon: LayoutDashboard,
        badge: 'QHSE',
        tcode: 'KQHS_DSH',
        description: 'Taux de fréquence accidents, alertes critiques, conformité',
        businessProcess: 'Supervision QHSE',
        requiredRoles: ['QHSE', 'MANAGER']
      },
      {
        label: 'Inspections Portuaires & Norme ISPS',
        path: '/qhse-securite/port-inspections',
        icon: Shield,
        badge: 'ISPS',
        tcode: 'KQHS_ISP',
        description: 'Contrôles de conformité au code ISPS, audits de quai et navires',
        businessProcess: 'Inspections réglementaires',
        isCemacSpecific: true,
        requiredRoles: ['QHSE', 'AUDITOR']
      },
      {
        label: 'Registre Incidents & Signalements',
        path: '/qhse-securite/incident-management',
        icon: Bell,
        badge: 'Incidents',
        tcode: 'KQHS_INC',
        description: 'Déclaration temps réel des incidents, arbres des causes, actions',
        businessProcess: 'Gestion incidents',
        requiredRoles: ['QHSE', 'ALL_USERS']
      },
      {
        label: 'Formations & Habilitations Sécurité',
        path: '/qhse-securite/safety-training',
        icon: Users,
        badge: 'Habilitations',
        tcode: 'KQHS_TRN',
        description: 'Certificats de sécurité portuaire, recyclages EPI et caristes',
        businessProcess: 'Habilitations',
        requiredRoles: ['QHSE', 'RH']
      }
    ]
  },

  // ============================================================================
  // 🤝 MODULE 10: PORTAIL CLIENT B2B & CRM
  // ============================================================================
  'client-b2b': {
    key: 'client-b2b',
    title: '🤝 Portail Client B2B & CRM',
    path: '/client-b2b/dashboard',
    icon: Globe,
    color: '#0284c7',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-indigo-600',
    businessArea: 'Relation Client & B2B',
    processPhase: 'Support: Relation Clientèle',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'COMMERCIAL', 'CLIENT_B2B', 'CLIENT', 'MANAGER'],
    subModules: [
      {
        label: 'Espace Client B2B Central',
        path: '/client-b2b/dashboard',
        icon: LayoutDashboard,
        badge: 'B2B',
        tcode: 'KB2B_DSH',
        description: 'Tableau de bord expéditions, conteneurs et factures en cours',
        businessProcess: 'Portail client',
        requiredRoles: ['CLIENT', 'CLIENT_B2B', 'COMMERCIAL', 'MANAGER']
      },
      {
        label: 'Mes Expéditions & Tracking Live',
        path: '/client-b2b/portal',
        icon: Radio,
        badge: 'Tracking',
        tcode: 'KB2B_TRK',
        description: 'Géolocalisation en temps réel des conteneurs et fret en transit',
        businessProcess: 'Tracking client',
        requiredRoles: ['CLIENT', 'CLIENT_B2B', 'COMMERCIAL']
      },
      {
        label: 'Factures, Règlements & Avoirs',
        path: '/client-b2b/contracts',
        icon: FileText,
        badge: 'Factures',
        tcode: 'KB2B_INV',
        description: 'Consultation et téléchargement des factures dématérialisées',
        businessProcess: 'Factures client',
        isOhadaCompliant: true,
        requiredRoles: ['CLIENT', 'CLIENT_B2B', 'FINANCE']
      },
      {
        label: 'Service Client, Litiges & Tickets',
        path: '/client-b2b/after-sales',
        icon: MessageSquare,
        badge: 'Support',
        tcode: 'KB2B_SAV',
        description: 'Ouverture de tickets, réclamations fret et suivi résolutions',
        businessProcess: 'Support réclamations',
        requiredRoles: ['CLIENT', 'CLIENT_B2B', 'COMMERCIAL']
      }
    ]
  },

  // ============================================================================
  // 📊 MODULE 11: REPORTS & BI EXECUTIVE
  // ============================================================================
  'reports-bi': {
    key: 'reports-bi',
    title: '📊 K-Analytics BI Executive',
    path: '/reports-bi/executive-dashboard',
    icon: BarChart3,
    color: '#8b5cf6',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    businessArea: 'Business Intelligence',
    processPhase: 'Support: Décision & Reporting',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER', 'ANALYST', 'AUDITOR'],
    subModules: [
      {
        label: 'Executive Dashboard Direction',
        path: '/reports-bi/executive-dashboard',
        icon: LayoutDashboard,
        badge: 'Direction',
        tcode: 'KRPT_EXE',
        description: 'Chiffre d affaires consolidé, marges par activité, rentabilité',
        businessProcess: 'Pilotage stratégique',
        requiredRoles: ['MANAGER', 'DIRECTOR', 'ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Analytics Opérationnels WMS & Transport',
        path: '/reports-bi/operational-analytics',
        icon: LineChart,
        badge: 'Ops',
        tcode: 'KRPT_OPS',
        description: 'Délais moyens de livraison, rotation de stock, cadences quai',
        businessProcess: 'Analyse performance',
        requiredRoles: ['ANALYST', 'MANAGER']
      },
      {
        label: 'Rapports Financiers & Rentabilité',
        path: '/reports-bi/financial-reports-ohada',
        icon: TrendingUp,
        badge: 'Finance',
        tcode: 'KRPT_FIN',
        description: 'États comparatifs N vs N-1, marges brutes et cash flow',
        businessProcess: 'Reporting financier',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'MANAGER', 'AUDITOR']
      },
      {
        label: 'Générateur de Rapports Personnalisés',
        path: '/reports-bi/report-generator',
        icon: FileText,
        badge: 'Sur Mesure',
        tcode: 'KRPT_GEN',
        description: 'Constructeur de rapports ad-hoc et export multi-formats',
        businessProcess: 'Génération rapports',
        requiredRoles: ['ANALYST', 'POWER_USER', 'ADMIN']
      }
    ]
  },

  // ============================================================================
  // 👑 MODULE 12-A: GOUVERNANCE PLATEFORME SAAS (SUPER ADMIN EXCLUSIF)
  // ============================================================================
  'admin-saas': {
    key: 'admin-saas',
    title: '👑 Gouvernance Plateforme SaaS',
    path: '/admin-saas',
    icon: Crown,
    color: '#f59e0b',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-600',
    businessArea: 'Gouvernance Plateforme Multi-Entreprises',
    processPhase: 'SaaS Platform Owner (CADC)',
    requiredRoles: ['SUPER_ADMIN'],
    subModules: [
      {
        label: 'Supervision des Entreprises & Tenants',
        path: '/admin-saas/tenants',
        icon: Building,
        badge: 'Tenants',
        tcode: 'KSAAS_TNT',
        description: 'Gestion globale des entreprises clientes, licences et accès',
        businessProcess: 'Gestion multi-tenants',
        requiredRoles: ['SUPER_ADMIN']
      },
      {
        label: 'Abonnements & Licences Globales',
        path: '/admin-saas/subscriptions',
        icon: Tag,
        badge: 'Plans',
        tcode: 'KSAAS_SUB',
        description: 'Configuration des forfaits Enterprise, Pro, Starter et facturation SaaS',
        businessProcess: 'Monétisation SaaS',
        requiredRoles: ['SUPER_ADMIN']
      },
      {
        label: 'Infrastructure, Quotas & API Gateway',
        path: '/admin-saas/infrastructure',
        icon: Zap,
        badge: 'Infra',
        tcode: 'KSAAS_INF',
        description: 'Monitoring des ressources serveur, bases isolées et passerelle API',
        businessProcess: 'Supervision technique',
        requiredRoles: ['SUPER_ADMIN']
      },
      {
        label: 'Logs d Audit & Sécurité Plateforme',
        path: '/admin-saas/audit',
        icon: ShieldAlert,
        badge: 'Audit',
        tcode: 'KSAAS_AUD',
        description: 'Traçabilité complète des accès inter-organisations',
        businessProcess: 'Sécurité globale',
        requiredRoles: ['SUPER_ADMIN']
      }
    ]
  },

  // ============================================================================
  // 🏢 MODULE 12-B: ADMINISTRATION DE L'ENTREPRISE (ADMIN SIMPLE / COMPANY ADMIN)
  // ============================================================================
  'admin-tenant': {
    key: 'admin-tenant',
    title: '🏢 Administration de l Entreprise',
    path: '/admin-tenant/dashboard',
    icon: Settings,
    color: '#6366f1',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-violet-600',
    businessArea: 'Administration Entreprise',
    processPhase: 'Gouvernance Locale de la Société',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'COMPANY_ADMIN'],
    subModules: [
      {
        label: 'Tableau de Bord Entreprise',
        path: '/admin-tenant/dashboard',
        icon: LayoutDashboard,
        badge: 'Vue DG',
        tcode: 'KADM_DSH',
        description: 'Vue d ensemble des agences, entrepôts et indicateurs de l entreprise',
        businessProcess: 'Pilotage entreprise',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Agences & Sites Opérationnels',
        path: '/admin-tenant/agencies',
        icon: Building,
        badge: 'Agences',
        tcode: 'KADM_AGC',
        description: 'Gestion des agences Siège Douala, Port Kribi et Bafoussam',
        businessProcess: 'Organisation locale',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Collaborateurs & Attribution des Rôles',
        path: '/admin-tenant/users-rbac',
        icon: Users,
        badge: 'RH & Rôles',
        tcode: 'KADM_USR',
        description: 'Gestion des comptes employés de l entreprise et permissions',
        businessProcess: 'Gestion du personnel',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Journal d Audit de l Entreprise',
        path: '/admin-tenant/audit-logs',
        icon: Activity,
        badge: 'Audit',
        tcode: 'KAUD_LOG',
        description: 'Traçabilité des opérations internes à l entreprise',
        businessProcess: 'Conformité interne',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'AUDITOR']
      },
      {
        label: 'Paramètres & Préférences Locales',
        path: '/admin-tenant/integrations',
        icon: Wifi,
        badge: 'Config',
        tcode: 'KADM_SET',
        description: 'Paramètres régionaux, devises XAF et notifications internes',
        businessProcess: 'Paramétrage local',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      }
    ]
  },

  // ============================================================================
  // 💬 MODULE 13: CHAT & FORUM D'ENTREPRISE EN TEMPS RÉEL (TOUS RÔLES)
  // ============================================================================
  'chat': {
    key: 'chat',
    title: '💬 Chat & Forum d Entreprise',
    path: '/chat',
    icon: MessageSquare,
    color: '#06b6d4',
    glow: 'shadow-cyan-500/50 border-cyan-500/60',
    bgGradient: 'from-cyan-600 to-blue-600',
    businessArea: 'Communication & Collaboration Interne',
    processPhase: 'Transversal : Tous Départements',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'SECRETAIRE', 'GARDIEN', 'AGENT_ENTRETIEN', 'SUPPORT_IT', 'CHEF_MAGASIN', 'MAGASINIER', 'CHEF_COMPTABLE', 'FINANCIER', 'DIRECTEUR_TRANSPORT', 'DISPATCHER', 'CHAUFFEUR', 'DECLARANT_DOUANE', 'CHEF_PARC', 'RESPONSABLE_QHSE', 'AUDITEUR', 'USER'],
    subModules: [
      {
        label: 'Grand Forum d Entreprise',
        path: '/chat?tab=forum',
        icon: MessageSquare,
        badge: 'Forum',
        tcode: 'KCOM_FRM',
        description: 'Canal général officiel où chaque collaborateur s exprime avec son badge de rôle officiel',
        businessProcess: 'Communication générale'
      },
      {
        label: 'Messages Directs (1-à-1)',
        path: '/chat?tab=direct',
        icon: Users,
        badge: 'Direct',
        tcode: 'KCOM_DIR',
        description: 'Échange individuel instantané avec recherche par Nom ou par Rôle dans l entreprise',
        businessProcess: 'Messagerie directe'
      }
    ]
  },

  // ============================================================================
  // 👤 MODULE 14: PORTAIL SALARIÉ RH & SELF-SERVICE (COLLABORATEURS & SUPPORT)
  // ============================================================================
  'portail-employe': {
    key: 'portail-employe',
    title: '👤 Mon Espace Salarié (RH)',
    path: '/portail-employe',
    icon: UserCheck,
    color: '#10b981',
    glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-teal-600',
    businessArea: 'Ressources Humaines & Salariés',
    processPhase: 'Portail Employé & Collaborateurs',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'SECRETAIRE', 'GARDIEN', 'AGENT_ENTRETIEN', 'SUPPORT_IT', 'CHEF_MAGASIN', 'MAGASINIER', 'CHEF_COMPTABLE', 'FINANCIER', 'DIRECTEUR_TRANSPORT', 'DISPATCHER', 'CHAUFFEUR', 'DECLARANT_DOUANE', 'CHEF_PARC', 'RESPONSABLE_QHSE', 'AUDITEUR', 'USER'],
    subModules: [
      {
        label: 'Mes Bulletins de Paie OHADA',
        path: '/portail-employe?tab=bulletins',
        icon: FileText,
        badge: 'Paie',
        tcode: 'KEMP_PAY',
        description: 'Consultation et téléchargement des fiches de paie mensuelles OHADA',
        businessProcess: 'Rémunération'
      },
      {
        label: 'Demandes de Congés & Absences',
        path: '/portail-employe?tab=conges',
        icon: Calendar,
        badge: 'Congés',
        tcode: 'KEMP_LV',
        description: 'Formulaire de dépôt de congés payés, maladie, autorisations et suivi en direct',
        businessProcess: 'Gestion du temps'
      },
      {
        label: 'Documents & Attestations RH',
        path: '/portail-employe?tab=documents',
        icon: FileCheck,
        badge: 'Documents',
        tcode: 'KEMP_DOC',
        description: 'Attestations d emploi, fiches de poste, notes de service et contrats',
        businessProcess: 'Administration du personnel'
      }
    ]
  },

  // ============================================================================
  // 🧭 HUB COLLABORATEUR CENTRALISÉ (CARREFOUR DES ESPACES MÉTIERS)
  // ============================================================================
  'portail-collaborateur': {
    key: 'portail-collaborateur',
    title: '🧭 Hub Collaborateurs',
    path: '/portail-collaborateur',
    icon: Compass,
    color: '#6366f1',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-slate-800',
    businessArea: 'Espaces Collaborateurs',
    processPhase: 'Carrefour Espaces Métiers',
    requiredRoles: [],
    subModules: [
      {
        label: 'Tous les Portails Métier',
        path: '/portail-collaborateur',
        icon: Compass,
        badge: 'Hub',
        tcode: 'KHUB_COL',
        description: 'Accès rapide et unifié à tous vos espaces de travail collaborateur',
        businessProcess: 'Navigation transversale'
      }
    ]
  },

  // ============================================================================
  // 🚚 PORTAIL COLLABORATEUR CHAUFFEUR & ROUTE
  // ============================================================================
  'portail-chauffeur': {
    key: 'portail-chauffeur',
    title: '🚚 Espace Chauffeur & Route',
    path: '/portail-chauffeur',
    icon: Truck,
    color: '#d97706',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-orange-600',
    businessArea: 'Transport & Flotte',
    processPhase: 'Mobilité & Équipage Route',
    requiredRoles: ['CHAUFFEUR', 'CONDUCTEUR', 'TRANSPORTEUR', 'DISPATCHER', 'CHEF_PARC', 'ADMIN', 'SUPER_ADMIN'],
    subModules: [
      {
        label: 'Ma Tournée & Missions',
        path: '/portail-chauffeur',
        icon: Navigation,
        badge: 'Tournée',
        tcode: 'KDRV_TRN',
        description: 'Ordres de transport, itinéraires GPS et statut de livraison',
        businessProcess: 'Exécution transport'
      }
    ]
  },

  // ============================================================================
  // 💼 PORTAIL COLLABORATEUR NOTES DE FRAIS & MISSIONS
  // ============================================================================
  'portail-frais': {
    key: 'portail-frais',
    title: '💼 Frais & Avances Missions',
    path: '/portail-frais',
    icon: Receipt,
    color: '#059669',
    glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-teal-600',
    businessArea: 'Finance & Personnel',
    processPhase: 'Gestion des Dépenses Collaborateurs',
    requiredRoles: [],
    subModules: [
      {
        label: 'Mes Notes de Frais',
        path: '/portail-frais',
        icon: Receipt,
        badge: 'Frais',
        tcode: 'KEXP_FEE',
        description: 'Saisie des notes de frais, justificatifs et demandes d avances',
        businessProcess: 'Gestion financière terrain'
      }
    ]
  },

  // ============================================================================
  // 📦 PORTAIL COLLABORATEUR MAGASINIER & QUAI
  // ============================================================================
  'portail-magasinier': {
    key: 'portail-magasinier',
    title: '📦 Espace Magasinier & Quai',
    path: '/portail-magasinier',
    icon: Warehouse,
    color: '#0891b2',
    glow: 'shadow-cyan-500/50 border-cyan-500/60',
    bgGradient: 'from-cyan-600 to-blue-700',
    businessArea: 'Entrepôt & WMS',
    processPhase: 'Opérations Quai & Stock',
    requiredRoles: ['MAGASINIER', 'MANUTENTIONNAIRE', 'LOGISTICIEN', 'CHEF_MAGASIN', 'ADMIN', 'SUPER_ADMIN'],
    subModules: [
      {
        label: 'Picking & Dépotage Quai',
        path: '/portail-magasinier',
        icon: Warehouse,
        badge: 'WMS',
        tcode: 'KWMS_OP',
        description: 'Préparation commandes, réceptions à quai et inventaires tournants',
        businessProcess: 'Manutention entrepôt'
      }
    ]
  },

  // ============================================================================
  // 🔧 PORTAIL COLLABORATEUR TECHNICIEN GMAO
  // ============================================================================
  'portail-technicien': {
    key: 'portail-technicien',
    title: '🔧 Espace Technicien GMAO',
    path: '/portail-technicien',
    icon: Wrench,
    color: '#7c3aed',
    glow: 'shadow-purple-500/50 border-purple-500/60',
    bgGradient: 'from-purple-600 to-indigo-700',
    businessArea: 'Atelier & Maintenance',
    processPhase: 'Maintenance Préventive & Curative',
    requiredRoles: ['TECHNICIEN', 'MECANICIEN', 'CHEF_ATELIER', 'MAINTENANCE', 'ADMIN', 'SUPER_ADMIN'],
    subModules: [
      {
        label: 'Ordres de Travail (OT)',
        path: '/portail-technicien',
        icon: Wrench,
        badge: 'GMAO',
        tcode: 'KTEC_OT',
        description: 'Interventions mécaniques, clôture OT et sortie pièces magasin',
        businessProcess: 'Atelier mécanique'
      }
    ]
  },

  // ============================================================================
  // 🏛️ PORTAIL COLLABORATEUR DÉCLARANT DOUANE TERRAIN
  // ============================================================================
  'portail-declarant': {
    key: 'portail-declarant',
    title: '🏛️ Espace Déclarant Douane',
    path: '/portail-declarant',
    icon: FileText,
    color: '#4f46e5',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-blue-800',
    businessArea: 'Transit & Douane',
    processPhase: 'Jalonnement Terrain Port & Frontières',
    requiredRoles: ['DECLARANT', 'DECLARANT_DOUANE', 'AGENT_TRANSIT', 'TRANSITAIRE', 'CHEF_TRANSIT', 'ADMIN', 'SUPER_ADMIN'],
    subModules: [
      {
        label: 'Dossiers & Visite Douane',
        path: '/portail-declarant',
        icon: FileText,
        badge: 'Douane',
        tcode: 'KCST_FLD',
        description: 'Pointage scanner, visite conjointe, pesage et BAE',
        businessProcess: 'Transit douanier'
      }
    ]
  },

  // ============================================================================
  // 🦺 PORTAIL COLLABORATEUR VIGIE SÉCURITÉ & QHSE
  // ============================================================================
  'portail-qhse': {
    key: 'portail-qhse',
    title: '🦺 Vigie Sécurité & QHSE',
    path: '/portail-qhse',
    icon: ShieldAlert,
    color: '#e11d48',
    glow: 'shadow-rose-500/50 border-rose-500/60',
    bgGradient: 'from-rose-600 to-red-700',
    businessArea: 'Sécurité & Prévention',
    processPhase: 'Signalement Risques & Conformité',
    requiredRoles: [],
    subModules: [
      {
        label: 'Signalement Flash Danger',
        path: '/portail-qhse',
        icon: ShieldAlert,
        badge: 'Sécurité',
        tcode: 'KQHS_ALR',
        description: 'Remontée des presqu accidents, vérification EPI et fiches matières dangereuses',
        businessProcess: 'Prévention des risques'
      }
    ]
  },

  // ============================================================================
  // 🤝 PORTAIL COLLABORATEUR COMMERCIAL & CRM
  // ============================================================================
  'portail-commercial': {
    key: 'portail-commercial',
    title: '🤝 Espace Commercial & Devis',
    path: '/portail-commercial',
    icon: TrendingUp,
    color: '#f59e0b',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-500 to-yellow-600',
    businessArea: 'Ventes & Facturation',
    processPhase: 'Cotation CEMAC & Gestion Portefeuille',
    requiredRoles: ['COMMERCIAL', 'CHARGE_AFFAIRES', 'DIRECTEUR_COMMERCIAL', 'ADMIN', 'SUPER_ADMIN'],
    subModules: [
      {
        label: 'Simulateur Cotation CEMAC',
        path: '/portail-commercial',
        icon: TrendingUp,
        badge: 'Ventes',
        tcode: 'KSAL_CRM',
        description: 'Cotation express transport corridor, pipeline devis et encours clients',
        businessProcess: 'Prospection commerciale'
      }
    ]
  },

  // ============================================================================
  // 🏢 ANNUAIRE DES PRESTATAIRES B2B & SOUS-TRAITANTS
  // ============================================================================
  'annuaire-prestataires': {
    key: 'annuaire-prestataires',
    title: 'Annuaire des Prestataires & Sous-traitants',
    path: '/annuaire-prestataires',
    icon: Building,
    color: '#d97706',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-600',
    businessArea: 'Achats & Sous-traitance Portuaire',
    processPhase: 'Consultations & Gestion Prestataires',
    requiredRoles: ['ACHATS', 'DIRECTEUR_TRANSPORT', 'CHEF_PARC', 'ADMIN', 'SUPER_ADMIN', 'DAF', 'CHEF_COMPTABLE'],
    subModules: [
      {
        label: 'Annuaire Prestataires Certifiés',
        path: '/annuaire-prestataires',
        icon: Building,
        badge: 'Annuaire',
        tcode: 'KPRST_DIR',
        description: 'Répertoire des sous-traitants agréés PAD/PAK avec filtres métiers et ports',
        businessProcess: 'Sourcing & Référencement'
      },
      {
        label: 'Demandes de Cotations (RFQ)',
        path: '/annuaire-prestataires?tab=cotations',
        icon: ShoppingCart,
        badge: 'RFQ',
        tcode: 'KPRST_RFQ',
        description: 'Consultations de prix, devis urgents et comparatifs sous-traitance',
        businessProcess: 'Négociation Achats'
      },
      {
        label: 'Conformité & Agréments Portuaires',
        path: '/annuaire-prestataires?tab=conformite',
        icon: Shield,
        badge: 'Agréments',
        tcode: 'KPRST_PAD',
        description: 'Statut légal NIF/RCCM et habilitations sûreté portuaire ISPS',
        businessProcess: 'Conformité Fournisseurs'
      }
    ]
  },

  // ============================================================================
  // 🛡️ CHEF DU PERSONNEL : SUPERVISION N+1 RÔLES PASSIFS
  // ============================================================================
  'chef-personnel': {
    key: 'chef-personnel',
    title: 'Chef du Personnel (N+1 Rôles Passifs)',
    path: '/chef-personnel',
    icon: UserCheck,
    color: '#059669',
    glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-teal-600',
    businessArea: 'Supervision & Encadrement de Terrain',
    processPhase: 'Supervision N+1 Secrétariat, Sécurité, Entretien & IT',
    requiredRoles: ['CHEF_PERSONNEL', 'RH', 'ADMIN', 'SUPER_ADMIN'],
    subModules: [
      {
        label: 'Supervision des Effectifs N+1',
        path: '/chef-personnel?tab=effectifs',
        icon: Users,
        badge: 'Effectifs',
        tcode: 'KCP_STF',
        description: 'Présence en temps réel des agents par site (Douala, Kribi, Bafoussam)',
        businessProcess: 'Contrôle présence'
      },
      {
        label: 'Validation Congés & Absences N+1',
        path: '/chef-personnel?tab=conges',
        icon: Calendar,
        badge: 'Validation',
        tcode: 'KCP_LV',
        description: 'Validation ou rejet direct des demandes de congés des rôles passifs',
        businessProcess: 'Arbitrage managérial'
      },
      {
        label: 'Plannings & Gardes 24/7',
        path: '/chef-personnel?tab=plannings',
        icon: Clock,
        badge: 'Rotations',
        tcode: 'KCP_PLN',
        description: 'Tours de garde jour/nuit et affectations aux postes stratégiques',
        businessProcess: 'Planification vacations'
      },
      {
        label: 'Pointages & Vacations de Nuit',
        path: '/chef-personnel?tab=pointages',
        icon: ClipboardList,
        badge: 'Émargement',
        tcode: 'KCP_CLK',
        description: 'Registre des émargements et calcul des primes de panier de nuit OHADA',
        businessProcess: 'Contrôle des temps'
      },
      {
        label: 'Dotations EPI & Matériel',
        path: '/chef-personnel?tab=dotations',
        icon: Shield,
        badge: 'EPI',
        tcode: 'KCP_EPI',
        description: 'Attribution des gilets ISPS, chaussures de sécurité et radios VHF',
        businessProcess: 'Dotations agents'
      }
    ]
  }
};

/**
 * Fonction d'orchestration RBAC Senior
 * Filtre dynamiquement les modules et sous-modules selon les rôles et permissions de l'utilisateur.
 */
export function getFilteredNavigationForUser(
  user: {
    roles?: string[];
    modulesAllowed?: string[];
    permissions?: string[];
  } | null
): ModuleNavConfig[] {
  if (!user) return Object.values(NAVIGATION_REGISTRY);

  const userRoles = (user.roles || []).map(r => r.toUpperCase());
  const isSuperAdmin = userRoles.includes('SUPER_ADMIN');
  const isCompanyAdmin = userRoles.includes('ADMIN') || userRoles.includes('COMPANY_ADMIN');
  const isSupportStaff = userRoles.some(r => ['SECRETAIRE', 'GARDIEN', 'AGENT_ENTRETIEN', 'SUPPORT_IT'].includes(r));
  const userModules = (user.modulesAllowed || []).map(m => m.toLowerCase());
  const userPermissions = user.permissions || [];

  return Object.values(NAVIGATION_REGISTRY).map(moduleConfig => {
    // 1. SUPER ADMIN: A accès exclusif à la plateforme SaaS et aux modules de supervision
    if (isSuperAdmin) {
      return moduleConfig;
    }

    // 2. STRICT RESTRICTION: Les non-SuperAdmins ne peuvent JAMAIS voir la gouvernance SaaS
    if (moduleConfig.key === 'admin-saas') {
      return null;
    }

    // 3. COMPANY ADMIN: Accède à l'administration d'entreprise, aux rapports BI, au chat, aux prestataires et au chef du personnel
    if (isCompanyAdmin) {
      if (['admin-tenant', 'reports-bi', 'chat', 'portail-employe', 'dashboard', 'master-data', 'rh', 'annuaire-prestataires', 'chef-personnel'].includes(moduleConfig.key)) {
        return moduleConfig;
      }
    }

    // 4. SUPPORT STAFF (Secrétaires, Gardiens, Entretien, Support IT):
    // Accès ciblé : Espaces Collaborateurs, Chat & Forum d'entreprise, Dashboard
    if (isSupportStaff) {
      if (!['portail-employe', 'portail-collaborateur', 'portail-frais', 'portail-qhse', 'chat', 'dashboard'].includes(moduleConfig.key)) {
        // Support IT peut aussi avoir accès à master-data si besoin
        if (userRoles.includes('SUPPORT_IT') && moduleConfig.key === 'master-data') {
          return moduleConfig;
        }
        return null;
      }
    }

    // 5. VÉRIFICATION GÉNÉRALE PAR RÔLE OU MODULE AUTORISÉ
    const hasRoleAccess = moduleConfig.requiredRoles?.some(role => userRoles.includes(role.toUpperCase())) ?? false;
    const hasModuleAccess = userModules.includes(moduleConfig.key.toLowerCase());

    const isUniversalPortal =
      moduleConfig.key === 'dashboard' ||
      moduleConfig.key === 'chat' ||
      moduleConfig.key === 'portail-employe' ||
      moduleConfig.key === 'portail-collaborateur' ||
      moduleConfig.key === 'portail-frais' ||
      moduleConfig.key === 'portail-qhse';

    const isModuleAllowed = isUniversalPortal || hasRoleAccess || hasModuleAccess;

    if (!isModuleAllowed) return null;

    // Filtrer les sous-modules pour cet utilisateur métier
    const filteredSubModules = moduleConfig.subModules.filter(sub => {
      if (!sub.requiredRoles || sub.requiredRoles.length === 0) return true;
      if (isSuperAdmin) return true;
      return sub.requiredRoles.some(r =>
        userRoles.includes(r.toUpperCase()) ||
        userPermissions.includes(r)
      );
    });

    if (filteredSubModules.length === 0 && moduleConfig.subModules.length > 0) return null;

    return {
      ...moduleConfig,
      subModules: filteredSubModules
    };
  }).filter(Boolean) as ModuleNavConfig[];
}

/**
 * Retourne les modules compatibles OHADA
 */
export function getOhadaCompliantModules(): ModuleNavConfig[] {
  return Object.values(NAVIGATION_REGISTRY).filter(module =>
    module.subModules.some(sub => sub.isOhadaCompliant)
  );
}

/**
 * Retourne les modules spécifiques CEMAC/Cameroun
 */
export function getCemacSpecificModules(): ModuleNavConfig[] {
  return Object.values(NAVIGATION_REGISTRY).filter(module =>
    module.subModules.some(sub => sub.isCemacSpecific)
  );
}