'use client';

import React, { useEffect, useState } from 'react';
import {
  FileText, Search, AlertTriangle, RefreshCw, Stamp, TrendingUp,
  Package, Scale, Receipt, Database,
} from 'lucide-react';
import { goodsDeclarationAPI } from '@/lib/api-client';

interface Stats {
  total_declarations: number;
  en_attente: number;
  validees: number;
  liquidees: number;
  valeur_douane_totale_xaf: number;
  droits_douane_total_xaf: number;
  tva_douaniere_total_xaf: number;
  recettes_fiscales_totales_xaf: number;
}

interface DumRow {
  id: number;
  numero_dum: string;
  importateur: string | null;
  marchandise: string | null;
  valeur_douane_xaf: number | null;
  montant_total: number | null;
  statut: string;
  reference_sydonia: string | null;
}

const STATUT_STYLES: Record<string, string> = {
  en_attente: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  valide: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  'liquidé': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
};
const STATUT_LABELS: Record<string, string> = {
  en_attente: 'En attente',
  valide: 'Validée',
  'liquidé': 'Liquidée',
};

function millions(n: number | null | undefined): string {
  if (!n) return '0';
  return (n / 1_000_000).toFixed(1);
}

export default function TransitDouaneDashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [rows, setRows] = useState<DumRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const charger = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, l] = await Promise.all([
        goodsDeclarationAPI.getStats(),
        goodsDeclarationAPI.getAll({ limit: 200 }),
      ]);
      setStats(s.data);
      setRows((l.data.items ?? []).map((d: DumRow) => d));
    } catch {
      setStats(null);
      setRows([]);
      setError('Données indisponibles. Vérifiez votre connexion ou réessayez.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  const kpis = stats
    ? [
        { label: 'Déclarations totales', value: stats.total_declarations, sub: 'enregistrées', icon: FileText, color: 'text-amber-400', bg: 'bg-slate-900/80', border: 'border-slate-800' },
        { label: 'En attente', value: stats.en_attente, sub: 'à valider', icon: Package, color: 'text-blue-400', bg: 'bg-slate-900/80', border: 'border-slate-800' },
        { label: 'Validées', value: stats.validees, sub: 'contrôlées', icon: Stamp, color: 'text-cyan-400', bg: 'bg-slate-900/80', border: 'border-slate-800' },
        { label: 'Liquidées', value: stats.liquidees, sub: 'droits acquittés', icon: Scale, color: 'text-emerald-400', bg: 'bg-slate-900/80', border: 'border-slate-800' },
        { label: 'Recettes fiscales', value: `${millions(stats.recettes_fiscales_totales_xaf)} M`, sub: 'XAF cumulés', icon: Receipt, color: 'text-emerald-400', bg: 'bg-slate-900/80', border: 'border-slate-800' },
        { label: 'Droits de douane', value: `${millions(stats.droits_douane_total_xaf)} M`, sub: 'XAF cumulés', icon: TrendingUp, color: 'text-amber-400', bg: 'bg-slate-900/80', border: 'border-slate-800' },
      ]
    : [];

  const filtered = rows.filter(r => {
    const q = searchQuery.toLowerCase();
    return (
      !q ||
      r.numero_dum.toLowerCase().includes(q) ||
      (r.importateur ?? '').toLowerCase().includes(q) ||
      (r.marchandise ?? '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white">Transit & Douane CEMAC</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Déclarations en douane (DUM) réellement enregistrées · taxation CEMAC estimative
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
          <Database className="w-3 h-3" /> Source : déclarations
        </span>
      </div>

      {loading ? (
        <div className="p-10 text-center text-slate-400 text-sm">Chargement du tableau de bord…</div>
      ) : error ? (
        <div className="p-10 text-center space-y-3 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
          <p className="text-sm text-slate-300">{error}</p>
          <button
            onClick={charger}
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold"
          >
            <RefreshCw className="w-4 h-4" /> Réessayer
          </button>
        </div>
      ) : (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 xl:grid-cols-3 gap-3">
            {kpis.map((kpi, i) => {
              const Icon = kpi.icon;
              return (
                <div key={i} className={`${kpi.bg} border ${kpi.border} rounded-2xl p-4 shadow-lg`}>
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-4 h-4 ${kpi.color}`} />
                    <span className="text-xs font-medium text-slate-400 truncate">{kpi.label}</span>
                  </div>
                  <div className={`text-2xl font-black ${kpi.color} font-mono`}>{kpi.value}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{kpi.sub}</div>
                </div>
              );
            })}
          </div>

          {stats && stats.total_declarations === 0 ? (
            <div className="p-10 text-center space-y-2 bg-slate-900/80 border border-slate-800 rounded-2xl">
              <FileText className="w-8 h-8 text-slate-600 mx-auto" />
              <p className="text-sm text-slate-400">
                Aucune déclaration en douane enregistrée pour l&apos;instant.
              </p>
            </div>
          ) : (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
              <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
                <h2 className="text-sm font-bold text-white">Déclarations DUM</h2>
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="DUM, Importateur, Marchandise..."
                    className="h-9 pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono w-60"
                  />
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-left">
                      <th className="px-4 py-3 text-slate-400 font-semibold uppercase">N° DUM</th>
                      <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Importateur</th>
                      <th className="px-4 py-3 text-slate-400 font-semibold uppercase hidden md:table-cell">Marchandise</th>
                      <th className="px-4 py-3 text-slate-400 font-semibold uppercase text-right hidden lg:table-cell">Valeur douane</th>
                      <th className="px-4 py-3 text-slate-400 font-semibold uppercase text-right">Total taxes</th>
                      <th className="px-4 py-3 text-slate-400 font-semibold uppercase">Statut</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filtered.map((row) => (
                      <tr key={row.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="px-4 py-3 font-mono font-bold text-amber-300">{row.numero_dum}</td>
                        <td className="px-4 py-3 text-slate-200 font-medium">{row.importateur ?? '—'}</td>
                        <td className="px-4 py-3 text-slate-400 hidden md:table-cell max-w-48 truncate">{row.marchandise ?? '—'}</td>
                        <td className="px-4 py-3 font-mono text-slate-300 hidden lg:table-cell text-right">
                          {millions(row.valeur_douane_xaf)} M
                        </td>
                        <td className="px-4 py-3 font-mono text-right text-slate-200">
                          {millions(row.montant_total)} M
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded-full text-[11px] font-black border ${STATUT_STYLES[row.statut] ?? 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                            {STATUT_LABELS[row.statut] ?? row.statut}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
