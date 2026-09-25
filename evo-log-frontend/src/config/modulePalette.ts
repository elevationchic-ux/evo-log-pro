// src/config/modulePalette.ts
// ─────────────────────────────────────────────────────────────────────────────
// SOURCE DE VÉRITÉ UNIQUE : une couleur UNIQUE par module majeur de l'ERP.
// Les classes Tailwind sont écrites en LITTÉRAL (et non concaténées) pour que
// le compilateur JIT les détecte et les génère. Toute la navigation (registry,
// thème du header/sidebar, dropdown, palette de commandes, bulle orbitale) doit
// consommer CE fichier pour rester cohérente.
//
// Règle produit : "une couleur par module". Les 15 modules métier ont 15 teintes
// distinctes ; les 8 portails de rôle ont chacun une teinte distincte. Dark-only.
// ─────────────────────────────────────────────────────────────────────────────

export interface ModulePaletteEntry {
  /** Hex principal, utilisé inline (style borderColor / boxShadow / color). */
  hex: string;
  /** Classes d'halo pour la bulle orbitale (littérales, non concaténées). */
  glow: string;
  /** Dégradé du badge/icône (littéral). */
  bgGradient: string;
  /** Accents de la sidebar (littéraux). */
  sidebar: {
    activeAccent: string;
    activeBgSubtle: string;
    brandIconBg: string;
  };
}

