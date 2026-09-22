'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Boxes, Search, Plus, CheckCircle2, Clock, AlertTriangle,
  ArrowDownRight, ArrowUpRight, RefreshCw, X, ShieldAlert, Wrench
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface ContainerItem {
  id: number;
  numero_conteneur: string;
  type_conteneur: string;
  taille: string;
  statut: string;
  port_actuel: string;
  emplacement?: string;
  date_dernier_mouvement?: string;
}

export default function ContainerLifecyclePage() {
  const [items, setItems] = useState<ContainerItem[]>([]);
  const [stats, setStats] = useState({
    total_conteneurs: 0,
    au_quai: 0,
    en_detention_client: 0,
    dommages_signales: 0,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statutFilter, setStatutFilter] = useState('');
  const [isGateInModalOpen, setIsGateInModalOpen] = useState(false);

  // Formulaire Gate-In
  const [gateInForm, setGateInForm] = useState({
    numero_conteneur: '',
    type_conteneur: 'DRY',
    taille: '40',
    port: 'PAD Douala',
    emplacement: 'TERRE-PLEIN-T3',
    navire: 'CMA CGM MONTE CARLO',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        apiClient.get('/api/v1/container-lifecycle', {
          params: { search: search || undefined, statut: statutFilter || undefined }
        }),
        apiClient.get('/api/v1/container-lifecycle/stats')
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement cycle de vie conteneurs:', err);
    } finally {
      setLoading(false);
    }
  }, [search, statutFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGateIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/api/v1/container-lifecycle/gate-in', gateInForm);
      setIsGateInModalOpen(false);
      setGateInForm({
        numero_conteneur: '',
        type_conteneur: 'DRY',
        taille: '40',
        port: 'PAD Douala',
        emplacement: 'TERRE-PLEIN-T3',
        navire: 'CMA CGM MONTE CARLO',
      });
      await fetchData();
    } catch (err) {
      console.error('Erreur enregistrement Gate-In:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Boxes className="w-3.5 h-3.5" /> Traçabilité EVP & Gestion de Parc Conteneurs
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Cycle de Vie des Conteneurs (Container Lifecycle)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Contrôle des mouvements Gate-In / Gate-Out, temps de franchise terre-plein, détentions et constats de dommages (EIR).
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
            onClick={() => setIsGateInModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Déclarer Entrée Gate-In
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Parc Conteneurs Sous Gestion</span>
            <Boxes className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_conteneurs || items.length}
          </div>
          <div className="text-xs text-slate-500 mt-1">Totalité des unités tracées</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Conteneurs au Quai (PAD/PAK)</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {stats.au_quai}
          </div>
          <div className="text-xs text-slate-500 mt-1">En attente d'enlèvement</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Détention Client (Surestaries)</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            {stats.en_detention_client}
          </div>
          <div className="text-xs text-slate-500 mt-1">Hors franchise armateur</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Dommages / Avaries (EIR)</span>
            <Wrench className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-black text-rose-400 mt-2">
            {stats.dommages_signales}
          </div>
          <div className="text-xs text-slate-500 mt-1">Fiches d'inspection non closes</div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher conteneur (ex: MSKU-908123)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statutFilter}
            onChange={(e) => setStatutFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value="">Tous les statuts</option>
            <option value="AU_QUAI">Au Quai / Magasin</option>
            <option value="EMBARQUE">Embarqué sur navire</option>
            <option value="DEGOTE">En livraison terrestre</option>
            <option value="RESTITUE">Restitué au parc vide</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">N° Conteneur (ISO)</th>
                <th className="py-4 px-5">Taille & Type</th>
                <th className="py-4 px-5">Port d'Attache</th>
                <th className="py-4 px-5">Emplacement Terre-Plein</th>
                <th className="py-4 px-5">Dernier Mouvement</th>
                <th className="py-4 px-5 text-right">Statut Opérationnel</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-500" />
                    Chargement des conteneurs...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    Aucun conteneur répertorié.
                  </td>
                </tr>
              ) : (
                items.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono font-bold text-cyan-400">
                      {c.numero_conteneur}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {c.taille}' {c.type_conteneur}
                    </td>
                    <td className="py-4 px-5 text-xs text-white">
                      {c.port_actuel}
                    </td>
                    <td className="py-4 px-5 font-mono text-xs text-slate-400">
                      {c.emplacement || 'Quai 14 - Pile B'}
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-400">
                      {c.date_dernier_mouvement || 'Aujourd\'hui'}
                    </td>
                    <td className="py-4 px-5 text-right">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        c.statut === 'AU_QUAI'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      }`}>
                        {c.statut}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Gate-In */}
      {isGateInModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Boxes className="w-5 h-5 text-cyan-400" /> Enregistrement Entrée (Gate-In)
              </h2>
              <button
                onClick={() => setIsGateInModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleGateIn} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">N° Conteneur (ISO 6346)</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: MSKU-908123"
                    value={gateInForm.numero_conteneur}
                    onChange={(e) => setGateInForm({ ...gateInForm, numero_conteneur: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Taille</label>
                  <select
                    value={gateInForm.taille}
                    onChange={(e) => setGateInForm({ ...gateInForm, taille: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  >
                    <option value="20">20 Pieds (1 EVP)</option>
                    <option value="40">40 Pieds (2 EVP / High Cube)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Port de Réception</label>
                  <input
                    type="text"
                    required
                    value={gateInForm.port}
                    onChange={(e) => setGateInForm({ ...gateInForm, port: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Emplacement Terre-Plein</label>
                  <input
                    type="text"
                    required
                    value={gateInForm.emplacement}
                    onChange={(e) => setGateInForm({ ...gateInForm, emplacement: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Navire Débarquant</label>
                <input
                  type="text"
                  required
                  value={gateInForm.navire}
                  onChange={(e) => setGateInForm({ ...gateInForm, navire: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsGateInModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold shadow-lg shadow-cyan-600/20 transition-all"
                >
                  Valider le Gate-In
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
