'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  PackageCheck, Search, Plus, CheckCircle2, Clock, AlertTriangle,
  Warehouse, Boxes, RefreshCw, X, ArrowDownRight, Layers
} from 'lucide-react';
import { receptionMag3API } from '@/lib/api-client';

interface ReceptionItem {
  id: number;
  numero_bon: string;
  fournisseur_id: number;
  entrepot_id: number;
  entrepot_nom?: string;
  date_reception: string;
  statut: string;
  nombre_lignes: number;
  notes?: string;
}

export default function ReceptionMag3Page() {
  const [items, setItems] = useState<ReceptionItem[]>([]);
  const [stats, setStats] = useState({
    total_receptions_mag3: 0,
    en_cours_controle: 0,
    validees: 0,
    refusees: 0,
    volume_total_receptionne: 0,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statutFilter, setStatutFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [validatingId, setValidatingId] = useState<number | null>(null);

  // Formulaire de saisie
  const [formData, setFormData] = useState({
    fournisseur_id: 1,
    entrepot_id: 1,
    notes: 'Réception dépotage conteneur maritime quai MAG3',
    lignes: [
      {
        stock_id: 1,
        quantite_recue: 120,
        quantite_commandee: 120,
        prix_unitaire: 4500,
        emplacement: 'MAG3-ZONE-A1',
        numero_lot: 'LOT-2026-08',
        commentaires: 'Marchandise conforme sans avarie',
      }
    ]
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        receptionMag3API.getAll({
          search: search || undefined,
          statut: statutFilter || undefined
        }),
        receptionMag3API.getStats()
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement réceptions MAG3:', err);
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
      await receptionMag3API.validate(id);
      await fetchData();
    } catch (err) {
      console.error('Erreur validation réception MAG3:', err);
    } finally {
      setValidatingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await receptionMag3API.create(formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur création réception:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Warehouse className="w-3.5 h-3.5" /> Magasin Sous Douane • Port de Douala
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Réceptions Fret Magasin 3 (MAG3)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Dépotage, pointage contradictoire, contrôle qualité et mise en stock sous douane portuaire.
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
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Réceptionner du Fret
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Réceptions MAG3</span>
            <Boxes className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_receptions_mag3}
          </div>
          <div className="text-xs text-slate-500 mt-1">Opérations enregistrées</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>En Cours de Pointage</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            {stats.en_cours_controle}
          </div>
          <div className="text-xs text-slate-500 mt-1">Inspection quai ou cale</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Réceptions Confirmées</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {stats.validees}
          </div>
          <div className="text-xs text-slate-500 mt-1">Stocks réels incrémentés</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Unités Réceptionnées</span>
            <PackageCheck className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {Number(stats.volume_total_receptionne).toLocaleString('fr-FR')} Colis
          </div>
          <div className="text-xs text-slate-500 mt-1">Volume inventorié</div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher par N° bon, notes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statutFilter}
            onChange={(e) => setStatutFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Tous les statuts</option>
            <option value="valide">Validé en stock</option>
            <option value="en_attente">En cours de contrôle</option>
            <option value="refuse">Refusé / Écart</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">N° Bon Réception</th>
                <th className="py-4 px-5">Entrepôt & Quai</th>
                <th className="py-4 px-5">Date d'Entrée</th>
                <th className="py-4 px-5">Articles</th>
                <th className="py-4 px-5">Notes de Dépotage</th>
                <th className="py-4 px-5">Statut</th>
                <th className="py-4 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
                    Chargement des réceptions Magasin 3...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucune réception enregistrée au Magasin 3.
                  </td>
                </tr>
              ) : (
                items.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono">
                      <div className="font-bold text-indigo-400">{r.numero_bon}</div>
                    </td>
                    <td className="py-4 px-5">
                      <div className="font-semibold text-white flex items-center gap-1.5">
                        <Warehouse className="w-3.5 h-3.5 text-indigo-400" /> {r.entrepot_nom || 'MAGASIN 3 SOUS DOUANE'}
                      </div>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {r.date_reception || 'Aujourd\'hui'}
                    </td>
                    <td className="py-4 px-5">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-800 text-xs font-semibold text-slate-300">
                        <Layers className="w-3 h-3 text-indigo-400" /> {r.nombre_lignes} ligne(s)
                      </span>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-400 max-w-xs truncate">
                      {r.notes || 'Dépotage normal'}
                    </td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        r.statut === 'valide'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {r.statut === 'valide' ? (
                          <>
                            <CheckCircle2 className="w-3 h-3" /> Validé en stock
                          </>
                        ) : (
                          <>
                            <Clock className="w-3 h-3" /> En cours
                          </>
                        )}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      {r.statut !== 'valide' && (
                        <button
                          onClick={() => handleValidate(r.id)}
                          disabled={validatingId === r.id}
                          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow transition-all disabled:opacity-50"
                        >
                          {validatingId === r.id ? 'Validation...' : 'Valider & Stocker'}
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

      {/* Modal Réception Fret */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <PackageCheck className="w-5 h-5 text-indigo-400" /> Réception de Marchandise (MAG3)
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
                <label className="block text-xs font-semibold text-slate-400 mb-1">ID Fournisseur / Armateur</label>
                <input
                  type="number"
                  required
                  value={formData.fournisseur_id}
                  onChange={(e) => setFormData({ ...formData, fournisseur_id: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Entrepôt Cible</label>
                <select
                  value={formData.entrepot_id}
                  onChange={(e) => setFormData({ ...formData, entrepot_id: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="1">MAG3 - Magasin Cale 3 (Zone Sous Douane)</option>
                  <option value="2">MAG1 - Magasin Conteneurs Pleins</option>
                  <option value="3">MAG2 - Parc Vrac & Équipements Lourds</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Quantité Réceptionnée</label>
                  <input
                    type="number"
                    required
                    value={formData.lignes[0].quantite_recue}
                    onChange={(e) => {
                      const newLignes = [...formData.lignes];
                      newLignes[0].quantite_recue = parseFloat(e.target.value) || 0;
                      setFormData({ ...formData, lignes: newLignes });
                    }}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Emplacement Magasin</label>
                  <input
                    type="text"
                    required
                    value={formData.lignes[0].emplacement}
                    onChange={(e) => {
                      const newLignes = [...formData.lignes];
                      newLignes[0].emplacement = e.target.value;
                      setFormData({ ...formData, lignes: newLignes });
                    }}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Observations & État Conteneur</label>
                <textarea
                  rows={2}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold shadow-lg shadow-indigo-600/20 transition-all"
                >
                  Enregistrer la Réception
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
