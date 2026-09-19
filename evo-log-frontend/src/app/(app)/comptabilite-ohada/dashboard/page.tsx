'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  BookOpen, Calculator, FileText, CheckCircle2, AlertTriangle,
  TrendingUp, TrendingDown, DollarSign, Calendar, Layers, ShieldCheck,
  ArrowRight, Filter, Download, Plus, Search, RefreshCw, Lock
} from 'lucide-react';

export default function ComptabiliteOhadaDashboard() {
  const [period, setPeriod] = useState('2026-08');

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header avec T-Code & CADC Badge */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-violet-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-violet-500/20 text-violet-300 border border-violet-500/30">
              SYSCOHADA Révisé • CEMAC
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KOHA_DSH
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-violet-400" />
            Comptabilité Générale OHADA
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Gestion intégrée des 7 journaux auxiliaires, Grand Livre, Balance et États Financiers normalisés (Sage-like).
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
              <option value="2026-08">Août 2026 (En cours)</option>
              <option value="2026-07">Juillet 2026 (Clôturé)</option>
              <option value="2026-06">Juin 2026 (Clôturé)</option>
              <option value="2026-Q2">2e Trimestre 2026</option>
              <option value="2026-YTD">Exercice 2026</option>
            </select>
          </div>
          <Link
            href="/comptabilite-ohada/journal"
            className="px-4 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-violet-500/25 transition-all"
          >
            <Plus className="w-4 h-4" /> Nouvelle Écriture
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl relative overflow-hidden group hover:border-violet-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Total Débit / Crédit</span>
            <Calculator className="w-5 h-5 text-violet-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono">148,920,500 <span className="text-xs text-violet-400 font-normal">XAF</span></div>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-emerald-400 font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" /> Équilibre Débit/Crédit Parfait (0.00 écart)
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl relative overflow-hidden group hover:border-emerald-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Trésorerie Nette (Cl. 5)</span>
            <DollarSign className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono">+42,350,800 <span className="text-xs font-normal">XAF</span></div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-2">
            <span>Banque : 38.5M</span> • <span>Caisse : 3.8M</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl relative overflow-hidden group hover:border-amber-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Écritures à Lettrer</span>
            <Layers className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 font-mono">14 <span className="text-xs font-normal text-slate-400">écritures</span></div>
          <div className="text-[11px] text-amber-300/80 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Clients 411 & Fournisseurs 401
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl relative overflow-hidden group hover:border-blue-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Résultat Provisoire (Cl. 6/7)</span>
            <TrendingUp className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-blue-400 font-mono">+18,640,000 <span className="text-xs font-normal">XAF</span></div>
          <div className="text-[11px] text-slate-400 mt-2">
            Marge brute estimée : 28.4%
          </div>
        </div>
      </div>

      {/* Raccourcis Rapides vers les 6 Sous-modules OHADA */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link
          href="/comptabilite-ohada/journal"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-violet-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-105 transition-transform">
              <BookOpen className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KOHA_JRN
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-violet-400 transition-colors">
            Journaux Auxiliaires & Saisie
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Achats, Ventes, Banque, Caisse, Salaires, Opérations Diverses (OD) et lettrage automatique.
          </p>
        </Link>

        <Link
          href="/comptabilite-ohada/general-ledger"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-violet-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-105 transition-transform">
              <Layers className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KOHA_GL
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-violet-400 transition-colors">
            Grand Livre & Balance 6 Colonnes
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Consultation détaillée par compte SYSCOHADA, grand livre auxiliaire tiers et balances de vérification.
          </p>
        </Link>

        <Link
          href="/comptabilite-ohada/financial-statements"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-violet-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-105 transition-transform">
              <FileText className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KOHA_BIL
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-violet-400 transition-colors">
            États Financiers OHADA
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Bilan normalisé actif/passif, Compte de Résultat, TAFIRE et Annexes certifiées conformes.
          </p>
        </Link>

        <Link
          href="/comptabilite-ohada/chart-accounts"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-violet-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-105 transition-transform">
              <Calculator className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KOHA_COA
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-violet-400 transition-colors">
            Plan Comptable SYSCOHADA
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Nomenclature officielle Classes 1 à 8, comptes centralisateurs et sous-comptes tiers.
          </p>
        </Link>

        <Link
          href="/comptabilite-ohada/monthly-closing"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-violet-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-105 transition-transform">
              <Lock className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KOHA_CLO
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-violet-400 transition-colors">
            Clôtures & Arrêtés Périodiques
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Verrouillage de période, calcul automatique des dotations aux amortissements et report à nouveau.
          </p>
        </Link>

        <Link
          href="/comptabilite-ohada/tax-package-cemac"
          className="p-5 bg-slate-900/90 border border-slate-800 hover:border-violet-500/50 rounded-2xl transition-all group hover:bg-slate-850"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              KOHA_TAX
            </span>
          </div>
          <h3 className="text-base font-bold text-slate-100 group-hover:text-violet-400 transition-colors">
            Liasse Fiscale CEMAC & Déclarations
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Déclarations TVA 19.25%, Impôt sur les Sociétés (IS), acomptes et tableaux fiscaux officiels.
          </p>
        </Link>
      </div>

      {/* Dernières Écritures Comptables Enregistrées */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-100">Dernières Écritures Enregistrées (Livre-Journal)</h3>
            <p className="text-xs text-slate-400">Flux récents validés et en attente de lettrage</p>
          </div>
          <Link href="/comptabilite-ohada/journal" className="text-xs text-violet-400 hover:text-violet-300 font-bold flex items-center gap-1">
            Voir tout le journal <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider">
                <th className="py-3 px-3">Date</th>
                <th className="py-3 px-3">N° Pièce</th>
                <th className="py-3 px-3">Journal</th>
                <th className="py-3 px-3">Compte</th>
                <th className="py-3 px-3">Libellé de l&apos;opération</th>
                <th className="py-3 px-3 text-right">Débit (XAF)</th>
                <th className="py-3 px-3 text-right">Crédit (XAF)</th>
                <th className="py-3 px-3 text-center">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              <tr className="hover:bg-slate-800/40">
                <td className="py-3 px-3 text-slate-400">27/08/2026</td>
                <td className="py-3 px-3 font-bold text-violet-400">FAC-2026-0842</td>
                <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">VENTES</span></td>
                <td className="py-3 px-3 font-bold">411100 (Client TOTAL CM)</td>
                <td className="py-3 px-3 font-sans">Prestation Transit & Fret Conteneurs Douala</td>
                <td className="py-3 px-3 text-right font-bold text-slate-100">8,500,000</td>
                <td className="py-3 px-3 text-right text-slate-500">-</td>
                <td className="py-3 px-3 text-center"><span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">Validé</span></td>
              </tr>
              <tr className="hover:bg-slate-800/40">
                <td className="py-3 px-3 text-slate-400">27/08/2026</td>
                <td className="py-3 px-3 font-bold text-violet-400">FAC-2026-0842</td>
                <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">VENTES</span></td>
                <td className="py-3 px-3 font-bold">706100 (Prestations Fret)</td>
                <td className="py-3 px-3 font-sans">Prestation Transit & Fret Conteneurs Douala (HT)</td>
                <td className="py-3 px-3 text-right text-slate-500">-</td>
                <td className="py-3 px-3 text-right font-bold text-slate-100">7,127,883</td>
                <td className="py-3 px-3 text-center"><span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">Validé</span></td>
              </tr>
              <tr className="hover:bg-slate-800/40">
                <td className="py-3 px-3 text-slate-400">27/08/2026</td>
                <td className="py-3 px-3 font-bold text-violet-400">FAC-2026-0842</td>
                <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">VENTES</span></td>
                <td className="py-3 px-3 font-bold">443100 (TVA Collectée 19.25%)</td>
                <td className="py-3 px-3 font-sans">TVA sur Prestations Fret</td>
                <td className="py-3 px-3 text-right text-slate-500">-</td>
                <td className="py-3 px-3 text-right font-bold text-slate-100">1,372,117</td>
                <td className="py-3 px-3 text-center"><span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">Validé</span></td>
              </tr>
              <tr className="hover:bg-slate-800/40">
                <td className="py-3 px-3 text-slate-400">26/08/2026</td>
                <td className="py-3 px-3 font-bold text-violet-400">REG-BNQ-0199</td>
                <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">BANQUE</span></td>
                <td className="py-3 px-3 font-bold">512100 (Afriland First Bank)</td>
                <td className="py-3 px-3 font-sans">Virement reçu Client CAMRAIL</td>
                <td className="py-3 px-3 text-right font-bold text-emerald-400">12,400,000</td>
                <td className="py-3 px-3 text-right text-slate-500">-</td>
                <td className="py-3 px-3 text-center"><span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">À Lettrer</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}