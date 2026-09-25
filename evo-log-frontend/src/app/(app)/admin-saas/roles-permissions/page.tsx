'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Shield, Users, Building2, Key, Search, Plus, CheckCircle2, XCircle, RefreshCw, Layers } from 'lucide-react';
import { toast } from 'sonner';
import { adminAPI } from '@/lib/api-client';

interface RoleItem {
  id: number;
  name: string;
  label?: string;
  description?: string;
  level: number;
  nb_users?: number;
  is_active: boolean;
  is_system?: boolean;
}

interface UserItem {
  id: number;
  full_name: string;
  email: string;
  role: string;
  tenant: string;
  is_active: boolean;
  last_login?: string;
}

const ROLE_COLORS: Record<string, string> = {
  SUPER_ADMIN: 'text-red-400 bg-red-500/10 border-red-500/30',
  ADMIN: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
  DAF: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  CHEF_COMPTABLE: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  DIRECTEUR_TRANSPORT: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  CHEF_PARC: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  TRANSITAIRE: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
  DECLARANT: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
  CHEF_PERSONNEL: 'text-pink-400 bg-pink-500/10 border-pink-500/30',
  MAGASINIER: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  OPERATEUR: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  CHAUFFEUR: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30',
  CLIENT_B2B: 'text-violet-400 bg-violet-500/10 border-violet-500/30',
};

const MODULES = [
  'Transport Flotte', 'Magasin WMS MAG3', 'Finance & Trésorerie', 
  'Comptabilité OHADA', 'RH & Personnel', 'Transit & Douane', 
  'Maintenance GMAO', 'Rapports & BI', 'Portail Client B2B'
];

