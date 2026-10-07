'use client';

/**
 * Centre de pilotage ⛴️ K-Transport Fluvial (module genere, expansion).
 * Grille de registres reellement servis par /api/v1/transport-fluvial : aucun chiffre
 * invente, aucune donnee factice. Chaque carte ouvre le registre correspondant ;
 * la lecture reste soumise aux habilitations du tenant.
 */
import Link from 'next/link';
import * as Icons from 'lucide-react';

import ModuleLayout from '@/components/layout/ModuleLayout';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';

const ENTITES = [
  { slug: 'barge-fleet', tcode: 'registre-barge-fleet', titre: 'Flotte peniches / chalands', titreEn: 'Barge fleet', description: 'Referentiel peniches, chalands et automoteurs fluviaux.', descriptionEn: 'Barges, lighters and self-propelled craft.', icon: 'Ship', perm: 'barge_fleet' },
  { slug: 'tow-fleet', tcode: 'registre-tow-fleet', titre: 'Remorqueurs fluviaux', titreEn: 'River tug fleet', description: 'Remorqueurs d\'estuaire et de voie interieure.', descriptionEn: 'Estuary and inland waterway tugs.', icon: 'Anchor', perm: 'tow_fleet' },
  { slug: 'lock-transits', tcode: 'registre-lock-transits', titre: 'Transits d\'ecluses', titreEn: 'Lock transits', description: 'Passages d\'ecluses avec horaires, poids, dimensions.', descriptionEn: 'Lock passages with timing, weight, dimensions.', icon: 'DoorOpen', perm: 'locks' },
  { slug: 'river-depth', tcode: 'registre-river-depth', titre: 'Sondes bathymetriques', titreEn: 'River depth surveys', description: 'Mesures periodiques de fond de voie / seuils / tirant d\'eau pratique.', descriptionEn: 'Periodic bed / threshold / practical draft survey.', icon: 'Ruler', perm: 'depth' },
  { slug: 'river-ports', tcode: 'registre-river-ports', titre: 'Terminaux fluviaux', titreEn: 'River terminals', description: 'Quais, appontements et zones de transbordement fluvial.', descriptionEn: 'Quays, jetties and transshipment areas.', icon: 'Warehouse', perm: 'terminals' },
  { slug: 'bulk-river', tcode: 'registre-bulk-river', titre: 'Vrac fluvial', titreEn: 'River bulk operations', description: 'Chargement/dechargement vrac solide ou liquide.', descriptionEn: 'Bulk solid or liquid loading/unloading.', icon: 'Droplet', perm: 'bulk' },
  { slug: 'navigation-safety', tcode: 'registre-navigation-safety', titre: 'Securite navigation', titreEn: 'Navigation safety', description: 'Balises, accidents, secours, arret technique.', descriptionEn: 'Beacons, incidents, rescue, technical stops.', icon: 'LifeBuoy', perm: 'safety' },
  { slug: 'river-tariffs', tcode: 'registre-river-tariffs', titre: 'Tarification fluviale', titreEn: 'River tariffs', description: 'Prix par tonne / km selon bief et type produit.', descriptionEn: 'Price per ton-km per reach and product.', icon: 'Calculator', perm: 'tariffs' },
  { slug: 'river-waybills', tcode: 'registre-river-waybills', titre: 'Lettres de voiture fluviale CMNI', titreEn: 'CMNI inland waybills', description: 'Titres de transport CMNI / nationaux fluviaux.', descriptionEn: 'CMNI or national inland waybills.', icon: 'FileText', perm: 'waybills' },
  { slug: 'fleet-positioning', tcode: 'registre-fleet-positioning', titre: 'Positionnement flotte fluviale', titreEn: 'Fleet positioning', description: 'AIS fluvial / GPS / VHF positionnement temps reel.', descriptionEn: 'Inland AIS / GPS / VHF real-time positioning.', icon: 'MapPinned', perm: 'positions' },
];

export default function PageDashboardTransportFluvial() {
  const can = useCan();
  const { language } = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  return (
    <ModuleLayout
      title={t('Centre de pilotage fluvial', 'Centre de pilotage fluvial')}
      description={t('Flotte fluviale, transits d\'ecluses, sondes, terminaux et lettres de voiture CMNI', 'River fleet, lock transits, depth surveys, terminals and CMNI waybills')}
      help={t(
        'Chaque carte ouvre un registre reellement servi par le serveur. Les compteurs ne sont affiches que lorsque la donnee existe.',
        'Each card opens a register actually served by the server. Counters are only shown when the data exists.',
      )}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {ENTITES.map((e) => {
          const Icon = (Icons as any)[e.icon] ?? Icons.Folder;
          const autorise = can('fluvial.' + e.perm + '.read');
          return (
            <Link
              key={e.slug}
              href={'/transport-fluvial/' + e.slug}
              className={`group rounded-2xl border p-4 transition ${autorise
                  ? 'border-slate-800 bg-slate-900/60 hover:border-teal-700/70 hover:bg-slate-900'
                  : 'border-slate-800/60 bg-slate-950/40'
                }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className={`p-2 rounded-xl ${autorise ? 'bg-teal-700 text-teal-50' : 'bg-slate-800 text-slate-400' }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="font-mono text-[10px] text-slate-500 border border-slate-800 rounded px-1.5 py-0.5">
                  {e.tcode}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-semibold text-slate-100 group-hover:text-teal-200">
                {lang === 'en' ? e.titreEn : e.titre}
              </h3>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400 line-clamp-2">
                {lang === 'en' ? e.descriptionEn : e.description}
              </p>
              {!autorise && (
                <p className="mt-2 text-[10px] font-semibold text-amber-300/90">
                  {t('Lecture soumise a ' + 'fluvial.' + e.perm + '.read', 'Reading requires fluvial.' + e.perm + '.read')}
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </ModuleLayout>
  );
}
