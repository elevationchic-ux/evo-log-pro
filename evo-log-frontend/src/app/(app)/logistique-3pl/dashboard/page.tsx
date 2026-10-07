'use client';

/**
 * Centre de pilotage 📦 K-Logistique 3PL (module genere, expansion).
 * Grille de registres reellement servis par /api/v1/logistique-3pl : aucun chiffre
 * invente, aucune donnee factice. Chaque carte ouvre le registre correspondant ;
 * la lecture reste soumise aux habilitations du tenant.
 */
import Link from 'next/link';
import * as Icons from 'lucide-react';

import ModuleLayout from '@/components/layout/ModuleLayout';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';

const ENTITES = [
  { slug: 'contract-agreements', tcode: 'registre-contract-agreements', titre: 'Contrats cadres 3PL', titreEn: '3PL framework contracts', description: 'Accords de sous-traitance logistique longue duree.', descriptionEn: 'Long-term logistics outsourcing agreements.', icon: 'FileSignature', perm: 'contracts' },
  { slug: 'warehouse-3pl', tcode: 'registre-warehouse-3pl', titre: 'Entrepots sous contrat', titreEn: 'Contracted warehouses', description: 'Sites 3PL engages avec client donneur d\'ordre.', descriptionEn: 'Sites committed under client contract.', icon: 'Building', perm: 'warehouses' },
  { slug: 'crossdock-plans', tcode: 'registre-crossdock-plans', titre: 'Plans cross-dock', titreEn: 'Cross-dock plans', description: 'Flux de transit rapide sans stockage.', descriptionEn: 'Fast-throughput no-storage flows.', icon: 'ArrowLeftRight', perm: 'crossdock' },
  { slug: 'pick-pack-lines', tcode: 'registre-pick-pack-lines', titre: 'Lignes de preparation', titreEn: 'Picking / packing lines', description: 'Ordres de preparation client, picking / packing / shipping.', descriptionEn: 'Client order preparation, picking / packing / shipping.', icon: 'ClipboardList', perm: 'pickpack' },
  { slug: 'kpi-slas', tcode: 'registre-kpi-slas', titre: 'KPI / SLA contractuels', titreEn: 'SLA / KPI contractual', description: 'Taux de service, OTIF, erreurs, penalites.', descriptionEn: 'Service rate, OTIF, errors, penalties.', icon: 'Target', perm: 'slakpi' },
  { slug: 'billing-3pl', tcode: 'registre-billing-3pl', titre: 'Facturation 3PL', titreEn: '3PL billing', description: 'Facturation mensuelle des prestations logistiques.', descriptionEn: 'Monthly logistics service billing.', icon: 'Receipt', perm: 'billing' },
  { slug: 'inventory-valuation', tcode: 'registre-inventory-valuation', titre: 'Valorisation stock client', titreEn: 'Client inventory valuation', description: 'Inventaires periodiques et valorisation aux conditions contractuelles.', descriptionEn: 'Periodic stock-take under contractual rules.', icon: 'Scale', perm: 'valuation' },
  { slug: 'sub-3pl-providers', tcode: 'registre-sub-3pl-providers', titre: 'Sous-traitants secondaires', titreEn: 'Sub-contractors', description: 'Prestataires appeles par le 3PL principal (carriers, handlers).', descriptionEn: 'Secondary providers engaged by the lead 3PL.', icon: 'Users', perm: 'subcontractors' },
  { slug: 'reverse-logistics', tcode: 'registre-reverse-logistics', titre: 'Logistique retour / SAV', titreEn: 'Reverse logistics', description: 'Retour produit, reconditionnement, recycling, destruction.', descriptionEn: 'Product returns, refurbish, recycle, dispose.', icon: 'Recycle', perm: 'reverse' },
  { slug: 'control-tower', tcode: 'registre-control-tower', titre: 'Tour de controle multi-flux', titreEn: 'Multi-flow control tower', description: 'Pilotage transversal commandes, stock, transport, incidents.', descriptionEn: 'Cross-cutting order/stock/transport/incident command.', icon: 'RadioTower', perm: 'controltower' },
];

export default function PageDashboardLogistique3pl() {
  const can = useCan();
  const { language } = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  return (
    <ModuleLayout
      title={t('Tour de controle 3PL', 'Tour de controle 3PL')}
      description={t('Contrats clients, entrepot sous contrat, pick&pack, cross-dock, KPI SLA et facturation 3PL', 'Client contracts, contracted warehouse, pick&pack, cross-dock, SLA KPIs and 3PL billing')}
      help={t(
        'Chaque carte ouvre un registre reellement servi par le serveur. Les compteurs ne sont affiches que lorsque la donnee existe.',
        'Each card opens a register actually served by the server. Counters are only shown when the data exists.',
      )}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {ENTITES.map((e) => {
          const Icon = (Icons as any)[e.icon] ?? Icons.Folder;
          const autorise = can('log3pl.' + e.perm + '.read');
          return (
            <Link
              key={e.slug}
              href={'/logistique-3pl/' + e.slug}
              className={`group rounded-2xl border p-4 transition ${autorise
                  ? 'border-slate-800 bg-slate-900/60 hover:border-orange-700/70 hover:bg-slate-900'
                  : 'border-slate-800/60 bg-slate-950/40'
                }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className={`p-2 rounded-xl ${autorise ? 'bg-orange-700 text-orange-50' : 'bg-slate-800 text-slate-400' }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="font-mono text-[10px] text-slate-500 border border-slate-800 rounded px-1.5 py-0.5">
                  {e.tcode}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-semibold text-slate-100 group-hover:text-orange-200">
                {lang === 'en' ? e.titreEn : e.titre}
              </h3>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400 line-clamp-2">
                {lang === 'en' ? e.descriptionEn : e.description}
              </p>
              {!autorise && (
                <p className="mt-2 text-[10px] font-semibold text-amber-300/90">
                  {t('Lecture soumise a ' + 'log3pl.' + e.perm + '.read', 'Reading requires log3pl.' + e.perm + '.read')}
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </ModuleLayout>
  );
}
