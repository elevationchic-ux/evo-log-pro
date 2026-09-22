// src/config/moduleColors.ts
export interface ModuleColorConfig {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
}

export const MODULE_COLORS: Record<string, ModuleColorConfig> = {
  auth: { primary: '#F59E0B', primaryLight: '#FBBF24', primaryDark: '#D97706', secondary: '#FCD34D', accent: '#FEF3C7', background: '#FFFBEB', text: '#92400E' },
  dashboard: { primary: '#6366F1', primaryLight: '#818CF8', primaryDark: '#4F46E5', secondary: '#C7D2FE', accent: '#E0E7FF', background: '#EEF2FF', text: '#3730A3' },
  transport: { primary: '#06B6D4', primaryLight: '#22D3EE', primaryDark: '#0891B2', secondary: '#67E8F9', accent: '#CFFAFE', background: '#ECFEFF', text: '#155E75' },
  'transport-avance': { primary: '#0891B2', primaryLight: '#22D3EE', primaryDark: '#0E7490', secondary: '#67E8F9', accent: '#CFFAFE', background: '#ECFEFF', text: '#164E63' },
  'transport-international': { primary: '#0E7490', primaryLight: '#22D3EE', primaryDark: '#155E75', secondary: '#67E8F9', accent: '#CFFAFE', background: '#ECFEFF', text: '#0C4A6E' },
  magasin: { primary: '#F59E0B', primaryLight: '#FBBF24', primaryDark: '#D97706', secondary: '#FCD34D', accent: '#FEF3C7', background: '#FFFBEB', text: '#78350F' },
  'magasin-avance': { primary: '#D97706', primaryLight: '#FBBF24', primaryDark: '#B45309', secondary: '#FCD34D', accent: '#FEF3C7', background: '#FFFBEB', text: '#92400E' },
  'magasin-douane': { primary: '#B45309', primaryLight: '#FBBF24', primaryDark: '#92400E', secondary: '#FCD34D', accent: '#FEF3C7', background: '#FFFBEB', text: '#78350F' },
  finance: { primary: '#10B981', primaryLight: '#34D399', primaryDark: '#059669', secondary: '#6EE7B7', accent: '#D1FAE5', background: '#ECFDF5', text: '#065F46' },
  acconage: { primary: '#3B82F6', primaryLight: '#60A5FA', primaryDark: '#2563EB', secondary: '#93C5FD', accent: '#DBEAFE', background: '#EFF6FF', text: '#1E40AF' },
  'acconage-avance': { primary: '#2563EB', primaryLight: '#60A5FA', primaryDark: '#1D4ED8', secondary: '#93C5FD', accent: '#DBEAFE', background: '#EFF6FF', text: '#1E3A8A' },
  transit: { primary: '#0284C7', primaryLight: '#38BDF8', primaryDark: '#0369A1', secondary: '#7DD3FC', accent: '#E0F2FE', background: '#F0F9FF', text: '#075985' },
  'transit-avance': { primary: '#0369A1', primaryLight: '#38BDF8', primaryDark: '#075985', secondary: '#7DD3FC', accent: '#E0F2FE', background: '#F0F9FF', text: '#0C4A6E' },
  qhse: { primary: '#EF4444', primaryLight: '#F87171', primaryDark: '#DC2626', secondary: '#FCA5A5', accent: '#FEE2E2', background: '#FEF2F2', text: '#991B1B' },
  maintenance: { primary: '#F97316', primaryLight: '#FB923C', primaryDark: '#EA580C', secondary: '#FDBA74', accent: '#FFEDD5', background: '#FFF7ED', text: '#9A3412' },
  'maintenance-gmao': { primary: '#EA580C', primaryLight: '#FB923C', primaryDark: '#C2410C', secondary: '#FDBA74', accent: '#FFEDD5', background: '#FFF7ED', text: '#9A3412' },
  parc: { primary: '#8B5CF6', primaryLight: '#A78BFA', primaryDark: '#7C3AED', secondary: '#C4B5FD', accent: '#EDE9FE', background: '#F5F3FF', text: '#5B21B6' },
  rh: { primary: '#EC4899', primaryLight: '#F472B6', primaryDark: '#DB2777', secondary: '#F9A8D4', accent: '#FCE7F3', background: '#FDF2F8', text: '#9D174D' },
  'master-data': { primary: '#EC4899', primaryLight: '#F472B6', primaryDark: '#DB2777', secondary: '#F9A8D4', accent: '#FCE7F3', background: '#FDF2F8', text: '#9D174D' },
  cotations: { primary: '#EAB308', primaryLight: '#FACC15', primaryDark: '#CA8A04', secondary: '#FDE047', accent: '#FEF9C3', background: '#FEFCE8', text: '#713F12' },
  tracking: { primary: '#06B6D4', primaryLight: '#22D3EE', primaryDark: '#0891B2', secondary: '#67E8F9', accent: '#CFFAFE', background: '#ECFEFF', text: '#155E75' },
  'fuel-guard': { primary: '#F97316', primaryLight: '#FB923C', primaryDark: '#EA580C', secondary: '#FDBA74', accent: '#FFEDD5', background: '#FFF7ED', text: '#9A3412' },
  procurement: { primary: '#10B981', primaryLight: '#34D399', primaryDark: '#059669', secondary: '#6EE7B7', accent: '#D1FAE5', background: '#ECFDF5', text: '#065F46' },
  purchase: { primary: '#059669', primaryLight: '#34D399', primaryDark: '#047857', secondary: '#6EE7B7', accent: '#D1FAE5', background: '#ECFDF5', text: '#064E3B' },
  compliance: { primary: '#14B8A6', primaryLight: '#2DD4BF', primaryDark: '#0D9488', secondary: '#5EEAD4', accent: '#CCFBF1', background: '#F0FDFA', text: '#0F766E' },
  bi: { primary: '#8B5CF6', primaryLight: '#A78BFA', primaryDark: '#7C3AED', secondary: '#C4B5FD', accent: '#EDE9FE', background: '#F5F3FF', text: '#5B21B6' },
  'client-portal': { primary: '#0284C7', primaryLight: '#38BDF8', primaryDark: '#0369A1', secondary: '#7DD3FC', accent: '#E0F2FE', background: '#F0F9FF', text: '#075985' },
  b2b: { primary: '#0284C7', primaryLight: '#38BDF8', primaryDark: '#0369A1', secondary: '#7DD3FC', accent: '#E0F2FE', background: '#F0F9FF', text: '#075985' },
  admin: { primary: '#6366F1', primaryLight: '#818CF8', primaryDark: '#4F46E5', secondary: '#C7D2FE', accent: '#E0E7FF', background: '#EEF2FF', text: '#3730A3' },
  'admin-agency': { primary: '#4F46E5', primaryLight: '#818CF8', primaryDark: '#4338CA', secondary: '#C7D2FE', accent: '#E0E7FF', background: '#EEF2FF', text: '#312E81' },
  settings: { primary: '#64748B', primaryLight: '#94A3B8', primaryDark: '#475569', secondary: '#CBD5E1', accent: '#F1F5F9', background: '#F8FAFC', text: '#1E293B' },
  'integration-cameroun': { primary: '#EF4444', primaryLight: '#F87171', primaryDark: '#DC2626', secondary: '#FCA5A5', accent: '#FEE2E2', background: '#FEF2F2', text: '#991B1B' },
  integration: { primary: '#DC2626', primaryLight: '#F87171', primaryDark: '#B91C1C', secondary: '#FCA5A5', accent: '#FEE2E2', background: '#FEF2F2', text: '#7F1D1D' },
  'fiscalite-cameroun': { primary: '#10B981', primaryLight: '#34D399', primaryDark: '#059669', secondary: '#6EE7B7', accent: '#D1FAE5', background: '#ECFDF5', text: '#065F46' },
  'paiement-local': { primary: '#06B6D4', primaryLight: '#22D3EE', primaryDark: '#0891B2', secondary: '#67E8F9', accent: '#CFFAFE', background: '#ECFEFF', text: '#155E75' },
  'shift-planning': { primary: '#FF6B6B', primaryLight: '#FF8E8E', primaryDark: '#E55555', secondary: '#FFB4B4', accent: '#FFE0E0', background: '#FFF0F0', text: '#CC4444' },
  'port-pricing': { primary: '#4ECDC4', primaryLight: '#7EDDD6', primaryDark: '#3DBDB5', secondary: '#A8E8E0', accent: '#D0F5F0', background: '#F0FBFA', text: '#2A9D96' },
  'gps-tracking': { primary: '#45B7D1', primaryLight: '#6DC5DE', primaryDark: '#3A9BC4', secondary: '#8DD3E6', accent: '#D0EAF7', background: '#F0F7FB', text: '#2A7A8C' },
  'real-customs': { primary: '#96CEB4', primaryLight: '#B5DFC7', primaryDark: '#7FB89E', secondary: '#C9E6D3', accent: '#E8F5EB', background: '#F7FCF8', text: '#5A9A78' },
  'port-incidents': { primary: '#FFEAA7', primaryLight: '#FFF4C7', primaryDark: '#FDDA6E', secondary: '#FFF8DC', accent: '#FFFEF0', background: '#FFFCF5', text: '#CC9900' },
  'auto-invoicing': { primary: '#DDA0DD', primaryLight: '#E8B8E8', primaryDark: '#C890C8', secondary: '#F0D0F0', accent: '#F8E8F8', background: '#FCF5FC', text: '#A070A0' },
  'port-performance': { primary: '#98D8C8', primaryLight: '#B8E8D8', primaryDark: '#78C8A8', secondary: '#D0F0E0', accent: '#E8F8F0', background: '#F7FCF8', text: '#5A9A78' },
  'notification-system': { primary: '#F7DC6F', primaryLight: '#FAEB8F', primaryDark: '#ECCC50', secondary: '#FCF4A8', accent: '#FEFAE0', background: '#FFFCF5', text: '#B89400' },
  'container-lifecycle': { primary: '#BB8FCE', primaryLight: '#D1AFDE', primaryDark: '#A57BBE', secondary: '#E3C9E8', accent: '#F2E8F4', background: '#FAF5FC', text: '#8A5A9E' },
  'partner-api': { primary: '#85C1E9', primaryLight: '#A3D4EF', primaryDark: '#6BAAD9', secondary: '#C0DCF0', accent: '#E0EEF7', background: '#F5F9FC', text: '#4A8BB8' },
  'bill-of-loading': { primary: '#5DADE2', primaryLight: '#7DBFE8', primaryDark: '#4A90C8', secondary: '#A0D0F0', accent: '#D0E8F8', background: '#F0F5FB', text: '#2A6A8C' },
  documents: { primary: '#95A5A6', primaryLight: '#B0BEBE', primaryDark: '#7A8A8A', secondary: '#D0DCDC', accent: '#E8EEEE', background: '#F8FAFA', text: '#5A6A6A' },
  alerts: { primary: '#E74C3C', primaryLight: '#EC7063', primaryDark: '#C0392B', secondary: '#F1948A', accent: '#FADBD8', background: '#FDEDEC', text: '#922B21' },
  notifications: { primary: '#F39C12', primaryLight: '#F5B041', primaryDark: '#D68910', secondary: '#F7DC6F', accent: '#FAE5D3', background: '#FEF9E7', text: '#B7950B' },
  acquisition: { primary: '#8E44AD', primaryLight: '#A569BD', primaryDark: '#7D3C98', secondary: '#BB8FCE', accent: '#D7BDE2', background: '#F5EEF8', text: '#6C3483' },
  gateway: { primary: '#34495E', primaryLight: '#5D6D7E', primaryDark: '#2C3E50', secondary: '#85929E', accent: '#D6DBDF', background: '#EBEDEF', text: '#1A252F' },
  goods: { primary: '#16A085', primaryLight: '#48C9B0', primaryDark: '#138D75', secondary: '#76D7C4', accent: '#D1F2EB', background: '#E8F8F5', text: '#0E6655' },
  incidents: { primary: '#C0392B', primaryLight: '#E74C3C', primaryDark: '#A93226', secondary: '#EC7063', accent: '#FADBD8', background: '#FDEDEC', text: '#922B21' },
  suppliers: { primary: '#27AE60', primaryLight: '#52BE80', primaryDark: '#229954', secondary: '#82E0AA', accent: '#D5F5E3', background: '#E9F7EF', text: '#1E8449' },
  tenant: { primary: '#2E86C1', primaryLight: '#5499C7', primaryDark: '#2874A6', secondary: '#7FB3D5', accent: '#D4E6F1', background: '#EBF5FB', text: '#1B4F72' },
  tiers: { primary: '#884EA0', primaryLight: '#A569BD', primaryDark: '#76448A', secondary: '#BB8FCE', accent: '#D7BDE2', background: '#F5EEF8', text: '#633974' },
  transactions: { primary: '#D35400', primaryLight: '#E67E22', primaryDark: '#BA4A00', secondary: '#EB984E', accent: '#FDEBD0', background: '#FDF2E9', text: '#A04000' },
  role: { primary: '#7F8C8D', primaryLight: '#95A5A6', primaryDark: '#6C7A7A', secondary: '#B0BEBE', accent: '#E8EEEE', background: '#F8FAFA', text: '#566565' },
  'reception-mag3': { primary: '#F39C12', primaryLight: '#F5B041', primaryDark: '#D68910', secondary: '#F7DC6F', accent: '#FAE5D3', background: '#FEF9E7', text: '#B7950B' },
  'removal-slip': { primary: '#E67E22', primaryLight: '#F39C12', primaryDark: '#D35400', secondary: '#EB984E', accent: '#FDEBD0', background: '#FDF2E9', text: '#A04000' },
  reporting: { primary: '#9B59B6', primaryLight: '#AF7AC5', primaryDark: '#884EA0', secondary: '#C39BD3', accent: '#E8DAEF', background: '#F5EEF8', text: '#6C3483' },
  'public-api': { primary: '#1ABC9C', primaryLight: '#48C9B0', primaryDark: '#17A589', secondary: '#76D7C4', accent: '#D1F2EB', background: '#E8F8F5', text: '#0E6655' },
};

