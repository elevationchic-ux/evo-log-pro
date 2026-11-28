'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { procurementAPI } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import {
  ShoppingCart, RefreshCw, FileText, FileCheck, GitCompare, ScrollText,
  PackageCheck, AlertTriangle, Star, ArrowLeft,
} from 'lucide-react';
import Link from 'next/link';

// ============================================================================
// Chaine complete d'achats — lecture des ressources du routeur acquisition :
// appels d'offres -> cahiers des charges -> offres -> comparatifs ->
// contrats-cadres -> bons de commande -> receptions -> litiges ->
// evaluations fournisseurs. Donnees reelles uniquement.
// ============================================================================

type Col = { key: string; label: string; render?: (v: any, row: any) => React.ReactNode };

const fmtXaf = (n: any, devise?: string) => {
  if (n === null || n === undefined || n === '') return '—';
  const num = Number(n);
  if (Number.isNaN(num)) return String(n);
  return new Intl.NumberFormat('fr-FR').format(num) + ' ' + (devise || 'XAF');
};

const dateFmt = (d: any) => (d ? String(d).slice(0, 10) : '—');

const RESOURCES: {
  key: string; label: string; icon: React.ReactNode;
  fetcher: (p?: Record<string, unknown>) => Promise<any>;
  columns: Col[];
}[] = [
  {
    key: 'appels-offres', label: 'Appels d’offres', icon: <FileText className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getAppelsOffres(p),
    columns: [
      { key: 'numero_appel', label: 'N° appel' },
      { key: 'titre', label: 'Objet' },
      { key: 'type_appel', label: 'Type' },
      { key: 'statut', label: 'Statut' },
      { key: 'budget_estime', label: 'Budget estimé', render: (v, r) => fmtXaf(v, r.devise) },
      { key: 'date_publication', label: 'Publication', render: dateFmt },
      { key: 'date_limite', label: 'Limite', render: dateFmt },
    ],
  },
  {
    key: 'cahiers-charges', label: 'Cahiers des charges', icon: <FileCheck className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getCahiersCharges(p),
    columns: [
      { key: 'numero_cdc', label: 'N° CDC' },
      { key: 'appel_offres_id', label: 'Appel lié' },
      { key: 'objet', label: 'Objet' },
      { key: 'version', label: 'Version' },
      { key: 'statut', label: 'Statut' },
      { key: 'date_version', label: 'Date version', render: dateFmt },
    ],
  },
  {
    key: 'offres', label: 'Offres fournisseurs', icon: <FileText className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getOffres(p),
    columns: [
      { key: 'numero_offre', label: 'N° offre' },
      { key: 'appel_offres_id', label: 'Appel lié' },
      { key: 'fournisseur_id', label: 'Fournisseur' },
      { key: 'montant_total', label: 'Montant', render: (v, r) => fmtXaf(v, r.devise) },
      { key: 'rang', label: 'Rang' },
      { key: 'statut', label: 'Statut' },
      { key: 'date_reception', label: 'Réception', render: dateFmt },
    ],
  },
  {
    key: 'comparatifs', label: 'Comparatifs', icon: <GitCompare className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getComparatifs(p),
    columns: [
      { key: 'numero_comparatif', label: 'N° comparatif' },
      { key: 'appel_offres_id', label: 'Appel lié' },
      { key: 'statut', label: 'Statut' },
      { key: 'recommandation', label: 'Recommandation' },
      { key: 'date_creation', label: 'Création', render: dateFmt },
      { key: 'date_cloture', label: 'Clôture', render: dateFmt },
    ],
  },
  {
    key: 'contrats-cadre', label: 'Contrats-cadres', icon: <ScrollText className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getContratsCadre(p),
    columns: [
      { key: 'numero_contrat', label: 'N° contrat' },
      { key: 'fournisseur_id', label: 'Fournisseur' },
      { key: 'type_contrat', label: 'Type' },
      { key: 'montant_annuel', label: 'Montant annuel', render: (v, r) => fmtXaf(v, r.devise) },
      { key: 'date_debut', label: 'Début', render: dateFmt },
      { key: 'date_fin', label: 'Fin', render: dateFmt },
      { key: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'receptions', label: 'Réceptions', icon: <PackageCheck className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getReceptions(p),
    columns: [
      { key: 'numero_reception', label: 'N° réception' },
      { key: 'bc_id', label: 'BC lié' },
      { key: 'fournisseur_id', label: 'Fournisseur' },
      { key: 'date_reception', label: 'Date', render: dateFmt },
      { key: 'type_reception', label: 'Type' },
      { key: 'condition_marchandise', label: 'Condition' },
      { key: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'litiges', label: 'Litiges fournisseurs', icon: <AlertTriangle className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getLitiges(p),
    columns: [
      { key: 'numero_litige', label: 'N° litige' },
      { key: 'fournisseur_id', label: 'Fournisseur' },
      { key: 'type_litige', label: 'Type' },
      { key: 'gravite', label: 'Gravité' },
      { key: 'montant_en_litige', label: 'Montant', render: (v, r) => fmtXaf(v, r.devise) },
      { key: 'date_ouverture', label: 'Ouverture', render: dateFmt },
      { key: 'statut', label: 'Statut' },
    ],
  },
  {
    key: 'evaluations-fournisseur', label: 'Évaluations fournisseurs', icon: <Star className="w-4 h-4" />,
    fetcher: (p) => procurementAPI.getEvaluationsFournisseur(p),
    columns: [
      { key: 'fournisseur_id', label: 'Fournisseur' },
      { key: 'periode', label: 'Période' },
      { key: 'note_globale', label: 'Note globale' },
      { key: 'classement', label: 'Classement' },
      { key: 'recommandation', label: 'Recommandation' },
      { key: 'date_evaluation', label: 'Date', render: dateFmt },
    ],
  },
];

const statutBadge = (s: any) => {
  const v = String(s ?? '').toLowerCase();
  const ok = ['actif', 'valide', 'livre', 'clos', 'resolu', 'complet', 'approuve'];
  const ko = ['annule', 'resilie', 'rejete', 'expire'];
  const cls = ok.includes(v)
    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    : ko.includes(v)
      ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
      : 'bg-slate-500/10 text-slate-300 border-slate-500/30';
  return <span className={`inline-block px-2 py-0.5 rounded-full border text-[11px] font-bold ${cls}`}>{s ?? '—'}</span>;
};

export default function ChaineAchatsPage() {
  const { language } = useSettings();
  const [tab, setTab] = useState(RESOURCES[0].key);
  const res = RESOURCES.find((r) => r.key === tab)!;

  const query = useQuery({
    queryKey: ['procurement-chaine', tab],
    queryFn: async () => {
      const out = await res.fetcher({ limit: 200 });
      const raw = out?.data ?? out;
      return (Array.isArray(raw) ? raw : []) as Record<string, any>[];
    },
  });

  const rows = query.data ?? [];

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">
            <ShoppingCart className="w-3.5 h-3.5" /> Procurement
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Chaîne complète d'achats</h1>
          <p className="text-xs text-slate-400 mt-1">
            Appels d'offres → CDC → offres → comparatifs → contrats-cadres → bons de commande → réceptions → litiges → évaluations.
            {language === 'fr' ? ' Données réelles uniquement.' : ' Real data only.'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/procurement" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold border border-slate-700">
            <ArrowLeft className="w-4 h-4" /> Bons de commande
          </Link>
          <button onClick={() => void query.refetch()} className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700" title="Actualiser">
            <RefreshCw className={`w-4 h-4 ${query.isFetching ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Onglets ressources */}
      <div className="flex flex-wrap gap-1 bg-slate-900/60 border border-slate-800 rounded-2xl p-1 w-fit">
        {RESOURCES.map((r) => (
          <button
            key={r.key}
            onClick={() => setTab(r.key)}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-colors whitespace-nowrap ${
              tab === r.key ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {r.icon} {r.label}
          </button>
        ))}
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h2 className="font-bold text-white flex items-center gap-2">{res.icon} {res.label}</h2>
          <span className="text-xs text-slate-500">{rows.length} ligne(s)</span>
        </div>
        {query.isLoading ? (
          <div className="p-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />Chargement…</div>
        ) : query.isError ? (
          <div className="p-12 text-center text-rose-400">Chargement impossible (droits insuffisants ou service indisponible).</div>
        ) : rows.length === 0 ? (
          <div className="p-12 text-center text-slate-500">Aucune donnée pour cette ressource.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                  {res.columns.map((c) => <th key={c.key} className="px-4 py-3 whitespace-nowrap">{c.label}</th>)}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={row.id ?? i} className="border-b border-slate-800/60 hover:bg-slate-800/40">
                    {res.columns.map((c) => (
                      <td key={c.key} className="px-4 py-3 text-slate-300 whitespace-nowrap">
                        {c.key === 'statut'
                          ? statutBadge(row[c.key])
                          : c.render
                            ? c.render(row[c.key], row)
                            : (row[c.key] ?? '—')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
