'use client';

import { useMemo } from 'react';
import { usePathname } from 'next/navigation';
import { MODULE_PALETTE, getModulePalette } from '@/config/modulePalette';

const VALID_MODULES = [
  // Modules principaux de l'architecture ERP portuaire
  'dashboard', 'port-operations', 'transit-douane', 'transport-flotte', 
  'magasin-stock', 'finance-ohada', 'comptabilite-ohada', 'parc-vehicules',
  'qhse-securite', 'rh-personnel', 'client-b2b', 'admin-tenant', 'reports-bi',
  
  // Legacy modules (compatibilité transition)
  'admin', 'master-data', 'transport', 'finance', 'magasin', 'parc', 'rh', 
  'acconage', 'qhse', 'transit', 'maintenance', 'client-portal', 'cotations',
  'tracking', 'fuel-guard', 'procurement', 'compliance', 'bi', 'settings',
  'integration-cameroun', 'fiscalite-cameroun', 'paiement-local', 'fournisseurs',
  'security', 'reports', 'documents', 'notifications', 'support',
] as const;

export type ModuleType = typeof VALID_MODULES[number] | string;

interface ModuleThemeConfig {
  /** Tailwind class for the main content background */
  mainBackground: string;
  /** CSS utility class for the module badge in the header (uses CSS variables) */
  headerClasses: string;
  sidebar: {
    activeAccent: string;
    activeBgSubtle: string;
    brandIconBg: string;
  };
}

