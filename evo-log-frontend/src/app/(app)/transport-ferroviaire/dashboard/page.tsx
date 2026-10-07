'use client';

/**
 * Centre de pilotage 🚆 K-Transport Ferroviaire (module genere, expansion).
 * Grille de registres reellement servis par /api/v1/transport-ferroviaire : aucun chiffre
 * invente, aucune donnee factice. Chaque carte ouvre le registre correspondant ;
 * la lecture reste soumise aux habilitations du tenant.
 */
import Link from 'next/link';
import * as Icons from 'lucide-react';

import ModuleLayout from '@/components/layout/ModuleLayout';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';

const ENTITES = [
  { slug: 'wagon-fleet', tcode: 'registre-wagon-fleet', titre: 'Parc wagons', titreEn: 'Rail wagon fleet', description: 'Referentiel des wagons du parc fret (couvert, tombereau, citerne, plateau, porte-conteneurs).', descriptionEn: 'Fleet register of freight wagons (box, gondola, tank, flat, container).', icon: 'TrainFront', perm: 'wagon_fleet' },
  { slug: 'locomotive-fleet', tcode: 'registre-locomotive-fleet', titre: 'Parc locomotives', titreEn: 'Locomotive fleet', description: 'Locomotives electriques, diesels et rames automotrices.', descriptionEn: 'Electric, diesel and EMU fleet.', icon: 'TrainTrack', perm: 'locomotive_fleet' },
  { slug: 'train-paths', tcode: 'registre-train-paths', titre: 'Sillons de circulation', titreEn: 'Train paths', description: 'Graphique des sillons attribues par le gestionnaire d\'infrastructure.', descriptionEn: 'Path allocation by infrastructure manager.', icon: 'CalendarClock', perm: 'train_paths' },
  { slug: 'shunting-yards', tcode: 'registre-shunting-yards', titre: 'Gares de triage', titreEn: 'Shunting yards', description: 'Installations de tri et de formation des rames.', descriptionEn: 'Classification and marshalling installations.', icon: 'Layers', perm: 'shunting_yards' },
  { slug: 'rail-terminals', tcode: 'registre-rail-terminals', titre: 'Terminaux fer portuaires', titreEn: 'Port rail terminals', description: 'Interfaces terminal portuaire / reseau fer (relic modal).', descriptionEn: 'Port-rail interface for modal shift.', icon: 'Container', perm: 'rail_terminals' },
  { slug: 'consistency-plans', tcode: 'registre-consistency-plans', titre: 'Plans de composition', titreEn: 'Train composition plans', description: 'Description de la composition theorique d\'un train (ordre, masse, longueur).', descriptionEn: 'Theoretical composition per train (order, mass, length).', icon: 'ListOrdered', perm: 'consistency' },
  { slug: 'waybills-rail', tcode: 'registre-waybills-rail', titre: 'Lettres de voiture CIM/OTIF', titreEn: 'CIM/OTIF waybills', description: 'Titres de transport fer internationaux (CIM) ou nationaux.', descriptionEn: 'CIM or domestic rail consignment notes.', icon: 'FileText', perm: 'waybills' },
  { slug: 'rail-tariffs', tcode: 'registre-rail-tariffs', titre: 'Tarification fret fer', titreEn: 'Rail freight tariffs', description: 'Grille tarifaire par relation, type marchandise et tonnage.', descriptionEn: 'Tariff grid by relation, commodity and tonnage.', icon: 'Calculator', perm: 'tariffs' },
  { slug: 'wagon-tracking', tcode: 'registre-wagon-tracking', titre: 'Suivi wagons / telegrammes RID', titreEn: 'Wagon tracking / RID telegrams', description: 'Position et etat de chaque wagon en temps reel via CID/TELEGRAMMES.', descriptionEn: 'Real-time wagon position via CID/RID telegrams.', icon: 'MapPin', perm: 'tracking' },
  { slug: 'wagon-maintenance', tcode: 'registre-wagon-maintenance', titre: 'Maintenance parc wagon', titreEn: 'Wagon maintenance', description: 'Ateliers, revisions periodiques et immobilisations techniques.', descriptionEn: 'Workshops, periodic overhauls and technical holds.', icon: 'Wrench', perm: 'maintenance' },
  { slug: 'rail-safety', tcode: 'registre-rail-safety', titre: 'Securite circulations', titreEn: 'Circulation safety', description: 'ETCS / signalisation / incidents securite ferroviaire.', descriptionEn: 'ETCS, signalling and safety incidents.', icon: 'ShieldAlert', perm: 'safety' },
  { slug: 'intermodal-corridors', tcode: 'registre-intermodal-corridors', titre: 'Corridors fer-port', titreEn: 'Rail-port corridors', description: 'Cartographie des corridors logistiques (Dorsal, Abidjan-Lagos, Douane Yaounde-Douala).', descriptionEn: 'Map of logistics corridors (Dorsal, Abidjan-Lagos, Yaounde-Douala customs).', icon: 'Route', perm: 'corridors' },
];

export default function PageDashboardTransportFerroviaire() {
  const can = useCan();
  const { language } = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  return (
    <ModuleLayout
      title={t('Centre de pilotage ferroviaire', 'Centre de pilotage ferroviaire')}
      description={t('Parc wagons/locomotives, sillons, lettres de voiture CIM et corridors fer-port', 'Wagon and locomotive fleet, train paths, CIM waybills and rail-port corridors')}
      help={t(
        'Chaque carte ouvre un registre reellement servi par le serveur. Les compteurs ne sont affiches que lorsque la donnee existe.',
        'Each card opens a register actually served by the server. Counters are only shown when the data exists.',
      )}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {ENTITES.map((e) => {
          const Icon = (Icons as any)[e.icon] ?? Icons.Folder;
          const autorise = can('ferroviaire.' + e.perm + '.read');
          return (
            <Link
              key={e.slug}
              href={'/transport-ferroviaire/' + e.slug}
              className={`group rounded-2xl border p-4 transition ${autorise
                  ? 'border-slate-800 bg-slate-900/60 hover:border-indigo-700/70 hover:bg-slate-900'
                  : 'border-slate-800/60 bg-slate-950/40'
                }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className={`p-2 rounded-xl ${autorise ? 'bg-indigo-700 text-indigo-50' : 'bg-slate-800 text-slate-400' }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="font-mono text-[10px] text-slate-500 border border-slate-800 rounded px-1.5 py-0.5">
                  {e.tcode}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-semibold text-slate-100 group-hover:text-indigo-200">
                {lang === 'en' ? e.titreEn : e.titre}
              </h3>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400 line-clamp-2">
                {lang === 'en' ? e.descriptionEn : e.description}
              </p>
              {!autorise && (
                <p className="mt-2 text-[10px] font-semibold text-amber-300/90">
                  {t('Lecture soumise a ' + 'ferroviaire.' + e.perm + '.read', 'Reading requires ferroviaire.' + e.perm + '.read')}
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </ModuleLayout>
  );
}
