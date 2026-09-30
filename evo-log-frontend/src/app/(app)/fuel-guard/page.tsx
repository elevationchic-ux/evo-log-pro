'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { transportAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { Fuel, AlertTriangle, Search, RefreshCw, ArrowRight } from 'lucide-react';
import Link from 'next/link';

// Source réelle : /api/v1/transport/fuel (table fleet_carburant_records).
// Il n'existe aucun capteur IoT de niveau de réservoir dans le système : la
// détection de fraude travaille uniquement sur les tickets saisis, et l'écran
// le dit. Un ticket isolé n'a pas de delta_km → sa consommation reste nulle,
// jamais inventée.
type Ticket = {
  id: number;
  vehicule_id: number | null;
  immatriculation: string | null;
  numero_ticket: string | null;
  date_plein: string | null;
  litres: number;
  prix_litre: number | null;
  cout: number;
  station: string | null;
  kilometrage: number | null;
  delta_km: number | null;
  conso_l100: number | null;
  chauffeur: string | null;
  statut: string;
  notes: string | null;
};

type Carburant = {
  items: Ticket[];
  total: number;
  litres_total: number;
  cout_total: number;
  prix_moyen_litre: number;
};

// Seuils d'alerte : le seuil de consommation est aligné sur la vue Alertes
// (même règle métier), l'écart de prix est exprimé en multiple du prix moyen
// calculé sur les tickets réellement chargés.
const SEUIL_L100 = 45;
const FACTEUR_PRIX = 1.15;

