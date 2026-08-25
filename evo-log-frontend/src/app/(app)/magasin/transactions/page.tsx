"use client";

import React, { useState } from "react";
import {
  ArrowRightLeft, Search, Filter, TrendingUp, TrendingDown,
  Package, RefreshCw, Download, Calendar, ChevronDown
} from "lucide-react";

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(n);

const TRANSACTIONS = [
  { id: "MVT-2026-001", type: "ENTREE", article: "Pneu Michelin 315/70R22.5", reference: "PR-PNEU-001", quantite: 8, unite: "UN", emplacement: "ATELIER-A", operateur: "NKOA Bertrand", created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: "MVT-2026-002", type: "SORTIE", article: "Huile Moteur 15W40 20L", reference: "PR-HUILE-001", quantite: 2, unite: "BIDON", emplacement: "CUVE-F01", operateur: "NGONO Serge", created_at: new Date(Date.now() - 7200000).toISOString() },
  { id: "MVT-2026-003", type: "TRANSFERT", article: "Gasoil B7", reference: "ART-FUEL-GASOIL", quantite: 5000, unite: "LITRES", emplacement: "CUVE-F01 â†’ DLA-TRK-001", operateur: "SystÃ¨me automatique", created_at: new Date(Date.now() - 10800000).toISOString() },
  { id: "MVT-2026-004", type: "ENTREE", article: "Europalettes 1200x800mm", reference: "ART-PAL-EUR", quantite: 50, unite: "UN", emplacement: "MAG3-C01", operateur: "ONDOUA Pierre", created_at: new Date(Date.now() - 21600000).toISOString() },
  { id: "MVT-2026-005", type: "AJUSTEMENT", article: "MatÃ©riel Soudure â€“ Kits", reference: "MAT-SOUDURE-006", quantite: -1, unite: "KIT", emplacement: "ATELIER-B", operateur: "MVONDO AndrÃ© (correction inventaire)", created_at: new Date(Date.now() - 86400000).toISOString() },
];

const typeConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  ENTREE: { label: "EntrÃ©e", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <TrendingUp size={12} /> },
  SORTIE: { label: "Sortie", color: "text-red-400 bg-red-400/10 border-red-400/30", icon: <TrendingDown size={12} /> },
  TRANSFERT: { label: "Transfert", color: "text-blue-400 bg-blue-400/10 border-blue-400/30", icon: <ArrowRightLeft size={12} /> },
  AJUSTEMENT: { label: "Ajustement", color: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <RefreshCw size={12} /> },
};

function timeAgo(d: string) {
  const diff = Math.floor((Date.now() - new Date(d).getTime()) / 1000);
  if (diff < 60) return "Ã€ l'instant";
  if (diff < 3600) return `${Math.floor(diff / 60)}min`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}j`;
}

export default function MagasinTransactionsPage() {
  const [filterType, setFilterType] = useState("TOUS");
  const [search, setSearch] = useState("");

  const filtered = TRANSACTIONS.filter(t => {
    const matchType = filterType === "TOUS" || t.type === filterType;
    const matchSearch = search === "" || t.article.toLowerCase().includes(search.toLowerCase()) || t.id.toLowerCase().includes(search.toLowerCase());
    return matchType && matchSearch;
  });

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <ArrowRightLeft className="text-amber-400" size={28} />
            Log Transactions Stock
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">Historique complet des mouvements de stock WMS â€” MAG3</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
          <Download size={14} />
          Exporter CSV
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {(["ENTREE", "SORTIE", "TRANSFERT", "AJUSTEMENT"] as const).map(type => {
          const cfg = typeConfig[type];
          return (
            <button key={type} onClick={() => setFilterType(filterType === type ? "TOUS" : type)} className={`rounded-2xl border p-4 text-left transition-all hover:scale-[1.02] ${cfg.color} ${filterType === type ? "ring-2 ring-current" : ""}`}>
              <div className="mb-2">{cfg.icon}</div>
              <p className="text-xl font-bold">{TRANSACTIONS.filter(t => t.type === type).length}</p>
              <p className="text-xs opacity-70 mt-0.5">{cfg.label}s</p>
            </button>
          );
        })}
      </div>

      {/* Filtres */}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 placeholder:text-muted-foreground" placeholder="Rechercher article, rÃ©fÃ©rence..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>{["RÃ©fÃ©rence", "Type", "Article", "QtÃ©", "Emplacement", "OpÃ©rateur", "Date"].map(h => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map(t => {
                const cfg = typeConfig[t.type];
                return (
                  <tr key={t.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-amber-400">{t.id}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${cfg.color}`}>{cfg.icon}{cfg.label}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground">{t.article}</div>
                      <div className="text-xs text-muted-foreground font-mono">{t.reference}</div>
                    </td>
                    <td className={`px-4 py-3 font-bold text-lg ${t.quantite > 0 ? "text-emerald-400" : "text-red-400"}`}>{t.quantite > 0 ? "+" : ""}{fmtNum(t.quantite)} {t.unite}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.emplacement}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.operateur}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{timeAgo(t.created_at)}</td>
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
