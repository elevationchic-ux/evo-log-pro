'use client';

/**
 * Centre de pilotage ✈️ K-Transport Aérien (module genere, expansion).
 * Grille de registres reellement servis par /api/v1/transport-aerien : aucun chiffre
 * invente, aucune donnee factice. Chaque carte ouvre le registre correspondant ;
 * la lecture reste soumise aux habilitations du tenant.
 */
import Link from 'next/link';
import * as Icons from 'lucide-react';

import ModuleLayout from '@/components/layout/ModuleLayout';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';

const ENTITES = [
  { slug: 'aircraft-fleet', tcode: 'registre-aircraft-fleet', titre: 'Flotte aeronefs', titreEn: 'Aircraft fleet', description: 'Avions cargo, passagers et mixtes.', descriptionEn: 'Cargo, passenger and combi aircraft.', icon: 'Plane', perm: 'fleet' },
  { slug: 'air-waybills', tcode: 'registre-air-waybills', titre: 'Lia / lettres de transport aerien', titreEn: 'Air waybills', description: 'AWB maitre (MAWB) et secondaire (HAWB).', descriptionEn: 'Master (MAWB) and house (HAWB) air waybills.', icon: 'FileSignature', perm: 'awb' },
  { slug: 'slots-coordination', tcode: 'registre-slots-coordination', titre: 'Creneaux aeroportuaires', titreEn: 'Airport slots', description: 'Coordination IATA (BABY) des creneaux decollage/atterrissage.', descriptionEn: 'IATA (BABY) slot coordination for take-off/landing.', icon: 'Clock', perm: 'slots' },
  { slug: 'ground-handling', tcode: 'registre-ground-handling', titre: 'Traitement au sol', titreEn: 'Ground handling', description: 'Prestations au sol : passagers, fret, chargement, ravitaillement.', descriptionEn: 'Ground services: pax, cargo, load, fuelling.', icon: 'Package', perm: 'handling' },
  { slug: 'uld-management', tcode: 'registre-uld-management', titre: 'Parc ULD', titreEn: 'ULD inventory', description: 'Conteneurs et palettes aerienes (AKE, PAG, PMC).', descriptionEn: 'Air containers and pallets (AKE, PAG, PMC).', icon: 'Boxes', perm: 'uld' },
  { slug: 'cargo-security', tcode: 'registre-cargo-security', titre: 'Sûreté fret arien', titreEn: 'Air cargo security', description: 'Screening RC/AC/KC selon reglement (RA, KC, AC statuses).', descriptionEn: 'Screening per regulated agent / known consignor statuses.', icon: 'ScanLine', perm: 'security' },
  { slug: 'dangerous-goods-air', tcode: 'registre-dangerous-goods-air', titre: 'Marchandises dangereuses IATA', titreEn: 'IATA dangerous goods', description: 'DGD / etiquette / classe ONU conforme IATA DGR.', descriptionEn: 'IATA DGD / labels / UN class.', icon: 'AlertOctagon', perm: 'dgr' },
  { slug: 'flight-ops', tcode: 'registre-flight-ops', titre: 'Operations vol', titreEn: 'Flight operations', description: 'Plans de vol, NOTAM, METAR, reserves equipage.', descriptionEn: 'Flight plans, NOTAM, METAR, crew reserves.', icon: 'PlaneTakeoff', perm: 'flightops' },
  { slug: 'crew-scheduling', tcode: 'registre-crew-scheduling', titre: 'Navigation planning', titreEn: 'Crew scheduling', description: 'PNT (pilotes), PNC (Cabin), qualification ligne / aeronef.', descriptionEn: 'Flight deck (PNT), cabin (PNC), type/route qualification.', icon: 'Users', perm: 'crew' },
  { slug: 'aircraft-maintenance', tcode: 'registre-aircraft-maintenance', titre: 'Maintenance aeronefs (MRO)', titreEn: 'Aircraft maintenance', description: 'Checks A/B/C/D, lourdes, AD/SB applicables.', descriptionEn: 'A/B/C/D checks, heavy, applicable AD/SB.', icon: 'Wrench', perm: 'mro' },
  { slug: 'airport-cargo', tcode: 'registre-airport-cargo', titre: 'Terminal fret aerien', titreEn: 'Air cargo terminal', description: 'Magasinage, temperature, zone DCU / surete.', descriptionEn: 'Storage, temperature, security/Customs zones.', icon: 'Building2', perm: 'cargo' },
  { slug: 'air-tariffs', tcode: 'registre-air-tariffs', titre: 'Tarification aerienne', titreEn: 'Air freight tariffs', description: 'Grille TACT / CDG / surcharges carburant et securite.', descriptionEn: 'TACT/CDG rate grid + fuel/security surcharges.', icon: 'Calculator', perm: 'tariffs' },
];

export default function PageDashboardTransportAerien() {
  const can = useCan();
  const { language } = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  return (
    <ModuleLayout
      title={t('Centre de pilotage aerien', 'Centre de pilotage aerien')}
      description={t('Flotte, AWB maitres/secondaires, slots IATA, ULD et surete du fret', 'Fleet, master/house AWBs, IATA slots, ULD inventory and cargo security')}
      help={t(
        'Chaque carte ouvre un registre reellement servi par le serveur. Les compteurs ne sont affiches que lorsque la donnee existe.',
        'Each card opens a register actually served by the server. Counters are only shown when the data exists.',
      )}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {ENTITES.map((e) => {
          const Icon = (Icons as any)[e.icon] ?? Icons.Folder;
          const autorise = can('aerien.' + e.perm + '.read');
          return (
            <Link
              key={e.slug}
              href={'/transport-aerien/' + e.slug}
              className={`group rounded-2xl border p-4 transition ${autorise
                  ? 'border-slate-800 bg-slate-900/60 hover:border-fuchsia-700/70 hover:bg-slate-900'
                  : 'border-slate-800/60 bg-slate-950/40'
                }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className={`p-2 rounded-xl ${autorise ? 'bg-fuchsia-700 text-fuchsia-50' : 'bg-slate-800 text-slate-400' }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="font-mono text-[10px] text-slate-500 border border-slate-800 rounded px-1.5 py-0.5">
                  {e.tcode}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-semibold text-slate-100 group-hover:text-fuchsia-200">
                {lang === 'en' ? e.titreEn : e.titre}
              </h3>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400 line-clamp-2">
                {lang === 'en' ? e.descriptionEn : e.description}
              </p>
              {!autorise && (
                <p className="mt-2 text-[10px] font-semibold text-amber-300/90">
                  {t('Lecture soumise a ' + 'aerien.' + e.perm + '.read', 'Reading requires aerien.' + e.perm + '.read')}
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </ModuleLayout>
  );
}
