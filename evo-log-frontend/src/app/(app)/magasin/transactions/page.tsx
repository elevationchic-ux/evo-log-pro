"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  ArrowRightLeft, Search, TrendingUp, TrendingDown, RefreshCw,
  PackageSearch, Download, Wrench, HelpCircle
} from "lucide-react";
import { apiClient } from "@/lib/api-client";

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(n);

// Contrat reel : /api/v1/magasin/transactions renvoie un MovementListResponse
// (alias metier de /history). type_mouvement porte les valeurs reelles de
// MouvementType en minuscules : entree | sortie | transfert | inventaire | ajustement.
interface MovementLine {
  id: number;
  reference: string;
  type_mouvement: string;
  quantite: number;
  valeur_totale?: number | null;
  raison?: string | null;
  document_reference?: string | null;
  destination?: string | null;
  operateur_id?: number | null;
  date_mouvement?: string | null;
  code_article?: string | null;
  designation?: string | null;
}

interface MovementListResponse {
  items: MovementLine[];
  total: number;
  entrees: number;
  sorties: number;
}

const typeConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  entree: { label: "Entrée", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <TrendingUp size={12} /> },
  sortie: { label: "Sortie", color: "text-red-400 bg-red-400/10 border-red-400/30", icon: <TrendingDown size={12} /> },
  transfert: { label: "Transfert", color: "text-blue-400 bg-blue-400/10 border-blue-400/30", icon: <ArrowRightLeft size={12} /> },
  inventaire: { label: "Inventaire", color: "text-sky-400 bg-sky-400/10 border-sky-400/30", icon: <PackageSearch size={12} /> },
  ajustement: { label: "Ajustement", color: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <Wrench size={12} /> },
};

const cfgInconnu = { label: "Inconnu", color: "text-slate-400 bg-slate-400/10 border-slate-400/30", icon: <HelpCircle size={12} /> };

function timeAgo(d: string) {
  const diff = Math.floor((Date.now() - new Date(d).getTime()) / 1000);
  if (diff < 60) return "À l'instant";
  if (diff < 3600) return `${Math.floor(diff / 60)}min`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}j`;
}

function TelechargerCSV(lignes: MovementLine[]) {
  const entetes = ["reference", "type_mouvement", "code_article", "designation", "quantite", "valeur_totale", "destination", "date_mouvement"];
  const corps = lignes.map(t =>
    entetes.map(h => {
      const v = (t as unknown as Record<string, unknown>)[h];
      const s = v == null ? "" : String(v);
      return /[",;\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    }).join(",")
  );
  const blob = new Blob(["" + [entetes.join(","), ...corps].join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `mouvements_stock_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function MagasinTransactionsContent() {
  const searchParams = useSearchParams();
  const [filterType, setFilterType] = useState("TOUS");
  // Le champ de recherche est initialise depuis ?q= : c'est la cible du lien
  // profond emit par le composant TransactionSearch.
  const [search, setSearch] = useState(searchParams.get("q") ?? "");
  const [items, setItems] = useState<MovementLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let annule = false;
    const charger = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get("/api/v1/magasin/transactions", { params: { limit: 500 } });
        if (!annule) setItems((res.data as MovementListResponse)?.items ?? []);
      } catch (e) {
        console.error("Chargement du journal de stock impossible", e);
        if (!annule) {
          setError("Journal indisponible  la liste vide affichée n'est pas une absence d'activité prouvée par le serveur.");
          setItems([]);
        }
      } finally {
        if (!annule) setLoading(false);
      }
    };
    charger();
    return () => { annule = true; };
  }, []);

  const filtered = useMemo(() => items.filter(t => {
    const matchType = filterType === "TOUS" || t.type_mouvement === filterType;
    const needle = search.toLowerCase();
    const matchSearch = search === "" ||
      (t.designation ?? "").toLowerCase().includes(needle) ||
      (t.code_article ?? "").toLowerCase().includes(needle) ||
      (t.reference ?? "").toLowerCase().includes(needle);
    return matchType && matchSearch;
  }), [items, filterType, search]);

  const comptePar = (type: string) => items.filter(t => t.type_mouvement === type).length;

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <ArrowRightLeft className="text-amber-400" size={28} />
            Journal des Mouvements de Stock
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Historique des entrées, sorties, transferts, inventaires et ajustements  source API /magasin/transactions
          </p>
        </div>
        <button
          onClick={() => TelechargerCSV(filtered)}
          disabled={filtered.length === 0}
          className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors disabled:opacity-40 disabled:hover:bg-transparent"
        >
          <Download size={14} />
          Exporter CSV ({filtered.length})
        </button>
      </div>

      {/* Stats calculees sur les lignes reels du journal */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        {Object.keys(typeConfig).map(type => {
          const cfg = typeConfig[type];
          return (
            <button key={type} onClick={() => setFilterType(filterType === type ? "TOUS" : type)} className={`rounded-2xl border p-4 text-left transition-all hover:scale-[1.02] ${cfg.color} ${filterType === type ? "ring-2 ring-current" : ""}`}>
              <div className="mb-2">{cfg.icon}</div>
              <p className="text-xl font-bold">{comptePar(type)}</p>
              <p className="text-xs opacity-70 mt-0.5">{cfg.label}</p>
            </button>
          );
        })}
      </div>

      {/* Filtres */}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 placeholder:text-muted-foreground" placeholder="Rechercher article, référence..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {loading && (
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <RefreshCw size={16} className="animate-spin" />
          Chargement du journal…
        </div>
      )}

      {!loading && error && (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>{["Référence", "Type", "Article", "Qté", "Valeur", "Destination", "Opérateur", "Date"].map(h => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-border">
              {!loading && filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-muted-foreground">
                    {items.length === 0
                      ? "Aucun mouvement retourné par l'API pour ce tenant."
                      : "Aucun mouvement ne correspond au filtre en cours."}
                  </td>
                </tr>
              )}
              {filtered.map(t => {
                const cfg = typeConfig[t.type_mouvement] ?? cfgInconnu;
                return (
                  <tr key={t.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-amber-400">{t.reference}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${cfg.color}`}>{cfg.icon}{cfg.label}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground">{t.designation || t.code_article || ""}</div>
                      {t.code_article && t.designation && (
                        <div className="text-xs text-muted-foreground font-mono">{t.code_article}</div>
                      )}
                    </td>
                    <td className={`px-4 py-3 font-bold text-lg ${t.type_mouvement === "sortie" ? "text-red-400" : "text-emerald-400"}`}>{fmtNum(t.quantite)}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.valeur_totale != null ? `${fmtNum(t.valeur_totale)} FCFA` : ""}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.destination || ""}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.operateur_id != null ? `#${t.operateur_id}` : ""}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">{t.date_mouvement ? timeAgo(t.date_mouvement) : ""}</td>
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

export default function MagasinTransactionsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-muted-foreground">Chargement…</div>}>
      <MagasinTransactionsContent />
    </Suspense>
  );
}
