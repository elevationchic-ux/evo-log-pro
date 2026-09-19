"use client";

import React, { useState } from "react";
import {
  Users, Plus, Search, Edit, Trash2, Shield, CheckCircle,
  XCircle, Eye, Filter, RefreshCw, Mail, Phone,
  UserCheck, UserX, ChevronDown
} from "lucide-react";

interface UserEntry {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  role: string;
  departement: string;
  statut: "ACTIF" | "INACTIF" | "SUSPENDU";
  derniere_connexion: string;
  avatar_initiales: string;
}

const roleColors: Record<string, string> = {
  ADMIN: "text-red-400 bg-red-400/10 border-red-400/30",
  MANAGER: "text-orange-400 bg-orange-400/10 border-orange-400/30",
  DISPATCHER: "text-cyan-400 bg-cyan-400/10 border-cyan-400/30",
  CHAUFFEUR: "text-sky-400 bg-sky-400/10 border-sky-400/30",
  MAGASINIER: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  RH: "text-pink-400 bg-pink-400/10 border-pink-400/30",
  FINANCE: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
  TRANSIT: "text-violet-400 bg-violet-400/10 border-violet-400/30",
  QHSE: "text-rose-400 bg-rose-400/10 border-rose-400/30",
  MAINTENANCE: "text-indigo-400 bg-indigo-400/10 border-indigo-400/30",
};

const USERS: UserEntry[] = [
  { id: 1, nom: "NJOYA", prenom: "Christian", email: "admin@evo-log.cm", telephone: "+237 699 000 001", role: "ADMIN", departement: "Direction Générale", statut: "ACTIF", derniere_connexion: new Date().toISOString(), avatar_initiales: "CN" },
  { id: 2, nom: "NGUEMA", prenom: "Marie-Claire", email: "rh@evo-log.cm", telephone: "+237 677 890 123", role: "RH", departement: "Ressources Humaines", statut: "ACTIF", derniere_connexion: new Date(Date.now() - 7200000).toISOString(), avatar_initiales: "MN" },
  { id: 3, nom: "KAMGA", prenom: "Paul", email: "dispatcher@evo-log.cm", telephone: "+237 699 222 333", role: "DISPATCHER", departement: "Transport", statut: "ACTIF", derniere_connexion: new Date(Date.now() - 1800000).toISOString(), avatar_initiales: "PK" },
  { id: 4, nom: "EBANG", prenom: "Patrick", email: "finance@evo-log.cm", telephone: "+237 677 444 555", role: "FINANCE", departement: "Finance & Comptabilité", statut: "ACTIF", derniere_connexion: new Date(Date.now() - 3600000).toISOString(), avatar_initiales: "PE" },
  { id: 5, nom: "MVONDO", prenom: "Jean-Marc", email: "jm.mvondo@evo-log.cm", telephone: "+237 655 678 901", role: "CHAUFFEUR", departement: "Transport", statut: "ACTIF", derniere_connexion: new Date(Date.now() - 86400000).toISOString(), avatar_initiales: "JM" },
  { id: 6, nom: "ONDOUA", prenom: "Pierre", email: "magasin@evo-log.cm", telephone: "+237 699 111 222", role: "MAGASINIER", departement: "Magasin WMS", statut: "ACTIF", derniere_connexion: new Date(Date.now() - 14400000).toISOString(), avatar_initiales: "PO" },
  { id: 7, nom: "EKOTTO", prenom: "Jules", email: "transit@evo-log.cm", telephone: "+237 677 333 444", role: "TRANSIT", departement: "Transit & Douane", statut: "ACTIF", derniere_connexion: new Date(Date.now() - 21600000).toISOString(), avatar_initiales: "JE" },
  { id: 8, nom: "MBIDA", prenom: "Albert", email: "qhse@evo-log.cm", telephone: "+237 655 555 666", role: "QHSE", departement: "QHSE & Sécurité", statut: "SUSPENDU", derniere_connexion: new Date(Date.now() - 604800000).toISOString(), avatar_initiales: "AM" },
];