const MODULE_THEME_CONFIG: Record<string, ModuleThemeConfig> = {
  // ═══════════════════════════════════════════════════════════════════════════════
  // MODULES PRINCIPAUX - ARCHITECTURE ERP PORTUAIRE COMPLÈTE
  // ═══════════════════════════════════════════════════════════════════════════════

  // Dashboard global
  dashboard: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-dashboard',
    sidebar: { activeAccent: 'text-indigo-400 border-indigo-400', activeBgSubtle: 'bg-indigo-500/10', brandIconBg: 'bg-indigo-600' },
  },

  // 1. Port Operations (🚢 Phase 1: Arrivée Navire)
  'port-operations': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-port-operations',
    sidebar: { activeAccent: 'text-sky-400 border-sky-400', activeBgSubtle: 'bg-sky-500/10', brandIconBg: 'bg-sky-600' },
  },

  // 2. Transit & Douane (🛃 Phase 2: Dédouanement)
  'transit-douane': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-transit-douane',
    sidebar: { activeAccent: 'text-violet-400 border-violet-400', activeBgSubtle: 'bg-violet-500/10', brandIconBg: 'bg-violet-600' },
  },

  // 3. Transport & Flotte (🚛 Phase 3: Transport Client)
  'transport-flotte': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-transport-flotte',
    sidebar: { activeAccent: 'text-cyan-400 border-cyan-400', activeBgSubtle: 'bg-cyan-500/10', brandIconBg: 'bg-cyan-600' },
  },

  // 4. Magasin & Stock WMS (📦 Phase 4: Stock & Préparation)
  'magasin-stock': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-magasin-stock',
    sidebar: { activeAccent: 'text-amber-400 border-amber-400', activeBgSubtle: 'bg-amber-500/10', brandIconBg: 'bg-amber-600' },
  },

  // 5. Finance OHADA (💰 Phase 5: Facturation)
  'finance-ohada': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-finance-ohada',
    sidebar: { activeAccent: 'text-emerald-400 border-emerald-400', activeBgSubtle: 'bg-emerald-500/10', brandIconBg: 'bg-emerald-600' },
  },

  // 6. Comptabilité OHADA (📚 Phase 6: États Financiers)
  'comptabilite-ohada': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-comptabilite-ohada',
    sidebar: { activeAccent: 'text-indigo-400 border-indigo-400', activeBgSubtle: 'bg-indigo-500/10', brandIconBg: 'bg-indigo-600' },
  },

  // 7. Parc & Véhicules (🚗 Support: Équipements)
  'parc-vehicules': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-parc-vehicules',
    sidebar: { activeAccent: 'text-violet-400 border-violet-400', activeBgSubtle: 'bg-violet-500/10', brandIconBg: 'bg-violet-600' },
  },

  // 8. QHSE & Sécurité (🛡️ Support: Conformité)
  'qhse-securite': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-qhse-securite',
    sidebar: { activeAccent: 'text-red-400 border-red-400', activeBgSubtle: 'bg-red-500/10', brandIconBg: 'bg-red-600' },
  },

  // 9. RH & Personnel (👥 Support: Capital Humain)
  'rh-personnel': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-rh-personnel',
    sidebar: { activeAccent: 'text-pink-400 border-pink-400', activeBgSubtle: 'bg-pink-500/10', brandIconBg: 'bg-pink-600' },
  },

  // 10. Client & B2B (🤝 Support: Relation Client)
  'client-b2b': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-client-b2b',
    sidebar: { activeAccent: 'text-sky-400 border-sky-400', activeBgSubtle: 'bg-sky-500/10', brandIconBg: 'bg-sky-600' },
  },

  // 11. Admin & Tenant (⚙️ Support: Gouvernance)
  'admin-tenant': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-admin-tenant',
    sidebar: { activeAccent: 'text-indigo-400 border-indigo-400', activeBgSubtle: 'bg-indigo-500/10', brandIconBg: 'bg-indigo-600' },
  },

  // 12. Reports & BI (📊 Support: Pilotage)
  'reports-bi': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-reports-bi',
    sidebar: { activeAccent: 'text-violet-400 border-violet-400', activeBgSubtle: 'bg-violet-500/10', brandIconBg: 'bg-violet-600' },
  },

  // ═══════════════════════════════════════════════════════════════════════════════
  // LEGACY MODULES (Compatibilité transition)
  // ═══════════════════════════════════════════════════════════════════════════════
  
  admin: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-admin',
    sidebar: { activeAccent: 'text-indigo-400 border-indigo-400', activeBgSubtle: 'bg-indigo-500/10', brandIconBg: 'bg-indigo-600' },
  },
  transport: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-transport',
    sidebar: { activeAccent: 'text-cyan-400 border-cyan-400', activeBgSubtle: 'bg-cyan-500/10', brandIconBg: 'bg-cyan-600' },
  },
  magasin: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-magasin',
    sidebar: { activeAccent: 'text-amber-400 border-amber-400', activeBgSubtle: 'bg-amber-500/10', brandIconBg: 'bg-amber-600' },
  },
  finance: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-finance',
    sidebar: { activeAccent: 'text-emerald-400 border-emerald-400', activeBgSubtle: 'bg-emerald-500/10', brandIconBg: 'bg-emerald-600' },
  },
  acconage: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-acconage',
    sidebar: { activeAccent: 'text-blue-400 border-blue-400', activeBgSubtle: 'bg-blue-500/10', brandIconBg: 'bg-blue-600' },
  },
  transit: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-transit',
    sidebar: { activeAccent: 'text-sky-400 border-sky-400', activeBgSubtle: 'bg-sky-500/10', brandIconBg: 'bg-sky-600' },
  },
  qhse: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-qhse',
    sidebar: { activeAccent: 'text-red-400 border-red-400', activeBgSubtle: 'bg-red-500/10', brandIconBg: 'bg-red-600' },
  },
  maintenance: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-maintenance',
    sidebar: { activeAccent: 'text-orange-400 border-orange-400', activeBgSubtle: 'bg-orange-500/10', brandIconBg: 'bg-orange-600' },
  },
  parc: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-parc',
    sidebar: { activeAccent: 'text-violet-400 border-violet-400', activeBgSubtle: 'bg-violet-500/10', brandIconBg: 'bg-violet-600' },
  },
  rh: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-rh',
    sidebar: { activeAccent: 'text-pink-400 border-pink-400', activeBgSubtle: 'bg-pink-500/10', brandIconBg: 'bg-pink-600' },
  },
  'master-data': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-master-data',
    sidebar: { activeAccent: 'text-pink-400 border-pink-400', activeBgSubtle: 'bg-pink-500/10', brandIconBg: 'bg-pink-600' },
  },
  cotations: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-cotations',
    sidebar: { activeAccent: 'text-yellow-400 border-yellow-400', activeBgSubtle: 'bg-yellow-500/10', brandIconBg: 'bg-yellow-600' },
  },
  tracking: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-tracking',
    sidebar: { activeAccent: 'text-cyan-400 border-cyan-400', activeBgSubtle: 'bg-cyan-500/10', brandIconBg: 'bg-cyan-600' },
  },
  'fuel-guard': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-fuel-guard',
    sidebar: { activeAccent: 'text-orange-400 border-orange-400', activeBgSubtle: 'bg-orange-500/10', brandIconBg: 'bg-orange-600' },
  },
  procurement: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-procurement',
    sidebar: { activeAccent: 'text-emerald-400 border-emerald-400', activeBgSubtle: 'bg-emerald-500/10', brandIconBg: 'bg-emerald-600' },
  },
  compliance: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-compliance',
    sidebar: { activeAccent: 'text-teal-400 border-teal-400', activeBgSubtle: 'bg-teal-500/10', brandIconBg: 'bg-teal-600' },
  },
  bi: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-bi',
    sidebar: { activeAccent: 'text-violet-400 border-violet-400', activeBgSubtle: 'bg-violet-500/10', brandIconBg: 'bg-violet-600' },
  },
  'client-portal': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-client-portal',
    sidebar: { activeAccent: 'text-sky-400 border-sky-400', activeBgSubtle: 'bg-sky-500/10', brandIconBg: 'bg-sky-600' },
  },
  settings: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-settings',
    sidebar: { activeAccent: 'text-slate-400 border-slate-400', activeBgSubtle: 'bg-slate-500/10', brandIconBg: 'bg-slate-600' },
  },
  'integration-cameroun': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-integration-cameroun',
    sidebar: { activeAccent: 'text-red-400 border-red-400', activeBgSubtle: 'bg-red-500/10', brandIconBg: 'bg-red-600' },
  },
  'fiscalite-cameroun': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-finance',
    sidebar: { activeAccent: 'text-emerald-400 border-emerald-400', activeBgSubtle: 'bg-emerald-500/10', brandIconBg: 'bg-emerald-600' },
  },
  'paiement-local': {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-transit',
    sidebar: { activeAccent: 'text-sky-400 border-sky-400', activeBgSubtle: 'bg-sky-500/10', brandIconBg: 'bg-sky-600' },
  },
  reports: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-bi',
    sidebar: { activeAccent: 'text-violet-400 border-violet-400', activeBgSubtle: 'bg-violet-500/10', brandIconBg: 'bg-violet-600' },
  },
  security: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-qhse',
    sidebar: { activeAccent: 'text-red-400 border-red-400', activeBgSubtle: 'bg-red-500/10', brandIconBg: 'bg-red-600' },
  },
  documents: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-settings',
    sidebar: { activeAccent: 'text-slate-400 border-slate-400', activeBgSubtle: 'bg-slate-500/10', brandIconBg: 'bg-slate-600' },
  },
  fournisseurs: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-procurement',
    sidebar: { activeAccent: 'text-emerald-400 border-emerald-400', activeBgSubtle: 'bg-emerald-500/10', brandIconBg: 'bg-emerald-600' },
  },
  notifications: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-qhse',
    sidebar: { activeAccent: 'text-red-400 border-red-400', activeBgSubtle: 'bg-red-500/10', brandIconBg: 'bg-red-600' },
  },
  support: {
    mainBackground: 'bg-slate-950',
    headerClasses: 'module-badge-settings',
    sidebar: { activeAccent: 'text-slate-400 border-slate-400', activeBgSubtle: 'bg-slate-500/10', brandIconBg: 'bg-slate-600' },
  },
};

