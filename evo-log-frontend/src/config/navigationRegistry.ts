// src/config/navigationRegistry.ts
// ERP Logistique Portuaire COMPLET - Architecture End-to-End Navire → Client
// Spécialisé Cameroun/CEMAC avec Comptabilité OHADA
// 12 Modules × 5+ Sous-modules = 60+ Routes Business Process

import {
  // Port & Maritime Icons
  Anchor, Ship, Waves, Harbor, Compass, Navigation, MapPin, Globe,
  
  // Transport & Fleet Icons  
  Truck, Plane, Train, Car, Bus, Bike, Fuel, Route, Zap,
  
  // Warehouse & Stock Icons
  Package, Boxes, Warehouse, Archive, RotateCw, ArrowUpDown, ArrowRightLeft,
  
  // Finance & Accounting Icons
  DollarSign, CreditCard, Receipt, Calculator, TrendingUp, Banknote, Euro,
  
  // Administration & Security Icons
  ShieldAlert, Shield, Lock, Key, Users, UserCheck, Crown, Flag, Search, Sliders, Star, Handshake,
  
  // Operations & Process Icons
  Settings, Wrench, Activity, Zap, Clock, Calendar, ClipboardList, FilePlus, Folder, Share, Download,
  
  // Analytics & Reporting Icons
  BarChart3, PieChart, LineChart, TrendingDown, FileText, BookOpen,
  
  // Communication & Integration Icons
  Radio, Wifi, Smartphone, Bot, MessageSquare, Bell, Monitor,
  
  // General UI Icons
  LayoutDashboard, Layers, Grid, Tag, Building, Landmark, FileCheck, AlertTriangle
} from 'lucide-react';

export interface SubModuleItem {
  label: string;
  path: string;
  icon: any;
  badge?: string;
  description?: string;
  businessProcess?: string; // Étape du processus navire→client
  requiredRoles?: string[];
  isOhadaCompliant?: boolean; // Conformité comptabilité OHADA
  isCemacSpecific?: boolean;  // Spécificité CEMAC/Cameroun
}

export interface ModuleNavConfig {
  key: string;
  title: string;
  path: string;
  icon: any;
  color: string;
  glow: string;
  bgGradient: string;
  businessArea: string; // Zone métier du processus
  processPhase: string; // Phase dans navire→client
  requiredRoles?: string[];
  subModules: SubModuleItem[];
}

