/**
 * T-Code Lookup Utility
 * Maps T-Codes to routes in the application
 */

export const getRouteFromTCode = (tcode: string): string => {
  const code = tcode.toUpperCase().trim()
  
  // T-Code mapping
  const tcodeMap: Record<string, string> = {
    // Transport
    'EVO-TR01': '/transport/control',
    'EVO-TR02': '/transport/missions',
    'EVO-TR03': '/tracking',
    
    // Magasin
    'EVO-MG01': '/magasin/dashboard',
    'EVO-MG02': '/magasin/entrees',
    'EVO-MG03': '/magasin/sorties',
    
    // Finance
    'EVO-FI01': '/finance/overview',
    'EVO-FI02': '/finance/factures',
    'EVO-FI03': '/finance/paiements',
    
    // Admin
    'EVO-AD01': '/admin',
    'EVO-AD02': '/admin/companies',
    'EVO-AD03': '/admin/users',
    
    // QHSE
    'EVO-QH01': '/qhse',
    'EVO-QH02': '/qhse/incidents',
    'EVO-QH03': '/qhse/inspections',
    
    // Transit
    'EVO-TS01': '/transit',
    'EVO-TS02': '/transit/declarations',
    'EVO-TS03': '/transit/dossiers',
    
    // Acconage
    'EVO-AC01': '/acconage',
    'EVO-AC02': '/acconage/operations',
    
    // Maintenance
    'EVO-MT01': '/maintenance',
    'EVO-MT02': '/maintenance/work-orders',
    
    // Fuel
    'EVO-FG01': '/fuel-guard',
    'EVO-FG02': '/fuel-guard/stations',
    
    // Procurement
    'EVO-PR01': '/procurement',
    'EVO-PR02': '/procurement/orders',
    
    // Reports
    'EVO-RP01': '/reports',
    'EVO-RP02': '/bi',
  }
  
  return tcodeMap[code] || '/dashboard'
}