'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

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

export function AppBreadcrumb() {
  const pathname = usePathname();

  if (!pathname || pathname === '/' || pathname === '/login') return null;

  const segments = pathname.split('/').filter(Boolean);

  let currentPath = '';

  return (
    <nav aria-label="Fil d'Ariane" className="flex items-center gap-1.5 text-xs text-on-surface-variant/80 py-1 overflow-x-auto no-scrollbar">
      <Link
        href="/dashboard/global"
        className="flex items-center gap-1 text-on-surface-variant hover:text-primary transition-colors font-medium shrink-0"
      >
        <span className="material-symbols-outlined text-[16px]">home</span>
        <span className="hidden sm:inline">Accueil</span>
      </Link>

      {segments.map((segment, index) => {
        currentPath += `/${segment}`;
        const isLast = index === segments.length - 1;
        const label = ROUTE_LABELS[segment] || segment.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());

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
