"use client";

import React, { useState } from "react";
import { Package, Plus, Search, Eye, Download, Truck, FileText, CheckCircle, Clock, AlertTriangle } from "lucide-react";

const fmtNum = (n: number) => new Intl.NumberFormat("fr-FR").format(n);

interface Conteneur {
  id: number;
  numero: string;
  type: string;
  taille: string;
  statut: "DISPONIBLE" | "EN_CHARGEMENT" | "EN_TRANSIT" | "AU_DEPOT" | "ENDOMMAGE";
  client: string;
  destination: string;
  poids_kg: number;
  navire?: string;
  date_livraison_prevue?: string;
}

const CONTENEURS: Conteneur[] = [
  { id: 1, numero: "MSCU-7234810-6", type: "DRY", taille: "40HC", statut: "EN_TRANSIT", client: "BOLLORE LOGISTICS", destination: "Bangui – RCA", poids_kg: 18500, navire: "MSC GIOVANNA", date_livraison_prevue: "2026-08-20" },
  { id: 2, numero: "CMAU-3291045-2", type: "REEFER", taille: "40RF", statut: "AU_DEPOT", client: "SDIC – SCDP", destination: "Douala – Entrepôt Bonaberi", poids_kg: 22000, navire: undefined },
  { id: 3, numero: "TCKU-1928374-5", type: "DRY", taille: "20GP", statut: "EN_CHARGEMENT", client: "CFAO MOTORS CM", destination: "Yaoundé – Zone Indus.", poids_kg: 11200 },
  { id: 4, numero: "HLCU-5647382-0", type: "OPEN_TOP", taille: "20OT", statut: "DISPONIBLE", client: "EVO-LOG ERP", destination: "", poids_kg: 0 },
  { id: 5, numero: "GLDU-9182736-4", type: "DRY", taille: "40HC", statut: "ENDOMMAGE", client: "MAERSK CM", destination: "En réparation – Quai 3", poids_kg: 0 },
];

const statutConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  DISPONIBLE: { label: "Disponible", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <CheckCircle size={12} /> },
  EN_CHARGEMENT: { label: "En Chargement", color: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <Package size={12} /> },
  EN_TRANSIT: { label: "En Transit", color: "text-blue-400 bg-blue-400/10 border-blue-400/30", icon: <Truck size={12} /> },
  AU_DEPOT: { label: "Au Dépôt", color: "text-slate-400 bg-slate-400/10 border-slate-400/30", icon: <Clock size={12} /> },
  ENDOMMAGE: { label: "Endommagé", color: "text-red-400 bg-red-400/10 border-red-400/30", icon: <AlertTriangle size={12} /> },
};

export default function TransportContainersPage() {
  const [search, setSearch] = useState("");
  const [filterStatut, setFilterStatut] = useState("TOUS");

  const filtered = CONTENEURS.filter(c => {
    const matchSearch = search === "" || c.numero.toLowerCase().includes(search.toLowerCase()) || c.client.toLowerCase().includes(search.toLowerCase()) || c.destination.toLowerCase().includes(search.toLowerCase());
    const matchStatut = filterStatut === "TOUS" || c.statut === filterStatut;
    return matchSearch && matchStatut;
  });

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Package className="text-cyan-400" size={28} />
            Gestion des Conteneurs
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">Suivi des conteneurs maritimes  Port de Douala</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium transition-colors">
          <Plus size={16} />Ajouter Conteneur
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {Object.entries(statutConfig).map(([statut, cfg]) => (
          <button key={statut} onClick={() => setFilterStatut(filterStatut === statut ? "TOUS" : statut)} className={`rounded-2xl border p-3 text-left transition-all hover:scale-[1.02] ${cfg.color} ${filterStatut === statut ? "ring-2 ring-current" : ""}`}>
            <div className="mb-1.5">{cfg.icon}</div>
            <p className="text-xl font-bold">{CONTENEURS.filter(c => c.statut === statut).length}</p>
            <p className="text-xs opacity-70 mt-0.5">{cfg.label}</p>
          </button>
        ))}
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/30 placeholder:text-muted-foreground" placeholder="Rechercher numéro, client, destination..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>{["Numéro", "Type", "Client", "Destination", "Poids (kg)", "Navire", "Statut", "Actions"].map(h => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map(c => {
                const cfg = statutConfig[c.statut];
                return (
                  <tr key={c.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-cyan-400">{c.numero}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground text-xs">{c.type}</div>
                      <div className="text-xs text-muted-foreground">{c.taille}</div>
                    </td>
                    <td className="px-4 py-3 text-sm text-foreground">{c.client}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{c.destination}</td>
                    <td className="px-4 py-3 text-sm text-foreground">{c.poids_kg > 0 ? fmtNum(c.poids_kg) : ""}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{c.navire || ""}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${cfg.color}`}>
                        {cfg.icon}{cfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button className="p-1.5 rounded-lg hover:bg-cyan-500/10 text-muted-foreground hover:text-cyan-400 transition-colors"><Eye size={14} /></button>
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