export const MODULE_PALETTE: Record<string, ModulePaletteEntry> = {
  // ── 15 modules métier majeurs ──
  dashboard: {
    hex: '#6366F1',
    glow: 'shadow-indigo-500/50 border-indigo-500/60',
    bgGradient: 'from-indigo-600 to-blue-600',
    sidebar: { activeAccent: 'text-indigo-400 border-indigo-400', activeBgSubtle: 'bg-indigo-500/10', brandIconBg: 'bg-indigo-600' },
  },
  'port-operations': {
    hex: '#0EA5E9',
    glow: 'shadow-sky-500/50 border-sky-500/60',
    bgGradient: 'from-sky-600 to-cyan-600',
    sidebar: { activeAccent: 'text-sky-400 border-sky-400', activeBgSubtle: 'bg-sky-500/10', brandIconBg: 'bg-sky-600' },
  },
  'transit-douane': {
    hex: '#3B82F6',
    glow: 'shadow-blue-500/50 border-blue-500/60',
    bgGradient: 'from-blue-600 to-indigo-600',
    sidebar: { activeAccent: 'text-blue-400 border-blue-400', activeBgSubtle: 'bg-blue-500/10', brandIconBg: 'bg-blue-600' },
  },
  'transport-flotte': {
    hex: '#06B6D4',
    glow: 'shadow-cyan-500/50 border-cyan-500/60',
    bgGradient: 'from-cyan-600 to-teal-500',
    sidebar: { activeAccent: 'text-cyan-400 border-cyan-400', activeBgSubtle: 'bg-cyan-500/10', brandIconBg: 'bg-cyan-600' },
  },
  'magasin-stock': {
    hex: '#F59E0B',
    glow: 'shadow-amber-500/50 border-amber-500/60',
    bgGradient: 'from-amber-500 to-orange-600',
    sidebar: { activeAccent: 'text-amber-400 border-amber-400', activeBgSubtle: 'bg-amber-500/10', brandIconBg: 'bg-amber-600' },
  },
  'comptabilite-ohada': {
    hex: '#8B5CF6',
    glow: 'shadow-violet-500/50 border-violet-500/60',
    bgGradient: 'from-violet-600 to-purple-600',
    sidebar: { activeAccent: 'text-violet-400 border-violet-400', activeBgSubtle: 'bg-violet-500/10', brandIconBg: 'bg-violet-600' },
  },
  'finance-ohada': {
    hex: '#10B981',
    glow: 'shadow-emerald-500/50 border-emerald-500/60',
    bgGradient: 'from-emerald-600 to-green-600',
    sidebar: { activeAccent: 'text-emerald-400 border-emerald-400', activeBgSubtle: 'bg-emerald-500/10', brandIconBg: 'bg-emerald-600' },
  },
  'parc-vehicules': {
    hex: '#F97316',
    glow: 'shadow-orange-500/50 border-orange-500/60',
    bgGradient: 'from-orange-500 to-red-500',
    sidebar: { activeAccent: 'text-orange-400 border-orange-400', activeBgSubtle: 'bg-orange-500/10', brandIconBg: 'bg-orange-600' },
  },
  'rh-personnel': {
    hex: '#EC4899',
    glow: 'shadow-pink-500/50 border-pink-500/60',
    bgGradient: 'from-pink-600 to-rose-500',
    sidebar: { activeAccent: 'text-pink-400 border-pink-400', activeBgSubtle: 'bg-pink-500/10', brandIconBg: 'bg-pink-600' },
  },
  'qhse-securite': {
    hex: '#EF4444',
    glow: 'shadow-red-500/50 border-red-500/60',
    bgGradient: 'from-red-600 to-rose-600',
    sidebar: { activeAccent: 'text-red-400 border-red-400', activeBgSubtle: 'bg-red-500/10', brandIconBg: 'bg-red-600' },
  },
  'client-b2b': {
    hex: '#14B8A6',
    glow: 'shadow-teal-500/50 border-teal-500/60',
    bgGradient: 'from-teal-500 to-cyan-600',
    sidebar: { activeAccent: 'text-teal-400 border-teal-400', activeBgSubtle: 'bg-teal-500/10', brandIconBg: 'bg-teal-600' },
  },
  'reports-bi': {
    hex: '#A855F7',
    glow: 'shadow-purple-500/50 border-purple-500/60',
    bgGradient: 'from-purple-600 to-fuchsia-600',
    sidebar: { activeAccent: 'text-purple-400 border-purple-400', activeBgSubtle: 'bg-purple-500/10', brandIconBg: 'bg-purple-600' },
  },
  'admin-saas': {
    hex: '#D946EF',
    glow: 'shadow-fuchsia-500/50 border-fuchsia-500/60',
    bgGradient: 'from-fuchsia-600 to-pink-600',
    sidebar: { activeAccent: 'text-fuchsia-400 border-fuchsia-400', activeBgSubtle: 'bg-fuchsia-500/10', brandIconBg: 'bg-fuchsia-600' },
  },
  'admin-tenant': {
    hex: '#64748B',
    glow: 'shadow-slate-500/50 border-slate-500/60',
    bgGradient: 'from-slate-600 to-gray-700',
    sidebar: { activeAccent: 'text-slate-400 border-slate-400', activeBgSubtle: 'bg-slate-500/10', brandIconBg: 'bg-slate-600' },
  },
  chat: {
    hex: '#22C55E',
    glow: 'shadow-green-500/50 border-green-500/60',
    bgGradient: 'from-green-500 to-emerald-600',
    sidebar: { activeAccent: 'text-green-400 border-green-400', activeBgSubtle: 'bg-green-500/10', brandIconBg: 'bg-green-600' },
  },

  // ── 8 portails de rôle (teintes distinctes) ──
  'portail-employe': {
    hex: '#84CC16',
    glow: 'shadow-lime-500/50 border-lime-500/60',
    bgGradient: 'from-lime-500 to-green-600',
    sidebar: { activeAccent: 'text-lime-400 border-lime-400', activeBgSubtle: 'bg-lime-500/10', brandIconBg: 'bg-lime-600' },
  },
  'portail-collaborateur': {
    hex: '#EAB308',
    glow: 'shadow-yellow-500/50 border-yellow-500/60',
    bgGradient: 'from-yellow-500 to-amber-600',
    sidebar: { activeAccent: 'text-yellow-400 border-yellow-400', activeBgSubtle: 'bg-yellow-500/10', brandIconBg: 'bg-yellow-600' },
  },
  'portail-chauffeur': {
    hex: '#F43F5E',
    glow: 'shadow-rose-500/50 border-rose-500/60',
    bgGradient: 'from-rose-500 to-pink-600',
    sidebar: { activeAccent: 'text-rose-400 border-rose-400', activeBgSubtle: 'bg-rose-500/10', brandIconBg: 'bg-rose-600' },
  },
  'portail-frais': {
    hex: '#0D9488',
    glow: 'shadow-teal-600/50 border-teal-600/60',
    bgGradient: 'from-teal-600 to-emerald-700',
    sidebar: { activeAccent: 'text-teal-300 border-teal-300', activeBgSubtle: 'bg-teal-600/10', brandIconBg: 'bg-teal-700' },
  },
  'portail-magasinier': {
    hex: '#71717A',
    glow: 'shadow-zinc-500/50 border-zinc-500/60',
    bgGradient: 'from-zinc-600 to-neutral-700',
    sidebar: { activeAccent: 'text-zinc-400 border-zinc-400', activeBgSubtle: 'bg-zinc-500/10', brandIconBg: 'bg-zinc-600' },
  },
  'portail-technicien': {
    hex: '#78716C',
    glow: 'shadow-stone-500/50 border-stone-500/60',
    bgGradient: 'from-stone-600 to-neutral-700',
    sidebar: { activeAccent: 'text-stone-400 border-stone-400', activeBgSubtle: 'bg-stone-500/10', brandIconBg: 'bg-stone-600' },
  },
  'portail-declarant': {
    hex: '#737373',
    glow: 'shadow-neutral-500/50 border-neutral-500/60',
    bgGradient: 'from-neutral-600 to-stone-700',
    sidebar: { activeAccent: 'text-neutral-400 border-neutral-400', activeBgSubtle: 'bg-neutral-500/10', brandIconBg: 'bg-neutral-600' },
  },
  'portail-qhse': {
    hex: '#E11D48',
    glow: 'shadow-rose-600/50 border-rose-600/60',
    bgGradient: 'from-rose-600 to-red-700',
    sidebar: { activeAccent: 'text-rose-500 border-rose-500', activeBgSubtle: 'bg-rose-600/10', brandIconBg: 'bg-rose-700' },
  },
};

