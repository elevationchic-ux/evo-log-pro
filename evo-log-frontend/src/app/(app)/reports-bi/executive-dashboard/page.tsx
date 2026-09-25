'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { BarChart3, TrendingUp, TrendingDown, Minus, RefreshCw, Target } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

interface ExecKpi {
  code: string;
  nom: string;
  valeur: number | null;
  unite?: string | null;
  objectif?: number | null;
  categorie?: string | null;
  type_rapport?: string | null;
  tendance?: string | null;
  variation?: number | null;
}

interface PoleRow {
  pole: string;
  nb_indicateurs: number;
  valeur_cumulee: number;
}

function fmtValeur(k: ExecKpi, locale: string): string {
  if (k.valeur == null || !Number.isFinite(k.valeur)) return '';
  const n = k.valeur;
  const asInt = Math.abs(n) >= 1 && Number.isInteger(n);
  const str = asInt ? n.toLocaleString(locale) : n.toLocaleString(locale, { maximumFractionDigits: 2 });
  return k.unite ? `${str} ${k.unite}` : str;
}

export default function ReportsBIExecutiveDashboard() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const locale = lang === 'en' ? 'en-US' : 'fr-FR';

  const [kpis, setKpis] = useState<ExecKpi[]>([]);
  const [poles, setPoles] = useState<PoleRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const charger = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get('/api/v1/reporting/rapports/executif');
      const data = res?.data?.data ?? res?.data ?? null;
      setKpis(Array.isArray(data?.kpis) ? data.kpis : []);
      setPoles(Array.isArray(data?.poles) ? data.poles : []);
    } catch {
      setError(t(
        'Le service de reporting n\'a pas pu être joint. Vérifiez votre connexion et réessayez.',
        'The reporting service could not be reached. Check your connection and try again.'
      ));
      setKpis([]);
      setPoles([]);
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { charger(); }, [charger]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-slate-900/90 border border-indigo-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {t('Direction Générale & Pilotage Stratégique', 'Executive & Strategic Steering')}
              </span>
              <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                T-Code : KBI_DSH
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-indigo-400" />
              {t('Executive Dashboard · Direction Générale EVO-LOG', 'Executive Dashboard · EVO-LOG Head Office')}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              {t(
                'Consolidation des KPIs de tous les pôles métiers, agrégée depuis le service de reporting.',
                'Consolidation of KPIs across all business poles, aggregated from the reporting service.'
              )}
            </p>
          </div>
          <button
            onClick={charger}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center justify-between gap-3 p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
          <span>{error}</span>
          <button onClick={charger} className="px-3 py-1.5 rounded-lg border border-red-500/40 text-xs font-bold hover:bg-red-500/10">
            {t('Réessayer', 'Retry')}
          </button>
        </div>
      )}

      {/* KPI Grid  rendu dynamique depuis les KPI réels renvoyés par le backend */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl animate-pulse h-24" />
          ))}
        </div>
      ) : kpis.length === 0 ? (
        <div className="bg-slate-900/80 border border-slate-800 p-8 rounded-2xl text-center text-slate-400 text-sm">
          {t(
            'Aucun indicateur de pilotage enregistré. Les KPIs définis dans le module Reporting s\'afficheront ici.',
            'No steering indicator recorded yet. KPIs defined in the Reporting module will appear here.'
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {kpis.map((k, i) => {
            const trend = String(k.tendance || '').toLowerCase();
            const TrendIcon = trend.includes('hausse') || trend.includes('up')
              ? TrendingUp
              : trend.includes('baisse') || trend.includes('down')
                ? TrendingDown
                : Minus;
            const trendColor = trend.includes('hausse') || trend.includes('up')
              ? 'text-emerald-400'
              : trend.includes('baisse') || trend.includes('down')
                ? 'text-red-400'
                : 'text-slate-400';
            return (
              <div key={i} className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 truncate" title={k.nom}>
                      {k.nom}
                    </div>
                    <div className="text-xl font-black font-mono text-slate-100">{fmtValeur(k, locale)}</div>
                    <div className="flex items-center gap-3 mt-1.5 text-[11px]">
                      {k.objectif != null && (
                        <span className="text-slate-500 flex items-center gap-1">
                          <Target className="w-3 h-3" />
                          {t('Obj.', 'Target')} {k.objectif.toLocaleString(locale)}
                        </span>
                      )}
                      {k.variation != null && Number.isFinite(k.variation) && (
                        <span className={`flex items-center gap-1 font-bold ${trendColor}`}>
                          <TrendIcon className="w-3 h-3" />
                          {k.variation > 0 ? '+' : ''}{k.variation.toFixed(1)}%
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0">
                    <BarChart3 className="w-5 h-5" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Table Activité par Pôle  agrégation réelle par type_rapport */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            {t('Activité Consolidée par Pôle Métier', 'Consolidated Activity by Business Pole')}
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">{t('Pôle Métier', 'Business Pole')}</th>
                <th className="py-3.5 px-4 text-right">{t('Indicateurs', 'Indicators')}</th>
                <th className="py-3.5 px-4 text-right">{t('Valeur Cumulée', 'Cumulative Value')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading && (
                <tr><td colSpan={3} className="py-12 px-4 text-center text-slate-500 font-sans">{t('Chargement de l\'activité consolidée…', 'Loading consolidated activity…')}</td></tr>
              )}
              {!loading && poles.length === 0 && (
                <tr>
                  <td colSpan={3} className="py-12 px-4 text-center text-slate-400 font-sans">
                    {t('Aucun pôle avec indicateurs enregistrés.', 'No pole with recorded indicators.')}
                  </td>
                </tr>
              )}
              {!loading && poles.map((row, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-sans font-bold text-slate-100">{row.pole}</td>
                  <td className="py-3.5 px-4 text-right text-slate-300">{row.nb_indicateurs}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-emerald-400">{row.valeur_cumulee.toLocaleString(locale)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