// ============================================================================
// 🚢 MODULE 1: OPÉRATIONS PORTUAIRES (Port Operations)
// Phase: Arrivée Navire → Déchargement → Documentation Portuaire
// ============================================================================
export const NAVIGATION_REGISTRY: Record<string, ModuleNavConfig> = {
  
  'port-operations': {
    key: 'port-operations',
    title: '🚢 Opérations Portuaires',
    path: '/port-operations/dashboard',
    icon: Ship,
    color: '#0ea5e9',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-blue-600',
    businessArea: 'Port Maritime',
    processPhase: 'Phase 1: Arrivée & Déchargement Navire',
    requiredRoles: ['ADMIN', 'PORT_OPERATIONS', 'MARITIME', 'MANAGER'],
    subModules: [
      {
        label: 'Control Tower Maritime',
        path: '/port-operations/dashboard',
        icon: LayoutDashboard,
        badge: 'Live',
        description: 'Centre de contrôle temps réel des opérations portuaires',
        businessProcess: 'Supervision globale port',
        requiredRoles: ['ADMIN', 'PORT_OPERATIONS', 'MANAGER']
      },
      {
        label: 'Manifestes & Escales Navires',
        path: '/port-operations/manifests',
        icon: FileText,
        badge: 'Manifestes',
        description: 'Gestion des manifestes de cargaison et programmation escales',
        businessProcess: 'Documentation arrivée navire',
        requiredRoles: ['PORT_OPERATIONS', 'MARITIME', 'DOUANE']
      },
      {
        label: 'Opérations de Quai Live',
        path: '/port-operations/quai-operations',
        icon: Anchor,
        badge: 'Quai',
        description: 'Coordination déchargement, manutention portuaire temps réel',
        businessProcess: 'Déchargement & manutention',
        requiredRoles: ['PORT_OPERATIONS', 'QUAI', 'MARITIME']
      },
      {
        label: 'Planning Accostage & Postes',
        path: '/port-operations/berth-planning',
        icon: Harbor,
        badge: 'Planning',
        description: 'Allocation des postes à quai et planning accostage navires',
        businessProcess: 'Planification maritime',
        requiredRoles: ['PORT_OPERATIONS', 'PLANNING']
      },
      {
        label: 'Statistiques Trafic Maritime',
        path: '/port-operations/maritime-stats',
        icon: BarChart3,
        badge: 'Analytics',
        description: 'Analyses trafic, performance portuaire, KPIs maritimes',
        businessProcess: 'Reporting maritime',
        requiredRoles: ['PORT_OPERATIONS', 'MANAGER', 'AUDITOR']
      },
      {
        label: 'Intégration Systèmes Portuaires',
        path: '/port-operations/port-integration',
        icon: Wifi,
        badge: 'API',
        description: 'Intégration EDI avec autorités portuaires Douala/Kribi',
        businessProcess: 'Intégration systèmes',
        isCemacSpecific: true,
        requiredRoles: ['ADMIN', 'INTEGRATION']
      }
    ]
  },

  // ============================================================================
  // 🛃 MODULE 2: TRANSIT & DOUANE (Customs & Transit)
  // Phase: Dédouanement → Procédures CEMAC → Sortie Port
  // ============================================================================
  'transit-douane': {
    key: 'transit-douane',
    title: '🛃 Transit & Douane',
    path: '/transit-douane/dashboard',
    icon: Landmark,
    color: '#7c3aed',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    businessArea: 'Dédouanement & Transit',
    processPhase: 'Phase 2: Procédures Douanières & Transit',
    requiredRoles: ['ADMIN', 'DOUANE', 'TRANSIT', 'MANAGER'],
    subModules: [
      {
        label: 'Centre de Dédouanement',
        path: '/transit-douane/dashboard',
        icon: LayoutDashboard,
        badge: 'Douane',
        description: 'Centre de traitement des procédures douanières',
        businessProcess: 'Dédouanement import/export',
        requiredRoles: ['DOUANE', 'TRANSIT', 'MANAGER']
      },
      {
        label: 'Dossiers Transit CEMAC',
        path: '/transit-douane/dossiers-cemac',
        icon: Globe,
        badge: 'CEMAC',
        description: 'Gestion dossiers transit zone CEMAC, TEC, TVA',
        businessProcess: 'Transit zone CEMAC',
        isCemacSpecific: true,
        requiredRoles: ['DOUANE', 'TRANSIT']
      },
      {
        label: 'Déclarations & DUM',
        path: '/transit-douane/declarations',
        icon: FileCheck,
        badge: 'DUM',
        description: 'Saisie DUM, déclarations en douane, certificats origine',
        businessProcess: 'Déclarations douanières',
        isCemacSpecific: true,
        requiredRoles: ['DOUANE', 'DECLARANT']
      },
      {
        label: 'Taxation Cameroun',
        path: '/transit-douane/taxation-cameroun',
        icon: Calculator,
        badge: '🇨🇲',
        description: 'Calcul droits & taxes Cameroun: DD, TVA, TEC, redevances',
        businessProcess: 'Taxation douanière',
        isCemacSpecific: true,
        isOhadaCompliant: true,
        requiredRoles: ['DOUANE', 'FINANCE']
      },
      {
        label: 'Conformité & Licences',
        path: '/transit-douane/compliance',
        icon: Shield,
        badge: 'Normes',
        description: 'Vérification conformité, licences import/export, OHADA',
        businessProcess: 'Conformité réglementaire',
        isOhadaCompliant: true,
        requiredRoles: ['DOUANE', 'COMPLIANCE']
      },
      {
        label: 'Bon à Enlever (BAE)',
        path: '/transit-douane/bae',
        icon: FileText,
        badge: 'BAE',
        description: 'Émission Bon à Enlever, mainlevée douanière',
        businessProcess: 'Sortie de douane',
        requiredRoles: ['DOUANE', 'MAGASIN']
      }
    ]
  },

  transport: {
    key: 'transport', title: 'K-Transport & Flotte', path: '/transport/control',
    icon: Truck, color: '#06b6d4', glow: 'shadow-cyan-500/50 border-cyan-500/60',
    bgGradient: 'from-cyan-600 to-blue-500',
    requiredRoles: ['ADMIN', 'DISPATCHER', 'TRANSPORT', 'MANAGER'],
    subModules: [
      { label: 'Poste de Contrôle Live', path: '/transport/control', icon: LayoutDashboard, badge: 'Live' },
      { label: 'Missions & Dispatch', path: '/transport/dispatch', icon: Navigation, badge: 'Planning' },
      { label: 'Flotte Camions & Tracteurs', path: '/transport/flotte', icon: Truck },
      { label: 'Gestion Chauffeurs', path: '/transport/drivers', icon: Users },
      { label: 'Tracking Live & e-POD', path: '/transport/epod', icon: Radio, badge: 'e-POD' },
      { label: 'Carte GPS Temps Réel', path: '/transport/carte-live', icon: MapPin },
      { label: 'ChatOps Missions', path: '/transport/chatops', icon: Bot },
      { label: 'Tickets Carburant', path: '/transport/saisie-ticket-carburant', icon: Fuel, badge: 'Fuel' },
      { label: 'Déclarations de Fret', path: '/transport/goods-declaration', icon: FileCheck },
      { label: 'Gestion des Conteneurs', path: '/transport/containers', icon: Boxes },
    ],
  },

  magasin: {
    key: 'magasin', title: 'K-Magasin WMS', path: '/magasin/dashboard',
    icon: Package, color: '#f59e0b', glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-500',
    requiredRoles: ['ADMIN', 'MAGASINIER', 'MAGASIN', 'MANAGER'],
    subModules: [
      { label: 'Dashboard WMS', path: '/magasin/dashboard', icon: LayoutDashboard, badge: 'Main' },
      { label: 'Réception MAG3', path: '/magasin/reception-mag3', icon: Boxes, badge: 'MAG3' },
      { label: "Bons d'Enlèvement (BL)", path: '/magasin/removal-slip', icon: FileText, badge: 'BL' },
      { label: 'Assistant IA Chat', path: '/magasin/ia-chat', icon: Bot, badge: 'IA' },
      { label: 'Saisie Inventaire Physique', path: '/magasin/saisie-inventaire-physique', icon: ClipboardList },
      { label: 'Ordres de Transfert', path: '/magasin/ordres-transfert', icon: ArrowRightLeft },
      { label: 'Mouvement Stock Manuel', path: '/magasin/mouvement-de-stock-manuel', icon: RotateCcw },
      { label: 'Emplacements WMS', path: '/magasin/wms-slots', icon: MapPin },
      { label: 'Bandes de Livraison', path: '/magasin/bandes-livraison', icon: Layers },
      { label: 'Log Transactions Stock', path: '/magasin/transactions', icon: Activity },
      { label: 'Rapports & Stats WMS', path: '/magasin/rapports', icon: BarChart3 },
    ],
  },

  finance: {
    key: 'finance', title: 'K-Finance & Comptabilité', path: '/finance/overview',
    icon: DollarSign, color: '#10b981', glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-teal-500',
    requiredRoles: ['ADMIN', 'FINANCE', 'MANAGER'],
    subModules: [
      { label: "Vue d'Ensemble Finance", path: '/finance/overview', icon: LayoutDashboard },
      { label: 'Factures & Recettes', path: '/finance/invoicing', icon: FileText, badge: 'Compta' },
      { label: 'Gestion Encaissements', path: '/finance/encaissements', icon: DollarSign },
      { label: 'Requisitions & Achats', path: '/finance/requisitions', icon: ShoppingCart },
      { label: 'Saisie Transactions Bancaires', path: '/finance/saisie-transaction-bancaire', icon: CreditCard },
      { label: 'Grilles Tarifaires', path: '/finance/tarifs', icon: Tag },
      { label: 'Simulateur Cotations & Devis', path: '/cotations', icon: Tag, badge: 'Fret' },
      { label: 'Fiscalité Cameroun', path: '/fiscalite-cameroun', icon: Flag, badge: '🇨🇲' },
      { label: 'Paiements Locaux', path: '/paiement-local', icon: CreditCard, badge: 'CM' },
    ],
  },

  acconage: {
    key: 'acconage', title: 'K-Acconage & Quai', path: '/acconage',
    icon: Building, color: '#3b82f6', glow: 'shadow-blue-500/50 border-blue-500/60',
    bgGradient: 'from-blue-600 to-cyan-500',
    requiredRoles: ['ADMIN', 'DISPATCHER', 'ACCONAGE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Acconage', path: '/acconage', icon: LayoutDashboard, badge: 'Quai' },
      { label: 'Manifestes & Escales Navires', path: '/acconage', icon: FileText },
      { label: 'Opérations de Quai', path: '/acconage', icon: Layers },
      { label: 'Dossiers Transit Portuaire', path: '/transit', icon: Globe },
      { label: 'Contrôle Porte Gate', path: '/parc/gate', icon: Navigation },
      { label: 'Intégration Cameroun', path: '/integration-cameroun', icon: Flag, badge: '🇨🇲' },
    ],
  },

  transit: {
    key: 'transit', title: 'K-Transit & Douane', path: '/transit',
    icon: Globe, color: '#0284c7', glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-blue-600',
    requiredRoles: ['ADMIN', 'DOUANE', 'TRANSIT', 'MANAGER'],
    subModules: [
      { label: 'Dossiers Transit CEMAC', path: '/transit', icon: Globe, badge: 'CEMAC' },
      { label: 'Gestion Acconage Port', path: '/acconage', icon: Building },
      { label: 'Conformité Douanière', path: '/compliance', icon: Landmark },
      { label: 'Déclarations Fret', path: '/transport/goods-declaration', icon: FileText },
      { label: 'Intégration Cameroun', path: '/integration-cameroun', icon: Flag, badge: '🇨🇲' },
    ],
  },

  qhse: {
    key: 'qhse', title: 'K-QHSE & Sécurité', path: '/qhse',
    icon: ShieldAlert, color: '#ef4444', glow: 'shadow-red-500/50 border-red-500/60',
    bgGradient: 'from-red-600 to-rose-500',
    requiredRoles: ['ADMIN', 'QHSE', 'MANAGER'],
    subModules: [
      { label: 'Inspections Portuaires QHSE', path: '/qhse', icon: ShieldAlert, badge: 'Port' },
      { label: 'Centre Incidents & Alertes', path: '/security/notifications', icon: Zap, badge: 'Alertes' },
      { label: 'Audit & Normes ISPS', path: '/compliance', icon: Landmark, badge: 'Normes' },
      { label: 'Rapports & Registres Sécurité', path: '/security/reports', icon: BookOpen },
    ],
  },

  maintenance: {
    key: 'maintenance', title: 'K-Maintenance & Atelier', path: '/maintenance',
    icon: Wrench, color: '#f97316', glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-600 to-amber-500',
    requiredRoles: ['ADMIN', 'MAINTENANCE', 'PARC', 'MANAGER'],
    subModules: [
      { label: 'Tableau de Bord Maintenance', path: '/maintenance', icon: LayoutDashboard, badge: 'Atelier' },
      { label: 'Ordres de Réparation', path: '/maintenance', icon: Wrench },
      { label: 'Pièces de Rechange & Stock', path: '/maintenance', icon: Package },
      { label: 'Work Orders Parc Véhicules', path: '/parc/work-orders/create', icon: ClipboardList },
      { label: 'Télémétrie FuelGuard', path: '/fuel-guard', icon: Fuel },
      { label: 'Achats Pièces & PO', path: '/purchase', icon: ShoppingCart },
    ],
  },

  parc: {
    key: 'parc', title: 'K-Parc Véhicules', path: '/parc',
    icon: MapPin, color: '#8b5cf6', glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    requiredRoles: ['ADMIN', 'PARC', 'GATE', 'MANAGER'],
    subModules: [
      { label: 'Gestion de la Flotte', path: '/parc/gestion-de-la-flotte', icon: Truck, badge: 'Flotte' },
      { label: 'Contrôle Porte Gate', path: '/parc/gate', icon: Navigation, badge: 'Gate' },
      { label: 'Yard Map & Zones', path: '/parc/yard-map', icon: MapPin },
      { label: 'Work Orders Atelier', path: '/parc/work-orders', icon: ClipboardList },
      { label: 'Workshop Réparations', path: '/parc/workshop', icon: Wrench },
      { label: 'Zones de Stockage', path: '/parc/zones', icon: Layers },
    ],
  },

  rh: {
    key: 'rh', title: 'Ressources Humaines', path: '/rh/dashboard',
    icon: UserCheck, color: '#ec4899', glow: 'shadow-pink-500/50 border-pink-500/60',
    bgGradient: 'from-pink-600 to-rose-500',
    requiredRoles: ['ADMIN', 'RH', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Ressources Humaines', path: '/rh/dashboard', icon: LayoutDashboard, badge: 'RH' },
      { label: 'Annuaire & Gestion Employés', path: '/rh/employes', icon: Users, badge: 'Personnel' },
      { label: 'Mon Espace RH & Demandes', path: '/rh/mon-espace', icon: UserCheck },
      { label: 'Gestion de la Paie', path: '/rh/paie', icon: DollarSign, badge: 'Paie' },
    ],
  },

  'master-data': {
    key: 'master-data', title: 'Données Maîtres ERP', path: '/master-data/tiers',
    icon: Users, color: '#ec4899', glow: 'shadow-pink-500/50 border-pink-500/60',
    bgGradient: 'from-pink-600 to-purple-600',
    requiredRoles: ['ADMIN', 'MANAGER', 'MAGASIN', 'FINANCE'],
    subModules: [
      { label: 'Répertoire Tiers & Clients', path: '/master-data/tiers', icon: Users, badge: 'Tiers' },
      { label: 'Catalogue Articles & Stock', path: '/master-data/articles', icon: Package, badge: 'Articles' },
      { label: 'Catégories Articles', path: '/master-data/article-categories', icon: Layers },
      { label: 'Emplacements WMS', path: '/magasin/wms-slots', icon: MapPin },
      { label: 'Fournisseurs', path: '/fournisseurs', icon: Building },
    ],
  },

  cotations: {
    key: 'cotations', title: 'K-Cotations & Devis', path: '/cotations',
    icon: Tag, color: '#eab308', glow: 'shadow-yellow-500/50 border-yellow-500/60',
    bgGradient: 'from-yellow-600 to-amber-500',
    requiredRoles: ['ADMIN', 'FINANCE', 'TRANSIT', 'MANAGER'],
    subModules: [
      { label: 'Simulateur Tarifs & Devis Fret', path: '/cotations', icon: Tag, badge: 'Fret' },
      { label: 'Calculateur de Cotation', path: '/cotations/calculateur', icon: DollarSign },
      { label: 'Commandes Procurement', path: '/procurement', icon: ShoppingCart },
      { label: 'Répertoire Tiers', path: '/master-data/tiers', icon: Users },
    ],
  },

  tracking: {
    key: 'tracking', title: 'K-Tracking & e-POD', path: '/tracking',
    icon: Radio, color: '#06b6d4', glow: 'shadow-cyan-500/50 border-cyan-500/60',
    bgGradient: 'from-cyan-600 to-teal-500',
    requiredRoles: ['ADMIN', 'DISPATCHER', 'TRANSPORT', 'MANAGER'],
    subModules: [
      { label: 'Suivi des Expéditions e-POD', path: '/tracking', icon: Radio, badge: 'Live' },
      { label: 'Carte GPS Flotte Live', path: '/transport/carte-live', icon: MapPin },
      { label: 'ChatOps Missions', path: '/transport/chatops', icon: Bot },
      { label: 'e-POD Signatures', path: '/tracking/epod', icon: FileCheck },
    ],
  },

  'fuel-guard': {
    key: 'fuel-guard', title: 'K-FuelGuard Télémétrie', path: '/fuel-guard',
    icon: Fuel, color: '#f97316', glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-600 to-amber-600',
    requiredRoles: ['ADMIN', 'PARC', 'TRANSPORT', 'MANAGER'],
    subModules: [
      { label: 'Télémétrie Carburant Live', path: '/fuel-guard', icon: Fuel, badge: 'Live' },
      { label: 'Alertes Consommation', path: '/fuel-guard/alerts', icon: Zap },
      { label: 'Saisie Tickets Carburant', path: '/transport/saisie-ticket-carburant', icon: FileText },
      { label: 'Flotte Camions', path: '/transport/flotte', icon: Truck },
    ],
  },

  procurement: {
    key: 'procurement', title: 'K-Procurement & Achats', path: '/procurement',
    icon: ShoppingCart, color: '#10b981', glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-green-500',
    requiredRoles: ['ADMIN', 'FINANCE', 'MAGASIN', 'MANAGER'],
    subModules: [
      { label: 'Achats & Requisitions PO', path: '/procurement', icon: ShoppingCart, badge: 'PO' },
      { label: 'Commandes Fournisseurs', path: '/procurement/orders', icon: FileText },
      { label: 'Catalogue Fournisseurs', path: '/fournisseurs', icon: Building },
      { label: 'Cotations Fret', path: '/cotations', icon: Tag },
    ],
  },

  compliance: {
    key: 'compliance', title: 'K-Compliance & Douane', path: '/compliance',
    icon: Landmark, color: '#14b8a6', glow: 'shadow-teal-500/50 border-teal-500/60',
    bgGradient: 'from-teal-600 to-emerald-500',
    requiredRoles: ['ADMIN', 'DOUANE', 'QHSE', 'MANAGER'],
    subModules: [
      { label: 'Compliance Douane & Normes', path: '/compliance', icon: Landmark, badge: 'ISPS' },
      { label: 'Centre Incidents & Sécurité', path: '/security/notifications', icon: Zap },
      { label: 'Inspections Portuaires', path: '/qhse', icon: ShieldAlert },
      { label: 'Audits de Conformité', path: '/compliance/audits', icon: BookOpen },
    ],
  },

  bi: {
    key: 'bi', title: 'K-Analytics BI Executive', path: '/reports',
    icon: BarChart3, color: '#8b5cf6', glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    requiredRoles: ['ADMIN', 'MANAGER', 'AUDITOR'],
    subModules: [
      { label: 'Rapports Personnalisés', path: '/reports', icon: BarChart3, badge: 'KPIs' },
      { label: 'Générateur de Rapports', path: '/reports/generateur-rapports-personnalises', icon: FileText },
      { label: "Journal d'Audit Système", path: '/admin/journal', icon: Activity },
      { label: 'Statistiques WMS', path: '/magasin/dashboard', icon: LayoutDashboard },
      { label: 'Statistiques Transport', path: '/transport/analytics', icon: Truck },
    ],
  },

  'client-portal': {
    key: 'client-portal', title: 'Portail Client B2B', path: '/client-portal',
    icon: Globe, color: '#0284c7', glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-indigo-600',
    requiredRoles: ['ADMIN', 'CLIENT', 'CLIENT_B2B', 'MANAGER'],
    subModules: [
      { label: 'Tableau de Bord Client', path: '/client-portal', icon: LayoutDashboard, badge: 'B2B' },
      { label: 'Mes Expéditions', path: '/client-portal/shipments', icon: Radio, badge: 'Tracking' },
      { label: 'Mes Commandes', path: '/client-portal/orders', icon: ShoppingCart },
      { label: 'Mes Factures', path: '/client-portal/invoices', icon: FileText },
      { label: 'Mes Litiges', path: '/client-portal/litiges', icon: ShieldAlert },
      { label: 'Rapports Personnalisés', path: '/client-portal/reports', icon: BarChart3 },
      { label: 'Mon Profil', path: '/client-portal/profile', icon: UserCheck },
    ],
  },

  settings: {
    key: 'settings', title: 'Paramètres & Profil', path: '/settings',
    icon: Settings, color: '#64748b', glow: 'shadow-slate-500/50 border-slate-500/60',
    bgGradient: 'from-slate-600 to-slate-800',
    subModules: [
      { label: 'Mon Profil Utilisateur', path: '/settings', icon: Settings },
      { label: 'Paramètres Système', path: '/settings/system', icon: ShieldAlert },
    ],
  },
};

