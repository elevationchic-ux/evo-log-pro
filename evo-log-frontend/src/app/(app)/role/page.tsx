'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Shield, Users, PlusCircle, RefreshCw, CheckCircle2,
  Settings, Layers, Lock, Edit2, Trash2, UserCheck, X, Save
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function RolePage() {
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newRole, setNewRole] = useState({
    nom: '',
    description: '',
    modules: [] as string[],
  });

  const availableModules = [
    'transport', 'finance', 'magasin', 'transit', 'acconage',
    'parc', 'rh', 'rapports', 'admin', 'maintenance', 'integration',
    'notifications', 'chat', 'douane', 'gps', 'prestataires'
  ];

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/roles/roles');
      if (res.data) setRoles(res.data || []);
    } catch (err) {
      console.error('Roles fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleInitSystemRoles = async () => {
    try {
      await apiClient.post('/api/v1/roles/init-system-roles');
      fetchData();
    } catch (err) { console.error('Erreur init rôles système:', err); }
  };

  const handleCreateRole = async () => {
    try {
      await apiClient.post('/api/v1/roles/roles', { ...newRole });
      setShowCreateForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création rôle:', err); }
  };

  const handleUpdateModules = async (id: number, modules: string[]) => {
    try {
      await apiClient.put(`/api/v1/roles/roles/${id}/modules`, { modules });
      fetchData();
    } catch (err) { console.error('Erreur mise à jour modules:', err); }
  };

  const toggleModule = (m: string) => {
    setNewRole(prev => ({
      ...prev,
      modules: prev.modules.includes(m) ? prev.modules.filter(x => x !== m) : [...prev.modules, m]
    }));
  };

  const getRoleColor = (nom: string) => {
    if (nom?.toLowerCase().includes('admin')) return 'text-rose-400 bg-rose-500/20 border-rose-500/30';
    if (nom?.toLowerCase().includes('directeur') || nom?.toLowerCase().includes('manager')) return 'text-purple-400 bg-purple-500/20 border-purple-500/30';
    if (nom?.toLowerCase().includes('opérateur') || nom?.toLowerCase().includes('agent')) return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
    return 'text-slate-400 bg-slate-500/20 border-slate-500/30';
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Shield className="w-3.5 h-3.5" /> RBAC — Contrôle d'Accès Basé sur les Rôles
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Gestion des Rôles & Permissions</h1>
          <p className="text-xs text-slate-400 mt-1">Configuration fine des rôles système (SuperAdmin, Directeur, Agent, Opérateur) et attribution des modules autorisés par rôle.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={handleInitSystemRoles} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <Settings className="w-3.5 h-3.5" /> Init Rôles Système
          </button>
          <button onClick={() => setShowCreateForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold shadow-lg shadow-red-900/20 transition-all">
            <PlusCircle className="w-4 h-4" /> Nouveau Rôle
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Rôles', value: roles.length, icon: Shield, color: 'text-red-400' },
          { label: 'Rôles Système', value: roles.filter(r => r.systeme || r.is_system).length, icon: Lock, color: 'text-purple-400' },
          { label: 'Rôles Personnalisés', value: roles.filter(r => !r.systeme && !r.is_system).length, icon: UserCheck, color: 'text-cyan-400' },
          { label: 'Modules Couverts', value: availableModules.length, icon: Layers, color: 'text-emerald-400' },
        ].map((s) => (
          <div key={s.label} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{s.label}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <p className={`text-2xl font-black mt-2 ${s.color}`}>{loading ? '—' : s.value}</p>
          </div>
        ))}
      </div>

      {showCreateForm && (
        <div className="bg-slate-900/90 border border-red-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Créer un Nouveau Rôle</h2>
            <button onClick={() => setShowCreateForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
            {[
              { key: 'nom', label: 'Nom du Rôle', type: 'text' },
              { key: 'description', label: 'Description', type: 'text' },
            ].map(f => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input type={f.type} value={(newRole as any)[f.key]} onChange={(e) => setNewRole({ ...newRole, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-red-500 transition-colors" />
              </div>
            ))}
          </div>
          <div>
            <label className="text-xs font-medium text-slate-400 block mb-2">Modules Autorisés</label>
            <div className="flex flex-wrap gap-2">
              {availableModules.map(m => (
                <button key={m} onClick={() => toggleModule(m)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition-all ${newRole.modules.includes(m) ? 'bg-red-600/30 text-red-300 border-red-500/50' : 'bg-slate-800/60 text-slate-400 border-slate-700/60 hover:border-slate-600/60'}`}>
                  {m}
                </button>
              ))}
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowCreateForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreateRole} className="px-5 py-2.5 rounded-2xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold flex items-center gap-2">
              <Save className="w-4 h-4" /> Créer le Rôle
            </button>
          </div>
        </div>
      )}

      {/* Roles Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <Shield className="w-5 h-5 text-red-400" />
          <h2 className="text-base font-black text-white">Rôles Configurés</h2>
          <span className="ml-auto text-xs text-slate-400">{roles.length} rôles</span>
        </div>
        {loading ? (
          <div className="p-12 text-center"><RefreshCw className="w-6 h-6 animate-spin text-red-400 mx-auto mb-2" /></div>
        ) : roles.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Shield className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="font-bold text-white">Aucun rôle configuré</p>
            <p className="text-xs text-slate-500 mt-1">Cliquez sur "Init Rôles Système" pour créer les rôles par défaut.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {roles.map((r: any) => (
              <div key={r.id} className="p-5 hover:bg-slate-800/40 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-xl text-xs font-bold uppercase border ${getRoleColor(r.nom)}`}>{r.nom}</span>
                    {(r.systeme || r.is_system) && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700/60 text-slate-400 border border-slate-600/60">Système</span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400">{r.description || 'Sans description'}</p>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {(r.modules || []).map((m: string) => (
                    <span key={m} className="px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">{m}</span>
                  ))}
                  {(!r.modules || r.modules.length === 0) && <span className="text-xs text-slate-600 italic">Aucun module assigné</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
