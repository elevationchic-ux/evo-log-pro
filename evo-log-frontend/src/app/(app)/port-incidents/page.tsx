'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  AlertTriangle, Search, Plus, CheckCircle2, Clock, ShieldAlert,
  HardHat, RefreshCw, X, FileText, AlertOctagon
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface IncidentItem {
  id: number;
  type: string;
  reference: string;
  date: string;
  lieu: string;
  gravite: string;
  description: string;
  statut: string;
  declarant: string;
}

export default function PortIncidentsPage() {
  const [items, setItems] = useState<IncidentItem[]>([]);
  const [stats, setStats] = useState({
    total_accidents_travail: 0,
    accidents_avec_arret: 0,
    investigations_en_cours: 0,
    jours_sans_accident: 84,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Formulaire
  const [formData, setFormData] = useState({
    type: 'travail',
    lieu: 'Quai 14 - Terminal Conteneurs',
    gravite: 'moyen',
    arret_travail: false,
    description: 'Chute de plain-pied lors de l\'arrimage conteneur',
    declarant: 'Chef de Bordée Dockers',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        apiClient.get('/api/v1/port-incidents', { params: { search: search || undefined } }),
        apiClient.get('/api/v1/port-incidents/stats')
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement incidents:', err);
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
      await apiClient.post('/api/v1/port-incidents', formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur déclaration incident:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold uppercase tracking-wider mb-2">
            <ShieldAlert className="w-3.5 h-3.5" /> Sécurité Portuaire & QHSE
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Gestion des Incidents Portuaires & Sécurité Quai
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Signalement en temps réel des avaries, accidents du travail dockers, enquêtes HSE et mesures correctives.
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
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-sm shadow-lg shadow-rose-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Déclarer un Incident
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Jours Sans Accident</span>
            <HardHat className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-black text-emerald-400 mt-2">
            {stats.jours_sans_accident || 84} Jours
          </div>
          <div className="text-xs text-slate-500 mt-1">Objectif Zéro Accident</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Accidents Enregistrés</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_accidents_travail}
          </div>
          <div className="text-xs text-slate-500 mt-1">Exercice en cours</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Enquêtes en Cours</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-400 mt-2">
            {stats.investigations_en_cours}
          </div>
          <div className="text-xs text-slate-500 mt-1">Analyses des causes racines</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Arrêts de Travail</span>
            <AlertOctagon className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-black text-rose-400 mt-2">
            {stats.accidents_avec_arret}
          </div>
          <div className="text-xs text-slate-500 mt-1">Déclarations CNPS transmises</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">Réf. Incident</th>
                <th className="py-4 px-5">Type & Date</th>
                <th className="py-4 px-5">Lieu / Poste Quai</th>
                <th className="py-4 px-5">Description des Faits</th>
                <th className="py-4 px-5">Gravité</th>
                <th className="py-4 px-5">Déclarant</th>
                <th className="py-4 px-5 text-right">Statut Enquête</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-rose-500" />
                    Chargement des incidents portuaires...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucun incident signalé. Opérations portuaires conformes aux normes QHSE.
                  </td>
                </tr>
              ) : (
                items.map((inc) => (
                  <tr key={inc.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono text-xs font-bold text-rose-400">
                      {inc.reference}
                    </td>
                    <td className="py-4 px-5 text-xs">
                      <div className="font-bold text-white capitalize">{inc.type}</div>
                      <div className="text-slate-400">{inc.date}</div>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {inc.lieu}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300 max-w-sm truncate">
                      {inc.description}
                    </td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                        inc.gravite === 'grave'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          : inc.gravite === 'moyen'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {inc.gravite}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-400">
                      {inc.declarant}
                    </td>
                    <td className="py-4 px-5 text-right">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                        <CheckCircle2 className="w-3 h-3" /> {inc.statut}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Déclaration Incident */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-rose-400" /> Signaler un Incident Portuaire
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Type d'Événement</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-rose-500"
                  >
                    <option value="travail">Accident du Travail (Docker / Quai)</option>
                    <option value="avarie">Avarie Fret / Conteneur Endommagé</option>
                    <option value="equipement">Panne / Incident Engin de Manutention</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Niveau de Gravité</label>
                  <select
                    value={formData.gravite}
                    onChange={(e) => setFormData({ ...formData, gravite: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-rose-500"
                  >
                    <option value="faible">Faible (Sans arrêt)</option>
                    <option value="moyen">Moyen (Soins infirmerie)</option>
                    <option value="grave">Grave (Évacuation hospitalière)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Lieu Exact / Quai</label>
                <input
                  type="text"
                  required
                  value={formData.lieu}
                  onChange={(e) => setFormData({ ...formData, lieu: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-rose-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Description des Circonstances</label>
                <textarea
                  rows={3}
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-rose-500"
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
                  className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-sm font-bold shadow-lg shadow-rose-600/20 transition-all"
                >
                  Enregistrer l'Incident
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
