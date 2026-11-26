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
  ArrowRightLeft, Bot, CheckCircle2, Inbox, AlertTriangle,
 // Identité du département Aménagement portuaire (registres réels du circuit
 // camerounais: schéma directeur, PIP/CDMT, COLIFE, titre domanial, PPP…).
  DraftingCompass, ScrollText, HardHat, CalendarRange, Gavel, Stamp,
  FileSignature, Building2, Waves, FileBadge
} from 'lucide-react';
import * as LUCIDE from 'lucide-react';
import { getModulePalette, LEGACY_ALIAS } from './modulePalette';
import { MODULE_TITLES_EN } from './navI18n';

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
  titleEn?: string;
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
      },
    ]
  },

 // ============================================================================
 // 🚢 MODULE 1: OPÉRATIONS PORTUAIRES & ACCONAGE
 // ============================================================================
  'port-operations': {
    key: 'port-operations',
    title: 'Opérations Portuaires & Quai',
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
      },
      {
        label: "Laissez-passer",
        path: "/port-operations/gate-passes",
        icon: (LUCIDE as any)["Ticket"],
        tcode: "registre-gate-passes",
        description: "Laissez-pisser de sortie de marchandise.",
        requiredRoles: ["port_ops.gate_pass.read"],
      },
    ]
  },

 // ============================================================================
 // 📐 MODULE 1-BIS: DÉPARTEMENT AMÉNAGEMENT PORTUAIRE (AUTONOME)
 // ----------------------------------------------------------------------------
 // Département autonome distinct de l'exploitation du quai: il tient le
 // domaine public, les schémas directeurs, la programmation budgétaire, les
 // marchés et les ouvrages des places de Douala, Kribi et Limbé. Les écrans
 // n'affichent QUE ce qui est saisi en base (voir router
 // /api/v1/amenagement-portuaire: nomenclatures, places et synthèse servies
 // par l'API, téléprocédures institutionnelles annoncées 501).
 // ============================================================================
  'amenagement-portuaire': {
    key: 'amenagement-portuaire',
    title: 'Aménagement Portuaire & Domaine Public',
    path: '/amenagement-portuaire/dashboard',
    icon: DraftingCompass,
    color: '#0e7490',
    glow: 'shadow-cyan-600/50 border-cyan-600/60',
    bgGradient: 'from-cyan-700 to-sky-900',
    businessArea: 'Aménagement & Domaine Public Portuaire',
    processPhase: 'Transverse: Structuration du Domaine, des Schémas & des Ouvrages',
    requiredRoles: [
      'ADMIN', 'SUPER_ADMIN', 'MANAGER',
 // Rôles système réels créés par la migration 039 côté backend.
      'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT',
      'AUDITEUR', 'DIRECTEUR_FINANCIER', 'CHEF_EXPLOITATION',
    ],
    subModules: [
      {
        label: 'Centre de Pilotage Aménagement',
        path: '/amenagement-portuaire/dashboard',
        icon: LayoutDashboard,
        badge: 'Synthèse',
        tcode: 'KAMT_DSH',
        description: 'Vue consolidée du domaine, de la programmation et des ouvrages (chiffres saisis uniquement)',
        businessProcess: 'Pilotage de l\'aménagement',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'AUDITEUR', 'CHEF_EXPLOITATION', 'DIRECTEUR_FINANCIER', 'MANAGER']
      },
      {
        label: 'Schémas Directeurs & Périmètres',
        path: '/amenagement-portuaire/schemas-directeurs',
        icon: ScrollText,
        badge: 'Urbanisme',
        tcode: 'KAMT_SCH',
        description: 'Schéma directeur d\'aménagement, périmètre du domaine public et horizon de révision',
        businessProcess: 'Planification du domaine',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'AUDITEUR']
      },
      {
        label: "Projets d'Aménagement",
        path: '/amenagement-portuaire/projets',
        icon: HardHat,
        badge: 'Portefeuille',
        tcode: 'KAMT_PRJ',
        description: 'Fiche technique, capacité additionnelle, maîtrise d\'ouvrage et avancement physique et financier',
        businessProcess: 'Portefeuille de projets',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'AUDITEUR', 'CHEF_EXPLOITATION']
      },
      {
        label: 'Programmation & Maturité (PIP/CDMT)',
        path: '/amenagement-portuaire/programmation',
        icon: CalendarRange,
        badge: 'Budget',
        tcode: 'KAMT_PIP',
        description: 'Circuit réel : visa de maturité, inscription au PIP/CDMT, engagement visé par le contrôle financier',
        businessProcess: 'Programmation des investissements',
        isOhadaCompliant: true,
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'DIRECTEUR_FINANCIER']
      },
      {
        label: 'Marchés Publics & PPP',
        path: '/amenagement-portuaire/marches',
        icon: Gavel,
        badge: 'COLIFE',
        tcode: 'KAMT_MCH',
        description: 'DAO, avis COLIFE ou CIP, attribution, réceptions et contrats de partenariat (loi n° 2023/008)',
        businessProcess: 'Passation des marchés',
        isCemacSpecific: true,
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'DIRECTEUR_FINANCIER']
      },
      {
        label: 'Titres Domaniaux & Occupations',
        path: '/amenagement-portuaire/titres-domaniaux',
        icon: Stamp,
        badge: 'Domaine',
        tcode: 'KAMT_DOM',
        description: 'Autorisation d\'occupation, bail domanial et concession de terrain : assiette, redevance, échéance',
        businessProcess: 'Gestion du domaine public',
        isCemacSpecific: true,
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'AUDITEUR']
      },
      {
        label: 'Inventaire des Infrastructures',
        path: '/amenagement-portuaire/infrastructures',
        icon: Building2,
        badge: 'Patrimoine',
        tcode: 'KAMT_INF',
        description: 'Ouvrages bâtis : quais, terre-pleins, digues  cotes, portance, inspections et état structural',
        businessProcess: 'Inventaire du patrimoine',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'AUDITEUR', 'CHEF_EXPLOITATION']
      },
      {
        label: 'Dragage & Profondeurs Disponibles',
        path: '/amenagement-portuaire/dragage',
        icon: Waves,
        badge: 'Bathymétrie',
        tcode: 'KAMT_DRG',
        description: 'Campagnes, volumes mesurés et facturés, profondeur obtenue et relevé bathymétrique de clôture',
        businessProcess: 'Maintien des profondeurs',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'AUDITEUR', 'CHEF_EXPLOITATION']
      },
      {
        label: 'Autorisations Administratives (EIES)',
        path: '/amenagement-portuaire/autorisations',
        icon: FileBadge,
        badge: 'Conformité',
        tcode: 'KAMT_AUT',
        description: 'Études et permis : administration saisine, dates de dépôt, d\'accord et d\'expiration',
        businessProcess: 'Conformité réglementaire',
        isCemacSpecific: true,
        requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CHEF_AMENAGEMENT_PORTUAIRE', 'INGENIEUR_AMENAGEMENT', 'QHSE', 'AUDITEUR']
      },
      {
        label: "Maintenance preventive ouvrages",
        path: "/amenagement-portuaire/infrastructure-maintenance",
        icon: (LUCIDE as any)["Wrench"],
        tcode: "registre-infrastructure-maintenance",
        description: "Plan de maintenance des ouvrages.",
        requiredRoles: ["amenagement.infrastructure_maintenance.read"],
      },
    ]
  },

 // ============================================================================
 // 🛃 MODULE 2: TRANSIT & DOUANE CEMAC
 // ============================================================================
  'transit-douane': {
    key: 'transit-douane',
    title: 'Transit & Douane CEMAC',
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
      },
      {
        label: "Regimes economiques",
        path: "/transit-douane/customs-regimes",
        icon: (LUCIDE as any)["Settings"],
        tcode: "registre-customs-regimes",
        description: "Admission temporaire, perfectionnement actif/passif, sous douane, exportation temporaire.",
        requiredRoles: ["transit.customs_regime.read"],
      },
      {
        label: "Enregistrement operateur economique",
        path: "/transit-douane/trader-registration",
        icon: (LUCIDE as any)["Fingerprint"],
        tcode: "registre-trader-registration",
        description: "Numeros operateur EORI local / agrements OEA.",
        requiredRoles: ["transit.trader_registration.read"],
      },
      {
        label: "Incoterms applicables",
        path: "/transit-douane/incoterm-terms",
        icon: (LUCIDE as any)["Scale"],
        tcode: "registre-incoterm-terms",
        description: "Referentiel des incoterms et de leur version.",
        requiredRoles: ["transit.incoterm_term.read"],
      },
    ]
  },

 // ============================================================================
 // 🚛 MODULE 3: TRANSPORT TMS & DISPATCH INTELLIGENT
 // ============================================================================
  'transport-flotte': {
    key: 'transport-flotte',
    title: 'K-Transport & Flotte TMS',
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
      },
      {
        label: "Fiche vehicule",
        path: "/transport-flotte/vehicle-registry",
        icon: (LUCIDE as any)["Truck"],
        tcode: "registre-vehicle-registry",
        description: "Registre technique des vehicules de la flotte.",
        requiredRoles: ["transport.vehicle_registry.read"],
      },
      {
        label: "Controles routiers et pesages",
        path: "/transport-flotte/checkpoint-tracking",
        icon: (LUCIDE as any)["MapPin"],
        tcode: "registre-checkpoint-tracking",
        description: "Controles effectues aux balises et ponts-bascules.",
        requiredRoles: ["transport.checkpoint.read"],
      },
      {
        label: "Facturation fret",
        path: "/transport-flotte/freight-billing",
        icon: (LUCIDE as any)["Receipt"],
        tcode: "registre-freight-billing",
        description: "Factures de transport, accessoires et supplement.",
        requiredRoles: ["transport.freight_billing.read"],
      },
      {
        label: "Transporteurs sous-traitants",
        path: "/transport-flotte/subcontractors",
        icon: (LUCIDE as any)["Users"],
        tcode: "registre-subcontractors",
        description: "Referentiel des transporteurs externes et capacites.",
        requiredRoles: ["transport.subcontractor.read"],
      },
      {
        label: "Boitiers GPS / telematique",
        path: "/transport-flotte/gps-devices",
        icon: (LUCIDE as any)["Satellite"],
        tcode: "registre-gps-devices",
        description: "Inventaire boitiers et plans de suivi.",
        requiredRoles: ["transport.gps_device.read"],
      },
      {
        label: "Infractions et PV routiers",
        path: "/transport-flotte/penalty-tracking",
        icon: (LUCIDE as any)["Ticket"],
        tcode: "registre-penalty-tracking",
        description: "PV recus, suites donnees, reglement.",
        requiredRoles: ["transport.penalty.read"],
      },
      {
        label: "Convois et escorte",
        path: "/transport-flotte/convoy-management",
        icon: (LUCIDE as any)["Users"],
        tcode: "registre-convoy-management",
        description: "Groupements de vehicules sous escorte armee ou civile.",
        requiredRoles: ["transport.convoy.read"],
      },
      {
        label: "TCO et taux de service",
        path: "/transport-flotte/performance-kpi",
        icon: (LUCIDE as any)["TrendingUp"],
        tcode: "registre-performance-kpi",
        description: "Indicateurs de performance de la flotte.",
        requiredRoles: ["transport.performance_kpi.read"],
      },
      {
        label: "Bons de mission / affectation",
        path: "/transport-flotte/mission-dispatches",
        icon: (LUCIDE as any)["Navigation"],
        tcode: "registre-mission-dispatches",
        description: "Affectation d'un vehicule et d'un chauffeur a une mission de transport.",
        requiredRoles: ["transport.dispatch.read"],
      },
      {
        label: "Preuves de livraison (POD)",
        path: "/transport-flotte/proof-of-delivery",
        icon: (LUCIDE as any)["FileSignature"],
        tcode: "registre-proof-of-delivery",
        description: "Accuse de livraison signe par le destinataire.",
        requiredRoles: ["transport.pod.read"],
      },
    ]
  },

 // ============================================================================
 // 📦 MODULE 4: MAGASIN & STOCK WMS
 // ============================================================================
  'magasin-stock': {
    key: 'magasin-stock',
    title: 'K-Magasin WMS & Stock',
    path: '/magasin-stock/picking',
    icon: Package,
    color: '#f59e0b',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-500',
    businessArea: 'Entreposage & Stock',
    processPhase: 'Phase 4: Gestion Stock & Préparation',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAGASIN', 'MAGASINIER', 'STOCK', 'MANAGER'],
    subModules: [
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
        label: "KPIs magasin",
        path: "/magasin-stock/wms-analytics",
        icon: (LUCIDE as any)["BarChart3"],
        tcode: "registre-wms-analytics",
        description: "Rotation, rupture, taux de service, cadence de preparation.",
        requiredRoles: ["magasin.wms_analytics.read"],
      },
      {
        label: "Valorisation & FEFO",
        path: "/magasin-stock/valorisation",
        icon: (LUCIDE as any)["Package"],
        badge: "FEFO",
        tcode: "KMAG_VAL",
        description: "Valorisation des stocks et allocation FEFO par péremption croissante",
        businessProcess: "Valorisation & sortie FEFO",
        isOhadaCompliant: true,
        requiredRoles: ['MAGASIN', 'FINANCE', 'AUDITOR']
      },
    ]
  },

 // ============================================================================
 // 📚 MODULE 5: COMPTABILITÉ OHADA (TYPE SAGE)
 // ============================================================================
  'comptabilite-ohada': {
    key: 'comptabilite-ohada',
    title: 'Comptabilité OHADA (Sage)',
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
      },
      {
        label: 'Immobilisations amortissables',
        path: '/comptabilite-ohada/immobilisations',
        icon: (LUCIDE as any)["Building2"],
        badge: 'Immo',
        tcode: 'KOHA_IMM',
        description: 'Registre des immobilisations, échéancier et dotations 681/28x automatiques',
        businessProcess: 'Amortissements SYSCOHADA',
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'FINANCE']
      },
      {
        label: 'Liasse fiscale CEMAC',
        path: '/comptabilite-ohada/liasse-fiscale',
        icon: (LUCIDE as any)["FileSpreadsheet"],
        badge: 'Liasse',
        tcode: 'KOHA_LIA',
        description: 'Consolidation TVA + IS depuis les déclarations réelles de l exercice',
        businessProcess: 'Déclarations fiscales',
        isCemacSpecific: true,
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'FINANCE']
      },
    ]
  },

 // ============================================================================
 // 💰 MODULE 6: FINANCE, TRÉSORERIE & FACTURATION
 // ============================================================================
  'finance-ohada': {
    key: 'finance-ohada',
    title: 'K-Finance & Trésorerie',
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
      },
    ]
  },

 // ============================================================================
 // 🚗 MODULE 7: PARC VÉHICULES & GMAO ATELIER
 // ============================================================================
  'parc-vehicules': {
    key: 'parc-vehicules',
    title: 'K-Parc Véhicules & GMAO',
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
      },
          
      
      
      
      

      
      
      
      
    ]
  },

 // ============================================================================
 // 👥 MODULE 8: RH, PAIE OHADA & PERSONNEL
 // ============================================================================
  'rh-personnel': {
    key: 'rh-personnel',
    title: 'Ressources Humaines & Paie',
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
        label: 'Récapitulatif annuel de paie',
        path: '/rh/paie-recapitulatif',
        icon: (LUCIDE as any)["Wallet"],
        badge: 'Paie',
        tcode: 'KRH_RCA',
        description: 'Cumuls annuels par employé : brut, net, CNPS salarial/patronal, IRGM',
        businessProcess: 'État récapitulatif paie',
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
      },
      {
        label: "Offres et candidatures",
        path: "/rh-personnel/recruitment",
        icon: (LUCIDE as any)["UserPlus"],
        tcode: "registre-recruitment",
        description: "Pipeline de recrutement par poste.",
        requiredRoles: ["rh.recruitment.read"],
      },
      {
        label: "Plan de formation",
        path: "/rh-personnel/training",
        icon: (LUCIDE as any)["GraduationCap"],
        tcode: "registre-training",
        description: "Actions de formation et habilitations.",
        requiredRoles: ["rh.training.read"],
      },
      {
        label: "Masse salariale previsionnelle",
        path: "/rh-personnel/workforce-planning",
        icon: (LUCIDE as any)["Calculator"],
        tcode: "registre-workforce-planning",
        description: "Projection mensuelle de masse salariale.",
        requiredRoles: ["rh.workforce_planning.read"],
      },
      {
        label: "Rapports RH periodiques",
        path: "/rh-personnel/hr-reports",
        icon: (LUCIDE as any)["FileBarChart"],
        tcode: "registre-hr-reports",
        description: "Effectif, absent., turnover.",
        requiredRoles: ["rh.hr_reports.read"],
      },
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
      },
      {
        label: "Suivi environnemental",
        path: "/qhse-securite/environmental-monitoring",
        icon: (LUCIDE as any)["Activity"],
        tcode: "registre-environmental-monitoring",
        description: "Bruit, air, eau.",
        requiredRoles: ["qhse.environmental.read"],
      },
          
      
      
      
      
      
      
      
      
      
      
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
      },
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
      },
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
        path: '/admin/subscriptions',
        icon: Tag,
        badge: 'Plans',
        tcode: 'KSAAS_SUB',
        description: 'Configuration des forfaits Enterprise, Pro, Starter et facturation SaaS',
        businessProcess: 'Monétisation SaaS',
        requiredRoles: ['SUPER_ADMIN']
      },
      {
        label: 'Infrastructure, Quotas & API Gateway',
        path: '/admin/audit/system-health',
        icon: Zap,
        badge: 'Infra',
        tcode: 'KSAAS_INF',
        description: 'Monitoring des ressources serveur, bases isolées et passerelle API',
        businessProcess: 'Supervision technique',
        requiredRoles: ['SUPER_ADMIN']
      },
      {
        label: 'Logs d Audit & Sécurité Plateforme',
        path: '/admin/audit',
        icon: ShieldAlert,
        badge: 'Audit',
        tcode: 'KSAAS_AUD',
        description: 'Traçabilité complète des accès inter-organisations',
        businessProcess: 'Sécurité globale',
        requiredRoles: ['SUPER_ADMIN']
      },
    ]
  },

 // ============================================================================
 // 👑 CONSOLE SUPER-ADMIN CADC (SaaS: entreprises, plans, prestataires,
 // accréditations). Visibility stricte: niveau 0 uniquement (role_level===0 /
 // is_superuser). Le backend exige require_superadmin sur chaque endpoint.
 // ============================================================================
  'superadmin-cadc': {
    key: 'superadmin-cadc',
    title: '👑 Console Super-Admin CADC',
    path: '/admin/super-admin/entreprises',
    icon: Crown,
    color: '#f59e0b',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-600',
    businessArea: 'Gouvernance Plateforme SaaS (CADC)',
    processPhase: 'Propriétaire Plateforme Multi-Entreprises',
    requiredRoles: ['SUPER_ADMIN', 'CADC'],
    subModules: [
      {
        label: 'Entreprises & Logos',
        path: '/admin/super-admin/entreprises',
        icon: Building,
        badge: 'Clients',
        tcode: 'KCADC_ENT',
        description: 'CRUD total des entreprises clientes, plans et allocation de modules',
        businessProcess: 'Gestion multi-tenants SaaS',
        requiredRoles: ['SUPER_ADMIN', 'CADC']
      },
      {
        label: 'Plans d\'Abonnement',
        path: '/admin/super-admin/plans-abonnement',
        icon: Tag,
        badge: 'Paliers',
        tcode: 'KCADC_PLN',
        description: 'Configuration des paliers SaaS et verrou max_modules',
        businessProcess: 'Monétisation SaaS',
        requiredRoles: ['SUPER_ADMIN', 'CADC']
      },
      {
        label: 'Annuaire Prestataires',
        path: '/admin/super-admin/prestataires',
        icon: Users,
        badge: 'B2B',
        tcode: 'KCADC_PRE',
        description: 'Gestion réservée CADC de l\'annuaire des prestataires',
        businessProcess: 'Référencement partenaires',
        requiredRoles: ['SUPER_ADMIN', 'CADC']
      },
      {
        label: 'Accréditations Entreprises',
        path: '/admin/super-admin/accreditations-entreprises',
        icon: ShieldAlert,
        badge: 'Délais',
        tcode: 'KCADC_ACR',
        description: 'Accords module datés débloquant un accès au-delà de l\'allocation',
        businessProcess: 'Conformité & délais',
        requiredRoles: ['SUPER_ADMIN', 'CADC']
      },
      {
        label: 'Demandes d\'Accréditation',
 // Phase 3: file d'arbitrage CADC des demandes émises par les admins
 // entreprise (module verrouillé -> demande). Approuver convertit la
 // demande en accréditation active datée; Refuser la marque refusée.
        path: '/admin/super-admin/demandes-accreditation',
        icon: Inbox,
        badge: 'Arbitrage',
        tcode: 'KCADC_REQ',
        description: 'File d\'attente des demandes de modules des entreprises à approuver ou refuser',
        businessProcess: 'Conformité & délais',
        requiredRoles: ['SUPER_ADMIN', 'CADC']
      },
      {
        label: "Analytique revenus SaaS / MRR",
        path: "/superadmin-cadc/revenue-analytics",
        icon: (LUCIDE as any)["DollarSign"],
        tcode: "registre-revenue-analytics",
        description: "MRR, churn, ARPU, expansion.",
        requiredRoles: ["superadmin.revenue_analytics.read"],
      },
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
        path: '/admin/agencies',
        icon: Building,
        badge: 'Agences',
        tcode: 'KADM_AGC',
        description: 'Gestion des agences Siège Douala, Port Kribi et limbé',
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
      },
      {
        label: 'Rôles & Permissions Granulaires',
        path: '/admin/configuration-des-roles-rbac',
        icon: ShieldAlert,
        badge: 'RBAC',
        tcode: 'KADM_RLS',
        description: 'Arbre des permissions par module, sous-module et action, et visibilité hiérarchique par rôle',
        businessProcess: 'Gouvernance des accès',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Accréditations & Habilitations',
        path: '/admin/accreditations',
        icon: UserCheck,
        badge: 'Habilitations',
        tcode: 'KADM_ACC',
        description: 'Octroi de droits granulaires et de périmètres de visibilité nominatifs, datés et révocables',
        businessProcess: 'Gouvernance des accès',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Espaces Communs par Entreprise',
        path: '/admin/espaces-communs',
        icon: Globe,
        badge: 'Communs',
        tcode: 'KADM_COM',
        description: 'Modules ouverts à tous les collaborateurs authentifiés (portail RH self-service, messagerie interne)',
        businessProcess: 'Gouvernance des accès',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Modules alloués & demandes SaaS',
        path: '/admin-entreprise/modules',
        icon: Layers,
        badge: 'Paliers',
        tcode: 'KADM_MOD',
        description: 'Modules alloués par le CADC, modules verrouillés et demandes d\'accréditation',
        businessProcess: 'Abonnement SaaS',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
      {
        label: 'Profil Entreprise (SaaS)',
 // Phase 2: la page /admin-entreprise/profil expose l'IDENTITE SAAS du
 // tenant (plan CADC, verrous max_modules/max_users, modules alloues,
 // admins designes niveau 1) via /api/v1/company-admin/profil.
 // /company (fiche legale OHADA: NIF, RCCM, agrements, RIB) reste la
 // page gemme pour les declarages fiscaux les deux ecrans restent
 // volontairement distincts (contrats backend differents).
        path: '/admin-entreprise/profil',
        icon: Building,
        badge: 'Société',
        tcode: 'KADM_PFE',
        description: 'Informations de la société, plan d\'abonnement, quotas et admins désignés par le CADC',
        businessProcess: 'Identité du tenant',
        requiredRoles: ['ADMIN', 'SUPER_ADMIN']
      },
    ]
  },

 // ============================================================================
 // 🧑‍💼 MODULE 12-C: ESPACE DÉPARTEMENT (CHEF DE DÉPARTEMENT NIVEAU 2)
 // ============================================================================
 // Plan Phase 3: espace dédié au chef de département. Visible par les rôles
 // d'encadrement (MANAGER) et l'administration; le garde route-level
 // /departement/layout.tsx (roleLevel <= 2) et le backend
 // require_department_head + _scoped_department font la vraie enforcement
 // (un niveau 3 est 403; un chef ne télécharge que SON département).
  'departement': {
    key: 'departement',
    title: '🧑\u200d💼 Mon Département',
    path: '/departement',
    icon: Building,
    color: '#0ea5e9',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-cyan-600',
    businessArea: 'Encadrement Opérationnel',
    processPhase: 'Pilotage d un Département',
    requiredRoles: ['MANAGER', 'ADMIN', 'SUPER_ADMIN', 'COMPANY_ADMIN'],
    subModules: [
      {
        label: 'Collaborateurs du département',
        path: '/departement',
        icon: Users,
        badge: 'Équipe',
        tcode: 'KDEP_EQP',
        description: 'Fiche du département (modules autorisés, effectif) et roster des collaborateurs rattachés',
        businessProcess: 'Périmètre départemental'
      },
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
      },
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
      },
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
      },
      {
        label: "Accuses de consignes",
        path: "/portail-collaborateur/work-instruction-receipts",
        icon: (LUCIDE as any)["FileCheck2"],
        tcode: "registre-work-instruction-receipts",
        description: "Accuse de reception d' une consigne de travail.",
        requiredRoles: ["rh.work_instruction_receipt.read"],
      },
      {
        label: "Depot de certifications",
        path: "/portail-collaborateur/certification-uploads",
        icon: (LUCIDE as any)["FileBadge"],
        tcode: "registre-certification-uploads",
        description: "Depot par le collaborateur d' une piece de certification.",
        requiredRoles: ["rh.certification_upload.read"],
      },
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
      },
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
      },
      {
        label: "Suivi budget de frais",
        path: "/portail-frais/expense-budget-tracking",
        icon: (LUCIDE as any)["TrendingUp"],
        tcode: "registre-expense-budget-tracking",
        description: "Comparaison budget alloue / frais engages par centre de cout.",
        requiredRoles: ["tresorerie.expense_budget_tracking.read"],
      },
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
      },
      {
        label: "Rondes de securite",
        path: "/portail-magasinier/safety-inspections",
        icon: (LUCIDE as any)["ShieldCheck"],
        tcode: "registre-safety-inspections",
        description: "Inspection periodique des zones du depot.",
        requiredRoles: ["magasin.safety_inspection.read"],
      },
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
      },
      {
        label: "RDV d' atelier",
        path: "/portail-technicien/service-appointments",
        icon: (LUCIDE as any)["CalendarDays"],
        tcode: "registre-service-appointments",
        description: "Creneau planifie pour une intervention en atelier.",
        requiredRoles: ["parc.service_appointment.read"],
      },
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
      },
      {
        label: "Certificats d' origine",
        path: "/portail-declarant/origin-certificates",
        icon: (LUCIDE as any)["Award"],
        tcode: "registre-origin-certificates",
        description: "Justificatif d' origine preferentielle ou non d' une marchandise.",
        requiredRoles: ["transit.origin_certificate.read"],
      },
      {
        label: "Entrees en entrepot sous douane",
        path: "/portail-declarant/bonded-warehouse-entries",
        icon: (LUCIDE as any)["Archive"],
        tcode: "registre-bonded-warehouse-entries",
        description: "Depot de marchandise sous controle douanier sans paiement immediat.",
        requiredRoles: ["transit.bonded_warehouse_entry.read"],
      },
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
      },
      {
        label: "Evaluations ergonomiques",
        path: "/portail-qhse/ergonomics-assessments",
        icon: (LUCIDE as any)["PersonStanding"],
        tcode: "registre-ergonomics-assessments",
        description: "Evaluation ergonomique d' un poste de travail.",
        requiredRoles: ["qhse.ergonomics_assessment.read"],
      },
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
        label: 'Chiffrage sur Grille Tarifaire',
        path: '/portail-commercial?tab=chiffrage',
        icon: Calculator,
        badge: 'Ventes',
        tcode: 'KSAL_CRM',
        description: 'Chiffrage bâti sur les tarifs saisis, puis émission du devis client',
        businessProcess: 'Prospection commerciale'
      },
      {
        label: 'Grille Tarifaire d Exploitation',
        path: '/portail-commercial?tab=tarifs',
        icon: Tag,
        badge: 'Tarifs',
        tcode: 'KSAL_TRF',
        description: 'Saisie et consultation des lignes tarifaires de la société',
        businessProcess: 'Paramétrage prix de vente'
      },
      {
        label: 'Devis Émis & Décisions',
        path: '/portail-commercial?tab=devis',
        icon: FileText,
        badge: 'Circuit',
        tcode: 'KSAL_QUO',
        description: 'Registre des devis et validation acceptation ou rejet',
        businessProcess: 'Négociation et closing'
      },
      {
        label: 'Portefeuille Clients & Encours',
        path: '/portail-commercial?tab=clients',
        icon: Users,
        badge: 'Comptes',
        tcode: 'KSAL_CLI',
        description: 'Comptes clients du registre des tiers et encours facturé encaissé',
        businessProcess: 'Suivi de portefeuille'
      },
      {
        label: "Etats de commission",
        path: "/portail-commercial/commission-statements",
        icon: (LUCIDE as any)["Percent"],
        tcode: "registre-commission-statements",
        description: "Calcul de la commission due au commercial sur ses ventes.",
        requiredRoles: ["b2b.commission_statement.read"],
      },
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
      },
      {
        label: "Attestations d' assurance",
        path: "/annuaire-prestataires/insurance-attestations",
        icon: (LUCIDE as any)["ShieldCheck"],
        tcode: "registre-insurance-attestations",
        description: "Attestation d' assurance RC / caution d' un prestataire.",
        requiredRoles: ["transport.insurance_attestation.read"],
      },
    ]
  },

 // ============================================================================
 // 🛡️ CHEF DU PERSONNEL: SUPERVISION N+1 RÔLES PASSIFS
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
        description: 'Présence en temps réel des agents par site (Douala, Kribi, limbé)',
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
      },
      {
        label: "Demandes d' ajustement de paie",
        path: "/chef-personnel/payroll-adjustment-requests",
        icon: (LUCIDE as any)["Banknote"],
        tcode: "registre-payroll-adjustment-requests",
        description: "Demande d' ajustement exceptionnel de la paie d' un collaborateur.",
        requiredRoles: ["rh.payroll_adjustment_request.read"],
      },
    ]
  },

 // Modules multimodaux : ferroviaire, aérien, fluvial et 3PL
  'transport-ferroviaire': {
    key: 'transport-ferroviaire',
    title: '🚆 K-Transport Ferroviaire',
    titleEn: 'Rail Freight & Infrastructure',
    path: '/transport-ferroviaire/dashboard',
    icon: (LUCIDE as any)["TrainFront"],
    color: '#6366F1',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-violet-600',
    businessArea: 'Transport Ferroviaire',
    processPhase: 'Mode Rail: Parc, Sillons, Fret & Corridors',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage ferroviaire",
        path: "/transport-ferroviaire/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-transport-ferroviaire-dash",
        description: "Parc wagons/locomotives, sillons, lettres de voiture CIM et corridors fer-port",
        businessProcess: "Pilotage du module",
        requiredRoles: ["ferroviaire.wagon_fleet.read"],
      },
      {
        label: "Sillons de circulation",
        path: "/transport-ferroviaire/train-paths",
        icon: (LUCIDE as any)["CalendarClock"],
        tcode: "registre-train-paths",
        description: "Graphique des sillons attribues par le gestionnaire d'infrastructure.",
        requiredRoles: ["ferroviaire.train_paths.read"],
      },
      {
        label: "Gares de triage",
        path: "/transport-ferroviaire/shunting-yards",
        icon: (LUCIDE as any)["Layers"],
        tcode: "registre-shunting-yards",
        description: "Installations de tri et de formation des rames.",
        requiredRoles: ["ferroviaire.shunting_yards.read"],
      },
      {
        label: "Plans de composition",
        path: "/transport-ferroviaire/consistency-plans",
        icon: (LUCIDE as any)["ListOrdered"],
        tcode: "registre-consistency-plans",
        description: "Description de la composition theorique d'un train (ordre, masse, longueur).",
        requiredRoles: ["ferroviaire.consistency.read"],
      },
      {
        label: "Lettres de voiture CIM/OTIF",
        path: "/transport-ferroviaire/waybills-rail",
        icon: (LUCIDE as any)["FileText"],
        tcode: "registre-waybills-rail",
        description: "Titres de transport fer internationaux (CIM) ou nationaux.",
        requiredRoles: ["ferroviaire.waybills.read"],
      },
      {
        label: "Composition de train",
        path: "/transport-ferroviaire/train-consists",
        icon: (LUCIDE as any)["TrainFront"],
        tcode: "registre-train-consists",
        description: "Liste ordonnee des wagons d une circulation.",
        requiredRoles: ["ferroviaire.train_consist.read"],
      },
    ]
  },

 // Modules multimodaux : ferroviaire, aérien, fluvial et 3PL
  'transport-aerien': {
    key: 'transport-aerien',
    title: '✈️ K-Transport Aérien',
    titleEn: 'Air Cargo & Airport Ops',
    path: '/transport-aerien/dashboard',
    icon: (LUCIDE as any)["Plane"],
    color: '#C026D3',
    glow: 'shadow-fuchsia-500/50 border-fuchsia-500/60',
    bgGradient: 'from-fuchsia-600 to-purple-600',
    businessArea: 'Transport Aérien',
    processPhase: 'Mode Air: Fret, AWB, Slots & Surete',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage aerien",
        path: "/transport-aerien/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-transport-aerien-dash",
        description: "Flotte, AWB maitres/secondaires, slots IATA, ULD et surete du fret",
        businessProcess: "Pilotage du module",
        requiredRoles: ["aerien.fleet.read"],
      },
      {
        label: "Creneaux aeroportuaires",
        path: "/transport-aerien/slots-coordination",
        icon: (LUCIDE as any)["Clock"],
        tcode: "registre-slots-coordination",
        description: "Coordination IATA (BABY) des creneaux decollage/atterrissage.",
        requiredRoles: ["aerien.slots.read"],
      },
      {
        label: "Parc ULD",
        path: "/transport-aerien/uld-management",
        icon: (LUCIDE as any)["Boxes"],
        tcode: "registre-uld-management",
        description: "Conteneurs et palettes aerienes (AKE, PAG, PMC).",
        requiredRoles: ["aerien.uld.read"],
      },
      {
        label: "Navigation planning",
        path: "/transport-aerien/crew-scheduling",
        icon: (LUCIDE as any)["Users"],
        tcode: "registre-crew-scheduling",
        description: "PNT (pilotes), PNC (Cabin), qualification ligne / aeronef.",
        requiredRoles: ["aerien.crew.read"],
      },
      {
        label: "Fret perishable (chaine du froid)",
        path: "/transport-aerien/perishable-cargo",
        icon: (LUCIDE as any)["Snowflake"],
        tcode: "registre-perishable-cargo",
        description: "Marchandises perissables sous temperature dirigee.",
        requiredRoles: ["aerien.perishable_cargo.read"],
      },
      {
        label: "Dedouanement fret aerien",
        path: "/transport-aerien/customs-clearance-air",
        icon: (LUCIDE as any)["Stamp"],
        tcode: "registre-customs-clearance-air",
        description: "Dossiers de dechargement et formalites douane aeroport.",
        requiredRoles: ["aerien.customs_clearance.read"],
      },
      {
        label: "Conformite nuisances sonores",
        path: "/transport-aerien/noise-compliance",
        icon: (LUCIDE as any)["VolumeX"],
        tcode: "registre-noise-compliance",
        description: "Mesures et conformite bruit des aéronefs / restrictions nocturnes.",
        requiredRoles: ["aerien.noise_compliance.read"],
      },
    ]
  },

 // Modules multimodaux : ferroviaire, aérien, fluvial et 3PL
  'transport-fluvial': {
    key: 'transport-fluvial',
    title: '⛴️ K-Transport Fluvial',
    titleEn: 'River & Lake Transport',
    path: '/transport-fluvial/dashboard',
    icon: (LUCIDE as any)["Anchor"],
    color: '#14B8A6',
    glow: 'shadow-teal-500/50 border-teal-500/60',
    bgGradient: 'from-teal-600 to-cyan-600',
    businessArea: 'Transport Fluvial & Lacustre',
    processPhase: 'Mode Eau interieure: Peniches, Ecluses & Terminaux',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage fluvial",
        path: "/transport-fluvial/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-transport-fluvial-dash",
        description: "Flotte fluviale, transits d'ecluses, sondes, terminaux et lettres de voiture CMNI",
        businessProcess: "Pilotage du module",
        requiredRoles: ["fluvial.barge_fleet.read"],
      },
      {
        label: "Remorqueurs fluviaux",
        path: "/transport-fluvial/tow-fleet",
        icon: (LUCIDE as any)["Anchor"],
        tcode: "registre-tow-fleet",
        description: "Remorqueurs d'estuaire et de voie interieure.",
        requiredRoles: ["fluvial.tow_fleet.read"],
      },
      {
        label: "Transits d'ecluses",
        path: "/transport-fluvial/lock-transits",
        icon: (LUCIDE as any)["DoorOpen"],
        tcode: "registre-lock-transits",
        description: "Passages d'ecluses avec horaires, poids, dimensions.",
        requiredRoles: ["fluvial.locks.read"],
      },
      {
        label: "Sondes bathymetriques",
        path: "/transport-fluvial/river-depth",
        icon: (LUCIDE as any)["Ruler"],
        tcode: "registre-river-depth",
        description: "Mesures periodiques de fond de voie / seuils / tirant d'eau pratique.",
        requiredRoles: ["fluvial.depth.read"],
      },
      {
        label: "Terminaux fluviaux",
        path: "/transport-fluvial/river-ports",
        icon: (LUCIDE as any)["Warehouse"],
        tcode: "registre-river-ports",
        description: "Quais, appontements et zones de transbordement fluvial.",
        requiredRoles: ["fluvial.terminals.read"],
      },
      {
        label: "Vrac fluvial",
        path: "/transport-fluvial/bulk-river",
        icon: (LUCIDE as any)["Droplet"],
        tcode: "registre-bulk-river",
        description: "Chargement/dechargement vrac solide ou liquide.",
        requiredRoles: ["fluvial.bulk.read"],
      },
      {
        label: "Securite navigation",
        path: "/transport-fluvial/navigation-safety",
        icon: (LUCIDE as any)["LifeBuoy"],
        tcode: "registre-navigation-safety",
        description: "Balises, accidents, secours, arret technique.",
        requiredRoles: ["fluvial.safety.read"],
      },
      {
        label: "Tarification fluviale",
        path: "/transport-fluvial/river-tariffs",
        icon: (LUCIDE as any)["Calculator"],
        tcode: "registre-river-tariffs",
        description: "Prix par tonne / km selon bief et type produit.",
        requiredRoles: ["fluvial.tariffs.read"],
      },
      {
        label: "Sections de voie navigable",
        path: "/transport-fluvial/canal-sections",
        icon: (LUCIDE as any)["Route"],
        tcode: "registre-canal-sections",
        description: "Troncons de voie d eau avec cotes, biefs et restrictions.",
        requiredRoles: ["fluvial.canal_section.read"],
      },
      {
        label: "Echelles d eau / limnimetres",
        path: "/transport-fluvial/water-gauges",
        icon: (LUCIDE as any)["Waves"],
        tcode: "registre-water-gauges",
        description: "Releves de niveau d eau par poste de mesure.",
        requiredRoles: ["fluvial.water_gauge.read"],
      },
      {
        label: "Manifestes de chargement fluviaux",
        path: "/transport-fluvial/cargo-manifests-river",
        icon: (LUCIDE as any)["ListChecks"],
        tcode: "registre-cargo-manifests-river",
        description: "Liste des marchandises chargees par convoi.",
        requiredRoles: ["fluvial.cargo_manifest.read"],
      },
      {
        label: "Droits de port fluvial",
        path: "/transport-fluvial/port-fees-river",
        icon: (LUCIDE as any)["Receipt"],
        tcode: "registre-port-fees-river",
        description: "Tarifs de stationnement et de manutention par terminal.",
        requiredRoles: ["fluvial.port_fee.read"],
      },
      {
        label: "Visites techniques batellerie",
        path: "/transport-fluvial/vessel-inspections",
        icon: (LUCIDE as any)["ClipboardCheck"],
        tcode: "registre-vessel-inspections",
        description: "Controles reglementaires des bateaux (communautaire/national).",
        requiredRoles: ["fluvial.vessel_inspection.read"],
      },
    ]
  },

 // Modules multimodaux : ferroviaire, aérien, fluvial et 3PL
  'logistique-3pl': {
    key: 'logistique-3pl',
    title: '📦 K-Logistique 3PL',
    titleEn: 'Contract Logistics 3PL',
    path: '/logistique-3pl/dashboard',
    icon: (LUCIDE as any)["Warehouse"],
    color: '#EA580C',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-600 to-amber-600',
    businessArea: 'Logistique sous contrat',
    processPhase: '3PL: Contrats, Entrepots, Pick&Pack & SLA',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Tour de controle 3PL",
        path: "/logistique-3pl/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-logistique-3pl-dash",
        description: "Contrats clients, entrepot sous contrat, pick&pack, cross-dock, KPI SLA et facturation 3PL",
        businessProcess: "Pilotage du module",
        requiredRoles: ["log3pl.contracts.read"],
      },
    ]
  },