export function getFilteredNavigationForUser(
  user: { roles?: string[]; modulesAllowed?: string[] } | null
): ModuleNavConfig[] {
  if (!user) return Object.values(NAVIGATION_REGISTRY);

  const userRoles = (user.roles || []).map(r => r.toUpperCase());
  const isAdmin = userRoles.includes('ADMIN');
  const userModules = user.modulesAllowed || [];

  return Object.values(NAVIGATION_REGISTRY).map(moduleConfig => {
    if (isAdmin) return moduleConfig;

    const isModuleAllowed =
      moduleConfig.key === 'dashboard' ||
      moduleConfig.key === 'settings' ||
      userModules.includes(moduleConfig.key) ||
      (moduleConfig.requiredRoles?.some(role => userRoles.includes(role)) ?? false);

    if (!isModuleAllowed) return null;

    const filteredSubModules = moduleConfig.subModules.filter(sub => {
      if (!sub.requiredRoles || sub.requiredRoles.length === 0) return true;
      return sub.requiredRoles.some(r => userRoles.includes(r.toUpperCase()));
    });

    return { ...moduleConfig, subModules: filteredSubModules };
  }).filter(Boolean) as ModuleNavConfig[];
}
  // ============================================================================
  // 🚛 MODULE 3: TRANSPORT & FLOTTE (Transport & Fleet Management)
  // Phase: Enlèvement → Transport → Livraison Client
  // ============================================================================
  'transport-flotte': {
    key: 'transport-flotte',
    title: '🚛 Transport & Flotte',
    path: '/transport-flotte/control-tower',
    icon: Truck,
    color: '#06b6d4',
    glow: 'shadow-cyan-500/50 border-cyan-500/60',
    bgGradient: 'from-cyan-600 to-blue-500',
    businessArea: 'Transport & Logistique',
    processPhase: 'Phase 3: Transport Marchandises vers Client',
    requiredRoles: ['ADMIN', 'TRANSPORT', 'DISPATCHER', 'MANAGER'],
    subModules: [
      {
        label: 'Control Tower Transport',
        path: '/transport-flotte/control-tower',
        icon: LayoutDashboard,
        badge: 'Live',
        description: 'Centre de contrôle transport temps réel, dispatch missions',
        businessProcess: 'Supervision transport',
        requiredRoles: ['TRANSPORT', 'DISPATCHER', 'MANAGER']
      },
      {
        label: 'Gestion Flotte Complète',
        path: '/transport-flotte/fleet-management',
        icon: Truck,
        badge: 'Flotte',
        description: 'Camions, tracteurs, remorques, engins manutention',
        businessProcess: 'Gestion parc véhicules',
        requiredRoles: ['TRANSPORT', 'FLEET_MANAGER']
      },
      {
        label: 'Missions & Dispatch',
        path: '/transport-flotte/missions-dispatch',
        icon: Navigation,
        badge: 'Dispatch',
        description: 'Affectation missions, optimisation tournées, planning chauffeurs',
        businessProcess: 'Planification transport',
        requiredRoles: ['DISPATCHER', 'TRANSPORT']
      },
      {
        label: 'Tracking GPS & e-POD',
        path: '/transport-flotte/tracking-epod',
        icon: MapPin,
        badge: 'GPS',
        description: 'Suivi temps réel GPS, e-POD signatures électroniques',
        businessProcess: 'Suivi livraisons',
        requiredRoles: ['TRANSPORT', 'CLIENT']
      },
      {
        label: 'Gestion Chauffeurs',
        path: '/transport-flotte/drivers',
        icon: UserCheck,
        badge: 'Chauffeurs',
        description: 'Permis, formations, planning, heures de conduite',
        businessProcess: 'Ressources transport',
        requiredRoles: ['TRANSPORT', 'RH']
      },
      {
        label: 'Carburant & Télémétrie',
        path: '/transport-flotte/fuel-telematics',
        icon: Fuel,
        badge: 'Fuel',
        description: 'Consommation carburant, télémétrie, optimisation routes',
        businessProcess: 'Optimisation coûts',
        requiredRoles: ['TRANSPORT', 'FINANCE']
      }
    ]
  },

  // ============================================================================
  // 📦 MODULE 4: MAGASIN & STOCK WMS (Warehouse Management System)
  // Phase: Réception → Stockage → Préparation → Expédition
  // ============================================================================
  'magasin-stock': {
    key: 'magasin-stock',
    title: '📦 Magasin & Stock WMS',
    path: '/magasin-stock/dashboard',
    icon: Warehouse,
    color: '#f59e0b',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-600 to-yellow-500',
    businessArea: 'Entreposage & Stock',
    processPhase: 'Phase 4: Gestion Stock & Préparation',
    requiredRoles: ['ADMIN', 'MAGASIN', 'STOCK', 'MANAGER'],
    subModules: [
      {
        label: 'Dashboard WMS Central',
        path: '/magasin-stock/dashboard',
        icon: LayoutDashboard,
        badge: 'WMS',
        description: 'Vue globale stock, mouvements, alertes, KPIs entrepôt',
        businessProcess: 'Supervision WMS',
        requiredRoles: ['MAGASIN', 'STOCK', 'MANAGER']
      },
      {
        label: 'Réception Marchandises',
        path: '/magasin-stock/reception',
        icon: Package,
        badge: 'Réception',
        description: 'Réception, contrôle qualité, mise en stock, étiquetage',
        businessProcess: 'Réception stock',
        requiredRoles: ['MAGASIN', 'RECEPTION']
      },
      {
        label: 'Gestion Emplacements',
        path: '/magasin-stock/locations',
        icon: MapPin,
        badge: 'Zones',
        description: 'Plan entrepôt, zones stockage, emplacements, picking',
        businessProcess: 'Organisation stock',
        requiredRoles: ['MAGASIN', 'STOCK']
      },
      {
        label: 'Mouvements de Stock',
        path: '/magasin-stock/movements',
        icon: ArrowUpDown,
        badge: 'Mouvements',
        description: 'Entrées, sorties, transferts, ajustements inventaire',
        businessProcess: 'Traçabilité stock',
        isOhadaCompliant: true,
        requiredRoles: ['MAGASIN', 'STOCK']
      },
      {
        label: 'Inventaire & Contrôle',
        path: '/magasin-stock/inventory',
        icon: ClipboardList,
        badge: 'Inventaire',
        description: 'Inventaires cycliques, comptages, écarts, valorisation',
        businessProcess: 'Contrôle stock',
        isOhadaCompliant: true,
        requiredRoles: ['MAGASIN', 'AUDITOR']
      },
      {
        label: 'Préparation Commandes',
        path: '/magasin-stock/picking',
        icon: Boxes,
        badge: 'Picking',
        description: 'Préparation, picking, colisage, bons de livraison',
        businessProcess: 'Préparation livraison',
        requiredRoles: ['MAGASIN', 'PREPARATEUR']
      }
    ]
  },

  // ============================================================================
  // 💰 MODULE 5: FINANCE OHADA (Finance & OHADA Accounting)
  // Phase: Facturation → Encaissement → Comptabilité → Reporting
  // ============================================================================
  'finance-ohada': {
    key: 'finance-ohada',
    title: '💰 Finance OHADA',
    path: '/finance-ohada/dashboard',
    icon: DollarSign,
    color: '#10b981',
    glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-teal-500',
    businessArea: 'Finance & Comptabilité',
    processPhase: 'Phase 5: Facturation & Encaissement',
    requiredRoles: ['ADMIN', 'FINANCE', 'COMPTABLE', 'MANAGER'],
    subModules: [
      {
        label: 'Tableau de Bord Finance',
        path: '/finance-ohada/dashboard',
        icon: LayoutDashboard,
        badge: 'Finance',
        description: 'KPIs financiers, cash flow, créances, dettes',
        businessProcess: 'Pilotage financier',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'MANAGER']
      },
      {
        label: 'Facturation Clients',
        path: '/finance-ohada/invoicing',
        icon: Receipt,
        badge: 'Facturation',
        description: 'Factures clients, avoirs, échéanciers, relances',
        businessProcess: 'Facturation',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'COMMERCIAL']
      },
      {
        label: 'Encaissements & Règlements',
        path: '/finance-ohada/collections',
        icon: CreditCard,
        badge: 'Encaissement',
        description: 'Saisie règlements, lettrage, rapprochements bancaires',
        businessProcess: 'Gestion créances',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'TRESORIER']
      },
      {
        label: 'Achats & Fournisseurs',
        path: '/finance-ohada/suppliers',
        icon: Receipt,
        badge: 'Achats',
        description: 'Factures fournisseurs, commandes, réceptions, paiements',
        businessProcess: 'Gestion dettes',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'ACHAT']
      },
      {
        label: 'Trésorerie & Banques',
        path: '/finance-ohada/treasury',
        icon: Banknote,
        badge: 'Trésorerie',
        description: 'Comptes bancaires, virements, prévisions trésorerie',
        businessProcess: 'Gestion trésorerie',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'TRESORIER']
      },
      {
        label: 'Taxes Cameroun/CEMAC',
        path: '/finance-ohada/taxes-cemac',
        icon: Calculator,
        badge: 'Taxes',
        description: 'TVA, IRCM, droits douane, déclarations fiscales CEMAC',
        businessProcess: 'Fiscalité',
        isCemacSpecific: true,
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'FISCAL']
      }
    ]
  },
  // ============================================================================
  // 📚 MODULE 6: COMPTABILITÉ OHADA (OHADA Accounting & Books)
  // Phase: Écritures → Grand Livre → Bilan → Reporting OHADA
  // ============================================================================
  'comptabilite-ohada': {
    key: 'comptabilite-ohada',
    title: '📚 Comptabilité OHADA',
    path: '/comptabilite-ohada/dashboard',
    icon: BookOpen,
    color: '#8b5cf6',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    businessArea: 'Comptabilité Générale',
    processPhase: 'Phase 6: Comptabilité & États Financiers',
    requiredRoles: ['ADMIN', 'COMPTABLE', 'EXPERT_COMPTABLE', 'MANAGER'],
    subModules: [
      {
        label: 'Journal Comptable OHADA',
        path: '/comptabilite-ohada/journal',
        icon: BookOpen,
        badge: 'Journal',
        description: 'Saisie écritures, journal général, validation comptable',
        businessProcess: 'Saisie comptable',
        isOhadaCompliant: true,
        requiredRoles: ['COMPTABLE', 'SAISISSEUR']
      },
      {
        label: 'Plan Comptable OHADA',
        path: '/comptabilite-ohada/chart-accounts',
        icon: Grid,
        badge: 'Plan',
        description: 'Plan de comptes SYSCOHADA, paramétrages, hiérarchie',
        businessProcess: 'Référentiel comptable',
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'COMPTABLE']
      },
      {
        label: 'Grand Livre & Balances',
        path: '/comptabilite-ohada/general-ledger',
        icon: Layers,
        badge: 'Grand Livre',
        description: 'Grand livre, balances, lettrage, centralisation',
        businessProcess: 'Livres comptables',
        isOhadaCompliant: true,
        requiredRoles: ['COMPTABLE', 'AUDITOR']
      },
      {
        label: 'Clôture Mensuelle',
        path: '/comptabilite-ohada/monthly-closing',
        icon: Calendar,
        badge: 'Clôture',
        description: 'Procédures clôture, régularisations, provisions',
        businessProcess: 'Arrêté comptable',
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'MANAGER']
      },
      {
        label: 'Bilan & Compte Résultat',
        path: '/comptabilite-ohada/financial-statements',
        icon: BarChart3,
        badge: 'États',
        description: 'Bilan OHADA, compte résultat, TAFIRE, annexes',
        businessProcess: 'États financiers',
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'MANAGER']
      },
      {
        label: 'Liasse Fiscale CEMAC',
        path: '/comptabilite-ohada/tax-package-cemac',
        icon: FileText,
        badge: 'Fiscal',
        description: 'Déclarations fiscales CEMAC, IS, patente, TVA',
        businessProcess: 'Déclarations fiscales',
        isCemacSpecific: true,
        isOhadaCompliant: true,
        requiredRoles: ['EXPERT_COMPTABLE', 'FISCAL']
      }
    ]
  },

  // ============================================================================
  // 🚗 MODULE 7: PARC & VÉHICULES (Vehicle & Equipment Fleet)
  // Phase: Gestion Flotte → Maintenance → Contrôles → Optimisation
  // ============================================================================
  'parc-vehicules': {
    key: 'parc-vehicules',
    title: '🚗 Parc & Véhicules',
    path: '/parc-vehicules/dashboard',
    icon: Car,
    color: '#f97316',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-600 to-amber-500',
    businessArea: 'Gestion Parc Automobile',
    processPhase: 'Support: Gestion Équipements Transport',
    requiredRoles: ['ADMIN', 'PARC', 'MAINTENANCE', 'MANAGER'],
    subModules: [
      {
        label: 'Tableau de Bord Parc',
        path: '/parc-vehicules/dashboard',
        icon: LayoutDashboard,
        badge: 'Parc',
        description: 'Vue globale flotte, disponibilité, alertes maintenance',
        businessProcess: 'Supervision parc',
        requiredRoles: ['PARC', 'MANAGER']
      },
      {
        label: 'Flotte Complète',
        path: '/parc-vehicules/fleet-complete',
        icon: Truck,
        badge: 'Flotte',
        description: 'Camions, tracteurs, remorques, engins, chariots',
        businessProcess: 'Inventaire parc',
        requiredRoles: ['PARC', 'FLEET_MANAGER']
      },
      {
        label: 'Maintenance Préventive',
        path: '/parc-vehicules/preventive-maintenance',
        icon: Wrench,
        badge: 'Maintenance',
        description: 'Plannings maintenance, révisions, contrôles techniques',
        businessProcess: 'Maintenance véhicules',
        requiredRoles: ['PARC', 'MAINTENANCE']
      },
      {
        label: 'Cartes Grises & Assurances',
        path: '/parc-vehicules/documents',
        icon: FileCheck,
        badge: 'Documents',
        description: 'Cartes grises, assurances, contrôles, permis Cameroun',
        businessProcess: 'Documentation véhicules',
        isCemacSpecific: true,
        requiredRoles: ['PARC', 'ADMINISTRATIF']
      },
      {
        label: 'Consommation & Coûts',
        path: '/parc-vehicules/costs-consumption',
        icon: TrendingUp,
        badge: 'Coûts',
        description: 'Carburant, réparations, amortissements, TCO',
        businessProcess: 'Optimisation coûts',
        isOhadaCompliant: true,
        requiredRoles: ['PARC', 'FINANCE']
      },
      {
        label: 'Plaques & Immatriculations',
        path: '/parc-vehicules/license-plates',
        icon: Tag,
        badge: 'Plaques',
        description: 'Gestion plaques, immatriculations, changements, historique',
        businessProcess: 'Gestion immatriculations',
        isCemacSpecific: true,
        requiredRoles: ['PARC', 'ADMINISTRATIF']
      }
    ]
  },

  // ============================================================================
  // 🛡️ MODULE 8: QHSE & SÉCURITÉ (Quality, Health, Safety, Environment)
  // Phase: Contrôles → Audits → Incidents → Conformité
  // ============================================================================
  'qhse-securite': {
    key: 'qhse-securite',
    title: '🛡️ QHSE & Sécurité',
    path: '/qhse-securite/dashboard',
    icon: ShieldAlert,
    color: '#ef4444',
    glow: 'shadow-red-500/50 border-red-500/60',
    bgGradient: 'from-red-600 to-rose-500',
    businessArea: 'Qualité & Sécurité',
    processPhase: 'Support: Conformité & Sécurité',
    requiredRoles: ['ADMIN', 'QHSE', 'SECURITE', 'MANAGER'],
    subModules: [
      {
        label: 'Centre Sécurité QHSE',
        path: '/qhse-securite/dashboard',
        icon: LayoutDashboard,
        badge: 'QHSE',
        description: 'Tableaux bord sécurité, incidents, conformité',
        businessProcess: 'Supervision sécurité',
        requiredRoles: ['QHSE', 'MANAGER']
      },
      {
        label: 'Inspections Portuaires',
        path: '/qhse-securite/port-inspections',
        icon: Shield,
        badge: 'Inspections',
        description: 'Inspections sécurité port, contrôles ISPS, audits',
        businessProcess: 'Contrôles sécurité',
        requiredRoles: ['QHSE', 'INSPECTOR']
      },
      {
        label: 'Gestion des Incidents',
        path: '/qhse-securite/incident-management',
        icon: Bell,
        badge: 'Incidents',
        description: 'Déclaration, investigation, actions correctives',
        businessProcess: 'Gestion incidents',
        requiredRoles: ['QHSE', 'ALL_USERS']
      },
      {
        label: 'Formations Sécurité',
        path: '/qhse-securite/safety-training',
        icon: Users,
        badge: 'Formations',
        description: 'Habilitations, formations sécurité, recyclages',
        businessProcess: 'Formation personnel',
        requiredRoles: ['QHSE', 'RH']
      },
      {
        label: 'Conformité OHADA',
        path: '/qhse-securite/ohada-compliance',
        icon: Landmark,
        badge: 'OHADA',
        description: 'Conformité réglementaire OHADA, droit social',
        businessProcess: 'Conformité légale',
        isOhadaCompliant: true,
        isCemacSpecific: true,
        requiredRoles: ['QHSE', 'JURIDIQUE']
      },
      {
        label: 'Environnement & RSE',
        path: '/qhse-securite/environment',
        icon: Activity,
        badge: 'Environnement',
        description: 'Impact environnemental, déchets, émissions CO2',
        businessProcess: 'Gestion environnementale',
        requiredRoles: ['QHSE', 'ENVIRONMENT']
      }
    ]
  },

  // ============================================================================
  // 👥 MODULE 9: RH & PERSONNEL (Human Resources & Payroll)
  // Phase: Recrutement → Gestion → Paie → Développement
  // ============================================================================
  'rh-personnel': {
    key: 'rh-personnel',
    title: '👥 RH & Personnel',
    path: '/rh-personnel/dashboard',
    icon: Users,
    color: '#ec4899',
    glow: 'shadow-pink-500/50 border-pink-500/60',
    bgGradient: 'from-pink-600 to-rose-500',
    businessArea: 'Ressources Humaines',
    processPhase: 'Support: Gestion Capital Humain',
    requiredRoles: ['ADMIN', 'RH', 'PAIE', 'MANAGER'],
    subModules: [
      {
        label: 'Dashboard RH Central',
        path: '/rh-personnel/dashboard',
        icon: LayoutDashboard,
        badge: 'RH',
        description: 'Effectifs, KPIs RH, turnover, absentéisme',
        businessProcess: 'Pilotage RH',
        requiredRoles: ['RH', 'MANAGER']
      },
      {
        label: 'Gestion des Employés',
        path: '/rh-personnel/employees',
        icon: UserCheck,
        badge: 'Personnel',
        description: 'Dossiers personnel, contrats, carrières, évaluations',
        businessProcess: 'Administration personnel',
        requiredRoles: ['RH', 'MANAGER']
      },
      {
        label: 'Paie OHADA Cameroun',
        path: '/rh-personnel/payroll-ohada',
        icon: CreditCard,
        badge: 'Paie',
        description: 'Bulletins paie, charges sociales CNPS, IRCM',
        businessProcess: 'Gestion paie',
        isOhadaCompliant: true,
        isCemacSpecific: true,
        requiredRoles: ['RH', 'PAIE']
      },
      {
        label: 'Temps & Présences',
        path: '/rh-personnel/time-attendance',
        icon: Clock,
        badge: 'Présences',
        description: 'Pointages, congés, RTT, heures supplémentaires',
        businessProcess: 'Gestion temps',
        requiredRoles: ['RH', 'POINTEUSE']
      },
      {
        label: 'Formation & Compétences',
        path: '/rh-personnel/training-skills',
        icon: BookOpen,
        badge: 'Formation',
        description: 'Plans formation, compétences, habilitations',
        businessProcess: 'Développement RH',
        requiredRoles: ['RH', 'FORMATION']
      },
      {
        label: 'Déclarations Sociales',
        path: '/rh-personnel/social-declarations',
        icon: FileText,
        badge: 'Social',
        description: 'CNPS, DIPE, déclarations sociales Cameroun',
        businessProcess: 'Obligations sociales',
        isCemacSpecific: true,
        requiredRoles: ['RH', 'PAIE']
      }
    ]
  },
  // ============================================================================
  // 🤝 MODULE 10: CLIENT & B2B (Customer Relationship & B2B Portal)
  // Phase: Prospects → Clients → Fidélisation → Support
  // ============================================================================
  'client-b2b': {
    key: 'client-b2b',
    title: '🤝 Client & B2B',
    path: '/client-b2b/dashboard',
    icon: Users,
    color: '#0284c7',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-indigo-600',
    businessArea: 'Relation Client',
    processPhase: 'Support: Gestion Relation Client',
    requiredRoles: ['ADMIN', 'COMMERCIAL', 'CLIENT_SERVICE', 'MANAGER'],
    subModules: [
      {
        label: 'CRM & Prospects',
        path: '/client-b2b/crm',
        icon: Users,
        badge: 'CRM',
        description: 'Prospects, opportunités, pipeline commercial',
        businessProcess: 'Prospection commerciale',
        requiredRoles: ['COMMERCIAL', 'MANAGER']
      },
      {
        label: 'Portail Client B2B',
        path: '/client-b2b/portal',
        icon: Globe,
        badge: 'B2B',
        description: 'Accès client : commandes, tracking, factures, litiges',
        businessProcess: 'Self-service client',
        requiredRoles: ['CLIENT', 'CLIENT_B2B']
      },
      {
        label: 'Contrats & Tarifications',
        path: '/client-b2b/contracts',
        icon: FileText,
        badge: 'Contrats',
        description: 'Contrats cadres, grilles tarifaires, conditions',
        businessProcess: 'Contractualisation',
        isOhadaCompliant: true,
        requiredRoles: ['COMMERCIAL', 'JURIDIQUE']
      },
      {
        label: 'Service Après-Vente',
        path: '/client-b2b/after-sales',
        icon: MessageSquare,
        badge: 'SAV',
        description: 'Tickets support, réclamations, résolution litiges',
        businessProcess: 'Support client',
        requiredRoles: ['CLIENT_SERVICE', 'SUPPORT']
      },
      {
        label: 'Fidélisation & Marketing',
        path: '/client-b2b/loyalty',
        icon: Crown,
        badge: 'Fidélité',
        description: 'Programmes fidélité, campagnes, analyses comportement',
        businessProcess: 'Fidélisation client',
        requiredRoles: ['MARKETING', 'COMMERCIAL']
      },
      {
        label: 'Analytics Client',
        path: '/client-b2b/analytics',
        icon: BarChart3,
        badge: 'Analytics',
        description: 'Chiffre affaires, rentabilité, satisfaction client',
        businessProcess: 'Analyse commerciale',
        requiredRoles: ['COMMERCIAL', 'MANAGER']
      }
    ]
  },

  // ============================================================================
  // ⚙️ MODULE 11: ADMIN & TENANT (Administration & Multi-Tenant)
  // Phase: Configuration → Sécurité → Audit → Gouvernance
  // ============================================================================
  'admin-tenant': {
    key: 'admin-tenant',
    title: '⚙️ Admin & Tenant',
    path: '/admin-tenant/dashboard',
    icon: Settings,
    color: '#6366f1',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-violet-600',
    businessArea: 'Administration Système',
    processPhase: 'Support: Gouvernance & Sécurité',
    requiredRoles: ['SUPER_ADMIN', 'ADMIN', 'TENANT_ADMIN'],
    subModules: [
      {
        label: 'Administration Système',
        path: '/admin-tenant/system-admin',
        icon: Crown,
        badge: 'Super Admin',
        description: 'Configuration globale, tenants, licences, performances',
        businessProcess: 'Administration système',
        requiredRoles: ['SUPER_ADMIN']
      },
      {
        label: 'Gestion Multi-Tenant',
        path: '/admin-tenant/multi-tenant',
        icon: Building,
        badge: 'Tenants',
        description: 'Organisations, isolation données, facturation SaaS',
        businessProcess: 'Gestion tenants',
        requiredRoles: ['SUPER_ADMIN', 'TENANT_ADMIN']
      },
      {
        label: 'Utilisateurs & RBAC',
        path: '/admin-tenant/users-rbac',
        icon: ShieldAlert,
        badge: 'Sécurité',
        description: 'Comptes, rôles, permissions, authentification',
        businessProcess: 'Gestion accès',
        requiredRoles: ['ADMIN', 'TENANT_ADMIN']
      },
      {
        label: 'Audit & Logs',
        path: '/admin-tenant/audit-logs',
        icon: Activity,
        badge: 'Audit',
        description: 'Journaux audit, traçabilité, conformité RGPD',
        businessProcess: 'Audit système',
        requiredRoles: ['ADMIN', 'AUDITOR']
      },
      {
        label: 'Intégrations & API',
        path: '/admin-tenant/integrations',
        icon: Wifi,
        badge: 'API',
        description: 'Connecteurs, webhooks, EDI, services tiers',
        businessProcess: 'Intégrations système',
        requiredRoles: ['ADMIN', 'INTEGRATION']
      },
      {
        label: 'Paramètres Globaux',
        path: '/admin-tenant/global-settings',
        icon: Settings,
        badge: 'Config',
        description: 'Configuration ERP, modules, fonctionnalités',
        businessProcess: 'Configuration ERP',
        requiredRoles: ['ADMIN', 'TENANT_ADMIN']
      }
    ]
  },

  // ============================================================================
  // 📊 MODULE 12: REPORTS & BI (Business Intelligence & Analytics)
  // Phase: Collecte → Analyse → Reporting → Décision
  // ============================================================================
  'reports-bi': {
    key: 'reports-bi',
    title: '📊 Reports & BI',
    path: '/reports-bi/executive-dashboard',
    icon: BarChart3,
    color: '#8b5cf6',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    businessArea: 'Business Intelligence',
    processPhase: 'Support: Pilotage & Décision',
    requiredRoles: ['ADMIN', 'MANAGER', 'ANALYST', 'AUDITOR'],
    subModules: [
      {
        label: 'Executive Dashboard',
        path: '/reports-bi/executive-dashboard',
        icon: LayoutDashboard,
        badge: 'Executive',
        description: 'KPIs direction, tableaux bord stratégiques',
        businessProcess: 'Pilotage stratégique',
        requiredRoles: ['MANAGER', 'DIRECTOR']
      },
      {
        label: 'Analytics Opérationnels',
        path: '/reports-bi/operational-analytics',
        icon: LineChart,
        badge: 'Analytics',
        description: 'Performance transport, WMS, financière, qualité',
        businessProcess: 'Analyse opérationnelle',
        requiredRoles: ['ANALYST', 'MANAGER']
      },
      {
        label: 'Rapports Financiers OHADA',
        path: '/reports-bi/financial-reports-ohada',
        icon: TrendingUp,
        badge: 'Finance',
        description: 'États financiers, analyse rentabilité, cash flow',
        businessProcess: 'Reporting financier',
        isOhadaCompliant: true,
        requiredRoles: ['FINANCE', 'MANAGER']
      },
      {
        label: 'Compliance & Audit',
        path: '/reports-bi/compliance-audit',
        icon: Shield,
        badge: 'Compliance',
        description: 'Rapports conformité, audit trails, risques',
        businessProcess: 'Contrôle conformité',
        requiredRoles: ['AUDITOR', 'COMPLIANCE']
      },
      {
        label: 'Générateur de Rapports',
        path: '/reports-bi/report-generator',
        icon: FileText,
        badge: 'Générateur',
        description: 'Création rapports personnalisés, requêtes ad hoc',
        businessProcess: 'Reporting personnalisé',
        requiredRoles: ['ANALYST', 'POWER_USER']
      },
      {
        label: 'Data Export & API',
        path: '/reports-bi/data-export',
        icon: ArrowUpDown,
        badge: 'Export',
        description: 'Exports données, API BI, intégrations décisionnelles',
        businessProcess: 'Extraction données',
        requiredRoles: ['ANALYST', 'INTEGRATION']
      }
    ]
  },

  // ============================================================================
  // 🎯 MODULE DASHBOARD: VUE GLOBALE ERP (Global ERP Overview)
  // ============================================================================
  dashboard: {
    key: 'dashboard',
    title: '🎯 Vue Globale ERP',
    path: '/dashboard/global',
    icon: LayoutDashboard,
    color: '#6366f1',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-blue-600',
    businessArea: 'Supervision Générale',
    processPhase: 'Vue Transversale Processus Complete',
    subModules: [
      {
        label: "Executive Dashboard",
        path: '/dashboard/global',
        icon: LayoutDashboard,
        badge: 'Main',
        description: 'Vue exécutive globale : KPIs, alertes, performance',
        businessProcess: 'Pilotage global'
      },
      {
        label: 'Processus Navire → Client',
        path: '/dashboard/process-flow',
        icon: Ship,
        badge: 'Process',
        description: 'Suivi temps réel du processus end-to-end complet',
        businessProcess: 'Supervision processus'
      },
      {
        label: 'Alertes & Incidents Live',
        path: '/dashboard/alerts',
        icon: Bell,
        badge: 'Live',
        description: 'Centre alertes temps réel tous modules',
        businessProcess: 'Monitoring'
      },
      {
        label: 'KPIs Cross-Modules',
        path: '/dashboard/cross-kpis',
        icon: PieChart,
        badge: 'KPIs',
        description: 'Indicateurs transverses performance globale',
        businessProcess: 'Performance globale'
      },
      {
        label: 'Activité Temps Réel',
        path: '/dashboard/real-time-activity',
        icon: Activity,
        badge: 'Temps Réel',
        description: 'Flux temps réel : navires, transport, stock, finance',
        businessProcess: 'Activité live'
      }
    ]
  },

  // ============================================================================
  // 🔧 ADDITIONAL BACKEND MODULES
  // ============================================================================
  'transport-avance': {
    key: 'transport-avance',
    title: '🚚 K-Transport Avancé',
    path: '/transport-avance/dashboard',
    icon: Truck,
    color: '#0891b2',
    glow: 'shadow-cyan-700/50 border-cyan-700/60',
    bgGradient: 'from-cyan-700 to-cyan-600',
    businessArea: 'Transport Avancé',
    processPhase: 'Phase 3: Transport Avancé',
    requiredRoles: ['ADMIN', 'TRANSPORT', 'DISPATCHER', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Transport Avancé', path: '/transport-avance/dashboard', icon: LayoutDashboard, badge: 'Advanced' },
      { label: 'Optimisation Routes', path: '/transport-avance/route-optimization', icon: Route },
      { label: 'Gestion Complexes', path: '/transport-avance/complex-loads', icon: Package },
      { label: 'Analytics Transport', path: '/transport-avance/analytics', icon: BarChart3 },
    ]
  },

  'transport-international': {
    key: 'transport-international',
    title: '🌍 Transport International',
    path: '/transport-international/dashboard',
    icon: Globe,
    color: '#0e7490',
    glow: 'shadow-cyan-800/50 border-cyan-800/60',
    bgGradient: 'from-cyan-800 to-cyan-700',
    businessArea: 'Transport International',
    processPhase: 'Phase 3: Transport International',
    requiredRoles: ['ADMIN', 'TRANSPORT', 'DISPATCHER', 'MANAGER'],
    subModules: [
      { label: 'Dashboard International', path: '/transport-international/dashboard', icon: LayoutDashboard, badge: 'Global' },
      { label: 'Fret Maritime', path: '/transport-international/maritime-freight', icon: Ship },
      { label: 'Fret Aérien', path: '/transport-international/air-freight', icon: Plane },
      { label: 'Douane International', path: '/transport-international/customs', icon: Landmark },
    ]
  },

  'magasin-avance': {
    key: 'magasin-avance',
    title: '🏭 K-Magasin Avancé',
    path: '/magasin-avance/dashboard',
    icon: Warehouse,
    color: '#d97706',
    glow: 'shadow-amber-700/50 border-amber-700/60',
    bgGradient: 'from-amber-700 to-amber-600',
    businessArea: 'Magasin Avancé',
    processPhase: 'Phase 4: Magasin Avancé',
    requiredRoles: ['ADMIN', 'MAGASIN', 'STOCK', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Magasin Avancé', path: '/magasin-avance/dashboard', icon: LayoutDashboard, badge: 'Advanced' },
      { label: 'Automatisation WMS', path: '/magasin-avance/automation', icon: Bot },
      { label: 'Cross-Docking', path: '/magasin-avance/cross-docking', icon: ArrowRightLeft },
      { label: 'Analytics Stock', path: '/magasin-avance/analytics', icon: BarChart3 },
    ]
  },

  'magasin-douane': {
    key: 'magasin-douane',
    title: '🛃 Magasin Douane',
    path: '/magasin-douane/dashboard',
    icon: Shield,
    color: '#b45309',
    glow: 'shadow-amber-800/50 border-amber-800/60',
    bgGradient: 'from-amber-800 to-amber-700',
    businessArea: 'Magasin Douane',
    processPhase: 'Phase 4: Magasin Douane',
    requiredRoles: ['ADMIN', 'MAGASIN', 'DOUANE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Magasin Douane', path: '/magasin-douane/dashboard', icon: LayoutDashboard, badge: 'Customs' },
      { label: 'Zone Douane', path: '/magasin-douane/customs-zone', icon: Shield },
      { label: 'Mainlevée', path: '/magasin-douane/release', icon: FileCheck },
      { label: 'Conformité', path: '/magasin-douane/compliance', icon: Landmark },
    ]
  },

  'acconage-avance': {
    key: 'acconage-avance',
    title: '🏗️ Acconage Avancé',
    path: '/acconage-avance/dashboard',
    icon: Building,
    color: '#2563eb',
    glow: 'shadow-blue-700/50 border-blue-700/60',
    bgGradient: 'from-blue-700 to-blue-600',
    businessArea: 'Acconage Avancé',
    processPhase: 'Phase 1: Acconage Avancé',
    requiredRoles: ['ADMIN', 'ACCONAGE', 'MARITIME', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Acconage Avancé', path: '/acconage-avance/dashboard', icon: LayoutDashboard, badge: 'Advanced' },
      { label: 'Planning Avancé', path: '/acconage-avance/advanced-planning', icon: Calendar },
      { label: 'Ressources Port', path: '/acconage-avance/port-resources', icon: Users },
      { label: 'Performance Quai', path: '/acconage-avance/quay-performance', icon: BarChart3 },
    ]
  },

  'transit-avance': {
    key: 'transit-avance',
    title: '📋 Transit Avancé',
    path: '/transit-avance/dashboard',
    icon: FileText,
    color: '#0369a1',
    glow: 'shadow-sky-700/50 border-sky-700/60',
    bgGradient: 'from-sky-700 to-sky-600',
    businessArea: 'Transit Avancé',
    processPhase: 'Phase 2: Transit Avancé',
    requiredRoles: ['ADMIN', 'TRANSIT', 'DOUANE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Transit Avancé', path: '/transit-avance/dashboard', icon: LayoutDashboard, badge: 'Advanced' },
      { label: 'Dossiers Complexes', path: '/transit-avance/complex-files', icon: FileText },
      { label: 'EDI Douane', path: '/transit-avance/edi-customs', icon: Wifi },
      { label: 'Tracking Transit', path: '/transit-avance/tracking', icon: MapPin },
    ]
  },

  'maintenance-gmao': {
    key: 'maintenance-gmao',
    title: '⚙️ Maintenance GMAO',
    path: '/maintenance-gmao/dashboard',
    icon: Wrench,
    color: '#ea580c',
    glow: 'shadow-orange-700/50 border-orange-700/60',
    bgGradient: 'from-orange-700 to-orange-600',
    businessArea: 'Maintenance GMAO',
    processPhase: 'Support: Maintenance GMAO',
    requiredRoles: ['ADMIN', 'MAINTENANCE', 'PARC', 'MANAGER'],
    subModules: [
      { label: 'Dashboard GMAO', path: '/maintenance-gmao/dashboard', icon: LayoutDashboard, badge: 'GMAO' },
      { label: 'Ordres Maintenance', path: '/maintenance-gmao/work-orders', icon: ClipboardList },
      { label: 'Préventif', path: '/maintenance-gmao/preventive', icon: Calendar },
      { label: 'Pièces Rechange', path: '/maintenance-gmao/spare-parts', icon: Package },
    ]
  },

  'shift-planning': {
    key: 'shift-planning',
    title: '📅 Planification Shifts',
    path: '/shift-planning/dashboard',
    icon: Calendar,
    color: '#ff6b6b',
    glow: 'shadow-red-500/50 border-red-500/60',
    bgGradient: 'from-red-500 to-rose-500',
    businessArea: 'Planification',
    processPhase: 'Support: Planification Shifts',
    requiredRoles: ['ADMIN', 'RH', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Shifts', path: '/shift-planning/dashboard', icon: LayoutDashboard, badge: 'Planning' },
      { label: 'Gestion Shifts', path: '/shift-planning/shifts', icon: Calendar },
      { label: 'Assignation Personnel', path: '/shift-planning/staff', icon: Users },
      { label: 'Performance Shifts', path: '/shift-planning/performance', icon: BarChart3 },
    ]
  },

  'port-pricing': {
    key: 'port-pricing',
    title: '💲 Tarification Portuaire',
    path: '/port-pricing/dashboard',
    icon: DollarSign,
    color: '#4ecdc4',
    glow: 'shadow-teal-500/50 border-teal-500/60',
    bgGradient: 'from-teal-500 to-cyan-500',
    businessArea: 'Tarification',
    processPhase: 'Support: Tarification Port',
    requiredRoles: ['ADMIN', 'FINANCE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Tarification', path: '/port-pricing/dashboard', icon: LayoutDashboard, badge: 'Pricing' },
      { label: 'Grilles Tarifaires', path: '/port-pricing/tariffs', icon: Tag },
      { label: 'Contrats', path: '/port-pricing/contracts', icon: FileText },
      { label: 'Facturation Auto', path: '/port-pricing/auto-billing', icon: Receipt },
    ]
  },

  'gps-tracking': {
    key: 'gps-tracking',
    title: '🛰️ Tracking GPS',
    path: '/gps-tracking/dashboard',
    icon: MapPin,
    color: '#45b7d1',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-500 to-blue-500',
    businessArea: 'Tracking GPS',
    processPhase: 'Phase 3: Tracking GPS',
    requiredRoles: ['ADMIN', 'TRANSPORT', 'DISPATCHER', 'MANAGER'],
    subModules: [
      { label: 'Dashboard GPS', path: '/gps-tracking/dashboard', icon: LayoutDashboard, badge: 'GPS' },
      { label: 'Carte Live', path: '/gps-tracking/live-map', icon: Map },
      { label: 'Historique', path: '/gps-tracking/history', icon: Clock },
      { label: 'Alertes GPS', path: '/gps-tracking/alerts', icon: Bell },
    ]
  },

  'real-customs': {
    key: 'real-customs',
    title: '🛃 Douane Temps Réel',
    path: '/real-customs/dashboard',
    icon: Landmark,
    color: '#96ceb4',
    glow: 'shadow-green-500/50 border-green-500/60',
    bgGradient: 'from-green-500 to-emerald-500',
    businessArea: 'Douane Temps Réel',
    processPhase: 'Phase 2: Douane Temps Réel',
    requiredRoles: ['ADMIN', 'DOUANE', 'TRANSIT', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Douane', path: '/real-customs/dashboard', icon: LayoutDashboard, badge: 'Real-time' },
      { label: 'Intégration SYDONIA', path: '/real-customs/sydonia', icon: Wifi },
      { label: 'Guichet Unique', path: '/real-customs/guichet-unique', icon: Monitor },
      { label: 'Conformité', path: '/real-customs/compliance', icon: Shield },
    ]
  },

  'port-incidents': {
    key: 'port-incidents',
    title: '⚠️ Incidents Port',
    path: '/port-incidents/dashboard',
    icon: AlertTriangle,
    color: '#ffeaa7',
    glow: 'shadow-yellow-500/50 border-yellow-500/60',
    bgGradient: 'from-yellow-500 to-amber-500',
    businessArea: 'Incidents Port',
    processPhase: 'Support: Incidents',
    requiredRoles: ['ADMIN', 'QHSE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Incidents', path: '/port-incidents/dashboard', icon: LayoutDashboard, badge: 'Incidents' },
      { label: 'Déclaration', path: '/port-incidents/report', icon: FileText },
      { label: 'Investigation', path: '/port-incidents/investigation', icon: Search },
      { label: 'Statistiques', path: '/port-incidents/stats', icon: BarChart3 },
    ]
  },

  'auto-invoicing': {
    key: 'auto-invoicing',
    title: '🧾 Facturation Auto',
    path: '/auto-invoicing/dashboard',
    icon: Receipt,
    color: '#dda0dd',
    glow: 'shadow-purple-500/50 border-purple-500/60',
    bgGradient: 'from-purple-500 to-pink-500',
    businessArea: 'Facturation Auto',
    processPhase: 'Phase 5: Facturation Auto',
    requiredRoles: ['ADMIN', 'FINANCE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Facturation', path: '/auto-invoicing/dashboard', icon: LayoutDashboard, badge: 'Auto' },
      { label: 'Règles Facturation', path: '/auto-invoicing/rules', icon: Settings },
      { label: 'Factures Générées', path: '/auto-invoicing/invoices', icon: FileText },
      { label: 'Relances Auto', path: '/auto-invoicing/reminders', icon: Bell },
    ]
  },

  'port-performance': {
    key: 'port-performance',
    title: '📈 Performance Port',
    path: '/port-performance/dashboard',
    icon: BarChart3,
    color: '#98d8c8',
    glow: 'shadow-green-500/50 border-green-500/60',
    bgGradient: 'from-green-500 to-teal-500',
    businessArea: 'Performance Port',
    processPhase: 'Support: Performance',
    requiredRoles: ['ADMIN', 'MANAGER', 'AUDITOR'],
    subModules: [
      { label: 'Dashboard Performance', path: '/port-performance/dashboard', icon: LayoutDashboard, badge: 'KPIs' },
      { label: 'KPIs Port', path: '/port-performance/kpis', icon: TrendingUp },
      { label: 'Benchmarking', path: '/port-performance/benchmarking', icon: BarChart3 },
      { label: 'Rapports', path: '/port-performance/reports', icon: FileText },
    ]
  },

  'notification-system': {
    key: 'notification-system',
    title: '🔔 Système Notifications',
    path: '/notification-system/dashboard',
    icon: Bell,
    color: '#f7dc6f',
    glow: 'shadow-yellow-500/50 border-yellow-500/60',
    bgGradient: 'from-yellow-500 to-amber-500',
    businessArea: 'Notifications',
    processPhase: 'Support: Notifications',
    requiredRoles: ['ADMIN', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Notifications', path: '/notification-system/dashboard', icon: LayoutDashboard, badge: 'System' },
      { label: 'Templates', path: '/notification-system/templates', icon: FileText },
      { label: 'Canaux', path: '/notification-system/channels', icon: Radio },
      { label: 'Historique', path: '/notification-system/history', icon: Clock },
    ]
  },

  'container-lifecycle': {
    key: 'container-lifecycle',
    title: '📦 Cycle Conteneurs',
    path: '/container-lifecycle/dashboard',
    icon: Package,
    color: '#bb8fce',
    glow: 'shadow-purple-500/50 border-purple-500/60',
    bgGradient: 'from-purple-500 to-violet-500',
    businessArea: 'Cycle Conteneurs',
    processPhase: 'Support: Conteneurs',
    requiredRoles: ['ADMIN', 'MAGASIN', 'TRANSIT', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Conteneurs', path: '/container-lifecycle/dashboard', icon: LayoutDashboard, badge: 'Cycle' },
      { label: 'Tracking Conteneurs', path: '/container-lifecycle/tracking', icon: MapPin },
      { label: 'Maintenance', path: '/container-lifecycle/maintenance', icon: Wrench },
      { label: 'Inspection', path: '/container-lifecycle/inspection', icon: Shield },
    ]
  },

  'partner-api': {
    key: 'partner-api',
    title: '🔌 API Partenaires',
    path: '/partner-api/dashboard',
    icon: Wifi,
    color: '#85c1e9',
    glow: 'shadow-blue-500/50 border-blue-500/60',
    bgGradient: 'from-blue-500 to-sky-500',
    businessArea: 'API Partenaires',
    processPhase: 'Support: API',
    requiredRoles: ['ADMIN', 'INTEGRATION', 'MANAGER'],
    subModules: [
      { label: 'Dashboard API', path: '/partner-api/dashboard', icon: LayoutDashboard, badge: 'API' },
      { label: 'Clés API', path: '/partner-api/keys', icon: Key },
      { label: 'Webhooks', path: '/partner-api/webhooks', icon: Radio },
      { label: 'Documentation', path: '/partner-api/docs', icon: BookOpen },
    ]
  },

  'bill-of-loading': {
    key: 'bill-of-loading',
    title: '📄 Connaissement',
    path: '/bill-of-loading/dashboard',
    icon: FileText,
    color: '#5dade2',
    glow: 'shadow-blue-500/50 border-blue-500/60',
    bgGradient: 'from-blue-500 to-cyan-500',
    businessArea: 'Connaissement',
    processPhase: 'Phase 1: Connaissement',
    requiredRoles: ['ADMIN', 'MARITIME', 'TRANSIT', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Connaissement', path: '/bill-of-loading/dashboard', icon: LayoutDashboard, badge: 'BL' },
      { label: 'Création BL', path: '/bill-of-loading/create', icon: FilePlus },
      { label: 'Validation BL', path: '/bill-of-loading/validate', icon: FileCheck },
      { label: 'Historique BL', path: '/bill-of-loading/history', icon: Clock },
    ]
  },

  documents: {
    key: 'documents',
    title: '📁 Documents',
    path: '/documents/dashboard',
    icon: FileText,
    color: '#95a5a6',
    glow: 'shadow-gray-500/50 border-gray-500/60',
    bgGradient: 'from-gray-500 to-slate-500',
    businessArea: 'Documents',
    processPhase: 'Support: Documents',
    requiredRoles: ['ADMIN', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Documents', path: '/documents/dashboard', icon: LayoutDashboard, badge: 'Docs' },
      { label: 'Gestion Documents', path: '/documents/management', icon: Folder },
      { label: 'Archives', path: '/documents/archives', icon: Archive },
      { label: 'Partage', path: '/documents/sharing', icon: Share },
    ]
  },

  alerts: {
    key: 'alerts',
    title: '🚨 Alertes',
    path: '/alerts/dashboard',
    icon: AlertTriangle,
    color: '#e74c3c',
    glow: 'shadow-red-500/50 border-red-500/60',
    bgGradient: 'from-red-500 to-rose-500',
    businessArea: 'Alertes',
    processPhase: 'Support: Alertes',
    requiredRoles: ['ADMIN', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Alertes', path: '/alerts/dashboard', icon: LayoutDashboard, badge: 'Alerts' },
      { label: 'Configuration Alertes', path: '/alerts/configuration', icon: Settings },
      { label: 'Historique Alertes', path: '/alerts/history', icon: Clock },
      { label: 'Règles Alertes', path: '/alerts/rules', icon: Sliders },
    ]
  },

  notifications: {
    key: 'notifications',
    title: '📢 Notifications',
    path: '/notifications/dashboard',
    icon: Bell,
    color: '#f39c12',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-500 to-amber-500',
    businessArea: 'Notifications',
    processPhase: 'Support: Notifications',
    requiredRoles: ['ADMIN', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Notifications', path: '/notifications/dashboard', icon: LayoutDashboard, badge: 'Notify' },
      { label: 'Centre Notifications', path: '/notifications/center', icon: Bell },
      { label: 'Préférences', path: '/notifications/preferences', icon: Settings },
      { label: 'Historique', path: '/notifications/history', icon: Clock },
    ]
  },

  acquisition: {
    key: 'acquisition',
    title: '🛍️ Acquisition',
    path: '/acquisition/dashboard',
    icon: ShoppingCart,
    color: '#8e44ad',
    glow: 'shadow-purple-500/50 border-purple-500/60',
    bgGradient: 'from-purple-500 to-violet-500',
    businessArea: 'Acquisition',
    processPhase: 'Support: Acquisition',
    requiredRoles: ['ADMIN', 'FINANCE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Acquisition', path: '/acquisition/dashboard', icon: LayoutDashboard, badge: 'Acquisition' },
      { label: 'Demandes Achat', path: '/acquisition/requests', icon: FileText },
      { label: 'Validation', path: '/acquisition/validation', icon: FileCheck },
      { label: 'Analytics', path: '/acquisition/analytics', icon: BarChart3 },
    ]
  },

  gateway: {
    key: 'gateway',
    title: '🌐 Passerelle API',
    path: '/gateway/dashboard',
    icon: Wifi,
    color: '#34495e',
    glow: 'shadow-slate-500/50 border-slate-500/60',
    bgGradient: 'from-slate-500 to-gray-500',
    businessArea: 'Passerelle API',
    processPhase: 'Support: API Gateway',
    requiredRoles: ['ADMIN', 'INTEGRATION', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Gateway', path: '/gateway/dashboard', icon: LayoutDashboard, badge: 'Gateway' },
      { label: 'Configuration', path: '/gateway/configuration', icon: Settings },
      { label: 'Monitoring', path: '/gateway/monitoring', icon: Activity },
      { label: 'Sécurité', path: '/gateway/security', icon: Shield },
    ]
  },

  goods: {
    key: 'goods',
    title: '🚢 Déclaration Fret',
    path: '/goods/dashboard',
    icon: Ship,
    color: '#16a085',
    glow: 'shadow-teal-500/50 border-teal-500/60',
    bgGradient: 'from-teal-500 to-green-500',
    businessArea: 'Déclaration Fret',
    processPhase: 'Phase 1: Déclaration Fret',
    requiredRoles: ['ADMIN', 'MARITIME', 'TRANSIT', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Fret', path: '/goods/dashboard', icon: LayoutDashboard, badge: 'Fret' },
      { label: 'Déclarations', path: '/goods/declarations', icon: FileText },
      { label: 'Validation', path: '/goods/validation', icon: FileCheck },
      { label: 'Tracking', path: '/goods/tracking', icon: MapPin },
    ]
  },

  suppliers: {
    key: 'suppliers',
    title: '🏭 Fournisseurs',
    path: '/suppliers/dashboard',
    icon: Building,
    color: '#27ae60',
    glow: 'shadow-green-500/50 border-green-500/60',
    bgGradient: 'from-green-500 to-emerald-500',
    businessArea: 'Fournisseurs',
    processPhase: 'Support: Fournisseurs',
    requiredRoles: ['ADMIN', 'FINANCE', 'PROCUREMENT', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Fournisseurs', path: '/suppliers/dashboard', icon: LayoutDashboard, badge: 'Suppliers' },
      { label: 'Annuaire', path: '/suppliers/directory', icon: Users },
      { label: 'Évaluation', path: '/suppliers/evaluation', icon: Star },
      { label: 'Contrats', path: '/suppliers/contracts', icon: FileText },
    ]
  },

  tenant: {
    key: 'tenant',
    title: '🏢 Tenant Multi-locataire',
    path: '/tenant/dashboard',
    icon: Building,
    color: '#2e86c1',
    glow: 'shadow-blue-500/50 border-blue-500/60',
    bgGradient: 'from-blue-500 to-sky-500',
    businessArea: 'Multi-tenant',
    processPhase: 'Support: Multi-tenant',
    requiredRoles: ['SUPER_ADMIN', 'ADMIN'],
    subModules: [
      { label: 'Dashboard Tenant', path: '/tenant/dashboard', icon: LayoutDashboard, badge: 'Tenant' },
      { label: 'Gestion Tenants', path: '/tenant/management', icon: Building },
      { label: 'Configuration', path: '/tenant/configuration', icon: Settings },
      { label: 'Billing', path: '/tenant/billing', icon: CreditCard },
    ]
  },

  tiers: {
    key: 'tiers',
    title: '👥 Tiers & Partenaires',
    path: '/tiers/dashboard',
    icon: Users,
    color: '#884ea0',
    glow: 'shadow-purple-500/50 border-purple-500/60',
    bgGradient: 'from-purple-500 to-violet-500',
    businessArea: 'Tiers',
    processPhase: 'Support: Tiers',
    requiredRoles: ['ADMIN', 'FINANCE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Tiers', path: '/tiers/dashboard', icon: LayoutDashboard, badge: 'Tiers' },
      { label: 'Clients', path: '/tiers/clients', icon: UserCheck },
      { label: 'Partenaires', path: '/tiers/partners', icon: Handshake },
      { label: 'Analytics', path: '/tiers/analytics', icon: BarChart3 },
    ]
  },

  transactions: {
    key: 'transactions',
    title: '💱 Transactions',
    path: '/transactions/dashboard',
    icon: ArrowRightLeft,
    color: '#d35400',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-500 to-red-500',
    businessArea: 'Transactions',
    processPhase: 'Support: Transactions',
    requiredRoles: ['ADMIN', 'FINANCE', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Transactions', path: '/transactions/dashboard', icon: LayoutDashboard, badge: 'Transactions' },
      { label: 'Historique', path: '/transactions/history', icon: Clock },
      { label: 'Réconciliation', path: '/transactions/reconciliation', icon: FileCheck },
      { label: 'Analytics', path: '/transactions/analytics', icon: BarChart3 },
    ]
  },

  role: {
    key: 'role',
    title: '👤 Gestion Rôles',
    path: '/role/dashboard',
    icon: Shield,
    color: '#7f8c8d',
    glow: 'shadow-gray-500/50 border-gray-500/60',
    bgGradient: 'from-gray-500 to-slate-500',
    businessArea: 'Rôles',
    processPhase: 'Support: Rôles',
    requiredRoles: ['ADMIN', 'SUPER_ADMIN'],
    subModules: [
      { label: 'Dashboard Rôles', path: '/role/dashboard', icon: LayoutDashboard, badge: 'RBAC' },
      { label: 'Définition Rôles', path: '/role/definition', icon: Shield },
      { label: 'Permissions', path: '/role/permissions', icon: Key },
      { label: 'Assignation', path: '/role/assignment', icon: UserCheck },
    ]
  },

  'reception-mag3': {
    key: 'reception-mag3',
    title: '📥 Réception MAG3',
    path: '/reception-mag3/dashboard',
    icon: Package,
    color: '#f39c12',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-500 to-amber-500',
    businessArea: 'Réception MAG3',
    processPhase: 'Phase 4: Réception',
    requiredRoles: ['ADMIN', 'MAGASIN', 'STOCK', 'MANAGER'],
    subModules: [
      { label: 'Dashboard Réception', path: '/reception-mag3/dashboard', icon: LayoutDashboard, badge: 'MAG3' },
      { label: 'Réception Marchandises', path: '/reception-mag3/reception', icon: Package },
      { label: 'Contrôle Qualité', path: '/reception-mag3/quality-control', icon: Shield },
      { label: 'Mise en Stock', path: '/reception-mag3/stocking', icon: Warehouse },
    ]
  },

  'removal-slip': {
    key: 'removal-slip',
    title: '📤 Bons Enlèvement',
    path: '/removal-slip/dashboard',
    icon: FileText,
    color: '#e67e22',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-500 to-red-500',
    businessArea: 'Bons Enlèvement',
    processPhase: 'Phase 4: Expédition',
    requiredRoles: ['ADMIN', 'MAGASIN', 'STOCK', 'MANAGER'],
    subModules: [
      { label: 'Dashboard BL', path: '/removal-slip/dashboard', icon: LayoutDashboard, badge: 'BL' },
      { label: 'Création BL', path: '/removal-slip/create', icon: FilePlus },
      { label: 'Validation BL', path: '/removal-slip/validate', icon: FileCheck },
      { label: 'Historique BL', path: '/removal-slip/history', icon: Clock },
    ]
  },

  reporting: {
    key: 'reporting',
    title: '📊 Rapports',
    path: '/reporting/dashboard',
    icon: BarChart3,
    color: '#9b59b6',
    glow: 'shadow-purple-500/50 border-purple-500/60',
    bgGradient: 'from-purple-500 to-violet-500',
    businessArea: 'Rapports',
    processPhase: 'Support: Rapports',
    requiredRoles: ['ADMIN', 'MANAGER', 'AUDITOR'],
    subModules: [
      { label: 'Dashboard Rapports', path: '/reporting/dashboard', icon: LayoutDashboard, badge: 'Reports' },
      { label: 'Rapports Standard', path: '/reporting/standard', icon: FileText },
      { label: 'Rapports Personnalisés', path: '/reporting/custom', icon: Settings },
      { label: 'Exports', path: '/reporting/exports', icon: Download },
    ]
  },

  'public-api': {
    key: 'public-api',
    title: '🌐 API Publique',
    path: '/public-api/dashboard',
    icon: Wifi,
    color: '#1abc9c',
    glow: 'shadow-teal-500/50 border-teal-500/60',
    bgGradient: 'from-teal-500 to-green-500',
    businessArea: 'API Publique',
    processPhase: 'Support: API Publique',
    requiredRoles: ['ADMIN', 'INTEGRATION', 'MANAGER'],
    subModules: [
      { label: 'Dashboard API Publique', path: '/public-api/dashboard', icon: LayoutDashboard, badge: 'Public' },
      { label: 'Documentation', path: '/public-api/docs', icon: BookOpen },
      { label: 'Clés API', path: '/public-api/keys', icon: Key },
      { label: 'Monitoring', path: '/public-api/monitoring', icon: Activity },
    ]
  },
};

