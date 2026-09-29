'use client';

/**
 * K-Magasin  Taux d'occupation des entrepôts.
 *
 * Source unique : GET /api/magasin/entrepots/occupation, qui agrège les
 * stockages réellement persistés. L'API ne connaît pas la surface occupée :
 * elle renvoie `occupancy = null` dès qu'aucune capacité n'a été enregistrée
 * sur l'entrepôt. Dans ce cas on affiche l'article et la valeur stockée
 * réels, et on le dit  aucun pourcentage n'est inventé.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { toast } from 'sonner';
import {
  Warehouse, RefreshCw, Download, Search, AlertTriangle,
  Boxes, ArrowDownWideNarrow, Gauge,
} from 'lucide-react';
import { magasinAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { classifyApiError, type ApiErrorInfo } from '@/hooks/useApi';

interface ZoneRow {
  entrepot_id: number;
  zone: string;
  nb_articles: number;
  valeur_stockee: number;
  occupancy: number | null;
}

const SEUIL_SATURE = 90;
const SEUIL_CHARGE = 70;

/** Couleur de la barre selon le taux réellement calculé côté serveur. */
function occupancyTone(rate: number | null): string {
  if (rate === null) return 'bg-slate-600';
  if (rate >= SEUIL_SATURE) return 'bg-red-500';
  if (rate >= SEUIL_CHARGE) return 'bg-amber-500';
  return 'bg-emerald-500';
}

