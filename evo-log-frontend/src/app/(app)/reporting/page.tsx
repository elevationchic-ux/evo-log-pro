'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart2, FileText, TrendingUp, Download, RefreshCw,
  PieChart, Activity, Calendar, CheckCircle2, Clock, ArrowUpRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

export default function ReportingPage() {
  const [rapportExecutif, setRapportExecutif] = useState<any>(null);
  const [kpis, setKpis] = useState<any[]>([]);
  const [dashboards, setDashboards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [periodeFinancier, setPeriodeFinancier] = useState('mensuel');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resExec, resKpis, resDash] = await Promise.allSettled([
        apiClient.get('/api/v1/reporting/rapports/executif'),
        apiClient.get('/api/v1/reporting/kpis', { params: { limit: 20 } }),
        apiClient.get('/api/v1/reporting/dashboards', { params: { limit: 10 } })
      ]);
      if (resExec.status === 'fulfilled' && resExec.value.data)
        setRapportExecutif(resExec.value.data);
      if (resKpis.status === 'fulfilled' && resKpis.value.data)
        setKpis(resKpis.value.data?.data || resKpis.value.data || []);
      if (resDash.status === 'fulfilled' && resDash.value.data)
        setDashboards(resDash.value.data?.data || resDash.value.data || []);
    } catch (err) {
      console.error('Reporting fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const telechargerRapport = async (endpoint: string, label: string) => {
    try {
      const res = await apiClient.get(endpoint);
      const data = res?.data?.data ?? res?.data ?? {};
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${label.replace(/[^a-z0-9]+/gi, '_').toLowerCase()}_${periodeFinancier}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      toast.success(`Rapport « ${label} » téléchargé.`);
    } catch {
      toast.error(`Échec du téléchargement du rapport « ${label} » : le service de reporting n'a pas répondu.`);
    }
  };

  const handleDownloadRapport = (type: string) =>
    telechargerRapport(`/api/v1/reporting/rapports/financier/${periodeFinancier}`, `Rapport ${type}`);

  const metricCards = [
    { key: 'ca_xaf', label: "Chiffre d'Affaires (XAF)", icon: TrendingUp, color: 'text-emerald-400', format: (v: number) => (v || 0).toLocaleString('fr-FR') },
    { key: 'taux_recouvrement_pct', label: 'Taux Recouvrement', icon: CheckCircle2, color: 'text-cyan-400', format: (v: number) => `${(v || 0).toFixed(1)}%` },
    { key: 'dossiers_traites', label: 'Dossiers Traités', icon: FileText, color: 'text-blue-400', format: (v: number) => (v || 0).toString() },
    { key: 'delai_moyen_dedouanement_j', label: 'Délai Moyen Dédouanement', icon: Clock, color: 'text-amber-400', format: (v: number) => `${(v || 0).toFixed(1)} j` },
  ];

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-400 text-xs font-bold uppercase tracking-wider mb-2">
            <BarChart2 className="w-3.5 h-3.5" /> Business Intelligence & Rapports OHADA  Direction Générale
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Reporting & Tableaux de Bord Exécutifs</h1>
          <p className="text-xs text-slate-400 mt-1">KPIs financiers OHADA, rapports douaniers, indicateurs de performance portuaire et exports réglementaires DGD/BEAC.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => handleDownloadRapport('financier')} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold shadow-lg shadow-violet-900/20 transition-all">
            <Download className="w-4 h-4" /> Exporter Rapport
          </button>
        </div>
      </div>

      {/* Executive KPIs from backend */}
      {rapportExecutif && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {metricCards.map((m) => (
            <div key={m.key} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">{m.label}</span>
                <m.icon className={`w-4 h-4 ${m.color}`} />
              </div>
              <p className={`text-xl font-black mt-2 ${m.color}`}>
                {loading ? '' : m.format(rapportExecutif[m.key])}
              </p>
            </div>
          ))}
        </div>
      )}

      {loading && !rapportExecutif && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {metricCards.map((m) => (
            <div key={m.key} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl animate-pulse">
              <div className="h-3 bg-slate-800 rounded w-2/3 mb-3"></div>
              <div className="h-7 bg-slate-800 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* KPIs */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <Activity className="w-5 h-5 text-violet-400" />
            <h2 className="text-base font-black text-white">KPIs Enregistrés</h2>
            <span className="ml-auto text-xs text-slate-400">{kpis.length} indicateurs</span>
          </div>
          {loading ? (
            <div className="p-8 text-center"><RefreshCw className="w-5 h-5 animate-spin text-violet-400 mx-auto mb-2 mt-2" /></div>
          ) : kpis.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">Aucun KPI configuré.</div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {kpis.slice(0, 8).map((k: any) => (
                <div key={k.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                  <div>
                    <span className="text-sm font-bold text-white">{k.nom}</span>
                    <p className="text-xs text-slate-400 mt-0.5">{k.unite || 'N/A'} • Seuil: {k.seuil_alerte}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-black text-violet-400">{k.valeur_actuelle}</p>
                    <p className="text-[10px] text-slate-500">/ Cible: {k.valeur_cible}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Dashboards & Rapports */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <PieChart className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-black text-white">Rapports Financiers</h2>
          </div>
          <div className="p-4 space-y-3">
            {[
              { label: 'Rapport Exécutif Global', endpoint: '/api/v1/reporting/rapports/executif', period: null },
              { label: 'Rapport Financier Mensuel', endpoint: `/api/v1/reporting/rapports/financier/mensuel`, period: 'mensuel' },
              { label: 'Rapport Financier Annuel', endpoint: `/api/v1/reporting/rapports/financier/annuel`, period: 'annuel' },
              { label: 'Rapport Douanier Mensuel', endpoint: `/api/v1/reporting/rapports/douanier/mensuel`, period: 'mensuel' },
              { label: 'Rapport Douanier Annuel', endpoint: `/api/v1/reporting/rapports/douanier/annuel`, period: 'annuel' },
            ].map((r) => (
              <div key={r.label} className="flex items-center justify-between p-3 rounded-2xl bg-slate-800/60 border border-slate-700/60 hover:border-slate-600/60 transition-colors">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-slate-400" />
                  <span className="text-sm font-semibold text-slate-200">{r.label}</span>
                </div>
                <button
                  onClick={() => telechargerRapport(r.endpoint, r.label)}
                  className="px-3 py-1.5 rounded-xl bg-violet-600/20 hover:bg-violet-600/30 text-violet-400 border border-violet-500/30 text-xs font-bold flex items-center gap-1.5 transition-all"
                >
                  <ArrowUpRight className="w-3.5 h-3.5" /> Générer
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
