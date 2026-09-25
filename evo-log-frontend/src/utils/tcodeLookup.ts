/**
 * T-Code Lookup & RBAC Access Matrix
 * Central Registry for SAP-style fast navigation codes and EVO-style T-Codes
 * Supports CADC Access Control, Auto-completion & Role Habilitations
 */

export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  ADMIN = 'ADMIN',
  TENANT_ADMIN = 'TENANT_ADMIN',
  MANAGER = 'MANAGER',
  DIRECTOR = 'DIRECTOR',
  AUDITOR = 'AUDITOR',
  EXPERT_COMPTABLE = 'EXPERT_COMPTABLE',
  COMPTABLE = 'COMPTABLE',
  FINANCE = 'FINANCE',
  DISPATCHER = 'DISPATCHER',
  TRANSPORT = 'TRANSPORT',
  FLEET_MANAGER = 'FLEET_MANAGER',
  CHAUFFEUR = 'CHAUFFEUR',
  MAGASINIER = 'MAGASINIER',
  MAGASIN = 'MAGASIN',
  STOCK = 'STOCK',
  DOUANE = 'DOUANE',
  DECLARANT = 'DECLARANT',
  TRANSIT = 'TRANSIT',
  PORT_OPERATIONS = 'PORT_OPERATIONS',
  MARITIME = 'MARITIME',
  QUAI = 'QUAI',
  MAINTENANCE = 'MAINTENANCE',
  PARC = 'PARC',
  RH = 'RH',
  PAIE = 'PAIE',
  QHSE = 'QHSE',
  SECURITE = 'SECURITE',
  COMMERCIAL = 'COMMERCIAL',
  CLIENT_B2B = 'CLIENT_B2B',
  CLIENT = 'CLIENT',
  USER = 'USER'
}