/** Alias legacy → module majeur de la palette (hérite de sa couleur). */
const LEGACY_ALIAS: Record<string, string> = {
  transport: 'transport-flotte',
  finance: 'finance-ohada',
  magasin: 'magasin-stock',
  parc: 'parc-vehicules',
  acconage: 'port-operations',
  qhse: 'qhse-securite',
  transit: 'transit-douane',
  maintenance: 'parc-vehicules',
  rh: 'rh-personnel',
  'master-data': 'admin-tenant',
  cotations: 'finance-ohada',
  tracking: 'transport-flotte',
  'fuel-guard': 'transport-flotte',
  procurement: 'finance-ohada',
  compliance: 'qhse-securite',
  bi: 'reports-bi',
  'client-portal': 'client-b2b',
  b2b: 'client-b2b',
  admin: 'admin-tenant',
  'admin-agency': 'admin-tenant',
  settings: 'admin-tenant',
  'integration-cameroun': 'transit-douane',
  'fiscalite-cameroun': 'finance-ohada',
  'paiement-local': 'finance-ohada',
  suppliers: 'admin-tenant',
  fournisseurs: 'admin-tenant',
  security: 'qhse-securite',
  reports: 'reports-bi',
  documents: 'admin-tenant',
  notifications: 'qhse-securite',
  support: 'admin-tenant',
};

/** Retourne l'entrée de palette d'un module (majeur ou alias legacy). */
export function getModulePalette(moduleKey: string): ModulePaletteEntry {
  const direct = MODULE_PALETTE[moduleKey];
  if (direct) return direct;
  const alias = LEGACY_ALIAS[moduleKey];
  if (alias && MODULE_PALETTE[alias]) return MODULE_PALETTE[alias];
  return MODULE_PALETTE.dashboard;
}
