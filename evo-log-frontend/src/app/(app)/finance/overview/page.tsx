'use client';

import { useCallback, useEffect, useState } from 'react';
import { AlertCircle, ArrowDownRight, ArrowUpRight, Banknote, DollarSign, RefreshCw, TrendingUp } from 'lucide-react';
import { financeAPI } from '@/lib/api-client';
import { Button } from '@/components/design-system/Button';
import { EmptyStates } from '@/components/design-system/EmptyState';

type FinanceKpis = {
  chiffre_affaires: number;
  total_factures: number;
  total_encaisse: number;
  montant_impaye: number;
  taux_recouvrement: number;
  tresorerie_disponible: number | null;
};

const money = (value: number | null | undefined) =>
  value == null ? 'Non disponible' : `${Number(value).toLocaleString('fr-FR')} XAF`;

export default function FinanceOverviewPage() {
  const [kpis, setKpis] = useState<FinanceKpis | null>(null);
  const [chartData, setChartData] = useState<Record<string, unknown[]> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [kpiResponse, chartResponse] = await Promise.all([
        financeAPI.getKpis(),
        financeAPI.getAnalyticsChartData(),
      ]);
      setKpis(kpiResponse.data);
      setChartData(chartResponse.data);
    } catch (requestError: any) {
      setKpis(null);
      setChartData(null);
      setError(requestError?.response?.data?.detail || 'Impossible de charger les données financières.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const cards = kpis ? [
    { label: 'Chiffre d’affaires', value: money(kpis.chiffre_affaires), icon: Banknote, color: 'text-amber-400' },
    { label: 'Total encaissé', value: money(kpis.total_encaisse), icon: ArrowUpRight, color: 'text-emerald-400' },
    { label: 'Montant impayé', value: money(kpis.montant_impaye), icon: ArrowDownRight, color: 'text-red-400' },
    { label: 'Taux de recouvrement', value: `${kpis.taux_recouvrement.toLocaleString('fr-FR')} %`, icon: TrendingUp, color: 'text-blue-400' },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2"><DollarSign className="w-6 h-6 text-amber-400" /> Finance & Trésorerie OHADA</h1>
          <p className="text-xs text-slate-400 mt-1">Données persistées et filtrées par société</p>
        </div>
        <Button
          onClick={load}
          disabled={loading}
          variant="ghost"
          size="sm"
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </Button>
      </div>

      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{error}</div>}
      {loading && <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80 text-slate-400 flex items-center justify-center gap-2"><RefreshCw className="w-5 h-5 animate-spin" /> Chargement des indicateurs financiers...</div>}
      {!loading && !error && !kpis && <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80">
        <EmptyStates.NoData
          description="Aucune donnée financière disponible."
          action={{
            label: 'Actualiser',
            onClick: load
          }}
        />
      </div>}

      {kpis && <>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          {cards.map(card => {
            const Icon = card.icon;
            return <div key={card.label} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
              <div className="flex items-center gap-2 text-xs text-slate-400"><Icon className={`w-4 h-4 ${card.color}`} />{card.label}</div>
              <div className={`mt-3 text-xl font-black font-mono ${card.color}`}>{card.value}</div>
            </div>;
          })}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
            <h2 className="text-sm font-bold text-slate-200 mb-4">Synthèse</h2>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between"><dt className="text-slate-400">Factures enregistrées</dt><dd className="text-white">{kpis.total_factures}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-400">Trésorerie disponible</dt><dd className="text-white">{money(kpis.tresorerie_disponible)}</dd></div>
            </dl>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
            <h2 className="text-sm font-bold text-slate-200 mb-4">Séries analytiques</h2>
            {chartData && Object.values(chartData).some(series => series.length > 0)
              ? <pre className="text-xs text-slate-400 overflow-auto">{JSON.stringify(chartData, null, 2)}</pre>
              : <div className="flex items-center gap-2 text-sm text-slate-400"><AlertCircle className="w-4 h-4" />Aucune série financière persistée.</div>}
          </div>
        </div>
      </>}
    </div>
  );
}