export default function MagasinCapacityPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = useCallback(
    (fr: string, en: string) => (lang === 'en' ? en : fr),
    [lang],
  );
  const locale = lang === 'en' ? 'en-GB' : 'fr-FR';

  const [zones, setZones] = useState<ZoneRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiErrorInfo | null>(null);
  const [search, setSearch] = useState('');
  const [sortDesc, setSortDesc] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await magasinAPI.getEntrepotsOccupation();
      const rows = res.data?.zones;
      setZones(Array.isArray(rows) ? rows : []);
    } catch (err) {
      setError(classifyApiError(err));
      setZones([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const money = useMemo(
    () => new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }),
    [locale],
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const rows = q
      ? zones.filter((z) => z.zone.toLowerCase().includes(q))
      : [...zones];
    // Les capacités connues ouvrent le classement, les null ferment toujours.
    return rows.sort((a, b) => {
      const av = a.occupancy ?? -1;
      const bv = b.occupancy ?? -1;
      return sortDesc ? bv - av : av - bv;
    });
  }, [zones, search, sortDesc]);

  const kpis = useMemo(() => {
    const avecCapacite = zones.filter((z) => z.occupancy !== null);
    const satures = avecCapacite.filter((z) => (z.occupancy ?? 0) >= SEUIL_SATURE);
    const totalArticles = zones.reduce((acc, z) => acc + (z.nb_articles || 0), 0);
    const totalValeur = zones.reduce((acc, z) => acc + (z.valeur_stockee || 0), 0);
    const tauxMoyen = avecCapacite.length
      ? avecCapacite.reduce((acc, z) => acc + (z.occupancy ?? 0), 0) / avecCapacite.length
      : null;
    return { avecCapacite, satures, totalArticles, totalValeur, tauxMoyen };
  }, [zones]);

  const exportCsv = useCallback(() => {
    if (!filtered.length) return;
    const entetes = [
      t('Entrepôt', 'Warehouse'),
      t('Articles', 'Items'),
      t('Valeur stockée', 'Stock value'),
      t('Occupation %', 'Occupancy %'),
    ];
    const lignes = filtered.map((z) => [
      z.zone,
      String(z.nb_articles),
      String(z.valeur_stockee),
      z.occupancy === null ? t('capacité non enregistrée', 'capacity not registered') : String(z.occupancy),
    ]);
    const csv = [entetes, ...lignes]
      .map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(';'))
      .join('\n');
    const url = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `occupation-entrepots-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(t('Export généré depuis les données affichées.', 'Export built from the displayed data.'));
  }, [filtered, t]);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3 min-w-0">
          <div className="p-2.5 bg-amber-500/10 rounded-xl text-amber-400 shrink-0">
            <Warehouse className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              {t("Taux d'occupation", 'Occupancy rate')}
            </h1>
            <p className="text-sm text-on-surface-variant">
              {t(
                'Surface et volume calculés depuis les stocks réellement enregistrés.',
                'Footprint and volume computed from actually recorded stock.',
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={load}
            disabled={loading}
            aria-label={t('Recharger', 'Reload')}
            className="p-2.5 min-h-11 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            type="button"
            onClick={exportCsv}
            disabled={!filtered.length}
            className="flex items-center gap-1.5 px-4 py-2 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface hover:bg-surface-container disabled:opacity-50"
          >
            <Download className="w-4 h-4" /> {t('Exporter', 'Export')}
          </button>
        </div>
      </div>

      {/* KPI agrégés depuis les lignes réelles */}
      {!loading && !error && zones.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-4 bg-surface border border-outline rounded-2xl">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Entrepôts suivis', 'Warehouses tracked')}
            </div>
            <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">{zones.length}</div>
          </div>
          <div className="p-4 bg-surface border border-outline rounded-2xl">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Articles en stock', 'Items in stock')}
            </div>
            <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">
              {money.format(kpis.totalArticles)}
            </div>
          </div>
          <div className="p-4 bg-surface border border-outline rounded-2xl">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Valeur stockée (XAF)', 'Stock value (XAF)')}
            </div>
            <div className="mt-1 text-2xl font-bold text-on-surface tabular-nums">
              {money.format(kpis.totalValeur)}
            </div>
          </div>
          <div className={`p-4 border rounded-2xl ${kpis.satures.length ? 'bg-red-500/10 border-red-500/30' : 'bg-surface border-outline'}`}>
            <div className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant">
              {t('Capacités connues', 'Capacities known')}
            </div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-on-surface tabular-nums">
                {kpis.tauxMoyen === null ? '' : `${kpis.tauxMoyen.toFixed(1)} %`}
              </span>
              {kpis.satures.length > 0 && (
                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-red-400">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  {t(`${kpis.satures.length} saturé(s)`, `${kpis.satures.length} saturated`)}
                </span>
              )}
            </div>
            <p className="mt-1 text-[11px] text-on-surface-variant">
              {t(
                `${kpis.avecCapacite.length} entrepôt(s) avec capacité enregistrée sur ${zones.length}.`,
                `${kpis.avecCapacite.length} of ${zones.length} warehouses have a registered capacity.`,
              )}
            </p>
          </div>
        </div>
      )}

      {/* Barre de filtres */}
      {!loading && !error && zones.length > 0 && (
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t('Rechercher un entrepôt…', 'Search a warehouse…')}
              aria-label={t('Rechercher un entrepôt', 'Search a warehouse')}
              className="w-full pl-9 pr-4 py-2.5 min-h-11 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-amber-500"
            />
          </div>
          <button
            type="button"
            onClick={() => setSortDesc((v) => !v)}
            className="flex items-center justify-center gap-1.5 px-4 py-2.5 min-h-11 text-xs font-semibold rounded-xl border border-outline text-on-surface hover:bg-surface-container"
          >
            <ArrowDownWideNarrow className="w-4 h-4" />
            {sortDesc ? t('Taux décroissant', 'Rate descending') : t('Taux croissant', 'Rate ascending')}
          </button>
        </div>
      )}

      {/* Corps */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-6">
            <DataLoadingState rows={5} />
          </div>
        ) : error ? (
          <div className="p-6">
            <DataErrorState error={error} onRetry={load} />
          </div>
        ) : zones.length === 0 ? (
          <DataEmptyState
            title={t('Aucun entrepôt enregistré', 'No warehouse registered')}
            description={t(
              "L'occupation se calcule à partir des entrepôts et des stocks créés dans la base. Aucun n'est encore enregistré.",
              'Occupancy is derived from warehouses and stock created in the database. None is registered yet.',
            )}
            actionLabel={t('Créer un entrepôt', 'Create a warehouse')}
            actionHref="/magasin/magasins"
          />
        ) : filtered.length === 0 ? (
          <DataEmptyState
            title={t('Aucun entrepôt ne correspond', 'No matching warehouse')}
            description={t(`Recherche : « ${search} ».`, `Search: "${search}".`)}
            actionLabel={t('Effacer la recherche', 'Clear search')}
            onAction={() => setSearch('')}
          />
        ) : (
          <ul className="divide-y divide-outline/40">
            {filtered.map((z) => {
              const rate = z.occupancy;
              return (
                <li key={z.entrepot_id} className="p-4 sm:p-5 hover:bg-surface-container/40 transition-colors">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    <div className="flex items-center gap-3 min-w-0 sm:w-64 shrink-0">
                      <Boxes className="w-4 h-4 text-amber-400 shrink-0" />
                      <div className="min-w-0">
                        <div className="font-semibold text-on-surface truncate" title={z.zone}>
                          {z.zone}
                        </div>
                        <div className="text-[11px] text-on-surface-variant tabular-nums">
                          {t(
                            `${money.format(z.nb_articles)} article(s)`,
                            `${money.format(z.nb_articles)} item(s)`,
                          )}
                          {' · '}
                          {money.format(z.valeur_stockee)} XAF
                        </div>
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      {rate === null ? (
                        <div className="flex items-center gap-2 text-xs text-on-surface-variant">
                          <Gauge className="w-4 h-4 text-slate-500" />
                          <span>
                            {t(
                              "Capacité d'entreposage non enregistrée  pourcentage non calculable.",
                              'Storage capacity not registered  percentage cannot be computed.',
                            )}
                          </span>
                          <Link
                            href="/magasin/magasins"
                            className="font-semibold text-amber-400 hover:underline shrink-0"
                          >
                            {t('Renseigner', 'Set it up')}
                          </Link>
                        </div>
                      ) : (
                        <>
                          <div
                            className="h-2.5 w-full rounded-full bg-slate-800 overflow-hidden"
                            role="progressbar"
                            aria-valuenow={Math.round(rate)}
                            aria-valuemin={0}
                            aria-valuemax={100}
                            aria-label={`${z.zone}  ${t('occupation', 'occupancy')}`}
                          >
                            <div
                              className={`h-full rounded-full ${occupancyTone(rate)} transition-all`}
                              style={{ width: `${Math.min(100, Math.max(2, rate))}%` }}
                            />
                          </div>
                          <div className="mt-1 flex items-center justify-between text-[11px]">
                            <span className="font-semibold text-on-surface tabular-nums">
                              {rate.toFixed(1)} %
                            </span>
                            <span
                              className={`font-semibold ${
                                rate >= SEUIL_SATURE
                                  ? 'text-red-400'
                                  : rate >= SEUIL_CHARGE
                                    ? 'text-amber-400'
                                    : 'text-emerald-400'
                              }`}
                            >
                              {rate >= SEUIL_SATURE
                                ? t('Saturé', 'Saturated')
                                : rate >= SEUIL_CHARGE
                                  ? t('Charge élevée', 'High load')
                                  : t('Nominal', 'Nominal')}
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <p className="text-[11px] text-on-surface-variant">
        {t(
          'Les seuils de couleur (70 % / 90 %) sont des repères d’exploitation, pas des données de la base.',
          'Colour thresholds (70% / 90%) are operational cues, not database values.',
        )}
      </p>
    </div>
  );
}