// ============================================================================
// FONCTIONS UTILITAIRES & FILTRAGE PAR RÔLE
// ============================================================================

/**
 * Retourne la navigation filtrée selon les rôles et modules autorisés de l'utilisateur
 */
export function getFilteredNavigationForUser(
  user: { 
    roles?: string[]; 
    modulesAllowed?: string[];
    tenantId?: string;
    permissions?: string[];
  } | null
): ModuleNavConfig[] {
  if (!user) return Object.values(NAVIGATION_REGISTRY);

  const userRoles = (user.roles || []).map(r => r.toUpperCase());
  const isAdmin = userRoles.includes('ADMIN') || userRoles.includes('SUPER_ADMIN');
  const userModules = user.modulesAllowed || [];
  const userPermissions = user.permissions || [];

  return Object.values(NAVIGATION_REGISTRY).map(moduleConfig => {
    // Super Admin a accès à tout
    if (userRoles.includes('SUPER_ADMIN')) return moduleConfig;

    // Vérifier si le module est autorisé
    const isModuleAllowed =
      moduleConfig.key === 'dashboard' ||
      isAdmin ||
      userModules.includes(moduleConfig.key) ||
      (moduleConfig.requiredRoles?.some(role => userRoles.includes(role)) ?? false);

    if (!isModuleAllowed) return null;

    // Filtrer les sous-modules selon les rôles/permissions
    const filteredSubModules = moduleConfig.subModules.filter(sub => {
      if (!sub.requiredRoles || sub.requiredRoles.length === 0) return true;
      return sub.requiredRoles.some(r => 
        userRoles.includes(r.toUpperCase()) || 
        userPermissions.includes(r)
      );
    });

    return { ...moduleConfig, subModules: filteredSubModules };
  }).filter(Boolean) as ModuleNavConfig[];
}

