'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  BarChart3, ArrowLeft, Download, RefreshCw, Ship, Truck, Gauge, CheckCircle2, Activity, Boxes,
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';

interface TableauBord {
  date?: string;
  missions_actives?: number;
  missions_terminees?: number;
  vehicules_disponibles?: number;
  vehicules_en_mission?: number;
  taux_occupation?: number;
}

export default function ReportsBiOperationalAnalyticsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [tb, setTb] = useState<TableauBord | null>(null);
  const [escalesCount, setEscalesCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [bordRes, escalesRes] = await Promise.all([
        api.get('/api/v1/transport-avance-complete/analytics/tableau-bord'),
        api.get('/api/v1/acconage/escales', { params: { limit: 200 } }),
      ]);
      setTb(bordRes.data ?? null);
      const es = escalesRes.data;
      setEscalesCount(Array.isArray(es) ? es.length : (es?.items?.length ?? es?.total ?? 0));
      setLoaded(true);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Erreur de chargement', 'Failed to load'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    load();
  }, [load]);

  const metrics = [
    { key: 'escales', label: t('Escale en cours', 'Vessel calls'), value: escalesCount, icon: Ship, suffix: '' },
    { key: 'missions_actives', label: t('Missions actives', 'Active missions'), value: tb?.missions_actives, icon: Truck, suffix: '' },
    { key: 'missions_terminees', label: t('Missions terminées', 'Completed missions'), value: tb?.missions_terminees, icon: CheckCircle2, suffix: '' },
    { key: 'vehicules_en_mission', label: t('Véhicules en mission', 'Vehicles on mission'), value: tb?.vehicules_en_mission, icon: Activity, suffix: '' },
    { key: 'vehicules_disponibles', label: t('Véhicules disponibles', 'Available vehicles'), value: tb?.vehicules_disponibles, icon: Boxes, suffix: '' },
    { key: 'taux_occupation', label: t("Taux d'occupation", 'Occupancy rate'), value: tb?.taux_occupation, icon: Gauge, suffix: '%' },
  ];

  const handleExport = () => {
    const rows = metrics.map((m) => `${m.label};${m.value ?? ''}${m.suffix}`);
    const csv = '\uFEFF' + rows.join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytique-operationnelle-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(t('Export généré.', 'Export generated.'));
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4 pb-24 text-slate-100 sm:p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/reports-bi/executive-dashboard" className="flex items-center gap-1 hover:text-blue-400">
          <ArrowLeft className="h-3.5 w-3.5" /> {t('BI & Tableaux de Bord', 'BI & Dashboards')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Analytique Opérationnelle', 'Operational Analytics')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 backdrop-blur-xl md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/10 p-2.5 text-indigo-400">
            <BarChart3 className="h-6 w-6" />
          </div>
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight text-white">
              {t('Analytique Opérationnelle', 'Operational Analytics')}
            </h1>
            <p className="text-sm text-slate-400">
              {t('Indicateurs réels agrégés depuis la base (transport & acconage).', 'Real indicators aggregated from the database (transport & cargo handling).')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={load}
            disabled={loading}
            className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={handleExport}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-500"
          >
            <Download className="h-4 w-4" />
            {t('Exporter', 'Export')}
          </button>
        </div>
      </div>

      {/* KPI cards (réels) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((m) => {
          const Icon = m.icon;
          return (
            <div key={m.key} className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase text-slate-400">{m.label}</span>
                <Icon className="h-4 w-4 text-indigo-400" />
              </div>
              <p className="mt-2 font-mono text-2xl font-extrabold text-white">
                {m.value == null ? '' : `${m.value}${m.suffix}`}
              </p>
            </div>
          );
        })}
      </div>

      {loaded && tb == null && escalesCount == null && (
        <p className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-center text-sm text-slate-400">
          {t('Aucune donnée opérationnelle disponible pour le moment.', 'No operational data available yet.')}
        </p>
      )}
    </div>
  );
}