export const TCODE_MAP: Record<string, string> = {
  // 🎯 Vue Globale & Audit
  'KM24': '/dashboard/global',
  'KPRC_FLW': '/dashboard/process-flow',
  'KAUD_LOG': '/admin-tenant/audit-logs',
  'KAUD_ALT': '/security/notifications',
  'KAUD_RPT': '/security/reports',
  'KAUD_SEC': '/security/notifications',
  'KBI_DSH': '/bi',

  // 🚢 Opérations Portuaires & Quai
  'KACC_DSH': '/port-operations/dashboard',
  'KACC_MNF': '/port-operations/manifests',
  'KACC_OPS': '/port-operations/quai-operations',
  'KACC_PLN': '/port-operations/berth-planning',
  'KACC_STS': '/port-operations/maritime-stats',
  'KACC_EDI': '/port-operations/port-integration',
  'EVO-AC01': '/acconage',
  'EVO-AC02': '/acconage/operations',

  // 🛃 Transit & Douane CEMAC
  'KDOU_DSH': '/transit-douane/dashboard',
  'KDOU_DUM': '/transit-douane/declarations',
  'KDOU_TAX': '/transit-douane/taxation-cameroun',
  'KDOU_COR': '/transit-douane/dossiers-cemac',
  'KDOU_BAE': '/transit-douane/bae',
  'KDOU_CMP': '/transit-douane/compliance',
  'EVO-TS01': '/transit',
  'EVO-TS02': '/transit-douane/declarations',
  'EVO-TS03': '/transit-douane/dossiers-cemac',

  // 🚛 Transport TMS & Flotte
  'TR01': '/transport/control',
  'KTRN_RTE': '/transport-flotte/control-tower',
  'KTRN_DSP': '/transport-flotte/missions-dispatch',
  'KTRN_POD': '/transport-flotte/tracking-epod',
  'KTRN_FLT': '/transport-flotte/fleet-management',
  'KTRN_DRV': '/transport-flotte/drivers',
  'KTRN_FUEL': '/transport-flotte/fuel-telematics',
  'KTRN_MAP': '/transport/carte-live',
  'EVO-TR01': '/transport-flotte/control-tower',
  'EVO-TR02': '/transport-flotte/missions-dispatch',
  'EVO-TR03': '/transport-flotte/tracking-epod',

  // 📦 Magasin WMS & Stock
  'KMAG_DSH': '/magasin-stock/dashboard',
  'KMAG_RCP': '/magasin-stock/reception',
  'KMAG_PIK': '/magasin-stock/picking',
  'KMAG_SLT': '/magasin-stock/locations',
  'KMAG_INV': '/magasin-stock/inventory',
  'KMAG_MVM': '/magasin-stock/movements',
  'KMAG_BL': '/magasin/removal-slip',
  'KMAG_DCL': '/magasin/declarations',
  'EVO-MG01': '/magasin-stock/dashboard',
  'EVO-MG02': '/magasin-stock/reception',
  'EVO-MG03': '/magasin-stock/movements',

  // 📚 Comptabilité OHADA (Sage-like)
  'KOHA_DSH': '/comptabilite-ohada/dashboard',
  'KOHA_JRN': '/comptabilite-ohada/journal',
  'KOHA_GL': '/comptabilite-ohada/general-ledger',
  'KOHA_COA': '/comptabilite-ohada/chart-accounts',
  'KOHA_BIL': '/comptabilite-ohada/financial-statements',
  'KOHA_CLO': '/comptabilite-ohada/monthly-closing',
  'KOHA_TAX': '/comptabilite-ohada/tax-package-cemac',

  // 💰 Finance & Trésorerie
  'KFIN_DSH': '/finance-ohada/dashboard',
  'KFIN_TRZ': '/finance-ohada/treasury',
  'KFIN_FAC': '/finance-ohada/invoicing',
  'KFIN_REC': '/finance-ohada/collections',
  'KFIN_DET': '/finance-ohada/suppliers',
  'KFIN_TAX': '/finance-ohada/taxes-cemac',
  'KFIN_OVR': '/finance/overview',
  'EVO-FI01': '/finance-ohada/dashboard',
  'EVO-FI02': '/finance-ohada/invoicing',
  'EVO-FI03': '/finance-ohada/collections',

  // 🚗 Parc & GMAO
  'KMNT_DSH': '/parc-vehicules/dashboard',
  'KMNT_WO': '/parc-vehicules/preventive-maintenance',
  'KMNT_PRV': '/parc-vehicules/fleet-complete',
  'KMNT_DOC': '/parc-vehicules/documents',
  'KMNT_TCO': '/parc-vehicules/costs-consumption',
  'KPARC_OVR': '/parc',
  'KPARC_WSH': '/parc/workshop',
  'EVO-MT01': '/parc-vehicules/dashboard',
  'EVO-MT02': '/parc-vehicules/preventive-maintenance',

  // 👥 RH & Paie OHADA
  'KRH_DSH': '/rh-personnel/dashboard',
  'KRH_PAY': '/rh-personnel/payroll-ohada',
  'KRH_EMP': '/rh-personnel/employees',
  'KRH_LEV': '/rh-personnel/time-attendance',
  'KRH_DIP': '/rh-personnel/social-declarations',
  'EVO-RH01': '/rh-personnel/dashboard',
  'EVO-RH02': '/rh-personnel/payroll-ohada',

  // 🛡️ QHSE & ISPS
  'KQHS_DSH': '/qhse-securite/dashboard',
  'KQHS_ISP': '/qhse-securite/port-inspections',
  'KQHS_INC': '/qhse-securite/incident-management',
  'KQHS_TRN': '/qhse-securite/safety-training',
  'EVO-QH01': '/qhse-securite/dashboard',
  'EVO-QH02': '/qhse-securite/incident-management',

  // 🤝 Client B2B
  'KB2B_DSH': '/client-b2b/dashboard',
  'KB2B_TRK': '/client-b2b/portal',
  'KB2B_INV': '/client-b2b/contracts',
  'KB2B_SAV': '/client-b2b/after-sales',

  // 📊 Reports & BI
  'KRPT_EXE': '/reports-bi/executive-dashboard',
  'KRPT_OPS': '/reports-bi/operational-analytics',
  'KRPT_FIN': '/reports-bi/financial-reports-ohada',
  'KRPT_GEN': '/reports-bi/report-generator',
  'EVO-RP01': '/reports-bi/executive-dashboard',
  'EVO-RP02': '/bi',

  // ⚙️ Super Admin & Admin RBAC
  'KSUP_TNT': '/admin-tenant/system-admin',
  'KSUP_ORG': '/admin-tenant/multi-tenant',
  'KADM_USR': '/admin-tenant/users-rbac',
  'KADM_SET': '/admin-tenant/integrations',
  'KADM_RLS': '/admin/configuration-des-roles-rbac',
  'KADM_ACC': '/admin/accreditations',
  'KADM_COM': '/admin/espaces-communs',
  'KMD_TIERS': '/master-data/tiers',
  'KMD_ART': '/master-data/articles',
  'EVO-AD01': '/admin-tenant/dashboard',
  'EVO-AD02': '/admin-tenant/multi-tenant',
  'EVO-AD03': '/admin-tenant/users-rbac',
};