/**
 * Retourne les modules par phase du processus navire → client
 */
export function getModulesByProcessPhase(): Record<string, ModuleNavConfig[]> {
  const modules = Object.values(NAVIGATION_REGISTRY);
  
  return {
    'Phase 1 - Arrivée Navire': modules.filter(m => m.processPhase?.includes('Phase 1')),
    'Phase 2 - Dédouanement': modules.filter(m => m.processPhase?.includes('Phase 2')),
    'Phase 3 - Transport': modules.filter(m => m.processPhase?.includes('Phase 3')),
    'Phase 4 - Stock & Préparation': modules.filter(m => m.processPhase?.includes('Phase 4')),
    'Phase 5 - Facturation': modules.filter(m => m.processPhase?.includes('Phase 5')),
    'Phase 6 - Comptabilité': modules.filter(m => m.processPhase?.includes('Phase 6')),
    'Support - Modules Transverses': modules.filter(m => m.processPhase?.includes('Support')),
  };
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

/**
 * Statistiques de la navigation
 */
export function getNavigationStats() {
  const modules = Object.values(NAVIGATION_REGISTRY);
  const totalSubModules = modules.reduce((acc, module) => acc + module.subModules.length, 0);
  const ohadaModules = modules.filter(m => m.subModules.some(sub => sub.isOhadaCompliant)).length;
  const cemacModules = modules.filter(m => m.subModules.some(sub => sub.isCemacSpecific)).length;

  return {
    totalModules: modules.length,
    totalSubModules,
    averageSubModulesPerModule: Math.round(totalSubModules / modules.length),
    ohadaCompliantModules: ohadaModules,
    cemacSpecificModules: cemacModules,
    businessAreas: [...new Set(modules.map(m => m.businessArea))].length
  };
}