export default function RolesPermissionsPage() {
  const [tab, setTab] = useState<'roles' | 'users' | 'matrix'>('roles');
  const [roles, setRoles] = useState<RoleItem[]>([]);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // Role creation modal
  const [showModal, setShowModal] = useState(false);
  const [newRole, setNewRole] = useState({ name: '', description: '', level: 3 });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [rRes, uRes] = await Promise.allSettled([
        adminAPI.getRoles(),
        adminAPI.getUsers()
      ]);

      if (rRes.status === 'fulfilled' && rRes.value?.data) {
        const raw = rRes.value.data;
        setRoles(Array.isArray(raw) ? raw : []);
      }

      if (uRes.status === 'fulfilled' && uRes.value?.data) {
        const raw = uRes.value.data?.items || uRes.value.data || [];
        setUsers(Array.isArray(raw) ? raw : []);
      }
    } catch (err) {
      console.error('Failed to load roles and users', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRole.name) return;
    try {
      await adminAPI.createRole(newRole);
      toast.success(`Rôle ${newRole.name} créé avec succès`);
      setShowModal(false);
      setNewRole({ name: '', description: '', level: 3 });
      loadData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création du rôle");
    }
  };

  const getRoleStyle = (name: string) => {
    const key = name.toUpperCase().replace(/[\s-]/g, '_');
    return ROLE_COLORS[key] || 'text-slate-400 bg-slate-800 border-slate-700';
  };

  const filteredUsers = users.filter(u =>
    (u.full_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (u.email || '').toLowerCase().includes(search.toLowerCase()) ||
    (u.role || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-slate-900/90 border border-red-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-red-500/20 text-red-300 border border-red-500/30">
            Administration SaaS • Contrôle d&apos;Accès & Permissions
          </span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            T-Code : KADM_RLS
          </span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <Shield className="w-8 h-8 text-red-400" />
              Gestion des Rôles & Permissions RBAC
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Hiérarchie granulaire : Super Admin → Admin Entreprise → DAF / Directeurs → Opérateurs → Chauffeurs → Clients B2B
            </p>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-center">
            <button
              onClick={loadData}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 transition-all"
              title="Rafraîchir"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-red-400' : ''}`} />
            </button>
            <button
              onClick={() => setShowModal(true)}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-lg shadow-red-600/20 transition-all"
            >
              <Plus className="w-4 h-4" /> Nouveau Rôle
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setTab('roles')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            tab === 'roles' ? 'bg-red-500/20 text-red-300 border border-red-500/40' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Rôles & Niveaux ({roles.length})</span>
        </button>
        <button
          onClick={() => setTab('users')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            tab === 'users' ? 'bg-red-500/20 text-red-300 border border-red-500/40' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Habilitations Utilisateurs ({users.length})</span>
        </button>
        <button
          onClick={() => setTab('matrix')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            tab === 'matrix' ? 'bg-red-500/20 text-red-300 border border-red-500/40' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Key className="w-4 h-4" />
          <span>Matrice des Accès Modules</span>
        </button>
      </div>

      {/* Tab: Roles */}
      {tab === 'roles' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {roles.map(r => (
            <div key={r.id} className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 p-5 rounded-2xl space-y-3 shadow-lg transition-all">
              <div className="flex items-center justify-between">
                <span className={`px-2.5 py-1 rounded-lg text-xs font-black border ${getRoleStyle(r.name)}`}>
                  {r.name}
                </span>
                <span className="text-[11px] font-mono text-slate-400">Niveau {r.level}</span>
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100">{r.label || r.name}</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{r.description || 'Habilitations standards'}</p>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
                <span>{r.nb_users || 0} utilisateurs affectés</span>
                <span className="text-emerald-400 font-bold">Actif</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab: Users */}
      {tab === 'users' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between gap-4">
            <div className="relative max-w-sm flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Rechercher par nom, email, rôle..."
                className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-red-500"
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">Utilisateur</th>
                  <th className="py-3.5 px-4">Entreprise (Tenant)</th>
                  <th className="py-3.5 px-4 text-center">Rôle Assigné</th>
                  <th className="py-3.5 px-4 text-center">Statut</th>
                  <th className="py-3.5 px-4 text-right">Dernière Connexion</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filteredUsers.map(u => (
                  <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold font-sans text-slate-100">{u.full_name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{u.email}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-sans">{u.tenant || 'CADC Global'}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black border ${getRoleStyle(u.role)}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        u.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}>
                        {u.is_active ? 'ACTIF' : 'VERROUILLÉ'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right text-slate-400">
                      {u.last_login ? new Date(u.last_login).toLocaleString('fr-FR') : 'Récent'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Matrix */}
      {tab === 'matrix' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-sm font-bold text-slate-100">Matrice des Droits par Module Métier</h3>
            <p className="text-xs text-slate-400">Cartographie d&apos;accès automatique selon le niveau hiérarchique RBAC</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                  <th className="py-3.5 px-4">Module Métier</th>
                  {roles.slice(0, 7).map(r => (
                    <th key={r.id} className="py-3.5 px-3 text-center">{r.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {MODULES.map((mod, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-sans font-bold text-slate-200">{mod}</td>
                    {roles.slice(0, 7).map(r => {
                      const hasAccess = r.level <= 1 || (r.level === 2 && idx < 7) || (r.level === 3 && (idx === 0 || idx === 1 || idx === 8));
                      return (
                        <td key={r.id} className="py-3.5 px-3 text-center">
                          {hasAccess ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <XCircle className="w-4 h-4 text-slate-400 mx-auto" />
                          )}
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

      {/* Create Role Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100">Créer un Nouveau Rôle RBAC</h3>
            <form onSubmit={handleCreateRole} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Code du Rôle * (Ex: AUDITEUR_QUALITE)</label>
                <input
                  type="text"
                  required
                  value={newRole.name}
                  onChange={e => setNewRole({ ...newRole, name: e.target.value })}
                  placeholder="CODE_DU_ROLE"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-red-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={newRole.description}
                  onChange={e => setNewRole({ ...newRole, description: e.target.value })}
                  placeholder="Périmètre d'action et responsabilités..."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-red-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Niveau Hiérarchique</label>
                <select
                  value={newRole.level}
                  onChange={e => setNewRole({ ...newRole, level: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-red-500"
                >
                  <option value={1}>Niveau 1 (Administrateur)</option>
                  <option value={2}>Niveau 2 (Direction / Chef Département)</option>
                  <option value={3}>Niveau 3 (Opérateur / Terrain / Partenaire)</option>
                </select>
              </div>
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-bold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold shadow-lg shadow-red-600/20"
                >
                  Créer le Rôle
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
