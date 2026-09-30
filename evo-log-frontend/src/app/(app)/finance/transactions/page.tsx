"use client";

import React, { useEffect, useState } from "react";
import {
  CreditCard, Search, TrendingUp, AlertTriangle, RefreshCw, Database, Download,
} from "lucide-react";
import { toast } from "sonner";
import { financeAPI } from "@/lib/api-client";
import { exportToCSV } from "@/lib/export";

interface Encaissement {
  id: number;
  facture_id: number | null;
  montant: number;
  date_paiement: string | null;
  mode_paiement: string | null;
  reference: string | null;
  statut: string;
}

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(Math.round(n));

const STATUT_STYLES: Record<string, string> = {
  confirme: "text-emerald-400",
  en_attente: "text-amber-400",
  annule: "text-slate-500",
  rembourse: "text-blue-400",
};
const STATUT_LABELS: Record<string, string> = {
  confirme: "Confirmé",
  en_attente: "En attente",
  annule: "Annulé",
  rembourse: "Remboursé",
};

function dateCourte(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleDateString("fr-FR");
}

export default function FinanceTransactionsPage() {
  const [rows, setRows] = useState<Encaissement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState("ALL");
  const [search, setSearch] = useState("");

  const charger = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await financeAPI.getEncaissements();
      setRows(Array.isArray(res.data) ? res.data : []);
    } catch {
      setRows([]);
      setError("Encaissements indisponibles. Vérifiez votre connexion ou réessayez.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  const filtered = rows.filter(t => {
    const matchStatus = filterStatus === "ALL" || t.statut === filterStatus;
    const q = search.toLowerCase();
    const matchSearch =
      q === "" ||
      (t.reference ?? "").toLowerCase().includes(q) ||
      String(t.facture_id ?? "").includes(q) ||
      (t.mode_paiement ?? "").toLowerCase().includes(q);
    return matchStatus && matchSearch;
  });

  const totalConfirme = rows.filter(t => t.statut === "confirme").reduce((s, t) => s + t.montant, 0);
  const totalAttente = rows.filter(t => t.statut === "en_attente").reduce((s, t) => s + t.montant, 0);

  const exporter = () => {
    if (filtered.length === 0) {
      toast.info("Aucun encaissement à exporter.");
      return;
    }
    exportToCSV(
      filtered.map(t => ({
        reference: t.reference ?? `ENC-${t.id}`,
        facture_id: t.facture_id ?? "",
        mode_paiement: t.mode_paiement ?? "",
        date_paiement: dateCourte(t.date_paiement),
        montant: t.montant,
        statut: STATUT_LABELS[t.statut] ?? t.statut,
      })),
      "encaissements",
    );
  };

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <CreditCard className="text-emerald-400" size={28} />
            Encaissements & Règlements
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Flux de trésorerie réellement enregistrés (table des paiements)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
            <Database size={12} /> Source : /finance/encaissements
          </span>
          <button
            onClick={charger}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Actualiser
          </button>
          <button onClick={exporter} className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <Download size={14} /> Export
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
          <div className="flex items-center gap-2 mb-2 text-emerald-400"><TrendingUp size={16} /><span className="text-xs">Total encaissé (confirmé)</span></div>
          <p className="text-2xl font-bold text-emerald-400">+{fmtNum(totalConfirme)}</p>
          <p className="text-xs text-muted-foreground mt-0.5">XAF réglés</p>
        </div>
        <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5">
          <div className="flex items-center gap-2 mb-2 text-amber-400"><CreditCard size={16} /><span className="text-xs">En attente</span></div>
          <p className="text-2xl font-bold text-amber-400">{fmtNum(totalAttente)}</p>
          <p className="text-xs text-muted-foreground mt-0.5">XAF à confirmer</p>
        </div>
        <div className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-5">
          <div className="flex items-center gap-2 mb-2 text-blue-400"><Database size={16} /><span className="text-xs">Nombre d&apos;encaissements</span></div>
          <p className="text-2xl font-bold text-blue-400">{rows.length}</p>
          <p className="text-xs text-muted-foreground mt-0.5">lignes enregistrées</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/30 placeholder:text-muted-foreground" placeholder="Rechercher référence, facture, mode..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
          <option value="ALL">Tous statuts</option>
          <option value="confirme">Confirmés</option>
          <option value="en_attente">En attente</option>
          <option value="rembourse">Remboursés</option>
          <option value="annule">Annulés</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        {loading ? (
          <div className="p-10 text-center text-muted-foreground text-sm">Chargement des encaissements…</div>
        ) : error ? (
          <div className="p-10 text-center space-y-3">
            <AlertTriangle size={32} className="mx-auto text-amber-400" />
            <p className="text-sm text-muted-foreground">{error}</p>
            <button onClick={charger} className="inline-flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/60 text-foreground rounded-xl text-xs font-bold">
              <RefreshCw size={14} /> Réessayer
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <CreditCard size={32} className="mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              {rows.length === 0
                ? "Aucun encaissement enregistré."
                : "Aucun encaissement ne correspond à ces critères."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/40 border-b border-border">
                <tr>{["Réf.", "Facture", "Mode", "Date", "Montant (XAF)", "Statut"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                ))}</tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-emerald-400">{t.reference ?? `ENC-${t.id}`}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.facture_id != null ? `#${t.facture_id}` : "—"}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{t.mode_paiement ?? "—"}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{dateCourte(t.date_paiement)}</td>
                    <td className="px-4 py-3 font-bold text-base text-emerald-400">+{fmtNum(t.montant)}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium ${STATUT_STYLES[t.statut] ?? "text-slate-400"}`}>
                        {STATUT_LABELS[t.statut] ?? t.statut}
                      </span>
                    </td>
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
