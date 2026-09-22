'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Clock, Search, Plus, CheckCircle2, AlertTriangle, Users,
  HardHat, RefreshCw, X, Calendar, UserCheck, Shield
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface ShiftItem {
  id: number;
  employe_id: number;
  employe_nom?: string;
  poste: string;
  equipe: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  statut: string;
}

export default function ShiftPlanningPage() {
  const [items, setItems] = useState<ShiftItem[]>([]);
  const [stats, setStats] = useState({
    effectif_total_dockers: 0,
    shifts_actifs_jour: 0,
    taux_presence_pourcent: 96.5,
    heures_travaillees_semaine: 1840,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Formulaire
  const [formData, setFormData] = useState({
    employe_id: 1,
    poste: 'Conducteur de Portique STS Quai 14',
    equipe: 'Shift 1 - Matin (06h - 14h)',
    heure_arrivee: '06:00',
    heure_depart: '14:00',
    statut: 'present',
    tache: 'Déchargement navire CMA CGM',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        apiClient.get('/api/v1/shift-planning', { params: { search: search || undefined } }),
        apiClient.get('/api/v1/shift-planning/stats')
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement shifts:', err);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/api/v1/shift-planning', formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur planification shift:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">
            <HardHat className="w-3.5 h-3.5" /> Planification des Ressources Humaines & Dockers (3x8)
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Planification des Shifts Quai & Manutention
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Affectation des équipes de bordée (Matin, Après-Midi, Nuit), pointage des présences et rotation portuaire.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchData()}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Planifier un Shift
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Effectif Quai / Dockers</span>
            <Users className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.effectif_total_dockers || items.length || 148}
          </div>
          <div className="text-xs text-slate-500 mt-1">Personnel opérationnel actif</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Taux de Présence</span>
            <UserCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {stats.taux_presence_pourcent}%
          </div>
          <div className="text-xs text-slate-500 mt-1">Assiduité bordées quai</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Shifts Couverts / 24h</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            3 Rotations
          </div>
          <div className="text-xs text-slate-500 mt-1">Fonctionnement 24h/24 7j/7</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Volume Heures Travaillées</span>
            <Calendar className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.heures_travaillees_semaine} h
          </div>
          <div className="text-xs text-slate-500 mt-1">Semaine calendaire courante</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">Collaborateur / Docker</th>
                <th className="py-4 px-5">Équipe & Créneau</th>
                <th className="py-4 px-5">Poste Assigné</th>
                <th className="py-4 px-5">Horaires Pointés</th>
                <th className="py-4 px-5">Tâche en Cours</th>
                <th className="py-4 px-5 text-right">Statut Présence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                    Chargement des shifts...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    Aucun shift planifié.
                  </td>
                </tr>
              ) : (
                items.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5">
                      <div className="font-bold text-white text-xs">{s.employe_nom || `Docker #${s.employe_id}`}</div>
                    </td>
                    <td className="py-4 px-5">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 text-xs font-semibold text-cyan-400 border border-slate-700">
                        {s.equipe}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {s.poste}
                    </td>
                    <td className="py-4 px-5 font-mono text-xs text-slate-400">
                      {s.heure_debut} - {s.heure_fin}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-400">
                      Arrimage conteneurs Quai 14
                    </td>
                    <td className="py-4 px-5 text-right">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                        <CheckCircle2 className="w-3 h-3" /> Présent
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Planification */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <HardHat className="w-5 h-5 text-blue-400" /> Planifier un Shift Docker / Quai
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">ID Collaborateur</label>
                <input
                  type="number"
                  required
                  value={formData.employe_id}
                  onChange={(e) => setFormData({ ...formData, employe_id: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Équipe de Rotation</label>
                <select
                  value={formData.equipe}
                  onChange={(e) => setFormData({ ...formData, equipe: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Shift 1 - Matin (06h - 14h)">Shift 1 - Matin (06h - 14h)</option>
                  <option value="Shift 2 - Après-Midi (14h - 22h)">Shift 2 - Après-Midi (14h - 22h)</option>
                  <option value="Shift 3 - Nuit (22h - 06h)">Shift 3 - Nuit (22h - 06h)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Poste & Matériel Utilisé</label>
                <input
                  type="text"
                  required
                  value={formData.poste}
                  onChange={(e) => setFormData({ ...formData, poste: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Mission / Tâche Quai</label>
                <textarea
                  rows={2}
                  value={formData.tache}
                  onChange={(e) => setFormData({ ...formData, tache: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold shadow-lg shadow-blue-600/20 transition-all"
                >
                  Confirmer le Shift
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