// Modules complémentaires
 
  'pipeline-oleoduc': {
    key: 'pipeline-oleoduc',
    title: '🛢️ K-Pipeline Oléoduc-Gazoduc',
    titleEn: 'Pipeline & Hydrocarbons',
    path: '/pipeline-oleoduc/dashboard',
    icon: (LUCIDE as any)["Waypoints"],
    color: '#0EA5E9',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-cyan-600',
    businessArea: 'Pipeline Oléoduc-Gazoduc',
    processPhase: 'Mode Pipeline: Sections, Stations, Stockage & Metering',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage pipeline",
        path: "/pipeline-oleoduc/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-pipeline-oleoduc-dash",
        description: "Pilotage transversal du module pipeline-oleoduc",
        businessProcess: "Pilotage du module",
        requiredRoles: ["pipeline.sections.read"],
      },
      {
        label: "Actions de reponse a deversement",
        path: "/pipeline-oleoduc/spill-response-actions",
        icon: (LUCIDE as any)["Droplets"],
        tcode: "registre-spill-response-actions",
        description: "Action declenchee suite a un deversement detecte.",
        requiredRoles: ["pipeline.spill_response_action.read"],
      },
    ]
  },

 

 
  'chaine-froid': {
    key: 'chaine-froid',
    title: '❄️ K-Chaine du Froid',
    titleEn: 'Cold Chain & Reefer Logistics',
    path: '/chaine-froid/dashboard',
    icon: (LUCIDE as any)["Snowflake"],
    color: '#0EA5E9',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-cyan-600',
    businessArea: 'Chaine du Froid',
    processPhase: 'Mode Froid: Chambres, Reefers, HACCP & Vaccins',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage coldchain",
        path: "/chaine-froid/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-chaine-froid-dash",
        description: "Pilotage transversal du module chaine-froid",
        businessProcess: "Pilotage du module",
        requiredRoles: ["coldchain.chambers.read"],
      },
    ]
  },

 
  'convoi-exceptionnel': {
    key: 'convoi-exceptionnel',
    title: '🏗️ K-Convoi Exceptionnel (Heavy-lift)',
    titleEn: 'Heavy Lift & Project Cargo',
    path: '/convoi-exceptionnel/dashboard',
    icon: (LUCIDE as any)["HardHat"],
    color: '#0EA5E9',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-cyan-600',
    businessArea: 'Convoi Exceptionnel / Heavy-lift',
    processPhase: 'Mode Heavy-Lift: Projets, Levage, Itineraire & Escorte',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage heavylift",
        path: "/convoi-exceptionnel/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-convoi-exceptionnel-dash",
        description: "Pilotage transversal du module convoi-exceptionnel",
        businessProcess: "Pilotage du module",
        requiredRoles: ["heavylift.projects.read"],
      },
      {
        label: "Releves de charge par essieu",
        path: "/convoi-exceptionnel/axle-load-readings",
        icon: (LUCIDE as any)["Weight"],
        tcode: "registre-axle-load-readings",
        description: "Mesure de la charge reposee par essieu du porte-engin.",
        requiredRoles: ["heavylift.axle_load_reading.read"],
      },
      {
        label: "Comptes-rendus de rassemblement",
        path: "/convoi-exceptionnel/convoy-staging-reports",
        icon: (LUCIDE as any)["Truck"],
        tcode: "registre-convoy-staging-reports",
        description: "Bilan du rassemblement et du depart d' un convoi.",
        requiredRoles: ["heavylift.convoy_staging_report.read"],
      },
    ]
  },