export const MODULE_ICONS: Record<string, string> = {
  auth: '🔐', dashboard: '🧭', transport: '🚛', 'transport-avance': '🚚', 'transport-international': '🌍',
  magasin: '📦', 'magasin-avance': '🏭', 'magasin-douane': '�',
  finance: '💰', acconage: '⚓', 'acconage-avance': '🏗️',
  transit: '🌐', 'transit-avance': '📋',
  qhse: '🛡️', maintenance: '🔧', 'maintenance-gmao': '⚙️',
  parc: '🚗', rh: '👥', 'master-data': '🗂️',
  cotations: '🏷️', tracking: '📡', 'fuel-guard': '⛽',
  procurement: '🛒', purchase: '📦', compliance: '🏛️',
  bi: '📊', 'client-portal': '💼', b2b: '🤝',
  admin: '⚙️', 'admin-agency': '🏢', settings: '🔩',
  'integration-cameroun': '🇨🇲', integration: '🔗',
  'fiscalite-cameroun': '📋', 'paiement-local': '💳',
  'shift-planning': '📅', 'port-pricing': '💲', 'gps-tracking': '🛰️',
  'real-customs': '🛃', 'port-incidents': '⚠️', 'auto-invoicing': '🧾',
  'port-performance': '📈', 'notification-system': '🔔',
  'container-lifecycle': '📦', 'partner-api': '🔌',
  'bill-of-loading': '📄', documents: '📁', alerts: '🚨',
  notifications: '📢', acquisition: '🛍️', gateway: '🌐',
  goods: '🚢', incidents: '🔥', suppliers: '🏭',
  tenant: '🏢', tiers: '👥', transactions: '💱',
  role: '👤', 'reception-mag3': '📥', 'removal-slip': '📤',
  reporting: '📊', 'public-api': '🌐',
};

