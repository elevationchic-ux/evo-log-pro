'use client';

/**
 * Navigation Registry for EVO-LOG
 * Central configuration for all modules with colors, gradients, submodules, and access control
 * Pattern: one module = one color identity (inspired by kamlog-frontend)
 */

export interface SubModule {
  id: string;
  name: string;
  path: string;
  icon?: string;
  description?: string;
  comingSoon?: boolean;
}

export interface NavigationModule {
  id: string;
  name: string;
  path: string;
  icon: string;
  color: string;
  gradient: string;
  category: string;
  description?: string;
  roles?: string[];
  subModules?: SubModule[];
  firstPage?: string; // First charging page (CADC pattern)
  comingSoon?: boolean;
}

// =====================================================
// NAVIGATION REGISTRY - All EVO-LOG Modules
// =====================================================

export const NAVIGATION_MODULES: NavigationModule[] = [
  // ───────────────────────────────────────────────────
  // OPERATIONS
  // ───────────────────────────────────────────────────
  {
    id: 'dashboard', name: 'Dashboard', path: '/dashboard', icon: '📊',
    color: '#3B82F6', gradient: 'linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%)',
    category: 'Operations', description: 'Tableau de bord principal',
    firstPage: '/dashboard',
    subModules: [
      { id: 'overview', name: 'Vue d\'ensemble', path: '/dashboard' },
      { id: 'analytics', name: 'Analytique', path: '/dashboard/analytics' },
    ],
  },
  {
    id: 'transport', name: 'Transport', path: '/transport', icon: '🚚',
    color: '#F59E0B', gradient: 'linear-gradient(135deg, #F59E0B 0%, #B45309 100%)',
    category: 'Operations', description: 'Gestion du transport',
    firstPage: '/transport/control',
    subModules: [
      { id: 'control', name: 'Poste de Contrôle', path: '/transport/control' },
      { id: 'flotte', name: 'Flotte', path: '/transport/flotte' },
      { id: 'planning', name: 'Planning', path: '/transport/planning' },
      { id: 'missions', name: 'Missions', path: '/transport/missions' },
      { id: 'dispatch', name: 'Dispatch', path: '/transport/dispatch' },
      { id: 'drivers', name: 'Chauffeurs', path: '/transport/drivers' },
      { id: 'cards', name: 'Carte Live', path: '/transport/carte-live' },
    ],
  },
  {
    id: 'acconage', name: 'Acconage', path: '/acconage', icon: '🚢',
    color: '#10B981', gradient: 'linear-gradient(135deg, #10B981 0%, #047857 100%)',
    category: 'Operations', description: 'Gestion des opérations d\'acconage',
    firstPage: '/acconage',
    subModules: [
      { id: 'list', name: 'Liste', path: '/acconage' },
      { id: 'create', name: 'Créer', path: '/acconage/create' },
    ],
  },
  {
    id: 'transit', name: 'Transit', path: '/transit', icon: '📋',
    color: '#8B5CF6', gradient: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
    category: 'Operations', description: 'Gestion du transit et douanes',
    firstPage: '/transit',
  },
  {
    id: 'port-operations', name: 'Port Operations', path: '/port-operations', icon: '�',
    color: '#0EA5E9', gradient: 'linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%)',
    category: 'Operations', description: 'Opérations portuaires',
    firstPage: '/port-operations',
  },
  {
    id: 'magasin', name: 'Magasin', path: '/magasin', icon: '📦',
    color: '#EC4899', gradient: 'linear-gradient(135deg, #EC4899 0%, #BE185D 100%)',
    category: 'Operations', description: 'Gestion des stocks et entrepôts',
    firstPage: '/magasin',
  },
  {
    id: 'parc', name: 'Parc', path: '/parc', icon: '🚗',
    color: '#14B8A6', gradient: 'linear-gradient(135deg, #14B8A6 0%, #0F766E 100%)',
    category: 'Operations', description: 'Gestion du parc véhicules',
    firstPage: '/parc',
  },
  {
    id: 'tracking', name: 'Tracking', path: '/tracking', icon: '📍',
    color: '#F97316', gradient: 'linear-gradient(135deg, #F97316 0%, #C2410C 100%)',
    category: 'Operations', description: 'Suivi en temps réel',
    firstPage: '/tracking',
  },
  {
    id: 'fuel-guard', name: 'Fuel Guard', path: '/fuel-guard', icon: '⛽',
    color: '#EF4444', gradient: 'linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)',
    category: 'Operations', description: 'Gestion carburant',
    firstPage: '/fuel-guard',
  },
  {
    id: 'maintenance', name: 'Maintenance', path: '/maintenance', icon: '🔧',
    color: '#64748B', gradient: 'linear-gradient(135deg, #64748B 0%, #334155 100%)',
    category: 'Operations', description: 'Maintenance des équipements',
    firstPage: '/maintenance',
  },
  {
    id: 'qhse', name: 'QHSE', path: '/qhse', icon: '🛡️',
    color: '#84CC16', gradient: 'linear-gradient(135deg, #84CC16 0%, #4D7C0F 100%)',
    category: 'Operations', description: 'Qualité, Hygiène, Sécurité, Environnement',
    firstPage: '/qhse',
  },
  {
    id: 'compliance', name: 'Compliance', path: '/compliance', icon: '⚖️',
    color: '#A855F7', gradient: 'linear-gradient(135deg, #A855F7 0%, #7E22CE 100%)',
    category: 'Operations', description: 'Conformité réglementaire',
    firstPage: '/compliance',
  },
  {
    id: 'reports', name: 'Rapports', path: '/reports', icon: '📈',
    color: '#0EA5E9', gradient: 'linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%)',
    category: 'Operations', description: 'Rapports et analytiques',
    firstPage: '/reports',
  },

  // ───────────────────────────────────────────────────
  // SUPPLY CHAIN
  // ───────────────────────────────────────────────────
  {
    id: 'purchase', name: 'Achat', path: '/purchase', icon: '�',
    color: '#6366F1', gradient: 'linear-gradient(135deg, #6366F1 0%, #4338CA 100%)',
    category: 'Supply', description: 'Gestion des achats',
    firstPage: '/purchase',
  },
  {
    id: 'procurement', name: 'Approvisionnement', path: '/procurement', icon: '📥',
    color: '#8B5CF6', gradient: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
    category: 'Supply', description: 'Chaîne d\'approvisionnement',
    firstPage: '/procurement',
  },
  {
    id: 'fournisseurs', name: 'Fournisseurs', path: '/fournisseurs', icon: '🤝',
    color: '#D946EF', gradient: 'linear-gradient(135deg, #D946EF 0%, #A21CAF 100%)',
    category: 'Supply', description: 'Gestion des fournisseurs',
    firstPage: '/fournisseurs',
  },
  {
    id: 'suppliers', name: 'Suppliers', path: '/suppliers', icon: '🏪',
    color: '#EC4899', gradient: 'linear-gradient(135deg, #EC4899 0%, #BE185D 100%)',
    category: 'Supply', description: 'Partenaires fournisseurs',
    firstPage: '/suppliers',
  },
  {
    id: 'tiers', name: 'Tiers', path: '/tiers', icon: '👥',
    color: '#14B8A6', gradient: 'linear-gradient(135deg, #14B8A6 0%, #0F766E 100%)',
    category: 'Supply', description: 'Clients et partenaires',
    firstPage: '/tiers',
  },
  {
    id: 'cotations', name: 'Cotations', path: '/cotations', icon: '💰',
    color: '#38BDF8', gradient: 'linear-gradient(135deg, #38BDF8 0%, #0284C7 100%)',
    category: 'Supply', description: 'Devis et cotations',
    firstPage: '/cotations',
  },

  // ───────────────────────────────────────────────────
  // FINANCE
  // ───────────────────────────────────────────────────
  {
    id: 'finance', name: 'Finance', path: '/finance', icon: '💰',
    color: '#22C55E', gradient: 'linear-gradient(135deg, #22C55E 0%, #15803D 100%)',
    category: 'Finance', description: 'Gestion financière',
    firstPage: '/finance',
  },
  {
    id: 'paiement-local', name: 'Paiements Locaux', path: '/paiement-local', icon: '💳',
    color: '#06B6D4', gradient: 'linear-gradient(135deg, #06B6D4 0%, #0E7490 100%)',
    category: 'Finance', description: 'Orange Money, MTN, Banques',
    firstPage: '/paiement-local',
  },
  {
    id: 'fiscalite-cameroun', name: 'Fiscalité Cameroun', path: '/fiscalite-cameroun', icon: '🧾',
    color: '#96CEB4', gradient: 'linear-gradient(135deg, #2DD4BF 0%, #0F766E 100%)',
    category: 'Finance', description: 'IRPP, IS, TCF, TDR, OHADA',
    firstPage: '/fiscalite-cameroun',
  },

  // ───────────────────────────────────────────────────
  // CAMEROON/CEMAC
  // ───────────────────────────────────────────────────
  {
    id: 'integration-cameroun', name: 'Intégration Cameroun', path: '/integration-cameroun', icon: '🇨🇲',
    color: '#FF6B6B', gradient: 'linear-gradient(135deg, #FF6B6B 0%, #DC2626 100%)',
    category: 'Cameroun', description: 'BSC, CSC, SYGED, APE',
    firstPage: '/integration-cameroun',
  },

  // ───────────────────────────────────────────────────
  // HR
  // ───────────────────────────────────────────────────
  {
    id: 'rh', name: 'Ressources Humaines', path: '/rh', icon: '👤',
    color: '#8B5CF6', gradient: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
    category: 'RH', description: 'Gestion des ressources humaines',
    firstPage: '/rh',
  },

  // ───────────────────────────────────────────────────
  // ADMIN
  // ───────────────────────────────────────────────────
  {
    id: 'admin', name: 'Admin', path: '/admin', icon: '⚙️',
    color: '#374151', gradient: 'linear-gradient(135deg, #374151 0%, #111827 100%)',
    category: 'Admin', description: 'Administration du système',
    firstPage: '/admin',
  },
  {
    id: 'integration', name: 'Integration', path: '/integration', icon: '🔗',
    color: '#0EA5E9', gradient: 'linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%)',
    category: 'Admin', description: 'Intégration API et systèmes',
    firstPage: '/integration',
  },
  {
    id: 'documents', name: 'Documents', path: '/documents', icon: '�',
    color: '#6366F1', gradient: 'linear-gradient(135deg, #6366F1 0%, #4338CA 100%)',
    category: 'Admin', description: 'Gestion documentaire',
    firstPage: '/documents',
  },
  {
    id: 'notifications', name: 'Notifications', path: '/notifications', icon: '🔔',
    color: '#F59E0B', gradient: 'linear-gradient(135deg, #F59E0B 0%, #B45309 100%)',
    category: 'Admin', description: 'Centre de notifications',
    firstPage: '/notifications',
  },
  {
    id: 'support', name: 'Support', path: '/support', icon: '🎧',
    color: '#10B981', gradient: 'linear-gradient(135deg, #10B981 0%, #047857 100%)',
    category: 'Admin', description: 'Support et assistance',
    firstPage: '/support',
  },
  {
    id: 'settings', name: 'Paramètres', path: '/settings', icon: '⚙️',
    color: '#64748B', gradient: 'linear-gradient(135deg, #64748B 0%, #334155 100%)',
    category: 'Admin', description: 'Configuration du système',
    firstPage: '/settings',
  },
  {
    id: 'security', name: 'Sécurité', path: '/security', icon: '�',
    color: '#EF4444', gradient: 'linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)',
    category: 'Admin', description: 'Sécurité et access control',
    firstPage: '/security',
  },
  {
    id: 'master-data', name: 'Données Masters', path: '/master-data', icon: '�️',
    color: '#3B82F6', gradient: 'linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%)',
    category: 'Admin', description: 'Données de référence',
    firstPage: '/master-data',
  },
  {
    id: 'company', name: 'Entreprise', path: '/company', icon: '🏢',
    color: '#8B5CF6', gradient: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
    category: 'Admin', description: 'Informations entreprise',
    firstPage: '/company',
  },
  {
    id: 'client-portal', name: 'Client Portal', path: '/client-portal', icon: '🌐',
    color: '#7C3AED', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    category: 'Support', description: 'Portail clients externes',
    firstPage: '/client-portal',
  },
];

// Helper functions
export const getModuleById = (id: string): NavigationModule | undefined =>
  NAVIGATION_MODULES.find(m => m.id === id);

export const getModuleByPath = (path: string): NavigationModule | undefined =>
  NAVIGATION_MODULES.find(m => m.path === path || path.startsWith(m.path + '/'));

export const getModulesByCategory = (category: string): NavigationModule[] =>
  NAVIGATION_MODULES.filter(m => m.category === category);

export const getCategories = (): string[] =>
  [...new Set(NAVIGATION_MODULES.map(m => m.category))];

export const getAllCategories = (): string[] =>
  [...new Set(NAVIGATION_MODULES.map(m => m.category))];

export const getFirstPage = (moduleId: string): string | undefined =>
  getModuleById(moduleId)?.firstPage;

export const getModuleColor = (module: string | undefined): string => {
  if (!module) return '#3B82F6';
  const mod = NAVIGATION_MODULES.find(m => m.id === module || m.path === module);
  return mod?.color || '#3B82F6';
};

export const getModuleGradient = (module: string | undefined): string => {
  if (!module) return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  const mod = NAVIGATION_MODULES.find(m => m.id === module || m.path === module);
  return mod?.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
};

