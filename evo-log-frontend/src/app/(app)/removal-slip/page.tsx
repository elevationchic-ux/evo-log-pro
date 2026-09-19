'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  FileCheck, Search, Plus, CheckCircle2, Clock, AlertTriangle,
  Truck, ArrowUpRight, RefreshCw, X, Warehouse, ShieldAlert
} from 'lucide-react';
import { removalSlipAPI } from '@/lib/api-client';

interface RemovalItem {
  id: number;
  numero_bon: string;
  client_id: number;
  entrepot_id: number;
  entrepot_nom?: string;
  date_sortie: string;
  statut: string;
  type_sortie: string;
  commande_reference?: string;
  nombre_lignes: number;
}

export default function RemovalSlipPage() {
  const [items, setItems] = useState<RemovalItem[]>([]);
  const [stats, setStats] = useState({
    total_bons_enlevement: 0,
    en_attente: 0,
    valides: 0,
    refuses: 0,
    quantite_totale_enlevee: 0,
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statutFilter, setStatutFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [validatingId, setValidatingId] = useState<number | null>(null);

  // Formulaire de saisie
  const [formData, setFormData] = useState({
    client_id: 1,
    entrepot_id: 1,
    type_sortie: 'enlevement',
    commande_reference: 'CMD-EXPORT-2026-44',
    notes: 'Enlèvement autorisé après dédouanement BAE',
    lignes: [
      {
        stock_id: 1,
        quantite_sortie: 50,
        prix_unitaire: 4500,
        numero_lot: 'LOT-2026-08',
        commentaires: 'Marchandise chargée sur camion LT-402-BB',
      }
    ]
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resList, resStats] = await Promise.allSettled([
        removalSlipAPI.getAll({
          search: search || undefined,
          statut: statutFilter || undefined
        }),
        removalSlipAPI.getStats()
      ]);

      if (resList.status === 'fulfilled' && resList.value.data) {
        setItems(resList.value.data.items || []);
      }
      if (resStats.status === 'fulfilled' && resStats.value.data) {
        setStats(resStats.value.data);
      }
    } catch (err) {
      console.error('Erreur chargement bons d\'enlèvement:', err);
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
      await removalSlipAPI.validate(id);
      await fetchData();
    } catch (err) {
      console.error('Erreur validation enlèvement:', err);
    } finally {
      setValidatingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await removalSlipAPI.create(formData);
      setIsModalOpen(false);
      await fetchData();
    } catch (err) {
      console.error('Erreur création bon d\'enlèvement:', err);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
            <FileCheck className="w-3.5 h-3.5" /> Bon à Enlever (BAE) & Déstockage
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            Bons d'Enlèvement Magasin (Removal Slips)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Délivrance des bons de sortie magasin, contrôle des quittances douanières et décrémentation des stocks.
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
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-sm shadow-lg shadow-amber-600/20 transition-all"
          >
            <Plus className="w-4 h-4" /> Créer un Bon d'Enlèvement
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Bons d'Enlèvement Émis</span>
            <FileCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {stats.total_bons_enlevement}
          </div>
          <div className="text-xs text-slate-500 mt-1">Autorisations de sortie</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>En Attente de Chargement</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 mt-2">
            {stats.en_attente}
          </div>
          <div className="text-xs text-slate-500 mt-1">Camions en cours de positionnement</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Enlèvements Validés</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 mt-2">
            {stats.valides}
          </div>
          <div className="text-xs text-slate-500 mt-1">Sorties effectives de l'enceinte</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Volume Total Enlevé</span>
            <Truck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white mt-2">
            {Number(stats.quantite_totale_enlevee).toLocaleString('fr-FR')} Colis
          </div>
          <div className="text-xs text-slate-500 mt-1">Déstockage certifié</div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Rechercher par N° bon, commande client..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statutFilter}
            onChange={(e) => setStatutFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
          >
            <option value="">Tous les statuts</option>
            <option value="valide">Enlevé & Validé</option>
            <option value="en_attente">En attente d'enlèvement</option>
            <option value="refuse">Refusé</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 font-semibold text-xs uppercase tracking-wider">
                <th className="py-4 px-5">N° Bon Enlèvement</th>
                <th className="py-4 px-5">Entrepôt Source</th>
                <th className="py-4 px-5">Date d'Enlèvement</th>
                <th className="py-4 px-5">Réf. Commande</th>
                <th className="py-4 px-5">Lignes</th>
                <th className="py-4 px-5">Statut</th>
                <th className="py-4 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-amber-500" />
                    Chargement des bons d'enlèvement...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    Aucun bon d'enlèvement enregistré.
                  </td>
                </tr>
              ) : (
                items.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-5 font-mono">
                      <div className="font-bold text-amber-400">{b.numero_bon}</div>
                    </td>
                    <td className="py-4 px-5">
                      <div className="font-semibold text-white flex items-center gap-1.5">
                        <Warehouse className="w-3.5 h-3.5 text-amber-400" /> {b.entrepot_nom || 'MAGASIN 3 SOUS DOUANE'}
                      </div>
                    </td>
                    <td className="py-4 px-5 text-xs text-slate-300">
                      {b.date_sortie || 'Aujourd\'hui'}
                    </td>
                    <td className="py-4 px-5 font-mono text-xs text-cyan-400">
                      {b.commande_reference || 'CMD-DIRECTE'}
                    </td>
                    <td className="py-4 px-5 text-xs">
                      {b.nombre_lignes} article(s)
                    </td>
                    <td className="py-4 px-5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        b.statut === 'valide'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {b.statut === 'valide' ? (
                          <>
                            <CheckCircle2 className="w-3 h-3" /> Enlevé
                          </>
                        ) : (
                          <>
                            <Clock className="w-3 h-3" /> En attente
                          </>
                        )}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      {b.statut !== 'valide' && (
                        <button
                          onClick={() => handleValidate(b.id)}
                          disabled={validatingId === b.id}
                          className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold shadow transition-all disabled:opacity-50"
                        >
                          {validatingId === b.id ? 'Déstockage...' : 'Valider & Déstocker'}
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

      {/* Modal Création Bon d'Enlèvement */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-amber-400" /> Émettre un Bon d'Enlèvement
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
                <label className="block text-xs font-semibold text-slate-400 mb-1">Client Destinataire (ID)</label>
                <input
                  type="number"
                  required
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Entrepôt Source</label>
                <select
                  value={formData.entrepot_id}
                  onChange={(e) => setFormData({ ...formData, entrepot_id: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option value="1">MAG3 - Magasin Cale 3 (Zone Sous Douane)</option>
                  <option value="2">MAG1 - Magasin Conteneurs Pleins</option>
                  <option value="3">MAG2 - Parc Vrac</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Quantité à Enlever</label>
                  <input
                    type="number"
                    required
                    value={formData.lignes[0].quantite_sortie}
                    onChange={(e) => {
                      const newLignes = [...formData.lignes];
                      newLignes[0].quantite_sortie = parseFloat(e.target.value) || 0;
                      setFormData({ ...formData, lignes: newLignes });
                    }}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Réf. Commande / Dossier</label>
                  <input
                    type="text"
                    required
                    value={formData.commande_reference}
                    onChange={(e) => setFormData({ ...formData, commande_reference: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Notes / Réf. Quittance Douane (BAE)</label>
                <textarea
                  rows={2}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
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
                  className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-bold shadow-lg shadow-amber-600/20 transition-all"
                >
                  Émettre le Bon d'Enlèvement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
