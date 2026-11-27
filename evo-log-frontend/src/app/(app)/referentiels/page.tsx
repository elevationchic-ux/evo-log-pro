'use client';

import React from 'react';
import Link from 'next/link';

const DOMAINES = [
      { href: '/admin-saas/donnees', label: 'Admin Saas' },
      { href: '/admin-saas/donnees', label: 'Admin Saas' },
      { href: '/admin-tenant/donnees', label: 'Admin Tenant' },
      { href: '/amenagement-portuaire/donnees', label: 'Amenagement Portuaire' },
      { href: '/amenagement-portuaire/donnees', label: 'Amenagement Portuaire' },
      { href: '/annuaire-prestataires/donnees', label: 'Annuaire Prestataires' },
      { href: '/chaine-froid/donnees', label: 'Chaine Froid' },
      { href: '/chaine-froid/donnees', label: 'Chaine Froid' },
      { href: '/chat/donnees', label: 'Chat' },
      { href: '/chef-personnel/donnees', label: 'Chef Personnel' },
      { href: '/client-b2b/donnees', label: 'Client B2B' },
      { href: '/client-b2b/donnees', label: 'Client B2B' },
      { href: '/convoi-exceptionnel/donnees', label: 'Convoi Exceptionnel' },
      { href: '/convoi-exceptionnel/donnees', label: 'Convoi Exceptionnel' },
      { href: '/courier-express/donnees', label: 'Courier Express' },
      { href: '/courier-express/donnees', label: 'Courier Express' },
      { href: '/dashboard/donnees', label: 'Dashboard' },
      { href: '/dashboard/donnees', label: 'Dashboard' },
      { href: '/departement/donnees', label: 'Departement' },
      { href: '/finance-ohada/donnees', label: 'Finance Ohada' },
      { href: '/finance-ohada/donnees', label: 'Finance Ohada' },
      { href: '/logistique-3pl/donnees', label: 'Logistique 3Pl' },
      { href: '/logistique-3pl/donnees', label: 'Logistique 3Pl' },
      { href: '/magasin-stock/donnees', label: 'Magasin Stock' },
      { href: '/magasin-stock/donnees', label: 'Magasin Stock' },
      { href: '/maintenance-industrielle/donnees', label: 'Maintenance Industrielle' },
      { href: '/parc-vehicules/donnees', label: 'Parc Vehicules' },
      { href: '/parc-vehicules/donnees', label: 'Parc Vehicules' },
      { href: '/pipeline-oleoduc/donnees', label: 'Pipeline Oleoduc' },
      { href: '/pipeline-oleoduc/donnees', label: 'Pipeline Oleoduc' },
      { href: '/port-operations/donnees', label: 'Port Operations' },
      { href: '/port-operations/donnees', label: 'Port Operations' },
      { href: '/portail-chauffeur/donnees', label: 'Portail Chauffeur' },
      { href: '/portail-collaborateur/donnees', label: 'Portail Collaborateur' },
      { href: '/portail-commercial/donnees', label: 'Portail Commercial' },
      { href: '/portail-commercial/donnees', label: 'Portail Commercial' },
      { href: '/portail-declarant/donnees', label: 'Portail Declarant' },
      { href: '/portail-employe/donnees', label: 'Portail Employe' },
      { href: '/portail-frais/donnees', label: 'Portail Frais' },
      { href: '/portail-magasinier/donnees', label: 'Portail Magasinier' },
      { href: '/portail-qhse/donnees', label: 'Portail Qhse' },
      { href: '/portail-technicien/donnees', label: 'Portail Technicien' },
      { href: '/qhse-securite/donnees', label: 'Qhse Securite' },
      { href: '/qhse-securite/donnees', label: 'Qhse Securite' },
      { href: '/reports-bi/donnees', label: 'Reports Bi' },
      { href: '/reports-bi/donnees', label: 'Reports Bi' },
      { href: '/rh-personnel/donnees', label: 'Rh Personnel' },
      { href: '/rh-personnel/donnees', label: 'Rh Personnel' },
      { href: '/superadmin-cadc/donnees', label: 'Superadmin Cadc' },
      { href: '/superadmin-cadc/donnees', label: 'Superadmin Cadc' },
      { href: '/tracabilite/donnees', label: 'Tracabilite' },
      { href: '/transit-douane/donnees', label: 'Transit Douane' },
      { href: '/transit-douane/donnees', label: 'Transit Douane' },
      { href: '/transport-aerien/donnees', label: 'Transport Aerien' },
      { href: '/transport-aerien/donnees', label: 'Transport Aerien' },
      { href: '/transport-ferroviaire/donnees', label: 'Transport Ferroviaire' },
      { href: '/transport-ferroviaire/donnees', label: 'Transport Ferroviaire' },
      { href: '/transport-flotte/donnees', label: 'Transport Flotte' },
      { href: '/transport-flotte/donnees', label: 'Transport Flotte' },
      { href: '/transport-fluvial/donnees', label: 'Transport Fluvial' },
      { href: '/transport-fluvial/donnees', label: 'Transport Fluvial' },
];

export default function ReferentielsPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Registres de donnees</h1>
        <p className="text-sm text-gray-500">
          Acces CRUD aux registres profonds de chaque domaine (données réelles).
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {DOMAINES.map((d) => (
          <Link key={d.href} href={d.href}
            className="bg-white border rounded-xl p-4 shadow-sm hover:border-blue-400 transition-colors">
            <p className="font-medium text-sm">{d.label}</p>
            <p className="text-xs text-gray-400 mt-1">{d.href}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
