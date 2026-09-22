"use client";

import React, { useState, useEffect } from "react";
import {
  Book, Search, Filter, AlertCircle, CheckCircle,
  Clock, User, Shield, Eye, Download, Calendar,
  RefreshCw, ChevronDown, Activity
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://EVO-LOG-backend-production.up.railway.app";

interface AuditLog {
  id: number;
  timestamp: string;
  utilisateur: string;
  role: string;
  action: string;
  module: string;
  ressource: string;
  resultat: "SUCCES" | "ECHEC" | "WARNING";
  ip_adresse: string;
  details?: string;
}

const FALLBACK_LOGS: AuditLog[] = [];

const resultatConfig = {
  SUCCES: { color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30", icon: <CheckCircle size={12} /> },
  ECHEC: { color: "text-red-400 bg-red-400/10 border-red-400/30", icon: <AlertCircle size={12} /> },
  WARNING: { color: "text-amber-400 bg-amber-400/10 border-amber-400/30", icon: <AlertCircle size={12} /> },
};

const actionColor: Record<string, string> = {
  LOGIN: "text-blue-400",
  LOGOUT: "text-slate-400",
  CREATE: "text-emerald-400",
  UPDATE: "text-amber-400",
  DELETE: "text-red-400",
  EXPORT: "text-indigo-400",
  CONFIG: "text-violet-400",
};

function timeAgo(dateStr: string) {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return `il y a ${diff}s`;
  if (diff < 3600) return `il y a ${Math.floor(diff / 60)}min`;
  if (diff < 86400) return `il y a ${Math.floor(diff / 3600)}h`;
  return `il y a ${Math.floor(diff / 86400)}j`;
}

export default function AdminJournalPage() {
  const [logs, setLogs] = useState<AuditLog[]>(FALLBACK_LOGS);
  const [search, setSearch] = useState("");
  const [filterResultat, setFilterResultat] = useState("TOUS");
  const [filterModule, setFilterModule] = useState("TOUS");
  const [filterAction, setFilterAction] = useState("TOUS");
  const [loading, setLoading] = useState(false);

  const modules = [...new Set(logs.map(l => l.module))];
  const actions = [...new Set(logs.map(l => l.action))];

  const filtered = logs.filter(l => {
    const matchSearch = search === "" || l.utilisateur.toLowerCase().includes(search.toLowerCase()) || l.action.toLowerCase().includes(search.toLowerCase()) || l.ressource.toLowerCase().includes(search.toLowerCase());
    const matchResultat = filterResultat === "TOUS" || l.resultat === filterResultat;
    const matchModule = filterModule === "TOUS" || l.module === filterModule;
    const matchAction = filterAction === "TOUS" || l.action === filterAction;
    return matchSearch && matchResultat && matchModule && matchAction;
  });

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Book className="text-slate-400" size={28} />
            Journal d'Audit Système
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Traçabilité complète de toutes les actions utilisateurs  EVO-LOG ERP
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setLogs([])} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <RefreshCw size={14} />
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">
            <Download size={14} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Actions Totales", value: logs.length, color: "text-foreground", bg: "border-border bg-card" },
          { label: "Succès", value: logs.filter(l => l.resultat === "SUCCES").length, color: "text-emerald-400", bg: "border-emerald-500/20 bg-emerald-500/5" },
          { label: "Échecs", value: logs.filter(l => l.resultat === "ECHEC").length, color: "text-red-400", bg: "border-red-500/20 bg-red-500/5" },
          { label: "Avertissements", value: logs.filter(l => l.resultat === "WARNING").length, color: "text-amber-400", bg: "border-amber-500/20 bg-amber-500/5" },
        ].map((s, i) => (
          <div key={i} className={`rounded-2xl border p-4 ${s.bg}`}>
            <p className="text-xs text-muted-foreground">{s.label}</p>
            <p className={`text-2xl font-bold mt-1 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30 placeholder:text-muted-foreground" placeholder="Rechercher utilisateur, action, ressource..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterResultat} onChange={e => setFilterResultat(e.target.value)}>
          <option value="TOUS">Tous les résultats</option>
          <option value="SUCCES">Succès</option>
          <option value="ECHEC">Échec</option>
          <option value="WARNING">Warning</option>
        </select>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterModule} onChange={e => setFilterModule(e.target.value)}>
          <option value="TOUS">Tous modules</option>
          {modules.map(m => <option key={m}>{m}</option>)}
        </select>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterAction} onChange={e => setFilterAction(e.target.value)}>
          <option value="TOUS">Toutes actions</option>
          {actions.map(a => <option key={a}>{a}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>
                {["Horodatage", "Utilisateur", "Action", "Module", "Ressource", "Résultat", "IP", "Détails"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((log) => {
                const resCfg = resultatConfig[log.resultat];
                return (
                  <tr key={log.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                      <div>{new Date(log.timestamp).toLocaleDateString("fr-FR")}</div>
                      <div className="text-xs opacity-60">{timeAgo(log.timestamp)}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                          {log.utilisateur[0].toUpperCase()}
                        </div>
                        <div>
                          <div className="text-xs font-medium text-foreground">{log.utilisateur}</div>
                          <div className="text-xs text-muted-foreground font-mono">{log.role}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-mono font-bold text-xs ${actionColor[log.action] || "text-foreground"}`}>{log.action}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground font-mono">{log.module}</td>
                    <td className="px-4 py-3 text-xs text-foreground max-w-[200px] truncate" title={log.ressource}>{log.ressource}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${resCfg.color}`}>
                        {resCfg.icon}{log.resultat}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground font-mono whitespace-nowrap">{log.ip_adresse}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground max-w-[200px] truncate" title={log.details}>{log.details}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-border text-xs text-muted-foreground">
          {filtered.length} entrée{filtered.length > 1 ? "s" : ""} affichée{filtered.length > 1 ? "s" : ""}
        </div>
      </div>
    </div>
  );
}