export default function FuelGuardPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const [searchQuery, setSearchQuery] = useState('');
  const [seuilsOnly, setSeuilsOnly] = useState(false);

  const fuelQuery = useQuery({
    queryKey: ['fuel-guard-tickets'],
    queryFn: async () => {
      const res = await transportAPI.getFuel({ limit: 500 });
      const body = (res.data ?? res) as Partial<Carburant>;
      return {
        items: Array.isArray(body?.items) ? body.items : [],
        total: body?.total ?? 0,
        litres_total: body?.litres_total ?? 0,
        cout_total: body?.cout_total ?? 0,
        prix_moyen_litre: body?.prix_moyen_litre ?? 0,
      } as Carburant;
    },
  });

  const data = fuelQuery.data;
  const tickets = data?.items ?? [];
  const prixMoyen = data?.prix_moyen_litre ?? 0;

  const depasseSeuil = (tk: Ticket) =>
    (tk.conso_l100 != null && tk.conso_l100 > SEUIL_L100) ||
    (tk.prix_litre != null && prixMoyen > 0 && tk.prix_litre > prixMoyen * FACTEUR_PRIX) ||
    (!!tk.notes && /anomal|siphonn|alerte consommation/i.test(tk.notes));

  const filtered = tickets.filter((tk) => {
    if (seuilsOnly && !depasseSeuil(tk)) return false;
    const hay = `${tk.immatriculation ?? ''} ${tk.numero_ticket ?? ''} ${tk.station ?? ''} ${tk.chauffeur ?? ''}`;
    return hay.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const nbAlertes = tickets.filter(depasseSeuil).length;

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-xl">
        <div className="min-w-0">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-semibold mb-2 border border-cyan-500/20">
            <Fuel className="w-3.5 h-3.5 shrink-0" />
            {t('Transport & Flotte • Contrôle carburant', 'Transport & Fleet • Fuel control')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight break-words">
            {t('Tickets carburant & dérives de consommation', 'Fuel tickets & consumption drifts')}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {t('Analyse des pleins réellement enregistrés. Aucun capteur de niveau n’est branché sur la flotte.', 'Analysis of refuels actually recorded. No tank-level sensor is connected to the fleet.')}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={() => fuelQuery.refetch()}
            disabled={fuelQuery.isFetching}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${fuelQuery.isFetching ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <Link
            href="/fuel-guard/alerts"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-cyan-600/30 transition-colors"
          >
            <AlertTriangle className="w-4 h-4" />
            {t('Journal d’alertes', 'Alert log')}
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* KPI reels */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {[
          { label: t('Tickets enregistrés', 'Tickets recorded'), value: String(data?.total ?? '—') },
          { label: t('Litres cumulés', 'Total litres'), value: data ? `${data.litres_total.toLocaleString(loc)} L` : '—' },
          { label: t('Coût cumulé (XAF)', 'Total cost (XAF)'), value: data ? data.cout_total.toLocaleString(loc) : '—' },
          { label: t('Prix moyen / litre', 'Average price / litre'), value: data && prixMoyen > 0 ? `${prixMoyen.toLocaleString(loc)} XAF` : '—' },
        ].map((k) => (
          <div key={k.label} className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wider">{k.label}</div>
            <div className="text-lg sm:text-xl font-black font-mono text-cyan-400 mt-1 break-words">{k.value}</div>
          </div>
        ))}
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            {t('Derniers pleins', 'Latest refuels')}
            <span className="ml-2 text-xs font-mono text-slate-400">
              ({filtered.length}) • {nbAlertes} {t('au-dessus des seuils', 'above thresholds')}
            </span>
          </h3>

          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-3.5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('Immatriculation, ticket, station…', 'Plate, ticket, station…')}
                aria-label={t('Rechercher un ticket carburant', 'Search a fuel ticket')}
                className="min-h-[44px] w-full pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <button
              type="button"
              onClick={() => setSeuilsOnly((v) => !v)}
              aria-pressed={seuilsOnly}
              className={`min-h-[44px] px-4 rounded-xl text-sm font-semibold border transition-colors ${
                seuilsOnly
                  ? 'bg-cyan-600 border-cyan-500 text-white'
                  : 'bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-800'
              }`}
            >
              {t('Anomalies seules', 'Anomalies only')}
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">{t('Camion', 'Truck')}</th>
                <th className="px-6 py-4">{t('Date du plein', 'Refuel date')}</th>
                <th className="px-6 py-4 text-right">{t('Litres', 'Litres')}</th>
                <th className="px-6 py-4 text-right">{t('Prix / L', 'Price / L')}</th>
                <th className="px-6 py-4 text-right">{t('Coût (XAF)', 'Cost (XAF)')}</th>
                <th className="px-6 py-4 text-right">{t('Conso L/100km', 'Consumption L/100km')}</th>
                <th className="px-6 py-4">{t('Station', 'Station')}</th>
                <th className="px-6 py-4 text-right">{t('Contrôle', 'Check')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {fuelQuery.isLoading ? (
                <tr><td colSpan={8} className="p-12 text-center text-slate-400">{t('Chargement des tickets carburant…', 'Loading fuel tickets…')}</td></tr>
              ) : fuelQuery.isError ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-red-400">
                    {t('Les données carburant n’ont pas pu être chargées.', 'Fuel data could not be loaded.')}
                    <button
                      type="button"
                      onClick={() => fuelQuery.refetch()}
                      className="block mx-auto mt-3 min-h-[44px] px-4 py-2 rounded-xl border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800"
                    >
                      {t('Réessayer', 'Retry')}
                    </button>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-500">
                    {tickets.length === 0
                      ? t('Aucun ticket carburant enregistré.', 'No fuel ticket recorded.')
                      : t('Aucun ticket ne correspond au filtre.', 'No ticket matches the filter.')}
                  </td>
                </tr>
              ) : (
                filtered.map((tk) => {
                  const anomalie = depasseSeuil(tk);
                  return (
                    <tr key={tk.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-100 font-mono whitespace-nowrap">
                        {tk.immatriculation || `#${tk.vehicule_id ?? tk.id}`}
                        {tk.numero_ticket ? (
                          <div className="text-[11px] font-normal text-slate-500 font-mono">{tk.numero_ticket}</div>
                        ) : null}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {tk.date_plein ? new Date(tk.date_plein).toLocaleString(loc, { dateStyle: 'short', timeStyle: 'short' }) : '—'}
                      </td>
                      <td className="px-6 py-4 text-right font-mono">{tk.litres.toLocaleString(loc)}</td>
                      <td className="px-6 py-4 text-right font-mono">{tk.prix_litre != null ? tk.prix_litre.toLocaleString(loc) : '—'}</td>
                      <td className="px-6 py-4 text-right font-mono">{tk.cout.toLocaleString(loc)}</td>
                      <td className="px-6 py-4 text-right font-mono">
                        {tk.conso_l100 != null
                          ? tk.conso_l100.toLocaleString(loc, { maximumFractionDigits: 1 })
                          : t('— (index manquant)', '— (odometer missing)')}
                      </td>
                      <td className="px-6 py-4 text-xs max-w-[180px] truncate" title={tk.station ?? undefined}>
                        {tk.station || '—'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${
                          anomalie ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-slate-600/20 text-slate-300 border-slate-600/40'
                        }`}>
                          {anomalie ? t('À contrôler', 'To review') : t('Nominal', 'Nominal')}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-xs text-slate-500">
        {t(
          `Seuils appliqués : consommation > ${SEUIL_L100} L/100 km, prix au litre > ${Math.round((FACTEUR_PRIX - 1) * 100)} % du prix moyen de la période, ou note signalant une anomalie.`,
          `Thresholds applied: consumption above ${SEUIL_L100} L/100 km, litre price above ${Math.round((FACTEUR_PRIX - 1) * 100)} % of the period average, or a note flagging an anomaly.`
        )}
      </p>
    </div>
  );
}
