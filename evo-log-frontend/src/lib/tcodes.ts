// src/lib/tcodes.ts
// T-Code Registry for EVO-LOG SaaS

export const T_CODES: Record<string, string> = {
  // Global & Dashboards
  'DB01': '/dashboard/global',
  'DB02': '/dashboard',

  // Magasin (M)
  'M01': '/magasin/dashboard',
  'M02': '/magasin/receptions',
  'M03': '/magasin/stocks',
  'M04': '/magasin/commandes',
  'M05': '/magasin/declarations',
  'M06': '/magasin/analytics',

  // Transport (T)
  'T01': '/transport/control',
  'T02': '/transport/missions',
  'T03': '/transport/dispatch',
  'T04': '/transport/fuel',
  'T05': '/transport/map',

  // Parc (P)
  'P01': '/parc/overview',
  'P02': '/parc/vehicles/new',
  'P03': '/parc/workshop',
  'P04': '/parc/work-orders/create',

  // Finance (F)
  'F01': '/finance/overview',
  'F02': '/finance/invoicing/create',
  'F04': '/finance/gateway',

  // Master Data (MD)
  'MD01': '/master-data/tiers',
  'MD02': '/master-data/clients/create',
  'MD03': '/master-data/suppliers/create',
  'MD04': '/master-data/article-categories',

  // Admin & Security (A)
  'A01': '/admin/users',
  'A02': '/admin/roles/configuration',
  'A03': '/admin/permissions',
  'A04': '/audit/dashboard/health',
  'A05': '/security/dashboard',
  'A06': '/security/alert-monitoring',

  // Reports (R)
  'R01': '/reports/custom/builder',
  'R02': '/reports/templates/library',
};

export function getRouteFromTCode(tcode: string): string | null {
  const normalized = tcode.trim().toUpperCase();
  return T_CODES[normalized] || null;
}