// Modules complémentaires
 
  'maintenance-industrielle': {
    key: 'maintenance-industrielle',
    title: '🔧 K-Maintenance Industrielle',
    titleEn: 'Industrial Maintenance (CMMS)',
    path: '/maintenance-industrielle/dashboard',
    icon: (LUCIDE as any)["Cog"],
    color: '#8B5CF6',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-fuchsia-600',
    businessArea: 'Maintenance Industrielle',
    processPhase: 'Mode CMMS: Actifs, GMAO, FMEA, RCM & Predictif',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage maintindustrielle",
        path: "/maintenance-industrielle/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-maintenance-industrielle-dash",
        description: "Pilotage transversal du module maintenance-industrielle",
        businessProcess: "Pilotage du module",
        requiredRoles: ["maintindustrielle.assets.read"],
      },
      {
        label: "Planification préventive GMAO",
        path: "/maintenance-gmao/planification",
        icon: (LUCIDE as any)["Wrench"],
        badge: "Préventif",
        tcode: "maint-planif",
        description: "OT préventifs par compteurs réels (heures/km), échéances et lubrifications",
        businessProcess: "Maintenance préventive ISO 55000",
        requiredRoles: ["maintindustrielle.work_orders.read"],
      },
    ]
  },

  'juridique': {
    key: 'juridique',
    title: 'Juridique & Contrats',
    path: '/juridique',
    icon: (LUCIDE as any)["Scale"],
    color: '#f59e0b',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-500',
    businessArea: 'Juridique & Conformité',
    processPhase: 'Support: Valeur documentaire',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: 'Contrats, Contentieux & Échéances',
        path: '/juridique',
        icon: (LUCIDE as any)["Scale"],
        badge: 'Juridique',
        tcode: 'KJUR_CON',
        description: 'Registre des contrats à valeur documentaire, contentieux et fenêtres de préavis',
        businessProcess: 'Gestion contractuelle',
        requiredRoles: ['juridique.contrats.read', 'juridique.contentieux.read', 'juridique.echeances.read']
      },
    ]
  },

 
  'tracabilite': {
    key: 'tracabilite',
    title: '🔗 K-Traçabilité Bout-en-Bout',
    titleEn: 'End-to-End Traceability',
    path: '/tracabilite/dashboard',
    icon: (LUCIDE as any)["Activity"],
    color: '#8B5CF6',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-fuchsia-600',
    businessArea: 'Tracabilite & Confiance Numerique',
    processPhase: 'Mode Tracabilite: Chaines custody, Merkle, eIDAS & RGPD',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'],
    subModules: [
      {
        label: "Centre de pilotage tracabilite",
        path: "/tracabilite/dashboard",
        icon: (LUCIDE as any)["LayoutDashboard"],
        badge: "Synthese",
        tcode: "registre-tracabilite-dash",
        description: "Pilotage transversal du module tracabilite",
        businessProcess: "Pilotage du module",
        requiredRoles: ["tracabilite.events.read"],
      },
      {
        label: "Journal audit inalterable",
        path: "/tracabilite/audit-logs",
        icon: (LUCIDE as any)["ScrollText"],
        tcode: "registre-audit-logs",
        description: "Log append-only a chaine de hash.",
        requiredRoles: ["tracabilite.audit_logs.read"],
      },
      {
        label: "Horodatage qualifie",
        path: "/tracabilite/timestamps",
        icon: (LUCIDE as any)["Clock"],
        tcode: "registre-timestamps",
        description: "Preuve d'antecidence (eIDAS / CAMPOST).",
        requiredRoles: ["tracabilite.timestamps.read"],
      },
      {
        label: "Sceau conteneur ISO 17712",
        path: "/tracabilite/seals",
        icon: (LUCIDE as any)["BadgeCheck"],
        tcode: "registre-seals",
        description: "Sceau haute securite conforme ISO 17712.",
        requiredRoles: ["tracabilite.seals.read"],
      },
    ]
  },


};

