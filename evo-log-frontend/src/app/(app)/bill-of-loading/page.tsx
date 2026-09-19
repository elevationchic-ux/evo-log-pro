'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText, Search, Plus, CheckCircle2, Clock, AlertTriangle,
  Ship, Anchor, Download, RefreshCw, Filter, Eye, ShieldCheck, X
} from 'lucide-react';
import { billOfLoadingAPI } from '@/lib/api-client';

interface BLItem {
  id: number;
  numero_bsc: string;
  numero_connaisse: string;
  navire: string;
  voyage?: string;
  port_chargement: string;
  port_dechargement: string;
  date_emission?: string;
  agent: string;
  importateur: string;
  poids_brut_tonnes: number;
  valeur_caf: number;
  devise: string;
  statut: string;
  reference_cncc?: string;
}

export default function BillOfLoadingPage() {
  const [items, setItems] = useState<BLItem[]>([]);
  const [stats, setStats] = useState({
    total_connaissements: 0,
    en_attente_validation: 0,
    valides: 0,
    tonnage_total_tonnes: 0,
    valeur_caf_totale: 0,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statutFilter, setStatutFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [validatingId, setValidatingId] = useState<number | null>(null);

  // Formulaire de création
  const [formData, setFormData] = useState({
    numero_connaisse: '',
    navire: '',
    voyage: '',
    port_chargement: 'Anvers (BEANT)',
    port_dechargement: 'Douala (CMDLA)',
    agent: '',
    importateur: '',
    poids_brut_tonnes: 150.0,
    valeur_caf: 85000.0,
    devise: 'USD',
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        billOfLoadingAPI.getAll({ search: search || undefined, statut: statutFilter || undefined }),
        billOfLoadingAPI.getStats()
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement connaissements:', err);
    } finally {
      setLoading(false);
    }
  }, [search, statutFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleValidate = async (id: number) => {
    try {
      setValidatingId(id);
      await billOfLoadingAPI.validate(id);
      await fetchData();
    } catch (err) {
      console.error('Erreur validation BSC:', err);
    } finally {
      setValidatingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await billOfLoadingAPI.create(formData);
      setIsModalOpen(false);
      setFormData({
        numero_connaisse: '',
        navire: '',
        voyage: '',
        port_chargement: 'Anvers (BEANT)',
        port_dechargement: 'Douala (CMDLA)',
        agent: '',
        importateur: '',
        poids_brut_tonnes: 150.0,
        valeur_caf: 85000.0,
        devise: 'USD',
      });
      await fetchData();
    } catch (err) {
      console.error('Erreur création connaissement:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Anchor className="w-3.5 h-3.5" /> Fret Maritime & CNCC Cameroun
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Connaissements Maritimes & BSC
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Gestion électronique des connaissements (Bill of Lading) et Bulletins de Soumission Connaissement.
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
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Nouveau B/L & BSC
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Connaissements</span>
            <FileText className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_connaissements}
          </div>
          <div className="text-xs text-slate-500 mt-1">Émis et enregistrés au port</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>En Attente Validation</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            {stats.en_attente_validation}
          </div>
          <div className="text-xs text-slate-500 mt-1">En cours d'homologation CNCC</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>BSC Validés & Conformes</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {stats.valides}
          </div>
          <div className="text-xs text-slate-500 mt-1">Prêts pour le dédouanement</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Tonnage Brut Déclaré</span>
            <Ship className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {Number(stats.tonnage_total_tonnes).toLocaleString('fr-FR')} T
          </div>
          <div className="text-xs text-slate-500 mt-1">Valeur CAF : ${(stats.valeur_caf_totale || 0).toLocaleString()}</div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher par B/L, BSC, navire, importateur..."
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
            <option value="en_attente">En attente</option>
            <option value="valide">Validé CNCC</option>
            <option value="expire">Expiré</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">N° Connaissement & BSC</th>
                <th className="py-4 px-5">Navire & Voyage</th>
                <th className="py-4 px-5">Trajet Maritime</th>
                <th className="py-4 px-5">Importateur & Agent</th>
                <th className="py-4 px-5">Poids & Valeur</th>
                <th className="py-4 px-5">Statut CNCC</th>
                <th className="py-4 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-500" />
                    Chargement des connaissements maritimes...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucun connaissement trouvé dans la base de données.
                  </td>
                </tr>
              ) : (
                items.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono">
                      <div className="font-bold text-cyan-400">{b.numero_connaisse}</div>
                      <div className="text-xs text-slate-400">{b.numero_bsc}</div>
                    </td>
                    <td className="py-4 px-5">
                      <div className="font-semibold text-white flex items-center gap-1.5">
                        <Ship className="w-3.5 h-3.5 text-cyan-400" /> {b.navire}
                      </div>
                      <div className="text-xs text-slate-400">Voyage: {b.voyage || 'Non spécifié'}</div>
                    </td>
                    <td className="py-4 px-5 text-xs">
                      <div><span className="text-slate-500">De :</span> {b.port_chargement}</div>
                      <div><span className="text-slate-500">À :</span> {b.port_dechargement}</div>
                    </td>
                    <td className="py-4 px-5 text-xs">
                      <div className="font-semibold text-slate-200">{b.importateur}</div>
                      <div className="text-slate-400">Agent : {b.agent}</div>
                    </td>
                    <td className="py-4 px-5 font-mono text-xs">
                      <div>{b.poids_brut_tonnes} Tonnes</div>
                      <div className="text-slate-400">{b.valeur_caf.toLocaleString()} {b.devise}</div>
                    </td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        b.statut === 'valide'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {b.statut === 'valide' ? (
                          <>
                            <CheckCircle2 className="w-3 h-3" /> Validé CNCC
                          </>
                        ) : (
                          <>
                            <Clock className="w-3 h-3" /> En attente
                          </>
                        )}
                      </span>
                      {b.reference_cncc && (
                        <div className="text-[10px] text-slate-500 font-mono mt-0.5">{b.reference_cncc}</div>
                      )}
                    </td>
                    <td className="py-4 px-5 text-right">
                      {b.statut !== 'valide' && (
                        <button
                          onClick={() => handleValidate(b.id)}
                          disabled={validatingId === b.id}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow transition-all disabled:opacity-50"
                        >
                          {validatingId === b.id ? 'Validation...' : 'Valider CNCC'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Création B/L & BSC */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Anchor className="w-5 h-5 text-cyan-400" /> Nouveau Connaissement & BSC
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
                  <label className="block text-xs font-semibold text-slate-400 mb-1">N° Connaissement (B/L)</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: MSCUDLA-2026-908"
                    value={formData.numero_connaisse}
                    onChange={(e) => setFormData({ ...formData, numero_connaisse: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Nom du Navire</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: MSC MONICA"
                    value={formData.navire}
                    onChange={(e) => setFormData({ ...formData, navire: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Port de Chargement</label>
                  <input
                    type="text"
                    required
                    value={formData.port_chargement}
                    onChange={(e) => setFormData({ ...formData, port_chargement: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Port de Déchargement</label>
                  <input
                    type="text"
                    required
                    value={formData.port_dechargement}
                    onChange={(e) => setFormData({ ...formData, port_dechargement: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Importateur / Destinataire</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: CAMLAIT S.A."
                    value={formData.importateur}
                    onChange={(e) => setFormData({ ...formData, importateur: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Agent / Transitaire</label>
                  <input
                    type="text"
                    required
                    placeholder="ex: BOLLORE TRANSIT DLA"
                    value={formData.agent}
                    onChange={(e) => setFormData({ ...formData, agent: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Poids Brut (Tonnes)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.poids_brut_tonnes}
                    onChange={(e) => setFormData({ ...formData, poids_brut_tonnes: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Valeur CAF ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.valeur_caf}
                    onChange={(e) => setFormData({ ...formData, valeur_caf: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
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
                  className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold shadow-lg shadow-cyan-600/20 transition-all"
                >
                  Enregistrer et Émettre le BSC
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
