"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { adminAPI, rbacAPI } from "../../../../../lib/api-client";
import {
  Users, Plus, Search, Edit, Trash2, Shield, CheckCircle,
  XCircle, Eye, Filter, RefreshCw, Mail, Phone,
  UserCheck, UserX, ChevronDown, BadgeCheck, X, Briefcase
} from "lucide-react";

interface UserEntry {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  role: string;
  roles: string[];
  matricule: string;
  job_title: string;
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

function timeAgo(dateStr: string) {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return "À l'instant";
  if (diff < 3600) return `${Math.floor(diff / 60)}min`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}j`;
  return `${Math.floor(diff / 604800)}sem`;
}

export default function UserManagementPage() {
  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("TOUS");
  const [filterStatut, setFilterStatut] = useState("TOUS");
  const [view, setView] = useState<"grid" | "table">("table");
  const queryClient = useQueryClient();
  const { data: apiUsers = [], isLoading } = useQuery({
    queryKey: ["admin-users", search],
    queryFn: async () => (await adminAPI.getUsers({ search: search || undefined, limit: 500 })).data,
  });
  // Accréditations granulaires de l'entreprise, agrégées par utilisateur.
  const { data: accreditations = [] } = useQuery({
    queryKey: ["admin-accreditations"],
    queryFn: async () => (await rbacAPI.listAccreditations()).data || [],
  });
  const accreditationsByUser = React.useMemo(() => {
    const map = new Map<number, { actif: number; total: number }>();
    for (const a of (Array.isArray(accreditations) ? accreditations : [])) {
      const uid = Number(a.user_id);
      const cur = map.get(uid) || { actif: 0, total: 0 };
      cur.total += 1;
      if ((a.statut || "actif") === "actif") cur.actif += 1;
      map.set(uid, cur);
    }
    return map;
  }, [accreditations]);
  const users: UserEntry[] = apiUsers.map((user: any) => {
    const [prenom = "", ...nomParts] = String(user.full_name || user.username || "").split(" ");
    const roleList: string[] = Array.isArray(user.roles) && user.roles.length
      ? user.roles
      : [user.role || "OPERATEUR"];
    return {
      id: user.id,
      nom: nomParts.join(" "),
      prenom,
      email: user.email,
      telephone: user.phone || "",
      role: user.role || roleList[0] || "OPERATEUR",
      roles: roleList,
      matricule: user.matricule || "",
      job_title: user.job_title || "",
      departement: user.department?.name || "",
      statut: user.is_active ? "ACTIF" : "SUSPENDU",
      derniere_connexion: user.last_login || user.created_at || new Date(0).toISOString(),
      avatar_initiales: `${prenom[0] || ""}${nomParts[0]?.[0] || ""}`.toUpperCase(),
    };
  });
  const statusMutation = useMutation({
    mutationFn: (user: UserEntry) =>
      adminAPI.toggleUserStatus(user.id, { is_active: user.statut !== "ACTIF" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
  });

  // --- Editeur "Utilisateur != Role" : identite (matricule/poste) + casquettes ---
  const [editUser, setEditUser] = useState<UserEntry | null>(null);
  const [form, setForm] = useState({ matricule: "", job_title: "" });
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const { data: roleCatalog = [] } = useQuery({
    queryKey: ["admin-roles-catalog"],
    queryFn: async () => (await adminAPI.getRoles()).data || [],
  });
  const assignableRoles: string[] = (Array.isArray(roleCatalog) ? roleCatalog : [])
    .map((r: any) => r.name as string)
    .filter(Boolean);

  useEffect(() => {
    if (editUser) {
      setForm({ matricule: editUser.matricule || "", job_title: editUser.job_title || "" });
      setSelectedRoles(editUser.roles || []);
    }
  }, [editUser]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!editUser) return;
      // 1) identite employe, 2) casquettes (role_level derive cote backend).
      await adminAPI.updateUser(editUser.id, { matricule: form.matricule, job_title: form.job_title });
      await adminAPI.assignUserRoles(editUser.id, selectedRoles);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      toast.success("Utilisateur mis à jour (identité & casquettes).");
      setEditUser(null);
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail;
      toast.error(detail || "Échec de la mise à jour.");
    },
  });

  const toggleRole = (name: string) =>
    setSelectedRoles(prev => prev.includes(name) ? prev.filter(r => r !== name) : [...prev, name]);

  const roles = [...new Set(users.flatMap(u => u.roles))];

  const filtered = users.filter(u => {
    const matchSearch = search === "" || `${u.prenom} ${u.nom}`.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase()) || u.departement.toLowerCase().includes(search.toLowerCase());
    const matchRole = filterRole === "TOUS" || u.roles.includes(filterRole);
    const matchStatut = filterStatut === "TOUS" || u.statut === filterStatut;
    return matchSearch && matchRole && matchStatut;
  });

  const toggleStatut = (id: number) => {
    const user = users.find((entry) => entry.id === id);
    if (user) statusMutation.mutate(user);
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
                {["Utilisateur", "Email", "Rôle", "Département", "Accréditations", "Dernière Connexion", "Statut", "Actions"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground text-xs uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map(user => {
                const acc = accreditationsByUser.get(user.id);
                return (
                  <tr key={user.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                          {user.avatar_initiales}
                        </div>
                        <div>
                          <p className="font-medium text-foreground">{user.prenom} {user.nom}</p>
                          <p className="text-xs text-muted-foreground">
                            {user.job_title ? <span className="inline-flex items-center gap-1"><Briefcase size={11} />{user.job_title}</span> : user.telephone}
                            {user.matricule && <span className="ml-2 font-mono text-[11px] text-slate-500">{user.matricule}</span>}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{user.email}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {user.roles.map(r => (
                          <span key={r} className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold border ${roleColors[r] || "text-slate-400 bg-slate-400/10 border-slate-400/30"}`}>{r}</span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{user.departement}</td>
                    <td className="px-4 py-3">
                      {acc ? (
                        <Link href="/admin/accreditations" title={`${acc.actif} accréditation(s) active(s) sur ${acc.total}`} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border text-emerald-400 bg-emerald-400/10 border-emerald-400/30 hover:bg-emerald-400/20 transition-colors">
                          <BadgeCheck size={12} />{acc.actif}
                        </Link>
                      ) : (
                        <span className="text-xs text-muted-foreground/60"></span>
                      )}
                    </td>
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
                        <button onClick={() => setEditUser(user)} className="p-1.5 rounded-lg hover:bg-amber-500/10 text-muted-foreground hover:text-amber-400 transition-colors" title="Modifier"><Edit size={14} /></button>
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

      {/* Modale "Utilisateur ≠ Rôle" : identité employé séparée des casquettes. */}
      {editUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={() => setEditUser(null)} aria-hidden="true" />
          <div className="relative z-10 w-full max-w-lg rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-5">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-bold text-foreground">Modifier l'utilisateur</h2>
                <p className="text-xs text-muted-foreground">{editUser.prenom} {editUser.nom} · {editUser.email}</p>
              </div>
              <button onClick={() => setEditUser(null)} className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground" aria-label="Fermer"><X size={18} /></button>
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Identité employé</h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs text-muted-foreground">Matricule</label>
                  <input className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30" placeholder="MAT-0001" value={form.matricule} onChange={e => setForm(p => ({ ...p, matricule: e.target.value }))} />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs text-muted-foreground">Poste / fonction</label>
                  <input className="w-full bg-background border border-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30" placeholder="Cariste, déclarant…" value={form.job_title} onChange={e => setForm(p => ({ ...p, job_title: e.target.value }))} />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Casquettes (rôles)</h3>
              <p className="text-[11px] text-muted-foreground">Un collaborateur peut porter plusieurs rôles ; l'accès découle du plus privilégié.</p>
              <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-1">
                {assignableRoles.map(r => {
                  const active = selectedRoles.includes(r);
                  return (
                    <button key={r} type="button" onClick={() => toggleRole(r)} className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${active ? "bg-indigo-600 text-white border-indigo-500" : "bg-background text-muted-foreground border-border hover:border-slate-500"}`}>{r}</button>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setEditUser(null)} className="px-4 py-2 rounded-xl border border-border text-sm hover:bg-accent transition-colors">Annuler</button>
              <button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending} className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium transition-colors">
                {saveMutation.isPending ? "Enregistrement…" : "Enregistrer"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
