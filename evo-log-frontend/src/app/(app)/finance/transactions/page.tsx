"use client";

import React, { useState } from "react";
import {
  CreditCard, Search, Filter, TrendingUp, TrendingDown,
  ArrowRightLeft, Plus, Download, Eye, Calendar
} from "lucide-react";

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(n);

const TRANSACTIONS: Array<any> = [];

const typeConfig: Record<string, { label: string; color: string }> = {
  ENCAISSEMENT: { label: "Encaissement", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30" },
  PAIEMENT: { label: "Paiement", color: "text-red-400 bg-red-400/10 border-red-400/30" },
  VIREMENT_INTERNE: { label: "Virement Interne", color: "text-blue-400 bg-blue-400/10 border-blue-400/30" },
};

export default function FinanceTransactionsPage() {
  const [filterType, setFilterType] = useState("TOUS");
  const [search, setSearch] = useState("");

  const filtered = TRANSACTIONS.filter(t => {
    const matchType = filterType === "TOUS" || t.type === filterType;
    const matchSearch = search === "" || t.libelle.toLowerCase().includes(search.toLowerCase()) || t.tiers.toLowerCase().includes(search.toLowerCase()) || t.id.toLowerCase().includes(search.toLowerCase());
    return matchType && matchSearch;
  });

  const totalEntrees = TRANSACTIONS.filter(t => t.montant_xaf > 0).reduce((s, t) => s + t.montant_xaf, 0);
  const totalSorties = TRANSACTIONS.filter(t => t.montant_xaf < 0).reduce((s, t) => s + Math.abs(t.montant_xaf), 0);
  const soldeNet = totalEntrees - totalSorties;

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <CreditCard className="text-emerald-400" size={28} />
            Transactions Bancaires
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">Flux de trésorerie, encaissements et paiements  Août 2026</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <Download size={14} />Export
          </button>
          <a href="/finance/saisie-transaction-bancaire" className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium transition-colors">
            <Plus size={16} />Saisir Transaction
          </a>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
          <div className="flex items-center gap-2 mb-2 text-emerald-400"><TrendingUp size={16} /><span className="text-xs">Total Entrées</span></div>
          <p className="text-2xl font-bold text-emerald-400">+{fmtNum(totalEntrees)}</p>
          <p className="text-xs text-muted-foreground mt-0.5">XAF encaissés</p>
        </div>
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5">
          <div className="flex items-center gap-2 mb-2 text-red-400"><TrendingDown size={16} /><span className="text-xs">Total Sorties</span></div>
          <p className="text-2xl font-bold text-red-400">-{fmtNum(totalSorties)}</p>
          <p className="text-xs text-muted-foreground mt-0.5">XAF décaissés</p>
        </div>
        <div className={`rounded-2xl border p-5 ${soldeNet >= 0 ? "border-blue-500/20 bg-blue-500/5" : "border-amber-500/20 bg-amber-500/5"}`}>
          <div className={`flex items-center gap-2 mb-2 ${soldeNet >= 0 ? "text-blue-400" : "text-amber-400"}`}><ArrowRightLeft size={16} /><span className="text-xs">Solde Net Période</span></div>
          <p className={`text-2xl font-bold ${soldeNet >= 0 ? "text-blue-400" : "text-amber-400"}`}>{soldeNet > 0 ? "+" : ""}{fmtNum(soldeNet)}</p>
          <p className="text-xs text-muted-foreground mt-0.5">XAF net</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/30 placeholder:text-muted-foreground" placeholder="Rechercher transaction, tiers..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterType} onChange={e => setFilterType(e.target.value)}>
          <option value="TOUS">Tous types</option>
          <option value="ENCAISSEMENT">Encaissements</option>
          <option value="PAIEMENT">Paiements</option>
          <option value="VIREMENT_INTERNE">Virements internes</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>{["Réf.", "Type", "Libellé", "Tiers", "Compte", "Montant (XAF)", "Statut"].map(h => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map(t => {
                const cfg = typeConfig[t.type];
                return (
                  <tr key={t.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-emerald-400">{t.id}</td>
                    <td className="px-4 py-3"><span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${cfg.color}`}>{cfg.label}</span></td>
                    <td className="px-4 py-3 max-w-[220px] truncate text-sm text-foreground" title={t.libelle}>{t.libelle}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.tiers}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.compte}</td>
                    <td className={`px-4 py-3 font-bold text-base ${t.montant_xaf > 0 ? "text-emerald-400" : "text-red-400"}`}>
                      {t.montant_xaf > 0 ? "+" : ""}{fmtNum(t.montant_xaf)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium ${t.statut === "VALIDE" ? "text-emerald-400" : "text-amber-400"}`}>
                        {t.statut === "VALIDE" ? "✓ Validé" : "⏳ En attente"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
