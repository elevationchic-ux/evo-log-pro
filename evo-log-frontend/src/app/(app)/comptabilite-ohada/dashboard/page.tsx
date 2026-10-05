'use client';

import React, { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  BookOpen, Calculator, FileText, Layers, ShieldCheck, Lock, ArrowRight,
  Plus, AlertTriangle, RefreshCw, Database, Calendar, CheckCheck,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface Ecriture {
  id: number;
  numero_ecriture: string;
  date_ecriture: string | null;
  numero_piece: string | null;
  libelle: string;
  compte_id: number | null;
  journal: string | null;
  periode: string | null;
  debit: number | string | null;
  credit: number | string | null;
  devise: string | null;
  valider: boolean | null;
}

const num = (v: number | string | null | undefined): number => {
  const n = typeof v === 'string' ? parseFloat(v) : v;
  return Number.isFinite(n as number) ? (n as number) : 0;
};
const fmt = (n: number) => Math.round(n).toLocaleString('fr-FR');
const dateCourte = (iso: string | null) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR');
};

export default function ComptabiliteOhadaDashboard() {
  const [ecritures, setEcritures] = useState<Ecriture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState('ALL');

  const charger = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get('/api/v1/comptabilite-avance/ecritures');
      setEcritures(Array.isArray(res.data) ? res.data : []);
    } catch {
      setEcritures([]);
      setError('Écritures comptables indisponibles. Vérifiez votre connexion ou réessayez.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  // Périodes réellement présentes dans les écritures (aucune période inventée).
  const periodes = useMemo(() => {
    const set = new Set<string>();
    ecritures.forEach(e => { if (e.periode) set.add(e.periode); });
    return Array.from(set).sort().reverse();
  }, [ecritures]);

  const filtrees = period === 'ALL' ? ecritures : ecritures.filter(e => e.periode === period);

  const totalDebit = filtrees.reduce((s, e) => s + num(e.debit), 0);
  const totalCredit = filtrees.reduce((s, e) => s + num(e.credit), 0);
  const ecart = totalDebit - totalCredit;
  const valides = filtrees.filter(e => e.valider === true).length;
  const enAttente = filtrees.filter(e => e.valider !== true).length;

  const shortcuts = [
    { href: '/comptabilite-ohada/journal', icon: BookOpen, code: 'KOHA_JRN', title: 'Journaux Auxiliaires & Saisie', desc: 'Achats, Ventes, Banque, Caisse, Salaires et OD.' },
    { href: '/comptabilite-ohada/general-ledger', icon: Layers, code: 'KOHA_GL', title: 'Grand Livre & Balance', desc: 'Consultation par compte SYSCOHADA et balances de vérification.' },
    { href: '/comptabilite-ohada/lettrage', icon: CheckCheck, code: 'KOHA_LET', title: 'Lettrage des comptes de tiers', desc: 'Rapprochement FIFO automatique ou manuel, annulation motivée.' },
    { href: '/comptabilite-ohada/financial-statements', icon: FileText, code: 'KOHA_BIL', title: 'États Financiers OHADA', desc: 'Bilan, Compte de Résultat, TAFIRE et Annexes.' },
    { href: '/comptabilite-ohada/chart-accounts', icon: Calculator, code: 'KOHA_COA', title: 'Plan Comptable SYSCOHADA', desc: 'Nomenclature officielle Classes 1 à 8.' },
    { href: '/comptabilite-ohada/monthly-closing', icon: Lock, code: 'KOHA_CLO', title: 'Clôtures & Arrêtés', desc: 'Verrouillage de période et dotations aux amortissements.' },
    { href: '/comptabilite-ohada/tax-package-cemac', icon: ShieldCheck, code: 'KOHA_TAX', title: 'Liasse Fiscale CEMAC', desc: 'Déclarations TVA 19.25%, IS, acomptes et tableaux fiscaux.' },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              SYSCOHADA Révisé • CEMAC
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
              <Database className="w-3 h-3" /> Source : écritures enregistrées
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-violet-400" />
            Comptabilité Générale OHADA
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Totaux et écritures agrégés depuis les pièces réellement saisies. Aucune valeur n&apos;est simulée.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-slate-300 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-violet-400" />
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="bg-transparent outline-none text-slate-200 cursor-pointer"
            >
              <option value="ALL">Toutes périodes</option>
              {periodes.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <button onClick={charger} className="p-2.5 bg-slate-800 hover:bg-slate-700 rounded-xl text-slate-300" title="Actualiser">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <Link href="/comptabilite-ohada/journal" className="px-4 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-violet-500/25 transition-all">
            <Plus className="w-4 h-4" /> Nouvelle Écriture
          </Link>
        </div>
      </div>

      {error ? (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-10 text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
          <p className="text-sm text-slate-300">{error}</p>
          <button onClick={charger} className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold">
            <RefreshCw className="w-4 h-4" /> Réessayer
          </button>
        </div>
      ) : (
        <>
          {/* KPI Cards  dérivées des écritures réelles */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl hover:border-violet-500/40 transition-all">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Total Débit</span>
                <Calculator className="w-5 h-5 text-violet-400" />
              </div>
              <div className="text-2xl font-black text-slate-100 font-mono">{fmt(totalDebit)} <span className="text-xs text-violet-400 font-normal">XAF</span></div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl hover:border-violet-500/40 transition-all">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Total Crédit</span>
                <Calculator className="w-5 h-5 text-violet-400" />
              </div>
              <div className="text-2xl font-black text-slate-100 font-mono">{fmt(totalCredit)} <span className="text-xs text-violet-400 font-normal">XAF</span></div>
            </div>

            <div className={`bg-slate-900/80 border p-5 rounded-2xl transition-all ${Math.abs(ecart) < 0.5 ? 'border-emerald-500/40' : 'border-amber-500/40'}`}>
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Écart Débit/Crédit</span>
                <ShieldCheck className={`w-5 h-5 ${Math.abs(ecart) < 0.5 ? 'text-emerald-400' : 'text-amber-400'}`} />
              </div>
              <div className={`text-2xl font-black font-mono ${Math.abs(ecart) < 0.5 ? 'text-emerald-400' : 'text-amber-400'}`}>{fmt(ecart)} <span className="text-xs font-normal">XAF</span></div>
              <div className="text-[11px] text-slate-400 mt-2">
                {Math.abs(ecart) < 0.5 ? 'Balance équilibrée' : 'Déséquilibre : à contrôler'}
              </div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl hover:border-amber-500/40 transition-all">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-bold uppercase tracking-wider">Écritures</span>
                <Layers className="w-5 h-5 text-amber-400" />
              </div>
              <div className="text-2xl font-black text-amber-400 font-mono">{filtrees.length} <span className="text-xs font-normal text-slate-400">lignes</span></div>
              <div className="text-[11px] text-slate-400 mt-2">{valides} validées • {enAttente} en attente</div>
            </div>
          </div>

          {/* Raccourcis */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {shortcuts.map(s => {
              const Icon = s.icon;
              return (
                <Link key={s.href} href={s.href} className="p-5 bg-slate-900/90 border border-slate-800 hover:border-violet-500/50 rounded-2xl transition-all group">
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-105 transition-transform">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">{s.code}</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-100 group-hover:text-violet-400 transition-colors">{s.title}</h3>
                  <p className="text-xs text-slate-400 mt-1">{s.desc}</p>
                </Link>
              );
            })}
          </div>

          {/* Dernières écritures réelles */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-100">Dernières Écritures Enregistrées (Livre-Journal)</h3>
                <p className="text-xs text-slate-400">{period === 'ALL' ? 'Toutes périodes' : `Période ${period}`}</p>
              </div>
              <Link href="/comptabilite-ohada/journal" className="text-xs text-violet-400 hover:text-violet-300 font-bold flex items-center gap-1">
                Voir tout le journal <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {loading ? (
              <div className="py-8 text-center text-slate-400 text-sm">Chargement des écritures…</div>
            ) : filtrees.length === 0 ? (
              <div className="py-8 text-center space-y-2">
                <BookOpen className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-sm text-slate-400">
                  {ecritures.length === 0
                    ? "Aucune écriture comptable enregistrée."
                    : "Aucune écriture pour cette période."}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[11px] tracking-wider">
                      <th className="py-3 px-3">Date</th>
                      <th className="py-3 px-3">N° Pièce</th>
                      <th className="py-3 px-3">Journal</th>
                      <th className="py-3 px-3">Compte</th>
                      <th className="py-3 px-3">Libellé</th>
                      <th className="py-3 px-3 text-right">Débit (XAF)</th>
                      <th className="py-3 px-3 text-right">Crédit (XAF)</th>
                      <th className="py-3 px-3 text-center">Statut</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {filtrees.slice(0, 10).map(e => (
                      <tr key={e.id} className="hover:bg-slate-800/40">
                        <td className="py-3 px-3 text-slate-400">{dateCourte(e.date_ecriture)}</td>
                        <td className="py-3 px-3 font-bold text-violet-400">{e.numero_piece ?? e.numero_ecriture}</td>
                        <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">{e.journal ?? ''}</span></td>
                        <td className="py-3 px-3 font-bold">{e.compte_id ?? ''}</td>
                        <td className="py-3 px-3 font-sans max-w-[240px] truncate" title={e.libelle}>{e.libelle}</td>
                        <td className="py-3 px-3 text-right font-bold text-slate-100">{num(e.debit) > 0 ? fmt(num(e.debit)) : ''}</td>
                        <td className="py-3 px-3 text-right font-bold text-slate-100">{num(e.credit) > 0 ? fmt(num(e.credit)) : ''}</td>
                        <td className="py-3 px-3 text-center">
                          <span className={`px-2 py-0.5 rounded ${e.valider ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>
                            {e.valider ? 'Validée' : 'En attente'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
