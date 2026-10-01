'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { biAnalyticsAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import {
  BarChart3, TrendingUp, DollarSign, Warehouse, Truck, Ship, RefreshCw, ArrowRight,
} from 'lucide-react';
import Link from 'next/link';

// Aucune table « KPI executive » n'existe dans l'ERP : ce tableau de bord
// agrège les agrégats réellement calculés par chaque module (finance,
// transport, magasin, port). Un module sans droit d'accès ou sans écriture
// affiche « — » ou 0 réel : rien n'est supposé.
type Synthese = {
  finance: {
    chiffre_affaires: number;
    total_factures: number;
    total_encaisse: number;
    montant_impaye: number;
    taux_recouvrement: number;
    tresorerie_disponible: number;
  } | null;
  transport: {
    vehicules_total: number;
    taux_disponibilite: number;
    missions_total: number;
    missions_en_cours: number;
    missions_terminees: number;
  } | null;
  magasin: {
    nb_articles: number;
    valeur_stock: number;
    nb_alertes_min: number;
    nb_entrepots: number;
  } | null;
  port: {
    periode_jours: number;
    conteneurs_traites: number;
    taux_rotation: number;
    temps_cycle_moyen_heures: number;
    taux_disponibilite_equipements_pct: number;
  } | null;
};

export default function BiAnalyticsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const loc = lang === 'en' ? 'en-GB' : 'fr-FR';

  const summaryQuery = useQuery<Synthese>({
    queryKey: ['bi-summary'],
    queryFn: async () => (await biAnalyticsAPI.getSummary()) as Synthese,
  });

  const s = summaryQuery.data;
  const nf = (v: number | null | undefined, digits = 0) =>
    v == null ? '—' : v.toLocaleString(loc, { maximumFractionDigits: digits });

  const cards = [
    {
      icon: DollarSign,
      label: t("Chiffre d'affaires facturé", 'Billed turnover'),
      value: s?.finance ? `${nf(s.finance.chiffre_affaires)} XAF` : '—',
      hint: s?.finance
        ? t(`${nf(s.finance.total_factures)} facture(s) • ${nf(s.finance.taux_recouvrement, 1)} % recouvré`, `${nf(s.finance.total_factures)} invoice(s) • ${nf(s.finance.taux_recouvrement, 1)} % collected`)
        : t('Finance OHADA : accès ou agrégat indisponible', 'OHADA Finance: aggregate unavailable'),
    },
    {
      icon: Truck,
      label: t('Missions de transport', 'Transport missions'),
      value: s?.transport ? nf(s.transport.missions_total) : '—',
      hint: s?.transport
        ? t(`${nf(s.transport.missions_terminees)} clôturées • ${nf(s.transport.missions_en_cours)} en cours`, `${nf(s.transport.missions_terminees)} closed • ${nf(s.transport.missions_en_cours)} in progress`)
        : t('Transport & Flotte : agrégat indisponible', 'Transport & Fleet: aggregate unavailable'),
    },
    {
      icon: Warehouse,
      label: t('Valeur du stock', 'Stock value'),
      value: s?.magasin ? `${nf(s.magasin.valeur_stock)} XAF` : '—',
      hint: s?.magasin
        ? t(`${nf(s.magasin.nb_articles)} article(s) • ${nf(s.magasin.nb_alertes_min)} sous le minimum`, `${nf(s.magasin.nb_articles)} item(s) • ${nf(s.magasin.nb_alertes_min)} below minimum`)
        : t('Magasin & Stock : agrégat indisponible', 'Warehouse & Stock: aggregate unavailable'),
    },
    {
      icon: Ship,
      label: t('Conteneurs traités', 'Containers handled'),
      value: s?.port ? nf(s.port.conteneurs_traites) : '—',
      hint: s?.port
        ? t(`sur ${s.port.periode_jours} j • cycle moyen ${nf(s.port.temps_cycle_moyen_heures, 1)} h`, `over ${s.port.periode_jours} d • average cycle ${nf(s.port.temps_cycle_moyen_heures, 1)} h`)
        : t('Opérations portuaires : agrégat indisponible', 'Port operations: aggregate unavailable'),
    },
  ];

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-xl">
        <div className="min-w-0">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-xs font-semibold mb-2 border border-purple-500/20">
            <BarChart3 className="w-3.5 h-3.5 shrink-0" />
            {t('Reports & BI • Agrégats transversaux', 'Reports & BI • Cross-module aggregates')}
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight break-words">
            {t('Tableau de bord décisionnel', 'Executive dashboard')}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {t('Consolidation des indicateurs réellement calculés par Finance, Transport, Magasin et Port.', 'Consolidation of indicators actually computed by Finance, Transport, Warehouse and Port.')}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={() => summaryQuery.refetch()}
            disabled={summaryQuery.isFetching}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-700 disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${summaryQuery.isFetching ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <Link
            href="/bi/margins"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 bg-purple-600 hover:bg-purple-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-purple-600/30 transition-colors"
          >
            <TrendingUp className="w-4 h-4" />
            {t('Écarts de coûts', 'Cost variances')}
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {summaryQuery.isError ? (
        <div className="bg-slate-900 border border-red-500/30 rounded-2xl p-8 text-center text-red-400 text-sm">
          {t('Les agrégats n’ont pas pu être calculés.', 'The aggregates could not be computed.')}
          <button
            type="button"
            onClick={() => summaryQuery.refetch()}
            className="block mx-auto mt-3 min-h-[44px] px-4 py-2 rounded-xl border border-slate-700 text-xs font-bold text-slate-200 hover:bg-slate-800"
          >
            {t('Réessayer', 'Retry')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map((c) => {
            const Icon = c.icon;
            return (
              <div key={c.label} className="bg-slate-900 border border-slate-800 p-5 sm:p-6 rounded-2xl shadow-xl">
                <div className="w-12 h-12 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-2xl flex items-center justify-center mb-3">
                  <Icon className="w-6 h-6" />
                </div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">{c.label}</p>
                <h2 className="text-xl sm:text-2xl font-black text-slate-100 font-mono break-words">
                  {summaryQuery.isLoading ? t('Chargement…', 'Loading…') : c.value}
                </h2>
                <p className="text-xs text-slate-400 mt-2 break-words">{c.hint}</p>
              </div>
            );
          })}
        </div>
      )}

      <p className="text-xs text-slate-500">
        {t(
          « Aucune marge ni rentabilité n'est calculée ici : l'ERP ne stocke pas de revenu par mission, seulement un coût estimé et un coût réel. » /!\
        )}
      </p>
    </div>
  );
}