function timeAgo(dateStr: string) {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return "À l'instant";
  if (diff < 3600) return `${Math.floor(diff / 60)}min`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}j`;
  return `${Math.floor(diff / 604800)}sem`;
}

export default function UserManagementPage() {
  const [users, setUsers] = useState<UserEntry[]>(USERS);
  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("TOUS");
  const [filterStatut, setFilterStatut] = useState("TOUS");
  const [view, setView] = useState<"grid" | "table">("table");

  const roles = [...new Set(USERS.map(u => u.role))];

  const filtered = users.filter(u => {
    const matchSearch = search === "" || `${u.prenom} ${u.nom}`.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase()) || u.departement.toLowerCase().includes(search.toLowerCase());
    const matchRole = filterRole === "TOUS" || u.role === filterRole;
    const matchStatut = filterStatut === "TOUS" || u.statut === filterStatut;
    return matchSearch && matchRole && matchStatut;
  });

  const toggleStatut = (id: number) => {
    setUsers(prev => prev.map(u => u.id === id ? { ...u, statut: u.statut === "ACTIF" ? "SUSPENDU" : "ACTIF" } : u));
  };

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Users className="text-slate-400" size={28} />
            Gestion des Utilisateurs
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            {users.filter(u => u.statut === "ACTIF").length} utilisateurs actifs sur {users.length} comptes
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium transition-colors border border-slate-600">
          <Plus size={16} />
          Nouvel Utilisateur
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Comptes", value: users.length, color: "text-foreground" },
          { label: "Actifs", value: users.filter(u => u.statut === "ACTIF").length, color: "text-emerald-400" },
          { label: "Suspendus", value: users.filter(u => u.statut === "SUSPENDU").length, color: "text-amber-400" },
          { label: "Rôles Définis", value: roles.length, color: "text-violet-400" },
        ].map((s, i) => (
          <div key={i} className="rounded-2xl border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">{s.label}</p>
            <p className={`text-2xl font-bold mt-1 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input className="w-full bg-card border border-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30 placeholder:text-muted-foreground" placeholder="Rechercher nom, email, département..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterRole} onChange={e => setFilterRole(e.target.value)}>
          <option value="TOUS">Tous les rôles</option>
          {roles.map(r => <option key={r}>{r}</option>)}
        </select>
        <select className="bg-card border border-border rounded-xl px-4 py-2.5 text-sm" value={filterStatut} onChange={e => setFilterStatut(e.target.value)}>
          <option value="TOUS">Tous les statuts</option>
          <option value="ACTIF">Actifs</option>
          <option value="SUSPENDU">Suspendus</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 border-b border-border">
              <tr>
                {["Utilisateur", "Email", "Rôle", "Département", "Dernière Connexion", "Statut", "Actions"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map(user => {
                const roleCfg = roleColors[user.role] || "text-slate-400 bg-slate-400/10 border-slate-400/30";
                return (
                  <tr key={user.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                          {user.avatar_initiales}
                        </div>
                        <div>
                          <p className="font-medium text-foreground">{user.prenom} {user.nom}</p>
                          <p className="text-xs text-muted-foreground">{user.telephone}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{user.email}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border ${roleCfg}`}>{user.role}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{user.departement}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{timeAgo(user.derniere_connexion)}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${user.statut === "ACTIF" ? "text-emerald-400 bg-emerald-400/10 border-emerald-400/30" : "text-amber-400 bg-amber-400/10 border-amber-400/30"}`}>
                        {user.statut === "ACTIF" ? <CheckCircle size={11} /> : <XCircle size={11} />}
                        {user.statut}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button className="p-1.5 rounded-lg hover:bg-blue-500/10 text-muted-foreground hover:text-blue-400 transition-colors" title="Voir"><Eye size={14} /></button>
                        <button className="p-1.5 rounded-lg hover:bg-amber-500/10 text-muted-foreground hover:text-amber-400 transition-colors" title="Modifier"><Edit size={14} /></button>
                        <button onClick={() => toggleStatut(user.id)} className={`p-1.5 rounded-lg transition-colors ${user.statut === "ACTIF" ? "hover:bg-red-500/10 text-muted-foreground hover:text-red-400" : "hover:bg-emerald-500/10 text-muted-foreground hover:text-emerald-400"}`} title={user.statut === "ACTIF" ? "Suspendre" : "Réactiver"}>
                          {user.statut === "ACTIF" ? <UserX size={14} /> : <UserCheck size={14} />}
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