// Matrice des rôles autorisés par préfixe ou code spécifique
const TCODE_ROLE_RESTRICTIONS: Record<string, string[]> = {
  'KSUP': ['SUPER_ADMIN'],
  'KADM': ['SUPER_ADMIN', 'ADMIN', 'TENANT_ADMIN'],
  'KOHA': ['SUPER_ADMIN', 'ADMIN', 'EXPERT_COMPTABLE', 'COMPTABLE', 'FINANCE', 'MANAGER'],
  'KFIN': ['SUPER_ADMIN', 'ADMIN', 'FINANCE', 'COMPTABLE', 'MANAGER'],
  'KTRN': ['SUPER_ADMIN', 'ADMIN', 'TRANSPORT', 'DISPATCHER', 'FLEET_MANAGER', 'CHAUFFEUR', 'MANAGER'],
  'KMAG': ['SUPER_ADMIN', 'ADMIN', 'MAGASIN', 'MAGASINIER', 'STOCK', 'MANAGER'],
  'KDOU': ['SUPER_ADMIN', 'ADMIN', 'DOUANE', 'DECLARANT', 'TRANSIT', 'MANAGER'],
  'KACC': ['SUPER_ADMIN', 'ADMIN', 'PORT_OPERATIONS', 'MARITIME', 'QUAI', 'ACCONAGE', 'MANAGER'],
  'KMNT': ['SUPER_ADMIN', 'ADMIN', 'MAINTENANCE', 'PARC', 'MANAGER'],
  'KRH': ['SUPER_ADMIN', 'ADMIN', 'RH', 'PAIE', 'MANAGER'],
  'KQHS': ['SUPER_ADMIN', 'ADMIN', 'QHSE', 'SECURITE', 'AUDITOR', 'MANAGER'],
  'KB2B': ['SUPER_ADMIN', 'ADMIN', 'CLIENT_B2B', 'CLIENT', 'COMMERCIAL', 'MANAGER'],
  'KRPT': ['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'DIRECTOR', 'AUDITOR', 'ANALYST']
};

/**
 * Vérifie si un rôle donné a l'autorisation d'exécuter un T-Code.
 */
export const canAccessTCode = (role: string, tcode: string): boolean => {
  const normalizedRole = role.toUpperCase().trim();
  const normalizedTCode = tcode.toUpperCase().trim();

  // Super Admin a accès absolu à tout
  if (normalizedRole === 'SUPER_ADMIN') return true;

  // Si le rôle est Admin
  if (normalizedRole === 'ADMIN') {
    // Seul KSUP_ est réservé au SUPER_ADMIN
    return !normalizedTCode.startsWith('KSUP');
  }

  // Trouver la restriction de préfixe
  const prefix = Object.keys(TCODE_ROLE_RESTRICTIONS).find(p => normalizedTCode.startsWith(p));
  if (prefix) {
    const allowedRoles = TCODE_ROLE_RESTRICTIONS[prefix];
    return allowedRoles.includes(normalizedRole);
  }

  return true;
};

/**
 * Résout la route associée à un T-Code.
 */
export const getRouteFromTCode = (tcode: string): string => {
  const normalized = tcode.toUpperCase().trim();
  return TCODE_MAP[normalized] || '/dashboard/global';
};