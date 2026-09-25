"use client";

import React, { useState, useEffect } from "react";
import {
  Calendar, Plus, Search, CheckCircle, Clock, XCircle,
  AlertTriangle, FileText, Filter, Download, Users
} from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";

interface CongeRequest {
  id: number;
  employe_id: number;
  employe_nom: string;
  employe_role: string;
  type_conge: string;
  date_debut: string;
  date_fin: string;
  jours_ouvrables: number;
  motif: string;
  statut: "EN_ATTENTE" | "APPROUVE" | "REFUSE" | "ANNULE";
  commentaire_superviseur?: string | null;
}

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
  const [conges, setConges] = useState<CongeRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filterStatut, setFilterStatut] = useState("TOUS");

  const chargerConges = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await apiClient.get("/api/v1/chef-personnel/conges");
      const data = res?.data?.data ?? res?.data ?? [];
      setConges(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setLoadError(e?.response?.data?.detail || "Impossible de charger les demandes de congés. Réessayez.");
      setConges([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    chargerConges();
  }, []);

  const filtered = conges.filter((c) => {
    const matchSearch = search === "" || c.employe_nom?.toLowerCase().includes(search.toLowerCase()) || c.employe_role?.toLowerCase().includes(search.toLowerCase());
    const matchStatut = filterStatut === "TOUS" || c.statut === filterStatut;
    return matchSearch && matchStatut;
  });

  const decider = async (id: number, decision: "APPROUVER" | "REJETER") => {
    const statutCible = decision === "APPROUVER" ? "APPROUVE" : "REFUSE";
    try {
      await apiClient.post(`/api/v1/chef-personnel/conges/${id}/decision`, { decision, commentaire: "" });
      setConges(prev => prev.map(c => c.id === id ? { ...c, statut: statutCible as CongeRequest["statut"] } : c));
      toast.success(decision === "APPROUVER" ? "Demande de congé approuvée." : "Demande de congé refusée.");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Échec de l'enregistrement de la décision.");
    }
  };

  const handleApprouver = (id: number) => decider(id, "APPROUVER");
  const handleRefuser = (id: number) => decider(id, "REJETER");

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
          <button
            onClick={() => toast.info("La génération du planning PDF est disponible depuis le Portail Employé.")}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors"
          >
            <Download size={16} />
            Planning PDF
          </button>
          <button
            onClick={() => toast.info("Pour créer une demande de congé, utilisez le Portail Employé (self-service salarié).")}
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
                {["Employé", "Type Congé", "Période", "Jours", "Motif", "Statut", "Actions"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading && (
                <tr><td colSpan={7} className="px-4 py-12 text-center text-muted-foreground text-sm">Chargement des demandes de congés…</td></tr>
              )}
              {!loading && loadError && (
                <tr><td colSpan={7} className="px-4 py-12 text-center text-red-400 text-sm flex flex-col items-center gap-2">
                  <AlertTriangle size={20} className="mx-auto" />
                  {loadError}
                  <button onClick={chargerConges} className="px-3 py-1.5 rounded-lg border border-border text-xs hover:bg-accent">Réessayer</button>
                </td></tr>
              )}
              {!loading && !loadError && filtered.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-12 text-center text-muted-foreground text-sm">
                  <Users size={22} className="mx-auto mb-2 opacity-50" />
                  Aucune demande de congé. {search || filterStatut !== "TOUS" ? "Aucun résultat pour les filtres appliqués." : "Les nouvelles demandes apparaîtront ici dès réception."}
                </td></tr>
              )}
              {!loading && filtered.map((c) => {
                const typeCfg = typeConfig[c.type_conge] ?? { label: c.type_conge, color: "text-slate-400 bg-slate-400/10 border-slate-400/30" };
                const statCfg = statutConfig[c.statut] ?? { label: c.statut, color: "text-slate-400 bg-slate-400/10 border-slate-400/30", icon: null };
                return (
                  <tr key={c.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground">{c.employe_nom}</div>
                      <div className="text-xs text-muted-foreground">{c.employe_role}</div>
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
                    <td className="px-4 py-3 text-xs text-muted-foreground max-w-[180px] truncate" title={c.motif || ""}>{c.motif || ""}</td>
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
                        <button
                          onClick={() => toast.info(`Demande #${c.id}  ${c.employe_nom} : ${c.motif || "aucun motif renseigné"}.`)}
                          className="px-3 py-1 rounded-lg text-xs bg-muted text-muted-foreground border border-border hover:bg-accent transition-colors"
                        >
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
