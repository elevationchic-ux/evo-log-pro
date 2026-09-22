"use client";

import React, { useState } from "react";
import {
  Calendar, Plus, Search, CheckCircle, Clock, XCircle,
  AlertTriangle, FileText, Filter, Download, Users
} from "lucide-react";

interface CongeRequest {
  id: number;
  matricule: string;
  nom_complet: string;
  poste: string;
  departement: string;
  type_conge: "ANNUEL" | "MALADIE" | "MATERNITE" | "EXCEPTIONNEL" | "SANS_SOLDE";
  date_debut: string;
  date_fin: string;
  jours_ouvrables: number;
  motif: string;
  statut: "EN_ATTENTE" | "APPROUVE" | "REFUSE" | "ANNULE";
  remplacant?: string;
}

const DEMO_CONGES: CongeRequest[] = [];

const typeConfig: Record<string, { label: string; color: string }> = {
  ANNUEL: { label: "Annuel", color: "text-blue-400 bg-blue-400/10 border-blue-400/30" },
  MALADIE: { label: "Maladie", color: "text-red-400 bg-red-400/10 border-red-400/30" },
  MATERNITE: { label: "Maternité", color: "text-pink-400 bg-pink-400/10 border-pink-400/30" },
  EXCEPTIONNEL: { label: "Exceptionnel", color: "text-amber-400 bg-amber-400/10 border-amber-400/30" },
  SANS_SOLDE: { label: "Sans Solde", color: "text-slate-400 bg-slate-400/10 border-slate-400/30" },
};

const statutConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  EN_ATTENTE: { label: "En attente", color: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <Clock size={12} /> },
  APPROUVE: { label: "Approuvé", color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <CheckCircle size={12} /> },
  REFUSE: { label: "Refusé", color: "text-red-400 bg-red-400/10 border-red-400/30", icon: <XCircle size={12} /> },
  ANNULE: { label: "Annulé", color: "text-slate-400 bg-slate-400/10 border-slate-400/30", icon: <XCircle size={12} /> },
};

export default function RHCongesPage() {
  const [conges, setConges] = useState<CongeRequest[]>(DEMO_CONGES);
  const [search, setSearch] = useState("");
  const [filterStatut, setFilterStatut] = useState("TOUS");
  const [showModal, setShowModal] = useState(false);

  const filtered = conges.filter((c) => {
    const matchSearch = search === "" || c.nom_complet.toLowerCase().includes(search.toLowerCase()) || c.departement.toLowerCase().includes(search.toLowerCase());
    const matchStatut = filterStatut === "TOUS" || c.statut === filterStatut;
    return matchSearch && matchStatut;
  });

  const handleApprouver = (id: number) => {
    setConges(prev => prev.map(c => c.id === id ? { ...c, statut: "APPROUVE" } : c));
  };

  const handleRefuser = (id: number) => {
    setConges(prev => prev.map(c => c.id === id ? { ...c, statut: "REFUSE" } : c));
  };

  const totalJoursApprouves = conges.filter(c => c.statut === "APPROUVE").reduce((s, c) => s + c.jours_ouvrables, 0);

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Calendar className="text-pink-500" size={28} />
            Congés & Absences
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Gestion et validation des demandes de congés du personnel EVO-LOG
          </p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <Download size={16} />
            Planning PDF
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-700 text-white text-sm font-medium transition-colors"
          >
            <Plus size={16} />
            Nouvelle Demande
          </button>
        </div>
      </div>

      {/* KPI Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "En Attente", value: conges.filter(c => c.statut === "EN_ATTENTE").length, color: "text-amber-400 bg-amber-400/10 border-amber-400/20", icon: <Clock size={18} /> },
          { label: "Approuvées", value: conges.filter(c => c.statut === "APPROUVE").length, color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20", icon: <CheckCircle size={18} /> },
          { label: "Refusées", value: conges.filter(c => c.statut === "REFUSE").length, color: "text-red-400 bg-red-400/10 border-red-400/20", icon: <XCircle size={18} /> },
          { label: "Jours Accordés", value: totalJoursApprouves, color: "text-blue-400 bg-blue-400/10 border-blue-400/20", icon: <Calendar size={18} /> },
        ].map((k, i) => (
          <div key={i} className={`rounded-2xl border p-4 ${k.color} flex items-center gap-3`}>
            {k.icon}
            <div>
              <p className="text-xs opacity-70">{k.label}</p>
              <p className="text-2xl font-bold">{k.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30 placeholder:text-muted-foreground"
            placeholder="Rechercher employé, département..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/30"
          value={filterStatut}
          onChange={(e) => setFilterStatut(e.target.value)}
        >
          <option value="TOUS">Tous les statuts</option>
          <option value="EN_ATTENTE">En attente</option>
          <option value="APPROUVE">Approuvés</option>
          <option value="REFUSE">Refusés</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>
                {["Employé", "Type Congé", "Période", "Jours", "Remplaçant", "Statut", "Actions"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((c) => {
                const typeCfg = typeConfig[c.type_conge];
                const statCfg = statutConfig[c.statut];
                return (
                  <tr key={c.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground">{c.nom_complet}</div>
                      <div className="text-xs text-muted-foreground">{c.departement} • {c.matricule}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${typeCfg.color}`}>
                        {typeCfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-foreground">
                      <div>{new Date(c.date_debut).toLocaleDateString("fr-FR")}</div>
                      <div className="text-xs text-muted-foreground">→ {new Date(c.date_fin).toLocaleDateString("fr-FR")}</div>
                    </td>
                    <td className="px-4 py-3 font-bold text-foreground text-center">{c.jours_ouvrables}j</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{c.remplacant || ""}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${statCfg.color}`}>
                        {statCfg.icon}
                        {statCfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {c.statut === "EN_ATTENTE" && (
                        <div className="flex gap-1">
                          <button onClick={() => handleApprouver(c.id)} className="px-3 py-1 rounded-lg text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors">
                            Approuver
                          </button>
                          <button onClick={() => handleRefuser(c.id)} className="px-3 py-1 rounded-lg text-xs bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors">
                            Refuser
                          </button>
                        </div>
                      )}
                      {c.statut !== "EN_ATTENTE" && (
                        <button className="px-3 py-1 rounded-lg text-xs bg-muted text-muted-foreground border border-border hover:bg-accent transition-colors">
                          <FileText size={12} className="inline mr-1" />
                          Détails
                        </button>
                      )}
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
