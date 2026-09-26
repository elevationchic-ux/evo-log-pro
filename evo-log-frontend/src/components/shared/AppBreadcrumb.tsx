'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useSettings } from '@/components/layout/SettingsProvider';

const ROUTE_LABELS: Record<string, string> = {
  dashboard: 'Supervision Globale',
  global: 'Vue Exécutive',
  'process-flow': 'Flux Navire ➔ Client',
  transport: 'Transport TMS & Flotte',
  'transport-flotte': 'Flotte & Convois',
  'control-tower': 'Tour de Contrôle',
  magasin: 'Magasin WMS & Stocks',
  'magasin-stock': 'État des Stocks',
  'magasin-avance': 'Gestion Avancée FEFO',
  'magasin-douane': 'Entrepôt Sous-Douane (MAD)',
  acconage: 'Acconage & Quai (TOS)',
  transit: 'Transit & Douane CAMCIS',
  'transit-douane': 'Déclarations DUM',
  'comptabilite-ohada': 'Comptabilité SYSCOHADA',
  finance: 'Finance & Trésorerie',
  'finance-ohada': 'Liasse Fiscale CEMAC',
  rh: 'Ressources Humaines',
  'rh-personnel': 'Personnel & Salariés',
  'chef-personnel': 'Chef du Personnel & Pointages',
  maintenance: 'Maintenance GMAO & Parc',
  'maintenance-gmao': 'Ordres de Travaux',
  qhse: 'QHSE & Sécurité ISPS',
  'qhse-securite': 'Registres Incidents',
  'portail-collaborateur': 'Hub Collaborateur',
  'portail-chauffeur': 'Espace Chauffeur & Tournées',
  'portail-magasinier': 'Espace Magasinier & Quai',
  'portail-technicien': 'Espace Technicien GMAO',
  'portail-declarant': 'Espace Déclarant Douane',
  'portail-frais': 'Notes de Frais & Avances',
  'portail-qhse': 'Sentinelle Sécurité QHSE',
  'portail-commercial': 'Espace Commercial CEMAC',
  'portail-employe': 'Portail Salarié & Paie',
  'portail-b2b': 'Portail Client B2B',
  'admin-saas': 'Administration SaaS',
  'admin-tenant': 'Paramètres Société',
};

// Équivalent anglais : le fil d'Ariane fait partie du chrome et doit suivre le toggle de langue.
const ROUTE_LABELS_EN: Record<string, string> = {
  dashboard: 'Global Oversight',
  global: 'Executive View',
  'process-flow': 'Vessel ➔ Client Flow',
  transport: 'Transport TMS & Fleet',
  'transport-flotte': 'Fleet & Convoys',
  'control-tower': 'Control Tower',
  magasin: 'Warehouse WMS & Stock',
  'magasin-stock': 'Stock Levels',
  'magasin-avance': 'Advanced FEFO Management',
  'magasin-douane': 'Bonded Warehouse (MAD)',
  acconage: 'Stevedoring & Quay (TOS)',
  transit: 'Transit & Customs CAMCIS',
  'transit-douane': 'DUM Declarations',
  'comptabilite-ohada': 'SYSCOHADA Accounting',
  finance: 'Finance & Treasury',
  'finance-ohada': 'CEMAC Tax Filing',
  rh: 'Human Resources',
  'rh-personnel': 'Staff & Employees',
  'chef-personnel': 'HR Manager & Time Tracking',
  maintenance: 'Maintenance CMMS & Fleet',
  'maintenance-gmao': 'Work Orders',
  qhse: 'QHSE & ISPS Security',
  'qhse-securite': 'Incident Registers',
  'portail-collaborateur': 'Collaborator Hub',
  'portail-chauffeur': 'Driver Space & Routes',
  'portail-magasinier': 'Warehouse Keeper Space & Dock',
  'portail-technicien': 'CMMS Technician Space',
  'portail-declarant': 'Customs Declarant Space',
  'portail-frais': 'Expense Reports & Advances',
  'portail-qhse': 'QHSE Security Watch',
  'portail-commercial': 'CEMAC Sales Space',
  'portail-employe': 'Employee & Payroll Portal',
  'portail-b2b': 'B2B Client Portal',
  'admin-saas': 'SaaS Administration',
  'admin-tenant': 'Company Settings',
};

export function AppBreadcrumb() {
  const pathname = usePathname();
  const { language } = useSettings();

  if (!pathname || pathname === '/' || pathname === '/login') return null;

  const labels = language === 'en' ? ROUTE_LABELS_EN : ROUTE_LABELS;
  const segments = pathname.split('/').filter(Boolean);

  let currentPath = '';

  return (
    <nav aria-label={language === 'en' ? 'Breadcrumb' : "Fil d'Ariane"} className="flex items-center gap-1.5 text-xs text-on-surface-variant/80 py-1 overflow-x-auto no-scrollbar">
      <Link
        href="/dashboard/global"
        className="flex items-center gap-1 text-on-surface-variant hover:text-primary transition-colors font-medium shrink-0"
      >
        <span className="material-symbols-outlined text-[16px]">home</span>
        <span className="hidden sm:inline">{language === 'en' ? 'Home' : 'Accueil'}</span>
      </Link>

      {segments.map((segment, index) => {
        currentPath += `/${segment}`;
        const isLast = index === segments.length - 1;
        const label = labels[segment]
          || (language === 'en'
            ? segment.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
            : (ROUTE_LABELS[segment] || segment.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())));

        return (
          <React.Fragment key={currentPath}>
            <span className="material-symbols-outlined text-[14px] text-outline shrink-0">
              chevron_right
            </span>
            {isLast ? (
              <span className="font-bold text-on-surface shrink-0">
                {label}
              </span>
            ) : (
              <Link
                href={currentPath}
                className="hover:text-primary transition-colors shrink-0 font-medium"
              >
                {label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
