'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  BarChart3, ArrowLeft, Calendar, Ship, Anchor, Clock,
  Box, Loader2
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

type Periode = 'CE_JOUR' | 'CE_MOIS' | 'TRIMESTRE';

export default function PortOperationsMaritimeStatsPage() {
  const { language } = useSettings();
  const lang = language || 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const PERIODES: { valeur: Periode; libelle: string }[] = [
    { valeur: 'CE_JOUR', libelle: t("Aujourd'hui", 'Today') },
    { valeur: 'CE_MOIS', libelle: t('Ce mois', 'This month') },
    { valeur: 'TRIMESTRE', libelle: t('Trimestre en cours', 'Current quarter') },
  ];

  const [periode, setPeriode] = useState<Periode>('CE_MOIS');
  const [portFiltre, setPortFiltre] = useState('ALL');
  const [escales, setEscales] = useState<any[]>([]);
  const [operations, setOperations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [esc, op] = await Promise.all([
        apiClient.get('/api/v1/acconage-avance/escales').catch(() => null),
        apiClient.get('/api/v1/registres/operations-quai').catch(() => null),
      ]);
      setEscales(Array.isArray(esc?.data) ? esc.data : (esc?.data?.items || []));
      const opList = Array.isArray(op?.data) ? op.data : (op?.data?.items || []);
      setOperations(opList);
    } catch {
      setEscales([]);
      setOperations([]);
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const debutPeriode = useMemo(() => {
    const now = new Date();
    if (periode === 'CE_JOUR') {
      return new Date(now.getFullYear(), now.getMonth(), now.getDate());
    }
    if (periode === 'CE_MOIS') {
      return new Date(now.getFullYear(), now.getMonth(), 1);
    }
    return new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1);
  }, [periode]);

  const dansPeriode = (d?: string | null) => {
    if (!d) return false;
    const dt = new Date(d);
    return !isNaN(dt.getTime()) && dt >= debutPeriode;
  };

  const portMatches = (text?: string | null) => {
    if (portFiltre === 'ALL') return true;
    const s = (text || '').toLowerCase();
    if (portFiltre === 'DOUALA') return s.includes('douala');
    if (portFiltre === 'KRIBI') return s.includes('kribi') || s.includes('boro');
    return true;
  };

  const escFiltrees = escales.filter(
    e => (dansPeriode(e.date_arrivee_estimee) || dansPeriode(e.date_arrivee_reelle)) &&
      portMatches(e.poste_quai || e.port)
  );
  const opFiltrees = operations.filter(
    o => (dansPeriode(o.heure_debut) || dansPeriode(o.created_at)) && portMatches(o.quai)
  );

  // Calculs réels
  const sejoursHeures: number[] = [];
  escFiltrees.forEach(e => {
    const dep = e.date_depart_reelle || e.date_depart_estimee;
    const arr = e.date_arrivee_reelle || e.date_arrivee_estimee;
    if (dep && arr) {
      const h = (new Date(dep).getTime() - new Date(arr).getTime()) / 3600000;
      if (h >= 0) sejoursHeures.push(h);
    }
  });
  const sejourMoyen = sejoursHeures.length
    ? (sejoursHeures.reduce((a, b) => a + b, 0) / sejoursHeures.length).toFixed(1)
    : null;
  const totalEvp = opFiltrees.reduce((acc, o) => acc + (Number(o.mouvements_realises) || 0), 0);
  const cadences = opFiltrees.map(o => Number(o.cadence_horaire)).filter(c => c > 0);
  const cadenceMoyenne = cadences.length
    ? Math.round(cadences.reduce((a, b) => a + b, 0) / cadences.length)
    : null;
  const mouvementsPrevus = opFiltrees.reduce((acc, o) => acc + (Number(o.mouvements_prevus) || 0), 0);

  const cards = [
    {
      icon: Ship, label: t('Escales sur la période', 'Port calls in period'),
      value: String(escFiltrees.length),
      sub: t('Source : registre des escales', 'Source: port call register'),
    },
    {
      icon: Clock, label: t('Séjour moyen à quai', 'Average stay alongside'),
      value: sejourMoyen ? `${sejourMoyen} h` : '',
      sub: t('Arrivées/départs enregistrés', 'Recorded arrivals/departures'),
    },
    {
      icon: Anchor, label: t('Cadence moyenne grues', 'Average crane rate'),
      value: cadenceMoyenne ? `${cadenceMoyenne} EVP/h` : '',
      sub: t('Opérations de quai ouvertes', 'Open wharf operations'),
    },
    {
      icon: Box, label: t('Mouvements réalisés', 'Completed moves'),
      value: `${totalEvp.toLocaleString()} EVP`,
      sub: mouvementsPrevus > 0
        ? `${Math.min(100, Math.round((totalEvp / mouvementsPrevus) * 100))}% ${t('des mouvements prévus', 'of planned moves')}`
        : t('Aucun objectif saisi', 'No target entered'),
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Statistiques de Rendement & Cadences', 'Performance & Rate Statistics')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-violet-500/10 text-violet-400 rounded-xl border border-violet-500/20">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex flex-wrap items-center gap-2">
              {t('Statistiques Maritimes & Ratios de Manutention', 'Maritime Statistics & Handling Ratios')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/30 font-mono">
                KACC_STA
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t("Analyse des cadences horaires portiques, temps d'attente en rade, séjour à quai et tonnage", 'Analysis of gantry hourly rates, roads waiting time, berth stay and tonnage')}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={periode}
            onChange={e => setPeriode(e.target.value as Periode)}
            aria-label={t("Période d'analyse", 'Analysis period')}
            className="px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-violet-500"
          >
            {PERIODES.map(p => (
              <option key={p.valeur} value={p.valeur}>{p.libelle}</option>
            ))}
          </select>
          <select
            value={portFiltre}
            onChange={e => setPortFiltre(e.target.value)}
            aria-label={t('Filtrer par terminal', 'Filter by terminal')}
            className="px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-violet-500"
          >
            <option value="ALL">{t('Tous les terminaux (PAD & PAK)', 'All terminals (PAD & PAK)')}</option>
            <option value="DOUALA">{t('Douala - Quai 14', 'Douala - Wharf 14')}</option>
            <option value="KRIBI">{t('Kribi - Port Mboro', 'Kribi - Mboro Port')}</option>
          </select>
        </div>
      </div>

      {/* Stats calculées depuis les registres réels */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        {loading ? (
          <div className="py-16 flex items-center justify-center gap-2 text-slate-400">
            <Loader2 className="w-5 h-5 animate-spin" />
            {t('Calcul des statistiques...', 'Computing statistics...')}
          </div>
        ) : (
          <>
            <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-violet-400" />
              {t('Indicateurs calculés à partir des registres', 'Indicators computed from the registers')}
              <span className="text-xs font-normal text-slate-400"> {PERIODES.find(p => p.valeur === periode)?.libelle}</span>
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {cards.map((c, i) => {
                const Icon = c.icon;
                return (
                  <div key={i} className="bg-slate-950/50 rounded-xl border border-slate-800 p-5">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-slate-400 uppercase">{c.label}</span>
                      <div className="p-1.5 bg-violet-500/10 text-violet-400 rounded-lg">
                        <Icon className="w-4 h-4" />
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-white">{c.value}</p>
                    <p className="text-xs text-slate-500 mt-1">{c.sub}</p>
                  </div>
                );
              })}
            </div>
            {escFiltrees.length === 0 && opFiltrees.length === 0 && (
              <div className="mt-6 py-10 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
                <BarChart3 className="w-10 h-10 text-slate-400 mx-auto mb-2" />
                <p className="text-sm text-slate-400 max-w-md mx-auto">
                  {t('Aucune donnée sur cette période : programmez une escale ou ouvrez une opération de quai pour alimenter les indicateurs.', 'No data for this period: schedule a port call or open a wharf operation to feed the indicators.')}
                </p>
                <Link
                  href="/port-operations"
                  className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium rounded-xl shadow transition"
                >
                  <Ship className="w-4 h-4" /> {t('Aller au registre des escales', 'Go to port call register')}
                </Link>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
