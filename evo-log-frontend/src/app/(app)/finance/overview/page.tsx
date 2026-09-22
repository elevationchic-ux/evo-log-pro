'use client';

import React, { useState } from 'react';
import {
  DollarSign, TrendingUp, TrendingDown, CreditCard, BarChart3,
  ArrowUpRight, ArrowDownRight, Building2, RefreshCw, Plus,
  Calendar, FileText, Banknote, AlertCircle, CheckCircle2, Eye
} from 'lucide-react';
import { toast } from 'sonner';

export default function FinanceOverviewPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('AOUT_2026');

  const cashflow: { tresorerieDisponible: number; entreesMois: number; sortiesMois: number; soldeNet: number; banques: Array<any> } = { tresorerieDisponible: 0, entreesMois: 0, sortiesMois: 0, soldeNet: 0, banques: [] };
  const balanceAgee: Array<any> = [];
  const recentEntries: Array<any> = [];
  const budgetLines: Array<any> = [];

  const statusColors: Record<string, string> = {
    OK: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    RISQUE: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    CRITIQUE: 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <DollarSign className="w-6 h-6 text-amber-400" /> Finance & Trésorerie OHADA
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Cash flow · Balance âgée · Rapprochements bancaires · Budget vs Réalisé · Journaux SYSCOHADA</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedPeriod}
            onChange={e => setSelectedPeriod(e.target.value)}
            className="h-9 px-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500"
          >
            <option value="AOUT_2026">Août 2026</option>
            <option value="JUIL_2026">Juillet 2026</option>
            <option value="JUIN_2026">Juin 2026</option>
          </select>
          <button onClick={() => toast.info('Saisie écriture comptable')} className="px-4 py-2 bg-gradient-to-r from-amber-500 to-yellow-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-2 shadow-lg">
            <Plus className="w-4 h-4" /> Écriture Comptable
          </button>
        </div>
      </div>

      {/* Cash Flow KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        {[
          { label: 'Trésorerie Globale', value: (cashflow.tresorerieDisponible / 1000000).toFixed(1) + ' M', sub: '3 comptes bancaires CEMAC', icon: Banknote, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
          { label: 'Entrées du Mois', value: (cashflow.entreesMois / 1000000).toFixed(1) + ' M', sub: 'Clients & produits financiers', icon: ArrowUpRight, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
          { label: 'Sorties du Mois', value: (cashflow.sortiesMois / 1000000).toFixed(1) + ' M', sub: 'Charges exploitation & admin', icon: ArrowDownRight, color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
          { label: 'Solde Net Mensuel', value: '+' + (cashflow.soldeNet / 1000000).toFixed(1) + ' M', sub: 'XAF (FCFA)', icon: TrendingUp, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
        ].map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className={`${kpi.bg} border rounded-2xl p-4 shadow-lg`}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-xs text-slate-400 truncate">{kpi.label}</span>
              </div>
              <div className={`text-2xl font-black font-mono ${kpi.color}`}>{kpi.value} XAF</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Bank Accounts */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h2 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <Building2 className="w-4 h-4 text-blue-400" /> Comptes Bancaires Domiciliés
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {cashflow.banques.map((bk, i) => (
            <div key={i} className="bg-slate-950 border border-slate-800 rounded-2xl p-4">
              <div className="text-xs font-bold text-slate-200 mb-0.5">{bk.nom}</div>
              <div className="text-[11px] font-mono text-slate-500 mb-2">{bk.compte}</div>
              <div className="text-xl font-black text-white font-mono">{(bk.solde / 1000000).toFixed(2)} M XAF</div>
              <div className={`text-[11px] font-mono mt-0.5 ${bk.variation > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {bk.variation > 0 ? '↑' : '↓'} {Math.abs(bk.variation)}% vs mois dernier
              </div>
              <button onClick={() => toast.info(`Relevé bancaire ${bk.nom}`)} className="mt-2 text-[10px] text-amber-400 hover:text-amber-300 flex items-center gap-1">
                Voir relevé <ArrowUpRight className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Balance âgée */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400" /> Balance Âgée Clients
            </h2>
            <button onClick={() => toast.info('Export balance âgée XLS')} className="text-xs text-amber-400 hover:text-amber-300">Export XLS</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="border-b border-slate-800 text-left">
                  <th className="px-3 py-2 text-slate-500 font-semibold">Client</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">0-30j</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">31-60j</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">&gt;60j</th>
                  <th className="px-3 py-2 text-slate-500 font-semibold">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {balanceAgee.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="px-3 py-2.5 font-medium text-slate-300">{row.client}</td>
                    <td className="px-3 py-2.5 font-mono text-slate-400">{row.en_cours > 0 ? (row.en_cours / 1000).toFixed(0) + 'k' : ''}</td>
                    <td className="px-3 py-2.5 font-mono text-amber-400">{row.j60 > 0 ? (row.j60 / 1000).toFixed(0) + 'k' : ''}</td>
                    <td className="px-3 py-2.5 font-mono text-red-400">{row.j90 > 0 ? (row.j90 / 1000).toFixed(0) + 'k' : ''}</td>
                    <td className="px-3 py-2.5">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statusColors[row.statut]}`}>{row.statut}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Budget vs Réalisé */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <h2 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-purple-400" /> Budget vs Réalisé (Août 2026)
          </h2>
          <div className="space-y-4">
            {budgetLines.map((line, i) => (
              <div key={i}>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-slate-400">{line.poste}</span>
                  <span className={`font-mono font-bold ${line.pct > 90 ? 'text-red-400' : line.pct > 75 ? 'text-amber-400' : 'text-emerald-400'}`}>{line.pct.toFixed(1)}%</span>
                </div>
                <div className="bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className={`h-full ${line.color} rounded-full`} style={{ width: `${Math.min(line.pct, 100)}%` }}></div>
                </div>
                <div className="flex justify-between text-[10px] mt-0.5">
                  <span className="text-slate-500 font-mono">Réalisé: {(line.realise / 1000000).toFixed(2)} M</span>
                  <span className="text-slate-600 font-mono">Budget: {(line.budget / 1000000).toFixed(2)} M XAF</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Entries */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" /> Journal de Trésorerie Récent
          </h2>
        </div>
        <div className="divide-y divide-slate-800/60">
          {recentEntries.map((entry, i) => (
            <div key={i} className="px-4 py-3 flex items-center gap-4 hover:bg-slate-800/20 transition-colors">
              <div className="text-[11px] font-mono text-slate-500 w-12 shrink-0">{entry.date}</div>
              <div className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 ${entry.type === 'RECETTE' ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
                {entry.type === 'RECETTE' ? <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" /> : <ArrowDownRight className="w-3.5 h-3.5 text-red-400" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs text-slate-200 truncate">{entry.libelle}</div>
                <div className="text-[11px] text-slate-500">{entry.compte} · {entry.statut}</div>
              </div>
              <div className={`text-xs font-mono font-black shrink-0 ${entry.montant > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {entry.montant > 0 ? '+' : ''}{entry.montant.toLocaleString()} XAF
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
