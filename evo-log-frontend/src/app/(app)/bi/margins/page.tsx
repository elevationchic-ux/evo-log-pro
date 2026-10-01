'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, RefreshCw, Route } from 'lucide-react';
import { transportAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

// L'ERP ne conserve aucun revenu par mission : une « marge » serait donc
// inventée. Ce que les missions stockent réellement, c'est un coût estimé et
// un coût réel — la page compare donc ces deux colonnes, regroupées par
// corridor saisi (point_depart → point_arrivee).
type Mission = {
  id: number;
  reference: string;
  point_depart: string | null;
  point_arrivee: string | null;
  distance_km: number | null;
  cout_estime: number | null;
  cout_reel: number | null;
  statut: string | null;
};

type Corridor = {
  cle: string;
  missions: number;
  distance: number;
  estime: number;
  reel: number;
  ecart: number | null;
  mesurees: number;
};

function corridorsDes(missions: Mission[]): Corridor[] {
  const map = new Map<string, Corridor>();
  for (const m of missions) {
    const cle = `${m.point_depart || '?'} → ${m.point_arrivee || '?'}`;
    const c = map.get(cle) ?? {
      cle, missions: 0, distance: 0, estime: 0, reel: 0, ecart: null, mesurees: 0,
    };
    c.missions += 1;
    c.distance += Number(m.distance_km ?? 0);
    c.estime += Number(m.cout_estime ?? 0);
    if (m.cout_reel != null) {
      c.reel += Number(m.cout_reel);
      c.mesurees += 1;
    }
    map.set(cle, c);
  }
  const out = [...map.values()];
  for (const c of out) {
    // Un écart n'a de sens que si le corridor a un coût estimé ET au moins un
    // coût réel : sinon on affiche null plutôt qu'un 0 % trompeur.
    c.ecart = c.estime > 0 && c.mesurees > 0 ? ((c.reel - c.estime) / c.estime) * 100 : null;
  }
  return out.sort((a, b) => b.missions - a.missions);
}

export default function BiMarginsSubPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const missionsQuery = useQuery({
    queryKey: ['bi-cost-variance'],
    queryFn: async () => {
      const res = await transportAPI.getMissions({ limit: 500 });
      const body = res.data ?? res;
      const raw = Array.isArray(body) ? body : (body?.items ?? body?.missions ?? []);
      return (Array.isArray(raw) ? raw : []) as Mission[];
    },
  });

  const missions = missionsQuery.data ?? [];
  const corridors = corridorsDes(missions);
  const fmt = (v: number) => v.toLocaleString(loc, { maximumFractionDigits: 0 });

  return (
    <div className="max-w-5xl mx-auto py-6 sm:py-8 px-4 text-white animate-in fade-in duration-500">
      <Link href="/bi" className="inline-flex min-h-[44px] items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4 text-purple-400" /> {t('Retour au tableau de bord BI', 'Back to the BI dashboard')}
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 sm:p-8 shadow-2xl">
        <div className="flex items-start sm:items-center gap-3 pb-6 border-b border-slate-800 mb-6 flex-wrap">
          <div className="w-12 h-12 bg-purple-500/10 text-purple-400 rounded-2xl flex items-center justify-center border border-purple-500/20 shrink-0">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="text-xl sm:text-2xl font-black break-words">
              {t('Écarts de coûts par corridor', 'Cost variance by corridor')}
            </h1>
            <p className="text-sm text-slate-400">
              {t('Coût réel contre coût estimé, sur les missions réellement enregistrées.', 'Actual cost versus estimated cost, over missions actually recorded.')}
            </p>
          </div>
          <button
            type="button"
            onClick={() => missionsQuery.refetch()}
            disabled={missionsQuery.isFetching}
            className="inline-flex min-h-[44px] items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-bold text-slate-200 hover:bg-slate-700 disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${missionsQuery.isFetching ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
        </div>

        {missionsQuery.isLoading ? (
          <div className="p-8 text-center text-slate-400 text-sm">{t('Chargement des missions…', 'Loading missions…')}</div>
        ) : missionsQuery.isError ? (
          <div className="p-8 rounded-2xl bg-slate-950 border border-red-500/30 text-center text-red-400 text-sm">
            {t('Les missions n’ont pas pu être chargées.', 'Missions could not be loaded.')}
            <button
              type="button"
              onClick={() => missionsQuery.refetch()}
              className="block mx-auto mt-3 min-h-[44px] px-4 py-2 rounded-xl border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800"
            >
              {t('Réessayer', 'Retry')}
            </button>
          </div>
        ) : corridors.length === 0 ? (
          <div className="p-8 rounded-2xl bg-slate-950 border border-slate-800 text-center text-slate-400 text-sm">
            {t('Aucune mission enregistrée : aucun écart de coût calculable.', 'No mission recorded: no cost variance can be computed.')}
          </div>
        ) : (
          <>
            <ul className="space-y-4">
              {corridors.map((c) => (
                <li key={c.cle} className="p-4 sm:p-5 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="flex items-start justify-between gap-4 flex-wrap">
                    <div className="min-w-0">
                      <p className="font-bold text-slate-200 flex items-center gap-2 break-words">
                        <Route className="w-4 h-4 text-purple-400 shrink-0" />
                        {c.cle}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        {c.missions} {t('mission(s)', 'mission(s)')}
                        {c.distance > 0 ? ` • ${fmt(c.distance)} km` : ''}
                        {c.mesurees < c.missions ? ` • ${c.missions - c.mesurees} ${t('sans coût réel', 'without actual cost')}` : ''}
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs text-slate-400">{t('Écart réel / estimé', 'Actual vs estimated')}</div>
                      <div className={`font-mono font-bold ${c.ecart == null ? 'text-slate-500' : c.ecart > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {c.ecart == null
                          ? t('non mesurable', 'not measurable')
                          : `${c.ecart > 0 ? '+' : ''}${c.ecart.toLocaleString(loc, { maximumFractionDigits: 1 })} %`}
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <div className="text-slate-500 uppercase tracking-wider">{t('Coût estimé', 'Estimated cost')}</div>
                      <div className="font-mono text-slate-200">{fmt(c.estime)} XAF</div>
                    </div>
                    <div>
                      <div className="text-slate-500 uppercase tracking-wider">{t('Coût réel relevé', 'Recorded actual cost')}</div>
                      <div className="font-mono text-slate-200">{c.mesurees > 0 ? `${fmt(c.reel)} XAF` : '—'}</div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>

            <p className="text-[11px] text-slate-500 mt-6">
              {t(
                'Le coût réel n’est que partiellement saisi : les corridors sans coût réel affichent « non mesurable » plutôt qu’un taux inventé.',
                'Actual cost is only partly entered: corridors without an actual cost show “not measurable” instead of an invented rate.'
              )}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