// Normalisation : aligne les accents de sidebar (et fond sombre) de CHAQUE
// module sur la palette canonique unique. Couvre aussi les modules/aliases qui
// n'avaient pas d'entrée (portails de rôle, chat, admin-saas…). Dark-only.
for (const key of Object.keys(MODULE_THEME_CONFIG)) {
  const pal = getModulePalette(key);
  const cfg = MODULE_THEME_CONFIG[key];
  cfg.mainBackground = 'bg-slate-950';
  cfg.sidebar = {
    activeAccent: pal.sidebar.activeAccent,
    activeBgSubtle: pal.sidebar.activeBgSubtle,
    brandIconBg: pal.sidebar.brandIconBg,
  };
}
for (const key of Object.keys(MODULE_PALETTE)) {
  if (!MODULE_THEME_CONFIG[key]) {
    const pal = MODULE_PALETTE[key];
    MODULE_THEME_CONFIG[key] = {
      mainBackground: 'bg-slate-950',
      headerClasses: 'module-badge-admin',
      sidebar: { ...pal.sidebar },
    };
  }
}

const DEFAULT_THEME: ModuleThemeConfig = MODULE_THEME_CONFIG.dashboard;

export function useModuleTheme() {
  const pathname = usePathname();

  const currentModule = useMemo((): string => {
    const seg = pathname.split('/')[1] || 'dashboard';
    return VALID_MODULES.includes(seg as any) ? seg : 'dashboard';
  }, [pathname]);

  const theme = MODULE_THEME_CONFIG[currentModule] || DEFAULT_THEME;

  return useMemo(() => ({ currentModule, theme }), [currentModule, theme]);
}
