"use client";

import React, { useState, useEffect } from "react";
import {
  FileText, Plus, Search, Globe, Truck, AlertTriangle,
  CheckCircle, Clock, Eye, Download, Filter, RefreshCw
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://EVO-LOG-backend-production.up.railway.app";

interface GoodsDeclaration {
  id: number;
  numero_manifeste: string;
  navire: string;
  armateur: string;
  port_origine: string;
  port_destination: string;
  date_arrivee_prevue: string;
  nature_marchandise: string;
  poids_tonnes: number;
  nombre_conteneurs: number;
  valeur_fob_usd: number;
  statut: string;
  created_at: string;
}

const statutConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  BROUILLON: { label: "Brouillon", color: "text-slate-400 bg-slate-400/10 border-slate-400/30", icon: <Clock size={12} /> },
  CONFIRMEE: { label: "Confirmée", color: "text-blue-400 bg-blue-400/10 border-blue-400/30", icon: <CheckCircle size={12} /> },
  EN_ROUTE: { label: "En Route", color: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <Truck size={12} /> },
  EN_RADE: { label: "En Rade", color: "text-cyan-400 bg-cyan-400/10 border-cyan-400/30", icon: <Globe size={12} /> },
  DEBARQUEE: { label: "Débarquée", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <CheckCircle size={12} /> },
  ANNULEE: { label: "Annulée", color: "text-red-400 bg-red-400/10 border-red-400/30", icon: <AlertTriangle size={12} /> },
};

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(n);

export default function GoodsDeclarationPage() {
  const [declarations, setDeclarations] = useState<GoodsDeclaration[]>([]);
  const [search, setSearch] = useState("");
  const [filterStatut, setFilterStatut] = useState("TOUS");
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchDeclarations();
  }, []);

  const fetchDeclarations = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/transport/goods-declarations/`, { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        if (data.declarations?.length > 0) setDeclarations(data.declarations);
      }
    } catch {}
    finally { setLoading(false); }
  };

  const filtered = declarations.filter((d) => {
    const matchSearch = search === "" || d.navire.toLowerCase().includes(search.toLowerCase()) || d.numero_manifeste.toLowerCase().includes(search.toLowerCase()) || d.nature_marchandise.toLowerCase().includes(search.toLowerCase());
    const matchStatut = filterStatut === "TOUS" || d.statut === filterStatut;
    return matchSearch && matchStatut;
  });

  const totalConteneurs = declarations.reduce((s, d) => s + (d.nombre_conteneurs || 0), 0);
  const totalPoids = declarations.reduce((s, d) => s + (d.poids_tonnes || 0), 0);
  const totalValeur = declarations.reduce((s, d) => s + (d.valeur_fob_usd || 0), 0);

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <FileText className="text-cyan-500" size={28} />
            Déclarations de Fret
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Manifestes d'escale, déclarations marchandises  Port de Douala
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchDeclarations} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium transition-colors">
            <Plus size={16} />
            Nouvelle Déclaration
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Manifestes", value: declarations.length, sub: "déclarations", color: "text-cyan-400 border-cyan-500/20 bg-cyan-500/5" },
          { label: "Conteneurs Déclarés", value: fmtNum(totalConteneurs), sub: "EVP", color: "text-amber-400 border-amber-500/20 bg-amber-500/5" },
          { label: "Tonnage Total", value: fmtNum(Math.round(totalPoids)), sub: "tonnes brut", color: "text-indigo-400 border-indigo-500/20 bg-indigo-500/5" },
          { label: "Valeur Totale", value: `$${fmtNum(Math.round(totalValeur / 1000))}K`, sub: "USD FOB", color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/5" },
        ].map((k, i) => (
          <div key={i} className={`rounded-2xl border p-4 ${k.color}`}>
            <p className="text-xs text-muted-foreground">{k.label}</p>
            <p className="text-2xl font-bold text-foreground mt-1">{k.value}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{k.sub}</p>
          </div>
        ))}
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/30 placeholder:text-muted-foreground"
            placeholder="Rechercher par navire, manifeste, marchandise..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/30" value={filterStatut} onChange={(e) => setFilterStatut(e.target.value)}>
          <option value="TOUS">Tous les statuts</option>
          {Object.keys(statutConfig).map(s => <option key={s}>{s}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>
                {["Manifeste", "Navire & Armateur", "Origine → Destination", "Marchandise", "Conteneurs", "Poids (t)", "Arrivée Prévue", "Statut", "Actions"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((d) => {
                const cfg = statutConfig[d.statut] || statutConfig.BROUILLON;
                return (
                  <tr key={d.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-cyan-400">{d.numero_manifeste}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground">{d.navire}</div>
                      <div className="text-xs text-muted-foreground">{d.armateur}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="text-muted-foreground">{d.port_origine}</div>
                      <div className="text-foreground font-medium">→ {d.port_destination}</div>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground max-w-[180px] truncate">{d.nature_marchandise}</td>
                    <td className="px-4 py-3 text-center font-bold text-foreground">{d.nombre_conteneurs}</td>
                    <td className="px-4 py-3 text-center text-muted-foreground">{fmtNum(d.poids_tonnes)}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap">
                      {d.date_arrivee_prevue ? new Date(d.date_arrivee_prevue).toLocaleDateString("fr-FR") : ""}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${cfg.color}`}>
                        {cfg.icon}{cfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button className="p-1.5 rounded-lg hover:bg-cyan-500/10 text-muted-foreground hover:text-cyan-400 transition-colors" title="Voir">
                          <Eye size={14} />
                        </button>
                        <button className="p-1.5 rounded-lg hover:bg-emerald-500/10 text-muted-foreground hover:text-emerald-400 transition-colors" title="Télécharger">
                          <Download size={14} />
                        </button>
                      </div>
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
