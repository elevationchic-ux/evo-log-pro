'use client';

import React from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart3, DollarSign, Truck, Anchor, Boxes,
  Layers, FileText, Sparkles, ArrowUpRight, RefreshCw, TrendingUp,
} from 'lucide-react';
import { biAnalyticsAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

// ─────────────────────────────────────────────────────────────────────────────
// Tableau de bord transversal des rapports.
//
// Ce qui a été retiré : le « Délai Moyen Douane (BAE) : 3,5 jours » était
// déduit de `transits > 0 ? 3.5 : 0`, c'est-à-dire un nombre inventé dès qu'un
// dossier existait, avec une « cible standard < 4,0 j » sans source. Il est
// remplacé par le temps de cycle portuaire réellement calculé (moyenne de la
// colonne temps_cycle_heures de la table cycles_conteneurs).
//
// Aucune valeur de repli : quand un module ne répond pas (droits insuffisants,
// agrégat vide), la carte affiche «  » et le motif, jamais un chiffre.
//
// Teinte : violet = module « reports-bi » (modulePalette).
// ─────────────────────────────────────────────────────────────────────────────

type Synthese = {
  finance: Record<string, number> | null;
  transport: Record<string, number> | null;
  magasin: Record<string, number> | null;
  port: Record<string, unknown> | null;
};

function nombre(v: unknown, decimals = 0): string | null {
  if (v === null || v === undefined) return null;
  const n = Number(v);
  if (Number.isNaN(n)) return null;
  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: decimals, minimumFractionDigits: decimals }).format(n);
}

