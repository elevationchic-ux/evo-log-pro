"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck, Users, Settings, Book, Bell, Plus,
  Search, Edit, Trash2, CheckCircle, XCircle, Lock,
  Shield, Eye, Database, FileText, BarChart3
} from "lucide-react";

const ROLES = [
  { id: 1, nom: "ADMIN", description: "Accès total à toutes les fonctions du système", permissions: ["all"], couleur: "#ef4444", utilisateurs: 2 },
  { id: 2, nom: "MANAGER", description: "Supervision multi-modules, validation workflows", permissions: ["transport.*", "magasin.*", "finance.read", "rh.read"], couleur: "#f97316", utilisateurs: 4 },
  { id: 3, nom: "DISPATCHER", description: "Gestion missions transport et affectation chauffeurs", permissions: ["transport.*", "parc.read"], couleur: "#06b6d4", utilisateurs: 3 },
  { id: 4, nom: "CHAUFFEUR", description: "Accès lecture missions assignées, ePOD, tickets carburant", permissions: ["transport.missions.own", "transport.epod", "transport.fuel.create"], couleur: "#22d3ee", utilisateurs: 18 },
  { id: 5, nom: "MAGASINIER", description: "Gestion stocks, réceptions, bons d'enlèvement", permissions: ["magasin.*"], couleur: "#f59e0b", utilisateurs: 5 },
  { id: 6, nom: "RH", description: "Gestion employés, congés, paie", permissions: ["rh.*"], couleur: "#ec4899", utilisateurs: 2 },
  { id: 7, nom: "FINANCE", description: "Facturation, encaissements, cotations", permissions: ["finance.*"], couleur: "#10b981", utilisateurs: 3 },
  { id: 8, nom: "TRANSIT", description: "Dossiers transit, douane CEMAC", permissions: ["transit.*", "acconage.read"], couleur: "#8b5cf6", utilisateurs: 2 },
  { id: 9, nom: "QHSE", description: "Rapports QHSE, incidents, conformité", permissions: ["qhse.*", "incidents.*"], couleur: "#dc2626", utilisateurs: 1 },
  { id: 10, nom: "MAINTENANCE", description: "Ordres réparation, pièces, atelier", permissions: ["maintenance.*", "parc.*"], couleur: "#6366f1", utilisateurs: 3 },
  { id: 11, nom: "CLIENT", description: "Accès portail client – tracking et documents", permissions: ["client-portal.*"], couleur: "#64748b", utilisateurs: 12 },
];

const MODULE_PERMISSIONS = [
  { module: "Transport", icon: "🚛", permissions: ["Voir missions", "Créer mission", "Modifier", "Supprimer", "Dispatch", "ePOD", "Carburant"] },
  { module: "Magasin WMS", icon: "📦", permissions: ["Voir stocks", "Réception", "Bon enlèvement", "Inventaire", "Ordres transfert", "Analytics"] },
  { module: "Finance", icon: "💰", permissions: ["Voir factures", "Créer facture", "Encaissements", "Rapports", "Cotations", "Export"] },
  { module: "RH", icon: "👥", permissions: ["Voir employés", "Gérer congés", "Paie", "Créer employé"] },
  { module: "Transit", icon: "🛂", permissions: ["Voir dossiers", "Créer dossier", "Validation", "Export douane"] },
  { module: "QHSE", icon: "⚠️", permissions: ["Voir rapports", "Créer rapport", "Incidents", "Conformité"] },
  { module: "Admin", icon: "⚙️", permissions: ["Utilisateurs", "Rôles", "Audit", "Configuration"] },
];

export default function RBACPage() {
  const [activeTab, setActiveTab] = useState<"roles" | "matrix">("roles");
  const [search, setSearch] = useState("");

  const filteredRoles = ROLES.filter(r =>
    search === "" || r.nom.toLowerCase().includes(search.toLowerCase()) || r.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Shield className="text-violet-400" size={28} />
            Gestion des Rôles & Permissions RBAC
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Configuration du contrôle d'accès basé sur les rôles  {ROLES.reduce((s, r) => s + r.utilisateurs, 0)} utilisateurs actifs
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium transition-colors">
          <Plus size={16} />
          Nouveau Rôle
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted/50 rounded-xl w-fit border border-border">
        {([{ id: "roles", label: "Rôles & Utilisateurs", icon: <Users size={14} /> }, { id: "matrix", label: "Matrice Permissions", icon: <Database size={14} /> }] as const).map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id ? "bg-card text-foreground shadow-sm border border-border" : "text-muted-foreground hover:text-foreground"}`}
          >
            {tab.icon}{tab.label}
          </button>
        ))}
      </div>

      {activeTab === "roles" && (
        <>
          {/* Search */}
          <div className="relative max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30 placeholder:text-muted-foreground"
              placeholder="Rechercher un rôle..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Roles Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredRoles.map((role) => (
              <div key={role.id} className="rounded-2xl border border-border bg-card p-5 hover:shadow-md transition-all group">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: role.couleur, boxShadow: `0 0 8px ${role.couleur}50` }} />
                    <span className="font-bold text-foreground font-mono text-sm">{role.nom}</span>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="p-1.5 rounded-lg hover:bg-violet-500/10 text-muted-foreground hover:text-violet-400 transition-colors">
                      <Edit size={13} />
                    </button>
                    {role.nom !== "ADMIN" && (
                      <button className="p-1.5 rounded-lg hover:bg-red-500/10 text-muted-foreground hover:text-red-400 transition-colors">
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mb-3 leading-relaxed">{role.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {role.permissions.slice(0, 2).map((p, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground font-mono">{p}</span>
                    ))}
                    {role.permissions.length > 2 && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">+{role.permissions.length - 2}</span>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Users size={11} />{role.utilisateurs}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {activeTab === "matrix" && (
        <div className="rounded-2xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-muted/40 border-b border-border">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-muted-foreground sticky left-0 bg-muted/40 min-w-[140px]">Module / Rôle</th>
                  {ROLES.filter(r => ["ADMIN","MANAGER","DISPATCHER","MAGASINIER","RH","FINANCE","TRANSIT","QHSE","MAINTENANCE"].includes(r.nom)).map(r => (
                    <th key={r.id} className="px-2 py-3 text-center font-mono" style={{ color: r.couleur }}>{r.nom}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {MODULE_PERMISSIONS.map((mod) => (
                  <tr key={mod.module} className="hover:bg-muted/20">
                    <td className="px-4 py-3 font-semibold text-foreground sticky left-0 bg-card whitespace-nowrap">
                      {mod.icon} {mod.module}
                    </td>
                    {ROLES.filter(r => ["ADMIN","MANAGER","DISPATCHER","MAGASINIER","RH","FINANCE","TRANSIT","QHSE","MAINTENANCE"].includes(r.nom)).map(role => {
                      const hasAccess = role.nom === "ADMIN" || role.permissions.some(p => p.startsWith(mod.module.split(" ")[0].toLowerCase()) || p === "all");
                      return (
                        <td key={role.id} className="px-2 py-3 text-center">
                          {hasAccess
                            ? <CheckCircle size={14} className="mx-auto text-emerald-400" />
                            : <XCircle size={14} className="mx-auto text-muted-foreground opacity-30" />
                          }
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