/**
 * Normalisation couleur : chaque module majeur hérite d'UNE couleur unique
 * depuis la palette canonique (modulePalette). Garantit la cohérence entre
 * registry, sidebar, dropdown, palette de commandes et bulle orbitale, et
 * supprime toute collision de teinte entre modules.
 */
for (const mod of Object.values(NAVIGATION_REGISTRY)) {
  const pal = getModulePalette(mod.key);
  mod.color = pal.hex;
  mod.glow = pal.glow;
  mod.titleEn = MODULE_TITLES_EN[mod.key];
  mod.bgGradient = pal.bgGradient;
}

/**
 * Fonction d'orchestration RBAC Senior
 * Filtre dynamiquement les modules et sous-modules selon les rôles et permissions de l'utilisateur.
 */
export function getFilteredNavigationForUser(
  user: {
    roles?: string[];
    modulesAllowed?: string[];
    permissions?: string[];
    sharedModules?: string[];
  } | null
): ModuleNavConfig[] {
  if (!user) return Object.values(NAVIGATION_REGISTRY);

  const userRoles = (user.roles || []).map(r => r.toUpperCase());
  const isSuperAdmin = userRoles.includes('SUPER_ADMIN');
  const isCompanyAdmin = userRoles.includes('ADMIN') || userRoles.includes('COMPANY_ADMIN');
  const isSupportStaff = userRoles.some(r => ['SECRETAIRE', 'GARDIEN', 'AGENT_ENTRETIEN', 'SUPPORT_IT'].includes(r));
  const userModules = (user.modulesAllowed || []).map(m => m.toLowerCase());
  const userPermissions = user.permissions || [];
  const sharedModules = (user.sharedModules || []).map(m => String(m).toLowerCase());

 // Correspondance clé de navigation -> module du catalogue de permissions.
 // Un module est accordé par le RBAC granulaire si l'utilisateur porte au moins
 // une permission effective sous ce module. Additif: cela NE RETIRE jamais un
 // accès déjà accordé par les rôles (requiredRoles restent la valeur par défaut).
  const NAV_TO_PERM_MODULE: Record<string, string[]> = {
    'comptabilite-avance': ['comptabilite', 'tresorerie', 'facturation', 'fiscalite', 'immobilisations'],
    'finance': ['comptabilite', 'tresorerie', 'facturation', 'fiscalite'],
    'transport': ['transport', 'parc', 'gps'],
    'magasin': ['magasin'],
    'transit': ['transit', 'acconage'],
    'rh': ['rh', 'paie', 'conges'],
    'achats': ['achats', 'fournisseurs', 'cotations'],
 // Département autonome: son module de catalogue s'appelle « amenagement »
 // (codes amenagement.<registre>.<action>) alors que la clé de navigation est
 // « amenagement-portuaire ». Sans cette ligne, un ingénieur d'aménagement
 // porteur de droits granulaires ne verrait jamais son département.
    'amenagement-portuaire': ['amenagement'],
  };
  const hasGranularAccessTo = (moduleKey: string): boolean => {
    if (userPermissions.length === 0) return false;
 // Module commun partagé par l'entreprise -> visible pour tout collaborateur.
    if (sharedModules.includes(moduleKey.toLowerCase())) return true;
    const permModules = NAV_TO_PERM_MODULE[moduleKey] || [moduleKey];
    return userPermissions.some(code =>
      permModules.some(pm => String(code).toLowerCase().startsWith(pm + '.'))
    );
  };

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
 // Accès ciblé: Espaces Collaborateurs, Chat & Forum d'entreprise, Dashboard
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

    const isModuleAllowed =
      isUniversalPortal || hasRoleAccess || hasModuleAccess || hasGranularAccessTo(moduleConfig.key);

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

// ============================================================================
// ENRICHISSEMENT « MODULES AVANCÉS » (Option A: rattachement en sous-modules)
// ----------------------------------------------------------------------------
// Ces écrans existent déjà comme vraies pages sous app/(app) (composants
// substantiels de 8 à 26 Ko) mais n'étaient référencés NULLE PART dans la
// navigation → donc invisibles dans la sidebar, la palette de commandes et la
// bulle orbitale. On les rattache à leur famille canonique selon la table
// LEGACY_ALIAS de modulePalette.ts (ex acconage→port-operations,
// master-data→admin-tenant, maintenance→parc-vehicules, fuel-guard→transport…).
//
// Correctif purement ADDITIF et IDEMPOTENT:
// - chaque `path` est une page RéELLE existante (aucun lien mort introduit);
// - si la famille cible brille par son absence, l'entrée est silencieusement
// ignorée (pas d'exception);
// - si le chemin est déjà référencé ailleurs dans la famille, on ne le duplique pas.
// La restriction d'accès réelle reste appliquée côté API; le champ
// `requiredRoles` aligne la visibilité sur celle des sous-modules frères.
// ============================================================================
type AdvancedSubModuleEntry = {
  family: string;
  label: string;
  path: string;
  icon: any;
  badge?: string;
  description?: string;
  requiredRoles?: string[];
};

const ADVANCED_SUBMODULES: AdvancedSubModuleEntry[] = [
 // 🚢 Opérations Portuaires & Acconage
  { family: 'port-operations', label: 'Acconage & Manutention', path: '/acconage', icon: Ship, badge: 'Avancé', description: 'Opérations d acconage, escales et navires (CRUD complet)', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS', 'ACCONAGE'] },
  { family: 'port-operations', label: 'Acconage Avancé', path: '/acconage-avance', icon: Anchor, badge: 'Avancé', description: 'Fonctions portuaires avancées (cadres, postes, rendements)', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS', 'ACCONAGE'] },
  { family: 'port-operations', label: 'Cycle de Vie Conteneurs', path: '/container-lifecycle', icon: Boxes, badge: 'Avancé', description: 'Suivi bout-en-bout du conteneur du port a la restitution', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS', 'MAGASIN'] },
  { family: 'port-operations', label: 'Connaissement (B/L)', path: '/bill-of-loading', icon: FileText, badge: 'Doc', description: 'Emission et gestion des bills of lading', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS', 'TRANSIT'] },
  { family: 'port-operations', label: 'Incidents Portuaires', path: '/port-incidents', icon: AlertTriangle, badge: 'QSE', description: 'Déclaration et suivi des incidents de quai', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS', 'QHSE'] },
  { family: 'port-operations', label: 'Performance Portuaire', path: '/port-performance', icon: BarChart3, badge: 'KPI', description: 'Indicateurs de cadence et de productivite portuaire', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'] },
  { family: 'port-operations', label: 'Grille Tarifaire Port', path: '/port-pricing', icon: Tag, badge: 'Tarifs', description: 'Barème des prestations portuaires et cotations', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PORT_OPERATIONS'] },

 // 🛃 Transit & Douane CEMAC
  { family: 'transit-douane', label: 'Transit Avancé', path: '/transit-avance', icon: Landmark, badge: 'Avancé', description: 'Moteur de transit avance : nomenclature CEMAC, taxes, T-Code', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSIT', 'DOUANE'] },
  { family: 'transit-douane', label: 'Dédouanement Réel', path: '/real-customs', icon: FileCheck, badge: 'SIGAS', description: 'Declarations douanieres reelles et rapprochement systeme', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSIT', 'DOUANE'] },
  { family: 'transit-douane', label: 'Intégration CEMAC/Cameroun', path: '/integration-cameroun', icon: Wifi, badge: 'EDI', description: 'Echange de donnees avec les systemes douaniers camerounais', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSIT', 'INTEGRATION'] },
  { family: 'transit-douane', label: 'Magasin sous Douane', path: '/magasin-douane', icon: Warehouse, badge: 'Avancé', description: 'Gestion des marchandises en magasin sous douane', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSIT', 'MAGASIN'] },

 // 🚚 Transport & Flotte
  { family: 'transport-flotte', label: 'Transport Avancé', path: '/transport-avance', icon: Truck, badge: 'Avancé', description: 'Transport avance : tournées, missions, tarification', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT'] },
  { family: 'transport-flotte', label: 'Tracking Temps Réel', path: '/tracking', icon: Radio, badge: 'Live', description: 'Suivi temps réel des véhicules et cargaisons', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT'] },
  { family: 'transport-flotte', label: 'ePOD & Preuves Livraison', path: '/tracking/epod', icon: Navigation, badge: 'ePOD', description: 'Preuves de livraison électroniques et signature', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT', 'CHAUFFEUR'] },
  { family: 'transport-flotte', label: 'Géolocalisation GPS', path: '/gps-tracking', icon: MapPin, badge: 'GPS', description: 'Telemetrie GPS et historical des parcours', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT'] },
  { family: 'transport-flotte', label: 'FuelGuard Carburant', path: '/fuel-guard', icon: Fuel, badge: 'Anti-fraude', description: 'Contrôle carburant et détection de fraude', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT'] },
  { family: 'transport-flotte', label: 'Espace Chauffeur Mobile', path: '/mobile-chauffeur/mission-active', icon: UserCheck, badge: 'Mobile', description: 'Mission active du chauffeur (version mobile)', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT', 'CHAUFFEUR'] },
  { family: 'transport-flotte', label: 'Transport International', path: '/transport-international', icon: Globe, badge: 'Export', description: 'Transit international, corridors et transit pays', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT'] },
  { family: 'transport-flotte', label: 'Planification Conducteurs', path: '/shift-planning', icon: Calendar, badge: 'Planning', description: 'Planning des services et roulement des conducteurs', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSPORT', 'MANAGER'] },

 // 📦 Magasin & Stock (WMS)
  { family: 'magasin-stock', label: 'Magasin Avancé (WMS)', path: '/magasin-avance', icon: Boxes, badge: 'Avancé', description: 'WMS avance : emplacements, onduleurs, inventaires tournants', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAGASIN'] },
  { family: 'magasin-stock', label: 'Réception Magasin 3', path: '/reception-mag3', icon: Package, badge: 'Avancé', description: 'Processus de reception qualite en magasin', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAGASIN'] },
  { family: 'magasin-stock', label: 'Bon de Sortie', path: '/removal-slip', icon: FileText, badge: 'Sortie', description: 'Emission et contrôle des bons de sortie de stock', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAGASIN'] },
  { family: 'magasin-stock', label: 'Marchandises', path: '/goods', icon: Package, badge: 'Articles', description: 'Catalogue avancé des marchandises et articles', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAGASIN'] },

 // 💰 Finance OHADA
  { family: 'finance-ohada', label: 'Cotations & Devis', path: '/cotations', icon: Calculator, badge: 'Avancé', description: 'Cotations, calculs de prix et generation de devis', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Achats / Procurement', path: '/procurement', icon: ShoppingCart, badge: 'Avancé', description: 'Processus achats, appels d offres et fournisseurs', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Passation Commandes', path: '/purchase', icon: ShoppingCart, badge: 'BC', description: 'Commandes d achat et suivis fournisseurs', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Facturation Automatique', path: '/auto-invoicing', icon: Receipt, badge: 'Auto', description: 'Facturation recurrente et emission automatique', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Paiement Local Mobile', path: '/paiement-local', icon: CreditCard, badge: 'Mobile Money', description: 'Encaissements mobile money et paiement locaux', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Transactions', path: '/transactions', icon: ArrowUpDown, badge: 'Journal', description: 'Journal detaille des transactions financieres', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Fiscalité Cameroun', path: '/fiscalite-cameroun', icon: Calculator, badge: 'CEMAC', description: 'Obligations fiscales camerounaises (impots, taxes, declarations)', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },

 // 🔧 Parc & Maintenance (GMAO)
  { family: 'parc-vehicules', label: 'Maintenance Véhicules', path: '/maintenance', icon: Wrench, badge: 'Avancé', description: 'Ordres de maintenance, interventions et historique', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAINTENANCE'] },
  { family: 'parc-vehicules', label: 'Tableau de bord GMAO', path: '/maintenance-gmao/dashboard', icon: Activity, badge: 'GMAO', description: 'Supervision GMAO : pannes, couts, disponibilite', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MAINTENANCE'] },

 // 🛡️ QHSE & Conformité
  { family: 'qhse-securite', label: 'Conformité & Audits', path: '/compliance', icon: Shield, badge: 'Avancé', description: 'Registre de conformite, audits et ecarts', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'QHSE'] },
  { family: 'qhse-securite', label: 'Alertes', path: '/alerts', icon: Zap, badge: 'Live', description: 'Centre des alertes operationnelles et securite', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'QHSE'] },
  { family: 'qhse-securite', label: 'Notifications', path: '/notifications', icon: Bell, badge: 'Fil', description: 'Fil de notifications internes de la plateforme', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },

 // 🧑‍💼 Portail Client B2B
  { family: 'client-b2b', label: 'Portail Client Self-service', path: '/client-portal', icon: Users, badge: 'Avancé', description: 'Portail client complet : commandes, factures, litiges, suivi', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CLIENT'] },
  { family: 'client-b2b', label: 'Suivi Dossiers (B2B)', path: '/portail-b2b/suivi-dossiers', icon: FileCheck, badge: 'B2B', description: 'Suivi des dossiers du portail B2B', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'CLIENT'] },

 // 📊 Rapports & BI
  { family: 'reports-bi', label: 'Rapports Métier', path: '/reports', icon: BarChart3, badge: 'Avancé', description: 'Bibliotheque de rapports metier et modeles enregistres', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'] },
  { family: 'reports-bi', label: 'Reporting Opérationnel', path: '/reporting', icon: LineChart, badge: 'KPI', description: 'Rapports operationnels de suivi d activite', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'MANAGER'] },

 // ⚙️ Administration & Données de référence
  { family: 'admin-tenant', label: 'Données de Référence (Master Data)', path: '/master-data', icon: Layers, badge: 'Avancé', description: 'Articles, categories, tiers et referentiels maitre', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'admin-tenant', label: 'Fiche Entreprise (OHADA)', path: '/company', icon: Building, badge: 'Legal', description: 'Identite legale OHADA : NIF, RCCM, agrements, RIB', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'admin-tenant', label: 'GED & Documents', path: '/documents', icon: FileText, badge: 'GED', description: 'Gestion electronique des documents et archive', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'admin-tenant', label: 'Intégrations API', path: '/integration', icon: Wifi, badge: 'API', description: 'Connecteurs et intégrations tiers (API partenaires)', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'admin-tenant', label: 'Support & Tickets', path: '/support', icon: MessageSquare, badge: 'Helpdesk', description: 'Guichet d assistance et tickets internes', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
];

// Applique l'enrichissement de façon idempotente (aucune duplication, aucune
// exception si une famille manque). Exécuté une seule fois au chargement du module.
const applyAdvanced = (entries: AdvancedSubModuleEntry[]) => {
  for (const entry of entries) {
    const family = NAVIGATION_REGISTRY[entry.family];
    if (!family) continue;
    if (family.subModules.some((s) => s.path === entry.path)) continue;
    family.subModules.push({
      label: entry.label,
      path: entry.path,
      icon: entry.icon,
      badge: entry.badge,
      description: entry.description,
      businessProcess: 'Modules avancés',
      requiredRoles: entry.requiredRoles,
    });
  }

};
applyAdvanced(ADVANCED_SUBMODULES);

// ----------------------------------------------------------------------------
// Écrans métier complémentaires restés hors menu (aucun doublon avec les pages
// canoniques déjà câblées). Pages substantielles des arbres /finance, /parc, /rh
// exposant des fonctionnalités que les modules canoniques ne couvrent pas
// (facturation détaillée, encaissements, réquisitions, saisie bancaire,
// contrôle d'accès parc, plan du yard), plus quelques consoles transverses
// (notifications, API publique/partenaire, fournisseurs, passerelle de paiement).
// ----------------------------------------------------------------------------
const ADVANCED_SUBMODULES_2: AdvancedSubModuleEntry[] = [
 // 💰 Finance OHADA detail: facturation/encaissements non couverts par /finance-ohada/*
  { family: 'finance-ohada', label: 'Facturation & Billing', path: '/finance/billing', icon: Receipt, badge: 'Avancé', description: 'Cycle de facturation détaillé et generation des documents', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Encaissements Clients', path: '/finance/encaissements', icon: ArrowUpDown, badge: 'Avancé', description: 'Suivi des reglements et encaissements clients', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Réquisitions d’Achat', path: '/finance/requisitions', icon: ShoppingCart, badge: 'Avancé', description: 'Demandes internes d’achat et circuit de validation', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Saisie Transaction Bancaire', path: '/finance/saisie-transaction-bancaire', icon: Banknote, badge: 'Banque', description: 'Saisie et rapprochement des transactions bancaires', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'finance-ohada', label: 'Passerelle de Paiement', path: '/gateway', icon: CreditCard, badge: 'Paiement', description: 'Console de la passerelle de paiement et des moyens', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },

 // 🚧 Parc & Yard gate/plan absent de /parc-vehicules/*
  { family: 'parc-vehicules', label: 'Contrôle d’Accès (Gate)', path: '/parc/gate', icon: Shield, badge: 'Gate', description: 'Entree/sortie du parc, controle et affectation des emplacements', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PARC', 'MAGASIN'] },
  { family: 'parc-vehicules', label: 'Plan du Parc (Yard Map)', path: '/parc/yard-map', icon: MapPin, badge: 'Yard', description: 'Carte interactive du parc et occupation des zones', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PARC'] },
  { family: 'parc-vehicules', label: 'Zones & Emplacements', path: '/parc/zones', icon: Grid, badge: 'Zonage', description: 'Definition des zones et emplacements du parc', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'PARC'] },

 // ⚙️ Consoles transverses
  { family: 'admin-tenant', label: 'Centre de Notifications', path: '/notification-system', icon: Bell, badge: 'System', description: 'Parametres et historique du systeme de notifications', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'admin-tenant', label: 'Fournisseurs (CRUD)', path: '/fournisseurs', icon: Users, badge: 'Tiers', description: 'Registre complet des fournisseurs et partenaires', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'admin-saas', label: 'API Partenaire', path: '/partner-api', icon: Wifi, badge: 'API', description: 'Administration des acces et cles API partenaires', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'admin-saas', label: 'API Publique', path: '/public-api', icon: Globe, badge: 'API', description: 'Portail de documentation de l’API publique', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
];
applyAdvanced(ADVANCED_SUBMODULES_2);

// ----------------------------------------------------------------------------
// Derniers écrans métier non couverts par les menus canoniques.
// (Les routes /logout, /settings, /chauffeur, /audit, /role, /tenant, /tiers,
// /suppliers restent volontairement hors liste: actions systeme ou doublons
// des modules canoniques deja cablés.)
// ----------------------------------------------------------------------------
const ADVANCED_SUBMODULES_3: AdvancedSubModuleEntry[] = [
  { family: 'finance-ohada', label: 'Acquisitions & Immobilisations', path: '/acquisition', icon: TrendingUp, badge: 'Immo', description: 'Suivi des acquisitions et entrees d’immobilisations', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'FINANCE'] },
  { family: 'qhse-securite', label: 'Registre QHSE', path: '/qhse', icon: Shield, badge: 'Avancé', description: 'Registre general QHSE (liste, creation, consultation)', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'QHSE'] },
  { family: 'admin-saas', label: 'Administration Agence', path: '/admin-agency', icon: Building, badge: 'Agence', description: 'Pilotage des agences et points de service du tenant', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
  { family: 'transit-douane', label: 'Dossiers Transit (listes)', path: '/transit', icon: Landmark, badge: 'Avancé', description: 'Registre et suivi des dossiers de transit (CRUD complet)', requiredRoles: ['ADMIN', 'SUPER_ADMIN', 'TRANSIT', 'DOUANE'] },
  { family: 'admin-tenant', label: 'Tiers (clients & fournisseurs)', path: '/tiers', icon: Users, badge: 'Tiers', description: 'Annuaire unifie des tiers : clients, fournisseurs, partenaires', requiredRoles: ['ADMIN', 'SUPER_ADMIN'] },
];
applyAdvanced(ADVANCED_SUBMODULES_3);

// ============================================================================
// RÉSOLVEUR D'IDENTITÉ DE MODULE (source de vérité unique)
// ----------------------------------------------------------------------------
// L'identité du module affiché (thème, en-tête, fil d'Ariane, surbrillance
// sidebar, bulle orbitale) NE DOIT PLUS dépendre du 1er segment de l'URL: de
// nombreuses familles canoniques câblent leurs sous-modules sous des préfixes
// legacy (ex. finance-ohada → /finance/billing, admin-tenant → /admin/agencies,
// superadmin-cadc → /admin/super-admin/*). Une résolution par segment faisait
// basculer l'écran vers un AUTRE module (« un autre module s'ouvre et tourne »).
//
// On résout désormais par PROPRIÉTÉ dans le registre: le chemin enregistré
// (path de famille OU path de sous-module) dont l'URL correspond avec le
// PLUS LONG préfixe gagne → la page présente toujours le module qui la liste.
// L'index est construit paresseusement au premier appel, donc APRES exécution
// de tous les enrichissements (appliqués au chargement du module).
// ============================================================================
let _moduleOwnershipIndex: [string, string][] | null = null;

function _normalizeNavPath(p: string): string {
  return (p || '').split('?')[0].split('#')[0].replace(/\/+$/, '') || '/';
}

function _buildModuleOwnershipIndex(): [string, string][] {
  const pairs: [string, string][] = [];
  for (const [key, fam] of Object.entries(NAVIGATION_REGISTRY)) {
    const collect = (raw?: string) => {
      if (!raw) return;
      const clean = _normalizeNavPath(raw);
      if (clean && clean !== '/') pairs.push([clean, key]);
    };
    collect(fam.path);
    (fam.subModules || []).forEach((s) => collect(s.path));
  }
 // Déduplique (1er gagnant) puis trie par longueur décroissante: le préfixe
 // le plus spécifique domine (ex. /admin/super-admin/... bat /admin/agencies).
  const uniq = Array.from(new Map(pairs.map((x) => [x[0], x[1]])));
  uniq.sort((a, b) => b[0].length - a[0].length);
  return uniq;
}

/**
 * Retourne la clé de famille canonique à laquelle appartient une URL, ou
 * 'dashboard' en dernier recours. À utiliser partout où l'on dérivait
 * l'identité d'un module depuis `pathname.split('/')[1]`.
 */
export function resolveModuleKeyForPath(pathname: string): string {
  if (!_moduleOwnershipIndex) _moduleOwnershipIndex = _buildModuleOwnershipIndex();
  const clean = _normalizeNavPath(pathname || '');
  if (!clean || clean === '/') return 'dashboard';
 // (a) correspondance exacte, (b) plus long préfixe à frontière de segment.
  for (const [p, key] of _moduleOwnershipIndex) {
    if (clean === p || clean.startsWith(p + '/')) return key;
  }
 // (c) fallback: 1er segment → clé de registre, puis alias legacy.
  const seg = clean.split('/')[1] || '';
  if (!seg) return 'dashboard';
  if (NAVIGATION_REGISTRY[seg]) return seg;
  const aliased = LEGACY_ALIAS[seg];
  if (aliased && NAVIGATION_REGISTRY[aliased]) return aliased;
  return 'dashboard';
}