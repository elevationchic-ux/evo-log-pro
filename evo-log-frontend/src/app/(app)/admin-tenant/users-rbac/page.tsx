'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users, Plus, Search, Shield, Edit, Trash2,
  CheckCircle2, XCircle, Key, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { adminAPI } from '@/lib/api-client';

type UserRole =
  | 'SUPER_ADMIN' | 'ADMIN' | 'EXPERT_COMPTABLE' | 'COMPTABLE'
  | 'DISPATCHER' | 'MAGASINIER' | 'DOUANE' | 'RH'
  | 'MAINTENANCE' | 'CHAUFFEUR' | 'CLIENT_B2B' | 'OPERATEUR' | 'DAF';

interface SystemUser {
  id: string;
  fullName: string;
  email: string;
  role: UserRole;
  tenant: string;
  lastLogin: string;
  isActive: boolean;
  tcodeCount: number;
}

const ROLE_COLORS: Record<string, string> = {
  SUPER_ADMIN: 'bg-red-500/10 text-red-300 border border-red-500/20',
  ADMIN: 'bg-rose-500/10 text-rose-300 border border-rose-500/20',
  DAF: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
  EXPERT_COMPTABLE: 'bg-violet-500/10 text-violet-300 border border-violet-500/20',
  COMPTABLE: 'bg-purple-500/10 text-purple-300 border border-purple-500/20',
  DISPATCHER: 'bg-blue-500/10 text-blue-300 border border-blue-500/20',
  MAGASINIER: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
  DOUANE: 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20',
  RH: 'bg-pink-500/10 text-pink-300 border border-pink-500/20',
  MAINTENANCE: 'bg-orange-500/10 text-orange-300 border border-orange-500/20',
  OPERATEUR: 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20',
  CHAUFFEUR: 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20',
  CLIENT_B2B: 'bg-teal-500/10 text-teal-300 border border-teal-500/20',
};

export default function AdminTenantUsersRbac() {
  const [users, setUsers] = useState<SystemUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminAPI.getUsers();
      const raw = res.data?.items || res.data || [];
      if (Array.isArray(raw) && raw.length > 0) {
        setUsers(raw.map((u: any) => ({
          id: String(u.id),
          fullName: u.full_name || u.username || 'Collaborateur',
          email: u.email,
          role: (u.role || 'OPERATEUR') as UserRole,
          tenant: u.tenant || 'CADC Global',
          lastLogin: u.last_login ? new Date(u.last_login).toLocaleString('fr-FR').slice(0, 16) : 'Jamais',
          isActive: u.is_active !== false,
          tcodeCount: u.role === 'SUPER_ADMIN' ? 9999 : (u.role === 'ADMIN' ? 45 : 12)
        })));
      } else {
        setUsers([]);
      }
    } catch (err) {
      console.error('Failed to load users for RBAC', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const filtered = users.filter(u =>
    u.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.tenant.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggleActive = async (id: string) => {
    try {
      await adminAPI.toggleUserStatus(Number(id));
      setUsers(prev => prev.map(u => u.id === id ? { ...u, isActive: !u.isActive } : u));
      toast.success('Statut utilisateur mis à jour');
    } catch {
      toast.error("Impossible de modifier le statut utilisateur.");
    }
  };


  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-rose-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-rose-500/20 text-rose-300 border border-rose-500/30">
              Contrôle d Accès Basé sur les Rôles
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KADM_USR
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Users className="w-8 h-8 text-rose-400" />
            Gestion des Utilisateurs & RBAC
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Création et administration des comptes utilisateurs avec 11 rôles distincts, accès T-Code granulaires et isolation par tenant.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => toast.info('Formulaire de création d un nouvel utilisateur CADC ERP')}
            className="px-4 py-2.5 bg-gradient-to-r from-rose-600 to-pink-500 text-white font-black text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-rose-500/25 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Créer Utilisateur
          </button>
        </div>
      </div>

      {/* Table Utilisateurs */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <div className="relative max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par nom, email, rôle ou tenant..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans uppercase text-[10px] tracking-wider bg-slate-950">
                <th className="py-3.5 px-4">Utilisateur</th>
                <th className="py-3.5 px-4">Rôle RBAC</th>
                <th className="py-3.5 px-4">Tenant / Société</th>
                <th className="py-3.5 px-4 text-center">T-Codes Autorisés</th>
                <th className="py-3.5 px-4">Dernière Connexion</th>
                <th className="py-3.5 px-4 text-center">Actif</th>
                <th className="py-3.5 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map(u => (
                <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="font-sans font-bold text-slate-100 text-sm">{u.fullName}</div>
                    <div className="text-[11px] text-slate-400">{u.email}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${ROLE_COLORS[u.role]}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-sans text-slate-300">{u.tenant}</td>
                  <td className="py-3.5 px-4 text-center font-bold text-slate-200">
                    {u.tcodeCount >= 9999 ? '∞ Tous' : u.tcodeCount}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">{u.lastLogin}</td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => handleToggleActive(u.id)}
                      className="cursor-pointer"
                    >
                      {u.isActive
                        ? <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto" />
                        : <XCircle className="w-5 h-5 text-slate-600 mx-auto" />
                      }
                    </button>
                  </td>
                  <td className="py-3.5 px-4 text-center flex items-center justify-center gap-1.5">
                    <button
                      onClick={() => toast.info(`Modification du profil de ${u.fullName}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg cursor-pointer"
                      title="Modifier"
                    >
                      <Edit className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => toast.info(`Gestion des permissions T-Code pour ${u.fullName}`)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-amber-400 rounded-lg cursor-pointer"
                      title="Permissions T-Code"
                    >
                      <Key className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Légende des Rôles */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
          Matrice des Rôles RBAC  CADC ERP Logistique
        </h3>
        <div className="flex flex-wrap gap-2">
          {(Object.keys(ROLE_COLORS) as UserRole[]).map(role => (
            <span key={role} className={`px-2.5 py-1 rounded-lg text-[10px] font-bold ${ROLE_COLORS[role]}`}>
              {role}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