export default function ReportsDashboardPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const syntheseQuery = useQuery<Synthese>({
    queryKey: ['bi-summary'],
    queryFn: () => biAnalyticsAPI.getSummary() as Promise<Synthese>,
  });

  const synthese = syntheseQuery.data;
  const fin = synthese?.finance ?? null;
  const trans = synthese?.transport ?? null;
  const mag = synthese?.magasin ?? null;
  const port = synthese?.port ?? null;

  const cartes: {
    label: string; value: string; hint: string;
    icon: React.ComponentType<{ className?: string }>; tone: string;
  }[] = [
      {
        label: t("Chiffre d'affaires facturé", 'Invoiced revenue'),
        value: fin ? `${nombre(fin.chiffre_affaires)} FCFA` : '',
        hint: fin
          ? t(`${nombre(fin.total_factures)} facture(s), ${nombre(fin.total_encaisse)} FCFA encaissé(s)`,
            `${nombre(fin.total_factures)} invoice(s), ${nombre(fin.total_encaisse)} FCFA collected`)
          : t('Agrégat finance indisponible.', 'Finance aggregate unavailable.'),
        icon: DollarSign,
        tone: 'text-emerald-400',
      },
      {
        label: t('Missions transport', 'Transport missions'),
        value: trans ? `${nombre(trans.missions_total ?? 0)}` : '',
        hint: trans
          ? t(`${nombre(trans.missions_terminees ?? 0)} terminée(s), ${nombre(trans.missions_en_cours ?? 0)} en cours`,
            `${nombre(trans.missions_terminees ?? 0)} completed, ${nombre(trans.missions_en_cours ?? 0)} in progress`)
          : t('Agrégat transport indisponible.', 'Transport aggregate unavailable.'),
        icon: Truck,
        tone: 'text-cyan-400',
      },
      {
        label: t('Valeur du stock', 'Stock value'),
        value: mag ? `${nombre(mag.valeur_stock)} FCFA` : '',
        hint: mag
          ? t(`${nombre(mag.nb_articles ?? 0)} article(s) · ${nombre(mag.mouvements_jour ?? 0)} mouvement(s) du jour`,
            `${nombre(mag.nb_articles ?? 0)} item(s) · ${nombre(mag.mouvements_jour ?? 0)} movements today`)
          : t('Agrégat magasin indisponible.', 'Warehouse aggregate unavailable.'),
        icon: Boxes,
        tone: 'text-amber-400',
      },
      {
        label: t('Temps de cycle portuaire', 'Port cycle time'),
        value: port ? `${nombre(port.temps_cycle_moyen_heures, 1)} h` : '',
        hint: port
          ? t(
            `Moyenne sur ${nombre(port.periode_jours)} j · ${nombre(port.conteneurs_traites ?? 0)} conteneur(s) traité(s)`,
            `Average over ${nombre(port.periode_jours)} days · ${nombre(port.conteneurs_traites ?? 0)} container(s) handled`
          )
          : t('Agrégat portuaire indisponible.', 'Port aggregate unavailable.'),
        icon: Anchor,
        tone: 'text-sky-400',
      },
    ];

  const retours: { href: string; label: string; desc: string; icon: React.ComponentType<{ className?: string }>; tone: string }[] = [
    {
      href: '/reports/templates',
      label: t('Catalogue des modèles', 'Template catalogue'),
      desc: t(
        'Modèles préétablis par métier (Transit, Flotte, Stocks WMS, Finances).',
        'Ready-made templates by business line (Transit, Fleet, WMS, Finance).'
      ),
      icon: Layers,
      tone: 'bg-purple-500/10 text-purple-400',
    },
    {
      href: '/reports/templates/library',
      label: t('Modèles enregistrés', 'Saved templates'),
      desc: t(
        'Registre des modèles réellement créés et enregistrés dans l’ERP.',
        'Register of templates actually created and stored in the ERP.'
      ),
      icon: FileText,
      tone: 'bg-emerald-500/10 text-emerald-400',
    },
    {
      href: '/reports/custom/builder',
      label: t('Générateur multicritère', 'Multi-criteria builder'),
      desc: t(
        'Requêtes à la demande sur les registres existants, avec export.',
        'On-demand queries over existing registers, with export.'
      ),
      icon: Sparkles,
      tone: 'bg-sky-500/10 text-sky-400',
    },
  ];

  const busy = syntheseQuery.isFetching;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3 min-w-0">
          <div className="p-2.5 bg-purple-500/10 rounded-xl text-purple-400 border border-purple-500/20 shrink-0">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-50 break-words">
              {t('Rapports d’exploitation & BI', 'Operational reports & BI')}
            </h1>
            <p className="text-sm text-slate-400">
              {t(
                'Agrégats calculés en direct depuis les registres de chaque module.',
                'Aggregates computed live from each module register.'
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={() => syntheseQuery.refetch()}
            disabled={busy}
            className="inline-flex min-h-[44px] items-center gap-2 px-3.5 py-2 border border-slate-700 rounded-xl text-slate-300 hover:bg-slate-800 text-sm disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${busy ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <Link
            href="/reports/custom/builder"
            className="inline-flex min-h-[44px] items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl bg-purple-600 hover:bg-purple-500 text-white transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            {t('Générateur personnalisé', 'Custom builder')}
          </Link>
        </div>
      </div>

      {syntheseQuery.isError ? (
        <p className="rounded-2xl border border-amber-500/30 bg-amber-500/10 text-amber-400 px-4 py-3 text-sm">
          {t(
            'Les agrégats n’ont pas pu être chargés : vérifiez vos droits d’accès aux modules concernés.',
            'Aggregates could not be loaded: check your access rights on the related modules.'
          )}
        </p>
      ) : null}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cartes.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.label} className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
              <div className="flex justify-between items-start gap-2 text-xs text-slate-400 font-medium">
                <span className="min-w-0 break-words">{c.label}</span>
                <Icon className={`w-4 h-4 shrink-0 ${c.tone}`} />
              </div>
              <p className="text-lg sm:text-xl font-bold font-mono text-slate-50 mt-1 break-words">
                {syntheseQuery.isLoading ? t('Chargement…', 'Loading…') : c.value}
              </p>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">{c.hint}</p>
            </div>
          );
        })}
      </div>

      {/* Indicateurs secondaires reels */}
      {(fin || trans || mag) && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-5">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-purple-400 shrink-0" />
            {t('Détail des agrégats disponibles', 'Detail of available aggregates')}
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-xs">
            {fin ? (
              <>
                <Ligne label={t('Impayé', 'Unpaid')} valeur={`${nombre(fin.montant_impaye)} FCFA`} />
                <Ligne label={t('Taux recouvrement', 'Collection rate')} valeur={`${nombre(fin.taux_recouvrement, 1)} %`} />
                <Ligne label={t('Créances douteuses', 'Doubtful debts')} valeur={`${nombre(fin.creances_douteuses)} FCFA`} />
                <Ligne label={t('Trésorerie', 'Treasury')} valeur={`${nombre(fin.tresorerie_disponible)} FCFA`} />
              </>
            ) : null}
            {trans ? (
              <>
                <Ligne label={t('Camions disponibles', 'Available trucks')} valeur={nombre(trans.camions_disponibles ?? 0) ?? ''} />
                <Ligne label={t('En maintenance', 'Under maintenance')} valeur={nombre(trans.camions_en_maintenance ?? 0) ?? ''} />
                <Ligne label={t('Disponibilité flotte', 'Fleet availability')} valeur={`${nombre(trans.taux_disponibilite, 1)} %`} />
                <Ligne label={t('Chauffeurs', 'Drivers')} valeur={nombre(trans.chauffeurs_total ?? 0) ?? ''} />
              </>
            ) : null}
            {mag ? (
              <>
                <Ligne label={t('Alertes stock minimum', 'Minimum stock alerts')} valeur={nombre(mag.nb_alertes_min ?? 0) ?? ''} />
                <Ligne label={t('Entrepôts', 'Warehouses')} valeur={nombre(mag.nb_entrepots ?? 0) ?? ''} />
              </>
            ) : null}
          </div>
          <p className="text-[11px] text-slate-500 mt-3">
            {t(
              'Un agrégat absent du module n’est pas remplacé : la carte affiche «  ».',
              'A missing module aggregate is never substituted: the card shows “”.'
            )}
          </p>
        </div>
      )}

      {/* Quick Navigation to Report Modules */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {retours.map((r) => {
          const Icon = r.icon;
          return (
            <Link
              key={r.href}
              href={r.href}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-purple-500/50 transition-all group block"
            >
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2.5 rounded-xl ${r.tone} shrink-0`}>
                  <Icon className="w-5 h-5" />
                </div>
                <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-purple-400 transition-colors shrink-0" />
              </div>
              <h3 className="font-bold text-sm text-slate-100 break-words">{r.label}</h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{r.desc}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function Ligne({ label, valeur }: { label: string; valeur: string }) {
  return (
    <div className="rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 min-w-0">
      <p className="text-slate-500 uppercase font-bold text-[10px] truncate" title={label}>{label}</p>
      <p className="font-mono text-slate-100 whitespace-nowrap">{valeur ?? ''}</p>
    </div>
  );
}
