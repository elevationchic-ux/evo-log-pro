'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Users, Search, Plus, CheckCircle2, XCircle, Shield, Mail, Phone, RefreshCw, Lock } from 'lucide-react';
import { toast } from 'sonner';
import { adminAPI } from '@/lib/api-client';

interface UserItem {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  tenant?: string;
  is_active: boolean;
  created_at?: string;
  last_login?: string;
}

const ROLE_COLORS: Record<string, string> = {
  SUPER_ADMIN: 'text-red-400 bg-red-500/10 border-red-500/30',
  ADMIN: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
  DAF: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  DIRECTEUR_TRANSPORT: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  CHEF_PARC: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  TRANSITAIRE: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
  CHEF_PERSONNEL: 'text-pink-400 bg-pink-500/10 border-pink-500/30',
  OPERATEUR: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  CHAUFFEUR: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30',
  CLIENT_B2B: 'text-violet-400 bg-violet-500/10 border-violet-500/30',
};

export default function AdminSaasUsersPage() {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const [newUser, setNewUser] = useState({
    username: '',
    full_name: '',
    email: '',
    phone: '',
    password: '',
    role: 'OPERATEUR'
  });

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminAPI.getUsers();
      const raw = res.data?.items || res.data || [];
      setUsers(Array.isArray(raw) ? raw : []);
    } catch (err) {
      console.error('Failed to fetch users', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await adminAPI.createUser({
        ...newUser,
        is_active: true
      });
      toast.success(`Compte utilisateur pour ${newUser.email} créé avec succès`);
      setShowModal(false);
      setNewUser({ username: '', full_name: '', email: '', phone: '', password: '', role: 'OPERATEUR' });
      fetchUsers();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création de l'utilisateur");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleStatus = async (user: UserItem) => {
    try {
      await adminAPI.toggleUserStatus(user.id);
      toast.success(`Statut de ${user.email} mis à jour`);
      fetchUsers();
    } catch {
      // Optimistic update
      setUsers(prev => prev.map(u => u.id === user.id ? { ...u, is_active: !u.is_active } : u));
    }
  };

  const filtered = users.filter(u => {
    const matchSearch = 
      (u.full_name || '').toLowerCase().includes(search.toLowerCase()) || 
      (u.email || '').toLowerCase().includes(search.toLowerCase()) ||
      (u.username || '').toLowerCase().includes(search.toLowerCase());
    const matchRole = roleFilter === 'ALL' || u.role === roleFilter;
    return matchSearch && matchRole;
  });

  const getRoleBadge = (roleName: string) => {
    const key = (roleName || '').toUpperCase().replace(/[\s-]/g, '_');
    const color = ROLE_COLORS[key] || 'text-slate-400 bg-slate-800 border-slate-700';
    return (
      <span className={`px-2 py-0.5 rounded text-[10px] font-black border ${color}`}>
        {roleName || 'UTILISATEUR'}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-slate-900/90 border border-blue-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Administration SaaS • Gestion des Utilisateurs
          </span>
          <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            T-Code : KADM_USR
          </span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-400" />
              Gestion des Utilisateurs & Accès
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Comptes collaborateurs, chauffeurs et clients B2B déployés sur la plateforme
            </p>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-center">
            <button
              onClick={fetchUsers}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 transition-all"
              title="Rafraîchir"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            </button>
            <button
              onClick={() => setShowModal(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-lg shadow-blue-600/20 transition-all"
            >
              <Plus className="w-4 h-4" /> Nouvel Utilisateur
            </button>
          </div>
        </div>
      </div>

      {/* Filters & Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Rechercher par nom, email, identifiant..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
            {['ALL', 'SUPER_ADMIN', 'ADMIN', 'DAF', 'DIRECTEUR_TRANSPORT', 'CHAUFFEUR', 'CLIENT_B2B'].map(role => (
              <button
                key={role}
                onClick={() => setRoleFilter(role)}
                className={`px-3 py-1.5 rounded-xl text-[11px] font-bold transition-all whitespace-nowrap ${
                  roleFilter === role
                    ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                    : 'text-slate-400 hover:text-slate-200 bg-slate-950'
                }`}
              >
                {role === 'ALL' ? 'Tous les rôles' : role}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Utilisateur</th>
                <th className="py-3.5 px-4">Coordonnées</th>
                <th className="py-3.5 px-4">Entreprise (Tenant)</th>
                <th className="py-3.5 px-4 text-center">Rôle</th>
                <th className="py-3.5 px-4 text-center">Statut</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(u => (
                <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-bold font-sans text-slate-100">{u.full_name}</div>
                    <div className="text-[11px] text-slate-500 font-mono">@{u.username}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="text-slate-300 font-sans flex items-center gap-1.5">
                      <Mail className="w-3.5 h-3.5 text-slate-500" />
                      <span>{u.email}</span>
                    </div>
                    {u.phone && (
                      <div className="text-[11px] text-slate-500 flex items-center gap-1.5 mt-0.5">
                        <Phone className="w-3 h-3 text-slate-600" />
                        <span>{u.phone}</span>
                      </div>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 font-sans">
                    {u.tenant || 'CADC Global'}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    {getRoleBadge(u.role)}
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      u.is_active
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-red-500/10 text-red-400 border-red-500/20'
                    }`}>
                      {u.is_active ? 'ACTIF' : 'VERROUILLÉ'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => handleToggleStatus(u)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all ${
                        u.is_active
                          ? 'bg-amber-500/15 text-amber-300 hover:bg-amber-500/25 border border-amber-500/30'
                          : 'bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25 border border-emerald-500/30'
                      }`}
                    >
                      {u.is_active ? 'Verrouiller' : 'Déverrouiller'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create User Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100">Créer un Compte Collaborateur</h3>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Nom complet *</label>
                <input
                  type="text"
                  required
                  value={newUser.full_name}
                  onChange={e => setNewUser({ ...newUser, full_name: e.target.value })}
                  placeholder="Ex: Jean Paul Ndongo"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Adresse Email Professionnelle *</label>
                <input
                  type="email"
                  required
                  value={newUser.email}
                  onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                  placeholder="nom@entreprise.cm"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Numéro de Téléphone</label>
                <input
                  type="text"
                  value={newUser.phone}
                  onChange={e => setNewUser({ ...newUser, phone: e.target.value })}
                  placeholder="+237 6 99 00 00 00"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Mot de passe temporaire *</label>
                <input
                  type="password"
                  required
                  value={newUser.password}
                  onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                  placeholder="8 caractères minimum"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Rôle Métier Assigné</label>
                <select
                  value={newUser.role}
                  onChange={e => setNewUser({ ...newUser, role: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="ADMIN">ADMIN (Administrateur)</option>
                  <option value="DAF">DAF (Finance & Comptabilité)</option>
                  <option value="DIRECTEUR_TRANSPORT">DIRECTEUR TRANSPORT</option>
                  <option value="CHEF_PARC">CHEF PARC & MATÉRIEL</option>
                  <option value="TRANSITAIRE">TRANSITAIRE AGRÉÉ</option>
                  <option value="CHEF_PERSONNEL">CHEF DU PERSONNEL</option>
                  <option value="OPERATEUR">OPÉRATEUR DE SAISIE</option>
                  <option value="CHAUFFEUR">CHAUFFEUR ROUTIER</option>
                  <option value="CLIENT_B2B">CLIENT PARTENAIRE B2B</option>
                </select>
              </div>
              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-bold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-600/20"
                >
                  {submitting ? 'Création...' : 'Créer le Compte'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
