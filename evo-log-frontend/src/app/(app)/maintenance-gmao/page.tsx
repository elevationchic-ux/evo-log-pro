'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Wrench, PlusCircle, CheckCircle2, AlertTriangle, RefreshCw,
  Settings, ClipboardList, Cpu, Calendar, BarChart2, X, Save
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function MaintenanceGMAOPage() {
  const [ordres, setOrdres] = useState<any[]>([]);
  const [equipements, setEquipements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newOrdre, setNewOrdre] = useState({
    numero_ordre: `OM-${Date.now().toString().slice(-6)}`,
    equipement_id: '',
    type_maintenance: 'préventive',
    priorite: 'normale',
    description: '',
    date_planifiee: new Date().toISOString().slice(0, 16),
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resOrdres, resEquip] = await Promise.allSettled([
        apiClient.get('/api/v1/maintenance-gmao/ordres', { params: { limit: 50 } }),
        apiClient.get('/api/v1/maintenance-gmao/equipements', { params: { limit: 50 } })
      ]);
      if (resOrdres.status === 'fulfilled' && resOrdres.value.data)
        setOrdres(resOrdres.value.data?.data || resOrdres.value.data || []);
      if (resEquip.status === 'fulfilled' && resEquip.value.data)
        setEquipements(resEquip.value.data?.data || resEquip.value.data || []);
    } catch (err) {
      console.error('GMAO fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreate = async () => {
    try {
      await apiClient.post('/api/v1/maintenance-gmao/ordres', {
        ...newOrdre,
        equipement_id: parseInt(newOrdre.equipement_id) || 1,
        date_planifiee: new Date(newOrdre.date_planifiee).toISOString()
      });
      setShowForm(false);
      fetchData();
    } catch (err) { console.error('Erreur création ordre:', err); }
  };

  const handleCompleter = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/maintenance-gmao/ordres/${id}/completer`, null, {
        params: {
          date_fin: new Date().toISOString(),
          duree_reelle: 120,
          observations: 'Intervention terminée avec succès'
        }
      });
      fetchData();
    } catch (err) { console.error('Erreur complétion:', err); }
  };

  const getPrioriteBadge = (p: string) => {
    switch (p) {
      case 'critique': return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      case 'haute': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'normale': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Wrench className="w-3.5 h-3.5" /> GMAO — Gestion de Maintenance Assistée par Ordinateur
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Maintenance & Équipements Portuaires</h1>
          <p className="text-xs text-slate-400 mt-1">Ordres de travaux préventifs et correctifs, plannings, calibrations et suivi des pièces de rechange.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-orange-600 hover:bg-orange-500 text-white text-xs font-bold shadow-lg shadow-orange-900/20 transition-all active:scale-95">
            <PlusCircle className="w-4 h-4" /> Nouvel Ordre
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Ordres', value: ordres.length, icon: ClipboardList, color: 'text-cyan-400' },
          { label: 'En Cours', value: ordres.filter(o => o.statut === 'en_cours' || !o.statut).length, icon: Wrench, color: 'text-amber-400' },
          { label: 'Complétés', value: ordres.filter(o => o.statut === 'complété').length, icon: CheckCircle2, color: 'text-emerald-400' },
          { label: 'Équipements', value: equipements.length, icon: Cpu, color: 'text-purple-400' },
        ].map((s) => (
          <div key={s.label} className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-3xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{s.label}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <p className={`text-2xl font-black mt-2 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-slate-900/90 border border-orange-500/30 p-6 rounded-3xl shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black text-white">Nouvel Ordre de Maintenance</h2>
            <button onClick={() => setShowForm(false)}><X className="w-5 h-5 text-slate-400 hover:text-white" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { key: 'numero_ordre', label: 'N° Ordre', type: 'text' },
              { key: 'equipement_id', label: 'ID Équipement', type: 'number' },
              { key: 'description', label: 'Description', type: 'text' },
              { key: 'date_planifiee', label: 'Date Planifiée', type: 'datetime-local' },
            ].map((f) => (
              <div key={f.key}>
                <label className="text-xs font-medium text-slate-400 block mb-1">{f.label}</label>
                <input
                  type={f.type}
                  value={(newOrdre as any)[f.key]}
                  onChange={(e) => setNewOrdre({ ...newOrdre, [f.key]: e.target.value })}
                  className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-orange-500 transition-colors"
                />
              </div>
            ))}
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Type Maintenance</label>
              <select value={newOrdre.type_maintenance} onChange={(e) => setNewOrdre({ ...newOrdre, type_maintenance: e.target.value })} className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-orange-500">
                <option value="préventive">Préventive</option>
                <option value="corrective">Corrective</option>
                <option value="prédictive">Prédictive</option>
                <option value="mise_en_service">Mise en Service</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Priorité</label>
              <select value={newOrdre.priorite} onChange={(e) => setNewOrdre({ ...newOrdre, priorite: e.target.value })} className="w-full bg-slate-950/60 border border-slate-700 text-sm text-white rounded-2xl px-4 py-2.5 focus:outline-none focus:border-orange-500">
                <option value="faible">Faible</option>
                <option value="normale">Normale</option>
                <option value="haute">Haute</option>
                <option value="critique">Critique</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <button onClick={() => setShowForm(false)} className="px-5 py-2.5 rounded-2xl bg-slate-800 text-slate-300 text-xs font-bold">Annuler</button>
            <button onClick={handleCreate} className="px-5 py-2.5 rounded-2xl bg-orange-600 hover:bg-orange-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg">
              <Save className="w-4 h-4" /> Créer l'Ordre
            </button>
          </div>
        </div>
      )}

      {/* Ordres Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <ClipboardList className="w-5 h-5 text-orange-400" />
          <h2 className="text-base font-black text-white">Ordres de Maintenance</h2>
          <span className="ml-auto text-xs text-slate-400">{ordres.length} ordres</span>
        </div>
        {loading ? (
          <div className="p-12 text-center text-slate-400"><RefreshCw className="w-6 h-6 animate-spin text-orange-400 mx-auto mb-2" /><span>Chargement depuis la base de données...</span></div>
        ) : ordres.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Wrench className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="font-bold text-white">Aucun ordre de maintenance</p>
            <p className="text-xs mt-1 text-slate-500">Créez le premier ordre de travaux pour commencer.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800/80">
                  {['N° Ordre', 'Type', 'Priorité', 'Description', 'Date Planifiée', 'Statut', 'Actions'].map(h => (
                    <th key={h} className="px-5 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {ordres.map((o: any) => (
                  <tr key={o.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-4 font-mono text-xs text-cyan-400">{o.numero_ordre}</td>
                    <td className="px-5 py-4 text-slate-300 capitalize">{o.type_maintenance}</td>
                    <td className="px-5 py-4">
                      <span className={`px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase border ${getPrioriteBadge(o.priorite)}`}>{o.priorite}</span>
                    </td>
                    <td className="px-5 py-4 text-slate-300 max-w-xs truncate">{o.description}</td>
                    <td className="px-5 py-4 text-slate-400 text-xs">{o.date_planifiee ? new Date(o.date_planifiee).toLocaleDateString('fr-FR') : '-'}</td>
                    <td className="px-5 py-4">
                      <span className={`px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase border ${o.statut === 'complété' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'}`}>
                        {o.statut || 'en_cours'}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      {o.statut !== 'complété' && (
                        <button onClick={() => handleCompleter(o.id)} className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5 transition-all">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Compléter
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
