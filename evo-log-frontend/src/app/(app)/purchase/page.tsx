"use client";

import React, { useState } from "react";
import {
  ShoppingCart, Plus, Search, CheckCircle, Clock,
  AlertTriangle, Download, Filter, TrendingDown,
  Package, FileText, DollarSign, Eye, Edit
} from "lucide-react";

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(n);

const PURCHASE_ORDERS = [
  { id: "PO-2026-001", fournisseur: "TOTALENERGIES CAMEROUN", description: "Gasoil B7 – 5 000 litres", categorie: "CARBURANT", quantite: 5000, unite: "L", montant_xaf: 3600000, demandeur: "Direction Parc", urgence: false, statut: "APPROUVE", date: "2026-08-10" },
  { id: "PO-2026-002", fournisseur: "MICHELIN AFRIQUE CENTRALE", description: "Pneus 315/70R22.5 – 8 unités", categorie: "PIECES_RECHANGE", quantite: 8, unite: "UN", montant_xaf: 960000, demandeur: "Chef Atelier", urgence: true, statut: "EN_ATTENTE", date: "2026-08-12" },
  { id: "PO-2026-003", fournisseur: "ONASER", description: "Vignettes techniques – 12 véhicules", categorie: "SERVICES", quantite: 12, unite: "UN", montant_xaf: 420000, demandeur: "Direction Parc", urgence: false, statut: "BROUILLON", date: "2026-08-14" },
];

const REQUISITIONS = [
  { id: "REQ-2026-001", titre: "Uniformes conducteurs 2026", description: "Renouvellement dotation annuelle – 25 conducteurs", categorie: "FOURNITURES", montant_xaf: 750000, demandeur: "Direction RH", statut: "APPROUVE" },
  { id: "REQ-2026-002", titre: "Licences antivirus serveurs", description: "Renouvellement Kaspersky Enterprise – 15 serveurs", categorie: "SERVICES", montant_xaf: 1200000, demandeur: "Direction IT", statut: "EN_ATTENTE" },
];

const statutConfig: Record<string, { label: string; color: string }> = {
  BROUILLON: { label: "Brouillon", color: "text-slate-400 bg-slate-400/10 border-slate-400/30" },
  EN_ATTENTE: { label: "En attente", color: "text-amber-400 bg-amber-400/10 border-amber-400/30" },
  APPROUVE: { label: "Approuvé", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30" },
  RECEPTIONNE: { label: "Réceptionné", color: "text-blue-400 bg-blue-400/10 border-blue-400/30" },
};

export default function PurchasePage() {
  const [activeTab, setActiveTab] = useState<"po" | "req">("po");
  const [search, setSearch] = useState("");

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <ShoppingCart className="text-violet-400" size={28} />
            Achats & Procurement
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">Bons de commande, réquisitions et suivi fournisseurs</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium transition-colors">
          <Plus size={16} />
          Nouveau PO
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "PO En Attente", value: PURCHASE_ORDERS.filter(p => p.statut === "EN_ATTENTE").length, color: "text-amber-400", bg: "border-amber-500/20 bg-amber-500/5" },
          { label: "Budget Engagé", value: `${fmtNum(Math.round(PURCHASE_ORDERS.reduce((s, p) => s + p.montant_xaf, 0) / 1000))}K XAF`, color: "text-violet-400", bg: "border-violet-500/20 bg-violet-500/5" },
          { label: "Urgences", value: PURCHASE_ORDERS.filter(p => p.urgence).length, color: "text-red-400", bg: "border-red-500/20 bg-red-500/5" },
          { label: "Réquisitions", value: REQUISITIONS.length, color: "text-blue-400", bg: "border-blue-500/20 bg-blue-500/5" },
        ].map((k, i) => (
          <div key={i} className={`rounded-2xl border p-4 ${k.bg}`}>
            <p className="text-xs text-muted-foreground">{k.label}</p>
            <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted/50 rounded-xl w-fit border border-border">
        {[{ id: "po", label: "Bons de Commande" }, { id: "req", label: "Réquisitions" }].map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id as any)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === t.id ? "bg-card text-foreground shadow-sm border border-border" : "text-muted-foreground hover:text-foreground"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Filtres */}
      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30 placeholder:text-muted-foreground" placeholder="Rechercher..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {activeTab === "po" && (
        <div className="rounded-2xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/40 border-b border-border">
                <tr>{["Référence", "Fournisseur", "Description", "Montant (XAF)", "Urgence", "Statut", "Actions"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                ))}</tr>
              </thead>
              <tbody className="divide-y divide-border">
                {PURCHASE_ORDERS.map(po => {
                  const cfg = statutConfig[po.statut];
                  return (
                    <tr key={po.id} className="hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs font-bold text-violet-400">{po.id}</td>
                      <td className="px-4 py-3 text-sm text-foreground font-medium">{po.fournisseur}</td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">{po.description}</td>
                      <td className="px-4 py-3 font-bold text-foreground">{fmtNum(po.montant_xaf)}</td>
                      <td className="px-4 py-3">{po.urgence && <span className="text-xs text-red-400 font-bold bg-red-400/10 px-2 py-0.5 rounded-full border border-red-400/30">URGENT</span>}</td>
                      <td className="px-4 py-3"><span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${cfg.color}`}>{cfg.label}</span></td>
                      <td className="px-4 py-3"><div className="flex gap-1">
                        <button className="p-1.5 rounded-lg hover:bg-violet-500/10 text-muted-foreground hover:text-violet-400 transition-colors"><Eye size={14} /></button>
                        {po.statut === "EN_ATTENTE" && <button className="px-2 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors">Approuver</button>}
                      </div></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "req" && (
        <div className="space-y-3">
          {REQUISITIONS.map(req => {
            const cfg = statutConfig[req.statut];
            return (
              <div key={req.id} className="rounded-2xl border border-border bg-card p-4 hover:shadow-md transition-all">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-xs text-violet-400">{req.id}</span>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${cfg.color}`}>{cfg.label}</span>
                    </div>
                    <p className="font-semibold text-foreground">{req.titre}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{req.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">Demandeur : <span className="text-foreground">{req.demandeur}</span></p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-lg font-bold text-violet-400">{fmtNum(req.montant_xaf)}</p>
                    <p className="text-xs text-muted-foreground">XAF estimé</p>
                    {req.statut === "EN_ATTENTE" && (
                      <div className="flex gap-1 mt-2">
                        <button className="px-2 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors">Approuver</button>
                        <button className="px-2 py-1 rounded-lg text-xs bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors">Refuser</button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