export const MODULE_NAMES: Record<string, string> = {
  auth: 'Authentification', dashboard: 'Vue Globale ERP', transport: 'K-Transport & Flotte',
  magasin: 'K-Magasin WMS', finance: 'K-Finance & Comptabilité', acconage: 'K-Acconage & Quai',
  transit: 'K-Transit & Douane', qhse: 'K-QHSE & Sécurité', maintenance: 'K-Maintenance & Atelier',
  parc: 'K-Parc Véhicules', rh: 'Ressources Humaines', 'master-data': 'Données Maîtres ERP',
  cotations: 'K-Cotations & Devis', tracking: 'K-Tracking & e-POD',
  'fuel-guard': 'K-FuelGuard Télémétrie', procurement: 'K-Procurement & Achats',
  compliance: 'K-Compliance & Douane', bi: 'K-Analytics BI Executive',
  'client-portal': 'Portail Client B2B', admin: 'Administration ERP',
  settings: 'Paramètres & Profil', 'integration-cameroun': 'Intégration Cameroun',
  'fiscalite-cameroun': 'Fiscalité Cameroun', 'paiement-local': 'Paiements Locaux',
};

export const getModuleColor = (module: string): ModuleColorConfig =>
  MODULE_COLORS[module] || MODULE_COLORS.auth;

export const getModuleIcon = (module: string): string =>
  MODULE_ICONS[module] || '📋';

export const getModuleName = (module: string): string =>
  MODULE_NAMES[module] || 'Module';
